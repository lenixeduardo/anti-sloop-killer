#!/usr/bin/env python3
"""Read-only HTML/template and CSS detectors using stdlib tokenization.

Unlike raw-source regex, HTMLParser understands quoted angle brackets and attributes;
CSS checks examine declarations within their own rules. No source is rewritten.
Findings remain review candidates, never automatic aesthetic decisions.
"""
from __future__ import annotations
from html.parser import HTMLParser
import re
from pathlib import Path

PLACEHOLDER = {'#', 'javascript:void(0)', 'javascript:;'}
ACTIVATORS = ('@click', 'v-on:click', 'on:click', 'onclick', 'onClick')
KEYBOARD = ('@keydown', '@keyup', 'v-on:keydown', 'on:keydown', 'onkeydown', 'onkeyup', 'onKeyDown', 'onKeyUp')


def issue(key, filename, line, rules, severity, confidence, note):
    return {'key':key,'file':filename,'line':line,'occurrences':1,'source_rules':list(rules),
            'severity':severity,'confidence':confidence,'note':note,'status':'candidate_not_verified',
            'detector_engine':'html-tokenizer'}


class TemplateParser(HTMLParser):
    def __init__(self, filename):
        super().__init__(convert_charrefs=True)
        self.filename=filename
        self.issues=[]
        self.labels=set()
        self.inputs=[]
        self.stack=[]

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        self.handle_endtag(tag)

    def handle_starttag(self,tag,attrs):
        attrs={k.lower():v for k,v in attrs if k is not None}
        lineno=self.getpos()[0]
        tag=tag.lower()
        inside_label=any(x=='label' for x in self.stack)
        if tag=='label' and attrs.get('for'):
            self.labels.add(attrs['for'])
        if tag in ('input', 'select', 'textarea'):
            self.inputs.append((lineno, attrs, inside_label, tag))
        # Only constant positive tabindex values: dynamic bindings need browser review.
        tab=(attrs.get('tabindex') or '').strip()
        if tab.isdecimal() and int(tab)>0 and not any(k.startswith(('v-bind:tabindex', ':tabindex', 'bind:tabindex')) for k in attrs):
            self.issues.append(issue('POSITIVE_TABINDEX',self.filename,lineno,('NX-037','SA-076'),
                'P1_CANDIDATE','high','tabindex positivo sobrepõe a ordem natural de foco.'))
        if tag=='img' and 'alt' not in attrs:
            self.issues.append(issue('MISSING_IMG_ALT',self.filename,lineno,('NX-021','SA-034'),
                         'P1_CANDIDATE','high','img sem atributo alt; WCAG 1.1.1.'))
        if tag=='iframe' and not attrs.get('title'):
            self.issues.append(issue('IFRAME_MISSING_TITLE',self.filename,lineno,('NX-021',),
                         'P1_CANDIDATE','high','iframe sem título acessível; WCAG 4.1.2.'))
        if tag=='a' and (attrs.get('href') or '').strip().lower() in PLACEHOLDER:
            self.issues.append(issue('PLACEHOLDER_HREF',self.filename,lineno,('NX-043','NX-056'),
                         'P0_CANDIDATE','medium','href literal placeholder; conferir se existe comportamento.'))
        if tag in ('div','span') and any(k.lower() in (x.lower() for x in ACTIVATORS) for k in attrs):
            keys={k.lower() for k in attrs}
            if not (attrs.get('role') and ('tabindex' in keys or 'tab-index' in keys) and
                    any(k.startswith(('on:keydown','@keydown','onkeydown','onkeyup','on:keyup','@keyup','v-on:keydown')) for k in keys)):
                self.issues.append(issue('NON_SEMANTIC_CLICK',self.filename,lineno,('NX-022','NX-056'),
                      'P1_CANDIDATE','medium','Elemento clicável sem teclado/semântica evidentes.'))
        if tag=='video' and 'autoplay' in attrs and 'muted' not in attrs:
            self.issues.append(issue('AUTOPLAY_UNMUTED',self.filename,lineno,('NX-038',),
                     'P1_CANDIDATE','medium','Vídeo com autoplay sem muted; verificar comportamento.'))
        if any(k in attrs and (attrs[k] is None or not attrs[k].strip()) for k in ('onclick','@click','v-on:click','on:click')):
            self.issues.append(issue('EMPTY_ONCLICK',self.filename,lineno,('NX-056',),
                     'P0_CANDIDATE','high','Handler de clique vazio.'))
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):
            self.stack.append(tag)

    def handle_endtag(self,tag):
        tag=tag.lower()
        if tag in self.stack:
            index=len(self.stack)-1-self.stack[::-1].index(tag)
            del self.stack[index:]

    def finish(self):
        for line, attrs, nested, tag in self.inputs:
            if tag=='input' and attrs.get('type','').lower() in {'hidden','button','submit','reset','image'}:
                continue
            named=any(attrs.get(key) for key in ('aria-label','aria-labelledby','title'))
            matching_id=attrs.get('id') in self.labels if attrs.get('id') else False
            if not (named or matching_id or nested):
                self.issues.append(issue({'input':'UNLABELED_INPUT','select':'UNLABELED_SELECT','textarea':'UNLABELED_TEXTAREA'}[tag],
                     self.filename,line,('SA-076','NX-040'), 'P1_CANDIDATE','high',
                     'Controle sem nome acessível estático; WCAG 3.3.2/4.1.2.'))
        return sorted(self.issues,key=lambda item:(item['line'],item['key']))


def extract_markup(code, filename):
    suffix=Path(filename).suffix.lower()
    if suffix=='.vue':
        m=re.search(r'<template(?:\s[^>]*)?>(.*?)</template\s*>',code,flags=re.I|re.S)
        if not m:return ''
        return '\n'*code[:m.start(1)].count('\n') + m.group(1)
    if suffix=='.astro' and code.lstrip().startswith('---'):
        m=re.match(r'\s*---\s*\n[\s\S]*?\n---\s*\n',code)
        if m:code='\n'*code[:m.end()].count('\n')+code[m.end():]
    return code


def scan_template(code,filename):
    markup=extract_markup(code,filename)
    parser=TemplateParser(filename)
    parser.feed(markup)
    parser.close()
    return parser.finish()


def hex_rgb(value):
    raw=value.strip().lower()
    if re.fullmatch(r'#[0-9a-f]{3}',raw):return tuple(int(x*2,16) for x in raw[1:])
    if re.fullmatch(r'#[0-9a-f]{6}',raw):return tuple(int(raw[i:i+2],16) for i in (1,3,5))
    return None


def wcag_contrast(fg,bg):
    def lum(rgb):
        channels=[(v/255/12.92 if v/255<=0.04045 else ((v/255+0.055)/1.055)**2.4) for v in rgb]
        return sum(a*b for a,b in zip(channels,(.2126,.7152,.0722)))
    a,b=sorted((lum(fg),lum(bg)),reverse=True)
    return (a+.05)/(b+.05)


def scan_css(code,filename):
    # Preserve line numbers; avoid declarations in comments and CSS string literals.
    def blank(m):return re.sub(r'[^\n]',' ',m.group(0))
    source=re.sub(r'/\*[\s\S]*?\*/',blank,code)
    results=[]
    for match in re.finditer(r'([^{}]+)\{([^{}]*)\}',source):
        selector,block=match.group(1).strip(),match.group(2)
        declarations={}
        for part in block.split(';'):
            if ':' not in part:continue
            prop,value=part.split(':',1)
            declarations[prop.strip().lower()]=value.strip().lower()
        fg=hex_rgb(declarations.get('color',''))
        bg=hex_rgb(declarations.get('background-color',''))
        if fg and bg:
            contrast=wcag_contrast(fg,bg)
            if contrast<4.5:
                line=source.count('\n',0,match.start())+1
                results.append(issue('LOW_STATIC_CONTRAST',filename,line,('IM-033',),'P1_CANDIDATE','high',
                      f'Contraste no mesmo seletor {selector[:70]}: {contrast:.2f}:1; verificar tamanho de texto/overrides.'))
                results[-1]['detector_engine']='css-declarations'
                results[-1]['contrast_ratio']=round(contrast,2)
        if ':focus' in selector and re.search(r'^(?:none|0(?:px)?)$',declarations.get('outline','')):
            if not any(k in declarations for k in ('box-shadow','border','background-color','outline-offset')):
                line=source.count('\n',0,match.start())+1
                entry=issue('FOCUS_OUTLINE_REMOVED',filename,line,('NX-037','SA-076'),'P1_CANDIDATE','medium',
                    'Foco sem outline e sem substituição perceptível no mesmo seletor; validar estilo computado.')
                entry['detector_engine']='css-declarations'
                results.append(entry)
    return results
