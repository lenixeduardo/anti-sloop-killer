#!/usr/bin/env python3
"""Run the locally installed Lighthouse CLI against an explicit HTTP(S) URL.

No downloads, shell execution or remote URLs are inferred. This audit cannot run
against a set_content HTML fixture: serve a trusted test site via HTTP first.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from browser_audit import validate_url

CATEGORIES=('performance','accessibility','best-practices','seo')

def summarize(payload:dict,thresholds:dict)->dict:
    cats=payload.get('categories')
    if not isinstance(cats,dict):raise ValueError('Invalid Lighthouse JSON: categories missing')
    scores={}
    for key in CATEGORIES:
        value=cats.get(key,{}).get('score')
        if type(value) not in (float,int) or not 0<=value<=1:
            raise ValueError(f'Missing score: {key}')
        scores[key]=round(value*100,1)
    below={key:{'actual':v,'minimum':thresholds[key]} for key,v in scores.items() if v<thresholds[key]}
    return {'scores':scores,'thresholds':thresholds,'below_thresholds':below,
            'passed':not below,'status':'pass' if not below else 'review_required',
            'final_url':payload.get('finalDisplayedUrl'), 'lighthouse_version':payload.get('lighthouseVersion')}


def run(url:str,out:Path,*,chrome_path:str|None=None,cli_path:str|None=None,thresholds:dict|None=None,timeout:int=180)->dict:
    validate_url(url)
    out.mkdir(parents=True,exist_ok=True)
    thresholds=thresholds or {'performance':80,'accessibility':90,'best-practices':90,'seo':80}
    if not 1<=timeout<=600:raise ValueError('Timeout out of bounds')
    local_cli=Path(cli_path) if cli_path else Path(__file__).resolve().parents[1]/'node_modules'/'.bin'/'lighthouse'
    if not local_cli.is_file():
        raise RuntimeError('Lighthouse not installed; run npm install in skill root. No fallback to network download.')
    chrome=chrome_path or shutil.which('chromium') or shutil.which('google-chrome')
    if not chrome or not Path(chrome).is_file():raise RuntimeError('Chrome/Chromium executable unavailable')
    raw=out/'lighthouse-raw.json'
    argv=[str(local_cli),url,'--output=json',f'--output-path={raw}', '--quiet',
          '--only-categories='+','.join(CATEGORIES),
          '--chrome-flags=--headless --no-sandbox --disable-dev-shm-usage',
          ]
    env=dict(os.environ)
    env['CHROME_PATH']=str(chrome)
    try:
        proc=subprocess.run(argv,capture_output=True,text=True,timeout=timeout,shell=False,env=env)
    except subprocess.TimeoutExpired as e:
        raise RuntimeError('Lighthouse execution timed out') from e
    if proc.returncode!=0 or not raw.exists():
        raise RuntimeError('Lighthouse failed (exit '+str(proc.returncode)+'): '+proc.stderr[-1200:])
    result=summarize(json.loads(raw.read_text(encoding='utf-8')),thresholds)
    result['url']=url
    result['raw_report']=str(raw)
    (out/'lighthouse-report.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('url',type=validate_url)
    p.add_argument('--out',type=Path,default=Path('reports/lighthouse'))
    p.add_argument('--chrome-path')
    p.add_argument('--cli-path')
    p.add_argument('--min-performance',type=int,default=80)
    p.add_argument('--min-accessibility',type=int,default=90)
    p.add_argument('--min-best-practices',type=int,default=90)
    p.add_argument('--min-seo',type=int,default=80)
    args=p.parse_args()
    thresholds=dict(zip(CATEGORIES,(args.min_performance,args.min_accessibility,args.min_best_practices,args.min_seo)))
    if any(not 0<=v<=100 for v in thresholds.values()):p.error('Thresholds must be between 0 and 100')
    try:r=run(args.url,args.out,chrome_path=args.chrome_path,cli_path=args.cli_path,thresholds=thresholds)
    except Exception as e:print('ERROR: '+str(e),file=sys.stderr);return 2
    print(json.dumps(r,indent=2,ensure_ascii=False))
    return 0 if r['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
