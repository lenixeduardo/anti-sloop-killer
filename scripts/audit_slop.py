#!/usr/bin/env python3
"""Read-only, deterministic frontend prescreen. Findings are hypotheses, not a slop score.

Use --format json to integrate with an agent; the separate browser audit examines the
rendered application. This scanner has no network, deletion, or rewrite operations.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from audit_templates import scan_template, scan_css
from false_positive_guard import guard_report, load_json, MAPPINGS

SUFFIXES = {'.tsx', '.jsx', '.ts', '.js', '.mjs', '.cjs', '.css', '.scss', '.sass', '.html', '.vue', '.svelte', '.astro', '.mdx'}
SKIP = {'node_modules', '.next', 'dist', 'build', 'coverage', '.git', 'vendor', '.nuxt', '.svelte-kit', '.turbo', '.astro', '.output', '.vercel', '.cache', '__pycache__', 'playwright-report', 'test-results'}
LIMIT_BYTES = 2_000_000

# Explicit provenance: each rule ID exists in references/rules.json.
DETECTORS = [
    ('GRADIENT_TEXT', r'(?:bg-clip-text[^\n]{0,120}text-transparent|text-transparent[^\n]{0,120}bg-clip-text|background-clip\s*:\s*text)', 1, ('IM-016','UH-004'), 'P2', 'medium', 'Verificar contraste, significado e identidade; não proibir gradientes.'),
    ('BLUE_VIOLET_GRADIENT', r'(?:from-(?:blue|indigo)-\d{2,3}[^\n]{0,150}to-(?:purple|violet|fuchsia)-\d{2,3}|linear-gradient\([^)]{0,200}#(?:2563eb|6366f1)[^)]{0,160}#(?:8b5cf6|a855f7))', 1, ('SA-013','IM-013','UH-003'), 'P3', 'low', 'Padrão comum; só corrigir se houver evidência de falta de identidade.'),
    ('UNIVERSAL_ROUNDING', r'\brounded-(?:2xl|3xl|full)\b', 4, ('SA-037','UH-006'), 'P3','low','Repetição de raios grandes: avaliar contexto e marca.'),
    ('OVERUSED_CENTERING', r'\btext-center\b', 5, ('IM-019','SA-028'), 'P3','low','Avaliar se centralização prejudica leitura ou hierarquia.'),
    ('REPEATED_THREE_COLUMN_GRID', r'\b(?:grid-cols-3|grid-template-columns\s*:\s*repeat\(3)\b', 3, ('SA-029','UH-010'),'P3','low','Avaliar variedade de layout conforme o conteúdo.'),
    ('ANIMATE_BOUNCE', r'\banimate-bounce\b|cubic-bezier\(\s*0\.68\s*,\s*-0\.55',1,('IM-026',),'P3','low','Checar intenção e movimento reduzido.'),
    ('EXCESSIVE_PULSE',r'\banimate-pulse\b',3,('SA-044',),'P3','low','Confirmar estados de loading reais.'),
    ('BACKDROP_BLUR_EVERYWHERE',r'\bbackdrop-blur(?:-[a-z0-9]+)?\b|backdrop-filter\s*:\s*blur\(',4,('IM-002',),'P3','low','Glassmorphism não é defeito automático.'),
    ('EXCESSIVE_IMPORTANT',r'!important\b',4,('NX-045',),'P2','low','Revisar especificidade CSS e manutenção.'),
    ('LIFT_ON_HOVER',r'\bhover:-translate-y-(?:\d+|px)\b|:hover\s*\{[^}]{0,180}translateY\s*\(\s*-',4,('UC-026',),'P3','low','Repetição de lift; comparar com direção aprovada.'),
    ('EMOJI_AS_ICON_CANDIDATE',r'(?:<(?:span|button|div)\b[^>]*>\s*[\U0001F300-\U0001FAFF][^<]{0,6}<|[\'\"][\U0001F300-\U0001FAFF][\'\"])',1,('UH-008','UC-034'),'P2','medium','Ícone em emoji pode violar diretrizes; revisar contexto.'),
    ('REPEATED_TRANSITION_ALL',r'\btransition-all\b',6,('SA-052',),'P3','low','Animar apenas propriedades necessárias.'),
    ('FIXED_VIEWPORT_HEIGHT',r'\bh-screen\b|height\s*:\s*100vh',3,(),'P2','low','Checar corte de conteúdo e teclado mobile.'),
    ('EXCESSIVE_Z_INDEX',r'\bz-\[?(?:9999|99999)\]?\b|z-index\s*:\s*9999',2,('NX-045',),'P2','low','Checar contexto de empilhamento e modais.'),
    ('PLACEHOLDER_TEXT',r'\b(?:lorem ipsum|your (?:amazing |awesome )?(?:tagline|headline) here|coming soon)\b',1,('NX-043',),'P2','medium','Texto provisório pode ter chegado à produção.'),
]

# Do not use regex on raw source: comments can contain entire fake JSX/CSS examples.
# Retain strings, including className and href values, but blank comments preserving
# newlines and offsets. This is a lexical prepass, not a full language parser.
def mask_comments(source: str, filename: str='index.tsx') -> str:
    chars = list(source)
    n = len(source)
    i = 0
    state = 'code'
    quote = ''
    js_file = Path(filename).suffix.lower() in {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.mdx'}
    while i < n:
        c = source[i]
        nxt = source[i:i+4]
        if state == 'string':
            if c == '\\':
                i += 2
                continue
            if c == quote:
                state = 'code'
            i += 1
            continue
        if nxt == '<!--':
            end = source.find('-->', i+4)
            j = n if end < 0 else end+3
            for k in range(i,j):
                if source[k] != '\n': chars[k] = ' '
            i = j
            continue
        if source[i:i+2] == '/*':
            end = source.find('*/', i+2)
            j = n if end < 0 else end+2
            for k in range(i,j):
                if source[k] != '\n': chars[k] = ' '
            i = j
            continue
        if source[i:i+2] == '//' and (i == 0 or source[i-1] != ':'):
            # Only treat // as a comment in JS-like contexts. In a CSS url or an
            # HTML attribute its presence may be legitimate, so limit to line-leading
            # comments or // following statement punctuation.
            prefix = source[source.rfind('\n',0,i)+1:i].strip()
            if js_file or not prefix or prefix.endswith((';','{','}','(',')',',')):
                end = source.find('\n', i)
                j = n if end < 0 else end
                for k in range(i,j): chars[k] = ' '
                i=j
                continue
        if c in ('"', "'", '`'):
            quote=c
            state='string'
        i += 1
    return ''.join(chars)

TAG_OPEN_RE = re.compile(r'<\s*(?P<tag>img|Image|a|Link|button|div|span|video|iframe)\b', re.I)

def iter_tags(code: str):
    """Yield tag start, tag name and attributes; don't terminate at arrow => or > in JSX expressions."""
    for match in TAG_OPEN_RE.finditer(code):
        i=match.end()
        depth=0
        quote=None
        while i<len(code):
            c=code[i]
            if quote:
                if c=='\\': i+=2;continue
                if c==quote:quote=None
            elif c in ('"', "'", '`'):
                quote=c
            elif c=='{':depth+=1
            elif c=='}' and depth>0:depth-=1
            elif c=='>' and depth==0:
                yield match.start(),match.group('tag'),code[match.end():i]
                break
            elif c=='<' and depth==0:
                break
            i+=1

ALT_RE = re.compile(r'(?<![\w:-])alt\s*=', re.I)
HREF_RE = re.compile(r'\bhref\s*=\s*(?:\{\s*)?(["\'])(#|javascript:void\(0\)|javascript:;)\1\s*\}?', re.I)
HANDLER_EMPTY = re.compile(r'\bonClick\s*=\s*\{\s*(?:\([^)]*\)|[a-z_$][\w$]*)\s*=>\s*(?:\{\s*\}|undefined|null|false|\(\s*\))\s*\}',re.I|re.S)
ROLE_RE = re.compile(r'\brole\s*=')
KEY_RE = re.compile(r'\bonKey(?:Down|Up|Press)\s*=|\btabindex\s*=|\btabIndex\s*=', re.I)


def line_of(src: str, offset: int) -> int:
    return src.count('\n',0,offset)+1


def finding(key: str, filename: str, line: int, rules: tuple[str,...], severity: str, confidence: str, note: str, occurrences: int = 1) -> dict:
    return {'key':key,'file':filename,'line':line,'occurrences':occurrences,'source_rules':list(rules), 'severity':severity,'confidence':confidence,'note':note,'status':'candidate_not_verified'}


def scan_text(src: str, filename: str) -> list[dict]:
    code = mask_comments(src, filename)
    findings=[]
    for key, pattern, minimum, rules, sev, conf, note in DETECTORS:
        hits=list(re.finditer(pattern,code,re.I))
        if len(hits)>=minimum:
            findings.append(finding(key,filename,line_of(code,hits[0].start()),rules,sev,conf,note,len(hits)))
    for position, tag, attrs in iter_tags(code):
        line=line_of(code,position)
        if tag in ('img','Image') and not ALT_RE.search(attrs):
            findings.append(finding('MISSING_IMG_ALT',filename,line,('SA-076',),'P1_CANDIDATE','high',f'<{tag}> sem alt; imagem decorativa requer alt="", informativa precisa descrição.'))
        if tag in ('a','Link') and HREF_RE.search(attrs):
            findings.append(finding('PLACEHOLDER_HREF',filename,line,('NX-043','NX-056'),'P0_CANDIDATE','medium','Link parece placeholder; # pode ser âncora de topo legítima.'))
        if HANDLER_EMPTY.search(attrs):
            findings.append(finding('EMPTY_ONCLICK',filename,line,('NX-056',),'P0_CANDIDATE','high','Handler vazio: funcionalidade incompleta possível.'))
        if tag in ('div','span') and re.search(r'\bonClick\s*=',attrs) and not (ROLE_RE.search(attrs) and KEY_RE.search(attrs)):
            findings.append(finding('NON_SEMANTIC_CLICK',filename,line,('SA-075',),'P1_CANDIDATE','medium','Elementos clicáveis não semânticos: preferir button ou garantir teclado e semântica.'))
        if tag=='video' and re.search(r'\bautoPlay\b|\bautoplay\b',attrs,re.I) and not re.search(r'\bmuted\b',attrs,re.I):
            findings.append(finding('AUTOPLAY_UNMUTED',filename,line,(),'P1_CANDIDATE','medium','Autoplay com áudio possível; verificar browser, acesso e controle de reprodução.'))
        if tag=='iframe' and not re.search(r'\btitle\s*=',attrs,re.I):
            findings.append(finding('IFRAME_MISSING_TITLE',filename,line,('SA-076',),'P1_CANDIDATE','high','iframe sem título acessível.'))
    if Path(filename).suffix.lower() in {'.html','.vue','.astro','.svelte'}:
        from markup_audit import scan_markup
        findings.extend(scan_markup(src, filename, lambda key,line,rules,sev,conf,note: finding(key,filename,line,rules,sev,conf,note)))
    # Catch empty handlers on multiline non-tag function calls/components too.
    for match in HANDLER_EMPTY.finditer(code):
        if any(x['key']=='EMPTY_ONCLICK' and x['line']==line_of(code,match.start()) for x in findings):
            continue
        findings.append(finding('EMPTY_ONCLICK',filename,line_of(code,match.start()),('NX-056',),'P0_CANDIDATE','high','Handler vazio: confirmar fluxo.'))
    return sorted(findings,key=lambda f:(f['line'],f['key']))


def audit(path: Path, max_bytes: int=LIMIT_BYTES, use_ast: bool=False, policy=None) -> dict:
    if not path.exists(): raise FileNotFoundError(path)
    if path.is_symlink(): raise ValueError('Pasta/arquivo symlink não permitido como raiz')
    root=path if path.is_dir() else path.parent
    safe_root=root.resolve()
    paths=[path] if path.is_file() else sorted(path.rglob('*'))
    findings=[]
    checked=0
    skipped_large=0
    skipped_unsafe=0
    errors=[]
    ast_used=0
    for candidate in paths:
        if any(part in SKIP for part in candidate.relative_to(root).parts): continue
        if candidate.is_symlink():
            skipped_unsafe+=1
            continue
        if not candidate.is_file() or candidate.suffix.lower() not in SUFFIXES: continue
        if safe_root not in candidate.resolve().parents and candidate.resolve()!=safe_root:
            skipped_unsafe+=1
            continue
        try:
            size=candidate.stat().st_size
            if size>max_bytes:
                skipped_large+=1
                continue
            data=candidate.read_text(encoding='utf-8',errors='replace')
        except OSError as e:
            errors.append({'file':str(candidate.relative_to(root)),'error':str(e)})
            continue
        checked+=1
        relative=str(candidate.relative_to(root))
        candidates=scan_text(data,relative)
        suffix=candidate.suffix.lower()
        if suffix in {'.html','.vue','.astro','.svelte'}:
            template_keys={'MISSING_IMG_ALT','IFRAME_MISSING_TITLE','PLACEHOLDER_HREF',
                           'EMPTY_ONCLICK','NON_SEMANTIC_CLICK','AUTOPLAY_UNMUTED'}
            candidates=[f for f in candidates if f['key'] not in template_keys]
            try:
                candidates.extend(scan_template(data,relative))
            except (ValueError,TypeError) as exc:
                errors.append({'file':relative,'error':f'Template tokenizer: {exc}'})
        if suffix in {'.css','.scss','.sass'}:
            candidates.extend(scan_css(data,relative))
        elif suffix in {'.html','.vue','.astro','.svelte'}:
            import re
            for style in re.finditer(r'<style(?:\s[^>]*)?>(.*?)</style\s*>',data,flags=re.S|re.I):
                prefix='\n'*data[:style.start(1)].count('\n')
                candidates.extend(scan_css(prefix+style.group(1),relative))
        if use_ast and candidate.suffix.lower() in {'.tsx','.jsx'}:
            try:
                proc=subprocess.run(['node',str(Path(__file__).with_name('audit_jsx_ast.cjs')),str(candidate)],
                                   capture_output=True,text=True,timeout=15,check=True)
                parsed=json.loads(proc.stdout)
                ast_keys={'MISSING_IMG_ALT','PLACEHOLDER_HREF','EMPTY_ONCLICK','NON_SEMANTIC_CLICK','IFRAME_MISSING_TITLE','AUTOPLAY_UNMUTED'}
                candidates=[x for x in candidates if x['key'] not in ast_keys]
                for item in parsed['findings']:
                    item['file']=str(candidate.relative_to(root))
                    candidates.append(item)
                ast_used+=1
            except (FileNotFoundError,subprocess.SubprocessError,json.JSONDecodeError,KeyError) as e:
                errors.append({'file':str(candidate.relative_to(root)),'error':f'AST indisponível: {str(e)[:250]}'})
        findings.extend(candidates)
    # The AST and lexical passes can produce the same finding on an element.
    unique={}
    for entry in findings:
        key=(entry['file'],entry['line'],entry['key'])
        if key not in unique or entry.get('detector_engine')=='typescript-jsx-ast':
            unique[key]=entry
    findings=list(unique.values())
    findings.sort(key=lambda f:(f['file'],f['line'],f['key']))
    for i, entry in enumerate(findings,1): entry['id']=f'STATIC-{i:04}'
    counts=dict(Counter(f['key'] for f in findings))
    static_covered=sorted({rid for ids in MAPPINGS.values() for rid in ids})
    report = {'scanner':'anti-ai-slop/static-prescreen-2.2','timestamp_utc':datetime.now(timezone.utc).isoformat(),
            'path':str(path.resolve()),'files_scanned':checked,'oversized_files_skipped':skipped_large,
            'unsafe_symlinks_skipped':skipped_unsafe,'ast_files_scanned':ast_used,'read_errors':errors,'candidate_count':len(findings),
            'static_rule_ids':static_covered,'static_rule_count':len(static_covered),'counts_by_key':counts,'findings':findings,
            'warning':'Heuristic candidates only. No files changed; use browser and agent triage before repairs.'}
    if policy is None and path.is_dir():
        automatic = path / '.anti-ai-slop' / 'false-positive-guard.json'
        if automatic.is_file():
            policy = load_json(automatic)
    return guard_report(report, policy=policy)


def to_markdown(result:dict)->str:
    lines=['# Pré-varredura estática Anti-AI-Slop','',f"- Arquivos: **{result['files_scanned']}**",f"- Candidatos: **{result['candidate_count']}**",f"- Symlinks ignorados: **{result['unsafe_symlinks_skipped']}**",'- Achados não são automaticamente defeitos confirmados.',f"- Revisões contextuais: **{result.get('guard',{}).get('reviewed_count',0)}**",'', '| ID | Detector | Fonte | Local | Severidade |','|---|---|---|---|---|']
    for f in result['findings']:
        lines.append(f"| {f['id']} | {f['key']} | {', '.join(f['source_rules'])} | `{f['file']}:{f['line']}` | {f['severity']} |")
    lines+=['','Executar revisão contextual, testes, build e validação de navegador antes de alterar código.','']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('path',type=Path)
    p.add_argument('--format',choices=['json','md','text'],default='text')
    p.add_argument('--out',type=Path)
    p.add_argument('--ast',action='store_true',help='Opcional: usa TypeScript AST para JSX/TSX (requer node + typescript)')
    p.add_argument('--policy', type=Path, help='Revisões justificadas; padrão: <projeto>/.anti-ai-slop/false-positive-guard.json')
    args=p.parse_args()
    try: result=audit(args.path,use_ast=args.ast,policy=load_json(args.policy) if args.policy else None)
    except (OSError,ValueError) as e: p.error(str(e))
    output=json.dumps(result,indent=2,ensure_ascii=False)+'\n' if args.format=='json' else to_markdown(result)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding='utf-8')
    else: print(output)

if __name__=='__main__': main()
