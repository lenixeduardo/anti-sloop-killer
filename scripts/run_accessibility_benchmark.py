#!/usr/bin/env python3
"""Evaluate high-confidence detector additions against fixed positive and negative cases.

Scores measure labelled file/issue pairs in our synthetic suite, not site-level
precision or recall in the wild. Dynamic template expressions are intentionally
not treated as definite defects.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from audit_slop import audit

ROOT=Path(__file__).resolve().parents[1]
KEYS={'POSITIVE_TABINDEX','UNLABELED_SELECT','UNLABELED_TEXTAREA'}

def measure(cases, *, use_ast=True):
    counts={'tp':0,'fp':0,'fn':0}
    results=[]
    for case in cases:
        path=ROOT/'benchmarks'/'fixtures'/'accessibility-v2'/case['path']
        payload=audit(path,use_ast=use_ast)
        expected=set(case['expected'])
        actual={row['key'] for row in payload['findings'] if row['key'] in KEYS}
        tp=len(actual&expected);fp=len(actual-expected);fn=len(expected-actual)
        for key,v in {'tp':tp,'fp':fp,'fn':fn}.items():counts[key]+=v
        results.append({'file':case['path'],'framework':case['framework'],'split':case['split'],
                        'tp':tp,'fp':fp,'fn':fn,'expected':sorted(expected),'observed':sorted(actual),
                        'other_candidates':[row['key'] for row in payload['findings'] if row['key'] not in KEYS],
                        'ast_files_scanned':payload['ast_files_scanned'],'read_errors':payload['read_errors']})
    counts['precision']=round(counts['tp']/(counts['tp']+counts['fp']),4) if counts['tp']+counts['fp'] else 1.0
    counts['recall']=round(counts['tp']/(counts['tp']+counts['fn']),4) if counts['tp']+counts['fn'] else 1.0
    counts['f1']=round(2*counts['precision']*counts['recall']/(counts['precision']+counts['recall']),4) if counts['precision']+counts['recall'] else 0.0
    return counts,results

def run(use_ast=True):
    gold=json.loads((ROOT/'benchmarks'/'accessibility-gold.json').read_text(encoding='utf-8'))
    overall,results=measure(gold['cases'],use_ast=use_ast)
    return {'benchmark':gold['schema'],'provenance':gold['provenance'],'metrics':overall,'cases':results,
            'frameworks':len(set(x['framework'] for x in results)),
            'limitations':['Synthetic and authored by the implementation team; not independent external evaluation.',
                'Dynamic expressions require live browser review.',
                'File/issue pair scoring is not an indication of all 228 catalog rules.']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--no-ast',action='store_true')
    p.add_argument('--out',type=Path)
    p.add_argument('--min-precision',type=float,default=.95)
    p.add_argument('--min-recall',type=float,default=.90)
    args=p.parse_args()
    output=run(use_ast=not args.no_ast)
    text=json.dumps(output,indent=2,ensure_ascii=False)+'\n'
    if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text,encoding='utf-8')
    else:print(text)
    return 0 if output['metrics']['precision']>=args.min_precision and output['metrics']['recall']>=args.min_recall else 1
if __name__=='__main__':raise SystemExit(main())
