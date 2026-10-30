"""Read-only HTML/template structural candidates, independent from visual style.

A parser can inspect literal markup but cannot resolve runtime bindings or framework
rendering. Findings therefore remain candidates and require browser verification.
"""
from __future__ import annotations
from html.parser import HTMLParser
from collections import defaultdict

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
INPUT_EXEMPT = {'hidden','submit','button','reset','image'}


def scan_markup(source: str, filename: str, emit):
    """Return candidate findings. ``emit(key,line,rules,severity,confidence,note)``."""
    from audit_slop import mask_comments
    code = mask_comments(source, filename)
    parser = _TemplateParser(emit, filename.lower().endswith(('.html','.astro')))
    try:
        parser.feed(code)
        parser.close()
    except (ValueError, AssertionError):
        return []  # malformed templates are not proven violations
    return parser.finish()


class _TemplateParser(HTMLParser):
    def __init__(self, emit, document):
        super().__init__(convert_charrefs=True)
        self.emit = emit
        self.document = document
        self.findings = []
        self.stack = []
        self.nodes = []
        self.ids = {}
        self.labels_for = set()
        self.controls = []
        self.has_html = False
        self.lang = False
        self.has_title = False
        self.has_viewport = False
        self.doc_line = 1

    def add(self, key, line, rules, severity, confidence, note):
        self.findings.append(self.emit(key, line, rules, severity, confidence, note))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID:
            self.handle_endtag(tag)

    def handle_starttag(self, tag, pairs):
        tag = tag.lower()
        attrs = {k.lower():v for k,v in pairs if k}
        line = self.getpos()[0]
        node = {'tag':tag, 'attrs':attrs, 'line':line, 'text':'', 'child_image_alt':False, 'label_ancestor':any(n['tag']=='label' for n in self.stack)}
        self.nodes.append(node)
        if tag == 'html':
            self.has_html = True
            self.doc_line = line
            self.lang = bool((attrs.get('lang') or '').strip())
        if tag == 'title':self.has_title = True
        if tag == 'meta' and (attrs.get('name') or '').lower() == 'viewport':self.has_viewport = True
        if tag == 'label' and attrs.get('for'):self.labels_for.add(attrs['for'])
        if attrs.get('id'):
            key = attrs['id']
            if key in self.ids:
                self.add('DUPLICATE_ID',line,('SA-034','NX-022'),'P1_CANDIDATE','high',f'id duplicado no template: {key[:64]}')
            self.ids[key] = line
        if tag == 'img':
            if attrs.get('src') == '':
                self.add('EMPTY_IMAGE_SRC',line,('NX-021',),'P1_CANDIDATE','high','Imagem com src vazio não carrega o recurso esperado.')
            if (attrs.get('alt') or '').strip():
                for ancestor in self.stack:
                    ancestor['child_image_alt'] = True
        if tag == 'input' and (attrs.get('type') or '').lower() not in INPUT_EXEMPT:
            self.controls.append(node)
        if (attrs.get('aria-hidden') or '').lower() == 'true':
            tabindex = attrs.get('tabindex')
            if (tag in {'a','button','input','select','textarea'} and not (tag == 'a' and 'href' not in attrs)) or (tabindex is not None and tabindex.lstrip('-').isdigit() and int(tabindex)>=0):
                if tabindex != '-1' and 'disabled' not in attrs:
                    self.add('ARIA_HIDDEN_FOCUSABLE',line,('NX-022','SA-076'),'P1_CANDIDATE','high','Elemento oculto da árvore de acessibilidade pode continuar focável.')
        if tag == 'a' and (attrs.get('target') or '').lower() == '_blank' and 'href' in attrs:
            rel = set((attrs.get('rel') or '').lower().split())
            if not rel.intersection({'noopener','noreferrer'}):
                self.add('EXTERNAL_TARGET_REL',line,('NX-022',),'P3_CANDIDATE','low','Verificar compatibilidade e política de rel=noopener/noreferrer; navegadores modernos já isolam _blank.')
        if tag == 'button' and any(n['tag']=='form' for n in self.stack) and 'type' not in attrs:
            self.add('IMPLICIT_SUBMIT_BUTTON',line,('NX-056',),'P2_CANDIDATE','medium','Button em form sem type faz submit implícito; confirmar intenção.')
        if tag not in VOID:
            self.stack.append(node)

    def handle_data(self,data):
        for node in self.stack:
            node['text'] += data

    def handle_endtag(self,tag):
        tag = tag.lower()
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                break

    def finish(self):
        if self.document and self.has_html:
            if not self.lang:self.add('MISSING_DOCUMENT_LANG',self.doc_line,('SA-034','SA-076'),'P1_CANDIDATE','high','Documento HTML sem lang válido.')
            if not self.has_title:self.add('MISSING_DOCUMENT_TITLE',self.doc_line,('NX-052','SA-034'),'P1_CANDIDATE','high','Documento HTML sem title.')
            if not self.has_viewport:self.add('MISSING_VIEWPORT_META',self.doc_line,('NX-031',),'P1_CANDIDATE','high','Documento HTML sem meta viewport.')
        for node in self.controls:
            attrs = node['attrs']
            accessible = (attrs.get('aria-label') or attrs.get('aria-labelledby') or attrs.get('title'))
            if not accessible and not node['label_ancestor'] and attrs.get('id') not in self.labels_for:
                self.add('UNLABELED_INPUT',node['line'],('SA-076','NX-022'),'P1_CANDIDATE','medium','Campo sem label associado; placeholder sozinho também não substitui label.')
        for node in self.nodes:
            tag,attrs = node['tag'],node['attrs']
            if tag not in {'button','a'}:continue
            if tag=='a' and not attrs.get('href'):continue
            if node['text'].strip() or node['child_image_alt'] or attrs.get('aria-label') or attrs.get('aria-labelledby') or attrs.get('title'):
                continue
            self.add('UNNAMED_BUTTON' if tag=='button' else 'UNNAMED_LINK',node['line'],('SA-076','NX-022'),'P1_CANDIDATE','medium',f'<{tag}> sem nome acessível evidente no HTML estático.')
        return self.findings
