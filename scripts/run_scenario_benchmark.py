#!/usr/bin/env python3
"""Five product-scenario test repositories (all synthetic, not deployed)."""
import argparse
from collections import Counter
import json
from pathlib import Path
from audit_slop import audit

ROOT=Path(__file__).resolve().parents[1]

def run(spec_path=ROOT/'benchmarks'/'ground-truth.json'):
    config=json.loads(spec_path.read_text(encoding='utf-8'))
    results=[]
    for case in config['cases']:
        base=(spec_path.parent/'cases'/case['id']).resolve()
        observed=audit(base,use_ast=True)
        if observed['read_errors']:
            raise RuntimeError(f"{case['id']}: AST unavailable / parse error: {observed['read_errors']}")
        expected=Counter((r['file'],r['key']) for r in case['expected'])
        actual=Counter((r['file'],r['key']) for r in observed['findings'])
        true=expected & actual
        false=actual-expected
        missed=expected-actual
        results.append({'case':case['id'],'runtime':case['runtime'], 'tp':sum(true.values()),
            'fp':sum(false.values()),'fn':sum(missed.values()),
            'false_positives': [{'file':f,'key':k,'count':n} for (f,k),n in sorted(false.items())],
            'false_negatives': [{'file':f,'key':k,'count':n} for (f,k),n in sorted(missed.items())],
            'safe_files':case['safe_files'],
            'safe_files_clean':not any(f in case['safe_files'] for f,k in actual)})
    tp=sum(x['tp'] for x in results);fp=sum(x['fp'] for x in results);fn=sum(x['fn'] for x in results)
    precision=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn) if tp+fn else 0
    pmin=config['thresholds']['precision_min'];rmin=config['thresholds']['recall_min']
    return {'suite':'anti-ai-slop/five-product-scenarios-v1','scenario_count':len(results),
        'all_synthetic':True,'https_previews_verified':False,'external_reviewer_approved':False,
        'thresholds':config['thresholds'],
        'overall':{'tp':tp,'fp':fp,'fn':fn,'precision':round(precision,4),'recall':round(recall,4)},
        'passed':precision>=pmin and recall>=rmin and all(x['safe_files_clean'] for x in results),
        'results':results,
        'limitations':['HTTPS preview slots are fixtures only; no public URLs verified.',
                       'Labels authored in-repository; independent adjudication is pending.',
                       'Metrics cover labeled static candidates, not all 228 design rules.']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args();result=run()
    text=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text,encoding='utf-8')
    else:print(text)
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
