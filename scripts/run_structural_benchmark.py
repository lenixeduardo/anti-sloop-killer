#!/usr/bin/env python3
"""Structural repair acceptance benchmark with exact diff, preservation and rollback.

This runs on isolated copies. It does NOT authenticate Codex/Claude/Cursor or
exercise compiled Next/Vue/Astro/Svelte applications. Optional Chromium tests
exercise actual anchor navigation only on the plain HTML case.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from apply_changes import apply
from audit_slop import audit
from structural_fix import plan

ROOT=Path(__file__).resolve().parents[1]
def digest(data):return hashlib.sha256(data).hexdigest()

def run(browser=False,out_dir=None):
    gold=json.loads((ROOT/'benchmarks'/'structural'/'gold.json').read_text(encoding='utf-8'))
    results=[]; negative=[]; browser_checks=[]
    for case in gold['cases']:
        original_path=ROOT/'benchmarks'/'structural'/case['file']
        with tempfile.TemporaryDirectory(prefix='aas-structural-') as work:
            project=Path(work); file=project/original_path.name
            shutil.copy2(original_path,file)
            before=file.read_bytes(); before_source=before.decode('utf-8')
            expected_sha=digest(before)
            original_audit=audit(file,use_ast=file.suffix in ('.jsx','.tsx'))
            assert {case['finding'],case['semantic_finding']}.issubset({f['key'] for f in original_audit['findings']}), case['file']
            proposal={'edits':[{'path':file.name,'id':case['id'],'expected_sha256':expected_sha,
                      'operation':'set_attribute','attribute':'href','value':'#projects'},
                     {'path':file.name,'id':'action','expected_sha256':expected_sha,
                      'operation':'replace_element','markup':case['semantic_new']}]}
            changes=plan(project,proposal)
            preview=apply(project,changes)
            preview_clean=preview['status']=='preview' and digest(file.read_bytes())==expected_sha and 'href="#projects"' in preview['diff']
            # Acceptance check is independent of the patch mechanism, and runs before output is considered verified.
            check=[sys.executable,'-c',
                'from pathlib import Path; s=Path('+repr(file.name)+').read_text(); assert s.count(\'href="#projects"\')==1; assert \'href="#"\' not in s; assert \'<button id="action"\' in s']
            applied=apply(project,changes,approved=True,checks=[check])
            after=file.read_text(encoding='utf-8')
            final_audit=audit(file,use_ast=file.suffix in ('.jsx','.tsx'))
            preserved=all(v in before_source and v in after for v in case['preserve'])
            minimal_diff=(before_source.replace(case['old'],case['new'],1).replace(case['semantic_old'],case['semantic_new'],1)==after)
            removed={case['finding'],case['semantic_finding']}.isdisjoint({f['key'] for f in final_audit['findings']})
            passed=all((preview_clean,applied['status']=='applied_verified',preserved,minimal_diff,removed))
            row={'framework':case['framework'],'passed':passed,'preview_no_mutation':preview_clean,
                 'acceptance_status':applied['status'],'brand_and_copy_preserved':preserved,
                 'only_approved_edits_changed':minimal_diff,'finding_removed':removed,
                 'baseline_sha256':expected_sha,'result_sha256':digest(file.read_bytes()),
                 'before_count':len(original_audit['findings']),'after_count':len(final_audit['findings'])}
            if browser and case['framework']=='html':
                from playwright.sync_api import sync_playwright
                with sync_playwright() as pw:
                    b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or None)
                    try:
                        for name,width,height in [('desktop',1440,900),('tablet',768,1024),('mobile',390,844)]:
                            page=b.new_page(viewport={'width':width,'height':height})
                            page.set_content(after,wait_until='load')
                            page.locator('#action').click()
                            activated=page.evaluate("document.body.dataset.activated === '1'")
                            page.locator('#cta').click()
                            ok=activated and page.evaluate('location.hash')=='#projects' and page.locator('#projects').is_visible()
                            capture=None
                            if out_dir:
                                p=Path(out_dir)/f'structural-{name}.png';p.parent.mkdir(parents=True,exist_ok=True)
                                capture=str(p);page.screenshot(path=capture,full_page=True)
                            browser_checks.append({'viewport':name,'passed':ok,'screenshot':capture})
                            page.close()
                    finally:b.close()
                row['browser_interactions_passed']=all(x['passed'] for x in browser_checks)
                passed=passed and row['browser_interactions_passed'];row['passed']=passed
            results.append(row)
    # Prove rollback restores exact original bytes on a failed acceptance check.
    example=ROOT/'benchmarks'/'structural'/'html'/'index.html'
    with tempfile.TemporaryDirectory() as work:
        project=Path(work);file=project/'index.html';shutil.copy2(example,file)
        original=file.read_bytes()
        change=plan(project,{'edits':[{'path':'index.html','id':'cta','expected_sha256':digest(original),
                      'operation':'set_attribute','attribute':'href','value':'#projects'}]})
        failed=apply(project,change,approved=True,checks=[[sys.executable,'-c','raise SystemExit(7)']])
        negative.append({'name':'failed_acceptance_rolls_back','passed':failed['status']=='rolled_back' and file.read_bytes()==original})
        try:
            plan(project,{'edits':[{'path':'index.html','id':'cta','expected_sha256':'0'*64,
                    'operation':'set_attribute','attribute':'href','value':'#projects'}]})
            denied=False
        except ValueError:denied=True
        negative.append({'name':'baseline_drift_rejected','passed':denied and file.read_bytes()==original})
    passed=sum(x['passed'] for x in results)
    return {'benchmark':'anti-ai-slop/structural-v1','tested':len(results),'passed':passed,
            'negative_tests':negative,'browser':browser_checks,'results':results,
            'status':'passed' if passed==len(results) and all(x['passed'] for x in negative) else 'failed',
            'limitations':['Isolated controlled fixtures; compiled SSR/framework apps and external HTTPS sites not tested.',
                  'Tests verify targeted attribute corrections and brand/content preservation, not design originality.',
                  'No authenticated agent execution or independent human adjudication.']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path)
    p.add_argument('--browser',action='store_true')
    args=p.parse_args()
    report=run(browser=args.browser,out_dir=args.out.parent if args.out else None)
    body=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(body,encoding='utf-8')
    else:print(body)
    return 0 if report['status']=='passed' else 1
if __name__=='__main__':raise SystemExit(main())
