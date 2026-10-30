#!/usr/bin/env python3
"""Optional Playwright browser evidence for an explicitly supplied running website.

Install: python -m pip install playwright; python -m playwright install chromium
No form submission or destructive clicks. No automated style changes. Produces screenshots
and machine-readable candidates, never a fabricated visual or functionality score.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

VIEWPORTS = {'mobile': (390, 844), 'tablet': (768, 1024), 'desktop': (1440, 900)}


def validate_url(value: str) -> str:
    uri = urlparse(value)
    if uri.scheme not in ('http', 'https') or not uri.hostname:
        raise ValueError('Informe uma URL HTTP(S) explícita de um site de teste.')
    if uri.username or uri.password:
        raise ValueError('Não inclua credenciais na URL.')
    return value


def _inspect(page):
    return page.evaluate(r'''() => {
      const visible = e => {const r=e.getBoundingClientRect(), s=getComputedStyle(e);
        return r.width>0 && r.height>0 && s.visibility!=='hidden' && s.display!=='none'};
      const buttons=[...document.querySelectorAll('button,[role="button"]')].filter(visible);
      const imgs=[...document.images].filter(visible);
      const links=[...document.querySelectorAll('a[href]')].filter(visible);
      const controls=[...document.querySelectorAll('input,select,textarea')].filter(visible);
      const unlabeled=controls.filter(e => e.type!=='hidden' && e.type!=='submit' &&
        !e.labels?.length && !e.getAttribute('aria-label') && !e.getAttribute('aria-labelledby'));
      const noName=buttons.filter(e=> !(e.innerText?.trim() || e.getAttribute('aria-label') || e.getAttribute('aria-labelledby') || e.title));
      const dead=links.filter(e=> ['#','javascript:void(0)','javascript:;'].includes(e.getAttribute('href')||''));
      const broken=imgs.filter(e=>!e.complete || e.naturalWidth===0);
      const headings=[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(visible);
      const order=headings.map(e=>Number(e.tagName[1]));
      const jumps=order.slice(1).map((n,i)=>n-order[i]).filter(delta=>delta>1);
      const blankLinks=links.filter(e=> !(e.innerText?.trim() || e.getAttribute('aria-label') || e.getAttribute('aria-labelledby') || e.querySelector('img[alt]')));
      const unsafeBlankLinks=links.filter(e=>e.target==='_blank' && !/\bnoopener\b/.test(e.rel));
      const contrastCandidates=[];
      const rgb=text=>{const m=text.match(/^rgba?\(([^)]+)\)/);if(!m)return null;
        const values=m[1].split(',').map(v=>parseFloat(v));
        return values.length>=3?values:null};
      const lum=values=>{const c=values.slice(0,3).map(n=>{const x=n/255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4});return .2126*c[0]+.7152*c[1]+.0722*c[2]};
      const sampled=[...document.querySelectorAll('p,a,button,label,li,span')].filter(visible).slice(0,200);
      for(const e of sampled){
        if(!e.textContent?.trim() || e.querySelector('*'))continue;
        const s=getComputedStyle(e),fg=rgb(s.color);if(!fg || (fg.length>=4 && fg[3]<.98))continue;
        let node=e,bg=null,uncertain=false;
        while(node && node.nodeType===1){
          const st=getComputedStyle(node);
          if(st.backgroundImage!=='none' || Number(st.opacity)<.98){uncertain=true;break}
          const color=rgb(st.backgroundColor);
          if(color && (color.length<4 || color[3]>=.98)){bg=color;break}
          node=node.parentElement;
        }
        if(!bg || uncertain)continue;
        const ratio=(Math.max(lum(fg),lum(bg))+.05)/(Math.min(lum(fg),lum(bg))+.05);
        const large=parseFloat(s.fontSize)>=24 || (parseFloat(s.fontSize)>=18.66 && Number(s.fontWeight)>=700);
        if(ratio<(large?3:4.5))contrastCandidates.push({tag:e.tagName,text:e.textContent.trim().slice(0,65),ratio:Number(ratio.toFixed(2))});
      }
      return {viewport:{width:innerWidth,height:innerHeight},
        horizontal_overflow:Math.max(document.documentElement.scrollWidth,document.body?.scrollWidth||0)>innerWidth+2,
        missing_image_alt:imgs.filter(e=>!e.hasAttribute('alt')).length,
        broken_images:broken.map(e=>e.getAttribute('src')).slice(0,20),
        dead_links:dead.map(e=>e.outerHTML.slice(0,180)).slice(0,20),
        unnamed_buttons:noName.map(e=>e.outerHTML.slice(0,180)).slice(0,20),
        unlabeled_controls:unlabeled.map(e=>e.outerHTML.slice(0,180)).slice(0,20),
        focusables:document.querySelectorAll('a[href],button,input,select,textarea,[tabindex]').length,
        title:document.title,lang:document.documentElement.lang || '',
        heading_h1_count:order.filter(n=>n===1).length,heading_level_skips:jumps.length,
        unnamed_links:blankLinks.map(e=>e.outerHTML.slice(0,180)).slice(0,20),
        blank_target_missing_noopener:unsafeBlankLinks.map(e=>e.outerHTML.slice(0,180)).slice(0,20),
        potential_text_contrast_failures:contrastCandidates.slice(0,20)};
    }''')


def run(url: str|None, out: Path, *, browser_path: str|None=None, timeout_ms: int=15000, reduced_motion: bool=False, html_path: Path|None=None, interaction_spec: list|None=None, axe: bool=False, axe_path: Path|None=None, fail_on_axe: bool=False) -> dict:
    from playwright.sync_api import sync_playwright
    if not url and html_path is None: raise ValueError('Informe URL ou --html de fixture.')
    if url:validate_url(url)
    if html_path is not None and not html_path.is_file(): raise FileNotFoundError(html_path)
    if axe or axe_path is not None:
        axe=True
        axe_path=axe_path or Path(__file__).resolve().parents[1]/'node_modules'/'axe-core'/'axe.min.js'
        if not axe_path.is_file():
            raise RuntimeError('axe-core unavailable; run npm install in the skill root or pass --axe-path')
    out.mkdir(parents=True, exist_ok=True)
    report={'auditor':'anti-ai-slop/browser-1.1','url':url,'fixture_html':str(html_path) if html_path else None,'timestamp_utc':datetime.now(timezone.utc).isoformat(),
            'viewport_results':{},'status':'completed','warning':'Candidates only; screenshots require human/agent review.'}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path=browser_path) if browser_path else p.chromium.launch(headless=True)
        try:
            for name,(w,h) in VIEWPORTS.items():
                page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1,
                    reduced_motion='reduce' if reduced_motion else 'no-preference',
                    is_mobile=name=='mobile',has_touch=name=='mobile')
                errors=[]
                page.on('pageerror',lambda exc:errors.append(str(exc)))
                try:
                    if html_path is not None:
                        page.set_content(html_path.read_text(encoding='utf-8'),wait_until='domcontentloaded',timeout=timeout_ms)
                        resp=None
                    else:
                        resp=page.goto(url,wait_until='domcontentloaded',timeout=timeout_ms)
                    page.wait_for_timeout(300)
                    state=_inspect(page)
                    axe_result=None
                    if axe:
                        page.add_script_tag(path=str(axe_path))
                        axe_result=page.evaluate('''async () => {
                          if (!window.axe || !window.axe.run) throw Error('axe.run unavailable');
                          const r = await window.axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});
                          return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,
                            help:v.help,help_url:v.helpUrl,nodes:v.nodes.slice(0,15).map(n=>({target:n.target,html:n.html.slice(0,250),failure_summary:n.failureSummary}))})),
                            incomplete_count:r.incomplete.length,passes_count:r.passes.length};
                        }''')
                    interactions=[]
                    for check in interaction_spec or []:
                        entry={'selector':check['selector'],'passed':False}
                        try:
                            page.locator(check['selector']).first.click(timeout=timeout_ms)
                            if 'expect_selector' in check:
                                page.locator(check['expect_selector']).first.wait_for(state='visible',timeout=timeout_ms)
                            if 'expect_text' in check:
                                subject=page.locator(check.get('expect_selector',check['selector'])).first
                                if check['expect_text'] not in subject.inner_text(timeout=timeout_ms):
                                    raise ValueError('Texto de aceitação não encontrado')
                            if 'expect_url_contains' in check and check['expect_url_contains'] not in page.url:
                                raise ValueError('Navegação esperada não ocorreu')
                            entry['passed']=True
                        except Exception as exc:
                            entry['error']=str(exc)
                        interactions.append(entry)
                    screenshot=str((out/f'{name}.png').resolve())
                    page.screenshot(path=screenshot,full_page=True,animations='disabled',timeout=timeout_ms)
                    if any(not item['passed'] for item in interactions): report['status']='failed_checks'
                    if fail_on_axe and axe_result and any(v['impact'] in ('critical','serious') for v in axe_result['violations']):
                        report['status']='failed_checks'
                    report['viewport_results'][name]={'http_status':resp.status if resp else None,
                        'screenshot':screenshot,'js_errors':errors,'checks':state,'interactions':interactions, 'axe_core':axe_result}
                except Exception as exc:
                    report['viewport_results'][name]={'error':str(exc)}
                    report['status']='incomplete'
                finally:page.close()
        finally:browser.close()
    (out/'browser-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return report


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url',nargs='?',type=validate_url)
    parser.add_argument('--html',type=Path,help='HTML local para teste offline de fixture, sem requisições de navegação')
    parser.add_argument('--out',type=Path,default=Path('reports/browser'))
    parser.add_argument('--browser-path',help='Caminho para Chromium existente (se não usar browser do Playwright)')
    parser.add_argument('--timeout-ms',type=int,default=15000)
    parser.add_argument('--reduced-motion',action='store_true')
    parser.add_argument('--interaction-spec',type=Path,help='JSON com checks explícitos de interações não destrutivas de teste')
    parser.add_argument('--axe',action='store_true',help='Executar axe-core real via node_modules/axe-core/axe.min.js')
    parser.add_argument('--axe-path',type=Path,help='Caminho para a distribuição JS axe-core')
    parser.add_argument('--fail-on-axe',action='store_true',help='Falhar se axe-core encontrar violações serious/critical')
    args=parser.parse_args()
    try:
        spec=json.loads(args.interaction_spec.read_text(encoding='utf-8'))['checks'] if args.interaction_spec else None
        result=run(args.url,args.out,browser_path=args.browser_path,timeout_ms=args.timeout_ms,reduced_motion=args.reduced_motion,html_path=args.html,interaction_spec=spec,axe=args.axe,axe_path=args.axe_path,fail_on_axe=args.fail_on_axe)
    except ImportError:
        print('Playwright ausente. Instale com: python -m pip install playwright',file=sys.stderr)
        return 2
    except Exception as e:
        print(f'Browser indisponível: {e}',file=sys.stderr)
        return 2
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0 if result['status']=='completed' else 1

if __name__=='__main__':sys.exit(main())
