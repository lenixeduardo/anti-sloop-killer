#!/usr/bin/env python3
"""Structural repair proposals addressed by stable DOM/JSX ids.

Generate a safe exact-diff proposal from parsed elements; reuse apply_changes for
approval, baseline hashes, isolated writes, acceptance checks and rollback.
Unlike generic regex search, element selection is structural and uniqueness is required.

Proposals are JSON with `edits`: [{path, id, operation, attribute?, value?, markup?, finding_id}].
Supported operations: set_attribute, remove_attribute, replace_element.
The agent MUST supply justified replacement content; this tool never invents design.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from apply_changes import apply, prepare

SUFFIXES = {'.html', '.htm', '.vue', '.astro', '.svelte', '.jsx', '.tsx'}
ATTR_NAME = re.compile(r'^[a-zA-Z_:][a-zA-Z0-9_:.-]*$')


class TagLocator(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.line_offsets = [0]
        for match in re.finditer(r'\n', source):
            self.line_offsets.append(match.end())
        self.entries = []
        self.stack = []
        self.feed(source)
        self.close()

    def position_offset(self):
        line, col = self.getpos()
        return self.line_offsets[line-1] + col

    def handle_starttag(self, tag, attrs):
        start = self.position_offset()
        original = self.get_starttag_text()
        entry = dict(tag=tag, attrs=dict(attrs), start=start, opening_end=start+len(original), end=None)
        self.entries.append(entry)
        if tag not in {'img','br','hr','meta','link','input','source','area','embed','wbr','param','track','col','base'}:
            self.stack.append(entry)
        else:
            entry['end'] = entry['opening_end']

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag,attrs)
        if self.stack and self.stack[-1]['start'] == self.position_offset():
            self.stack.pop()['end'] = self.position_offset()+len(self.get_starttag_text())

    def handle_endtag(self, tag):
        end = self.source.find('>', self.position_offset())
        if end == -1:
            return
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i]['tag'] == tag:
                self.stack[i]['end'] = end+1
                del self.stack[i:]
                break


def find_html_element(source: str, identifier: str) -> dict:
    # TagLocator is used only on literal HTML-like templates; JS content is not
    # considered a valid match unless it parses as a literal element with that id.
    entries = [e for e in TagLocator(source).entries if e['attrs'].get('id') == identifier]
    if len(entries) != 1:
        raise ValueError(f'Expected exactly one HTML element id={identifier!r}; got {len(entries)}')
    return entries[0]


def find_jsx_element(source: str, identifier: str) -> dict:
    helper=Path(__file__).with_name('jsx_target.cjs')
    proc=subprocess.run(['node',str(helper)],input=json.dumps({'source':source,'id':identifier}),
                        capture_output=True,text=True,timeout=15)
    if proc.returncode:
        raise ValueError('JSX parser rejected target: '+proc.stderr.strip())
    return json.loads(proc.stdout)


def update_opening(opening: str, operation: str, attribute: str, value: str|None) -> str:
    if not ATTR_NAME.fullmatch(attribute) or attribute.lower().startswith('on'):
        raise ValueError('Unsafe/invalid attribute name: '+attribute)
    # Only unambiguous static attributes. JSX expressions in other attributes remain intact.
    pattern=re.compile(r'(?<![\w:.-])'+re.escape(attribute)+r'\s*=\s*(?:"[^"<>]*"|\'[^\'<>]*\')')
    matches=list(pattern.finditer(opening))
    if len(matches)>1:
        raise ValueError('Duplicate attribute; manual repair required')
    if operation=='remove_attribute':
        if len(matches)!=1:
            raise ValueError('Attribute is missing or dynamic; cannot remove safely')
        m=matches[0]
        return opening[:m.start()]+opening[m.end():]
    if not isinstance(value,str) or any(c in value for c in '\n\r\0<>"'):
        raise ValueError('Attribute value must be plain safely quoted text')
    if attribute.lower() in ('href','src','action','formaction') and re.match(r'^\s*(?:javascript|data|vbscript)\s*:',value,re.I):
        raise ValueError('Unsafe URL scheme')
    encoded=value.replace('&','&amp;')
    part=f'{attribute}="{encoded}"'
    if len(matches)==1:
        return opening[:matches[0].start()]+part+opening[matches[0].end():]
    if not opening.endswith('>'):
        raise ValueError('Invalid opening tag')
    insert_at = len(opening)-2 if opening.endswith('/>') else len(opening)-1
    return opening[:insert_at].rstrip()+ ' '+part+opening[insert_at:]


def plan(project:Path, proposal:dict) -> dict:
    if project.is_symlink() or not project.is_dir():
        raise ValueError('Invalid project directory')
    root=project.resolve()
    edits=proposal.get('edits')
    if not isinstance(edits,list) or not 1<=len(edits)<=50:
        raise ValueError('Provide 1..50 structural edits')
    staged={}
    for edit in edits:
        if not isinstance(edit,dict): raise ValueError('Edit must be an object')
        name=edit.get('path'); identifier=edit.get('id')
        if not isinstance(name,str) or not name or '\\' in name or '\0' in name: raise ValueError('Invalid path')
        rel=Path(name)
        if rel.is_absolute() or '..' in rel.parts or '.' in rel.parts or rel.suffix not in SUFFIXES:
            raise ValueError('Invalid or unsupported source path')
        path=root/rel
        if any(p.is_symlink() for p in (path,*path.parents) if p!=root and root in p.parents):
            raise ValueError('Symlink refused')
        if not path.is_file() or root not in path.resolve().parents:raise ValueError('File missing/outside project')
        if not isinstance(identifier,str) or not identifier or len(identifier)>160:
            raise ValueError('Each edit needs a stable literal element id')
        initial=path.read_bytes()
        if len(initial)>2_000_000:raise ValueError('Source file too large')
        digest=hashlib.sha256(initial).hexdigest()
        if edit.get('expected_sha256')!=digest:
            raise ValueError('Baseline hash mismatch')
        state=staged.setdefault(name,dict(original=initial.decode('utf-8'),current=initial.decode('utf-8'),sha=digest))
        source=state['current']
        is_jsx=path.suffix in ('.tsx','.jsx')
        node=find_jsx_element(source,identifier) if is_jsx else find_html_element(source,identifier)
        operation=edit.get('operation')
        if operation in ('set_attribute','remove_attribute'):
            start=node['opening_start'] if is_jsx else node['start']
            end=node['opening_end']
            replacement=update_opening(source[start:end],operation,edit.get('attribute',''),edit.get('value'))
        elif operation=='replace_element':
            start,end=node['start'],node.get('end')
            replacement=edit.get('markup')
            if end is None or not isinstance(replacement,str) or not replacement.strip():
                raise ValueError('Replacement must provide complete literal markup and a closed element')
            # Full-element replacement must preserve target identity to make future fixes traceable.
            if is_jsx:
                target=find_jsx_element(replacement,identifier)
                if target['start'] != len(replacement)-len(replacement.lstrip()) or target['end'] != len(replacement.rstrip()):
                    raise ValueError('Replacement must be a single JSX element with same id')
            else:
                target=find_html_element(replacement,identifier)
                if target['end'] is None or replacement[:target['start']].strip() or replacement[target['end']:].strip():
                    raise ValueError('Replacement must be one closed element with same id')
        else: raise ValueError('Unsupported operation')
        old=source[start:end]
        if old==replacement: raise ValueError('Edit does not change source')
        state['current']=source[:start]+replacement+source[end:]
    # One exact replacement per file is sufficient to keep transforms atomic.
    return {'changes':[{'path':name,'finding_id':'STRUCTURAL', 'expected_sha256':state['sha'],
           'search':state['original'],'replace':state['current']} for name,state in staged.items()]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project',type=Path)
    parser.add_argument('proposal',type=Path)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--check',action='append',default=[])
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    try:
        doc=json.loads(args.proposal.read_text(encoding='utf-8'))
        result=apply(args.project,plan(args.project,doc),approved=args.apply,checks=[shlex.split(x) for x in args.check])
        payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(payload,encoding='utf-8')
        else:print(payload)
        return 0 if result['status'] in ('preview','applied_verified','applied_unverified') else 1
    except (ValueError,OSError,json.JSONDecodeError,subprocess.SubprocessError) as e:
        print('ERROR: '+str(e),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
