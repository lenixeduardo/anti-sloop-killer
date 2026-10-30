#!/usr/bin/env python3
"""Score labelled five-stack fixture corpus: file + detector key are evaluation units.

No learning or auto-labeling. Gold labels are explicit and can be externally reviewed.
The holdout is transparent and local, not a hidden or production benchmark.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from audit_slop import audit

ROOT = Path(__file__).resolve().parents[1]


def metrics(tp,fp,fn):
    p=tp/(tp+fp) if tp+fp else (1.0 if not fn else 0.0)
    r=tp/(tp+fn) if tp+fn else 1.0
    return {'tp':tp,'fp':fp,'fn':fn,'precision':round(p,4),'recall':round(r,4),'f1':round(2*p*r/(p+r),4) if p+r else 0.0}


def evaluate(gold_path:Path=ROOT/'benchmarks/gold.json', use_ast:bool=True):
    gold=json.loads(gold_path.read_text(encoding='utf-8'))
    root=gold_path.parent/'fixtures'
    splits={'development':{'tp':0,'fp':0,'fn':0},'holdout':{'tp':0,'fp':0,'fn':0}}
    entries=[]
    for case in gold['cases']:
        rel=case['path']
        if Path(rel).is_absolute() or '..' in Path(rel).parts:raise ValueError('Unsafe fixture path')
        source=root/rel
        if not source.is_file():raise FileNotFoundError(source)
        result=audit(source,use_ast=use_ast)
        if result['read_errors']:
            raise RuntimeError(f"Não foi possível verificar {rel}: {result['read_errors']}")
        actual={f['key'] for f in result['findings']}
        expected=set(case['expected'])
        split=case['split']
        if split not in splits:raise ValueError('Unknown split')
        tp=actual & expected; fp=actual - expected; fn=expected - actual
        for field,value in [('tp',tp),('fp',fp),('fn',fn)]:splits[split][field]+=len(value)
        entries.append({'path':rel,'split':split,'expected':sorted(expected),'actual':sorted(actual),'true_positive':sorted(tp),'false_positive':sorted(fp),'false_negative':sorted(fn),'ast_files_scanned':result['ast_files_scanned']})
    overall={k:sum(splits[name][k] for name in splits) for k in ('tp','fp','fn')}
    return {'benchmark':gold['benchmark'],'schema_version':gold['schema_version'],'metric_unit':gold['metric_unit'],'frameworks':5,'cases':len(entries),'splits':{k:metrics(**v) for k,v in splits.items()},'overall':metrics(**overall),'entries':entries,'limitations':['Fixture corpus is synthetic and small.','Labels were authored locally, not verified by independent raters.','Only exact detector keys per file are scored.','A high score does not prove 228-rule coverage or production efficacy.']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gold',type=Path,default=ROOT/'benchmarks/gold.json')
    p.add_argument('--no-ast',action='store_true')
    p.add_argument('--out',type=Path)
    p.add_argument('--min-precision',type=float,default=0.0)
    p.add_argument('--min-recall',type=float,default=0.0)
    args=p.parse_args()
    report=evaluate(args.gold,use_ast=not args.no_ast)
    formatted=json.dumps(report,indent=2,ensure_ascii=False)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(formatted,encoding='utf-8')
    else:print(formatted)
    return int(report['overall']['precision']<args.min_precision or report['overall']['recall']<args.min_recall)

if __name__=='__main__':raise SystemExit(main())
