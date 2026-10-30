#!/usr/bin/env python3
"""Inventory the full catalog and make automation gaps explicit."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from audit_slop import DETECTORS

ROOT=Path(__file__).resolve().parents[1]
STATIC_IDS={x for item in DETECTORS for x in item[3]} | {'NX-021','SA-034','NX-043','NX-056','NX-022','NX-038','SA-076','NX-040','IM-033','NX-037','NX-052','NX-031'}
BROWSER_IDS={'NX-021','NX-022','NX-031','NX-043','NX-056','IM-033','IM-034'}


def build():
    data=json.loads((ROOT/'references'/'rules.json').read_text(encoding='utf-8'))
    rules=[]
    for rule in data['rules']:
        rid=rule['id']
        channels=[]
        if rid in STATIC_IDS:channels.append('static_candidate')
        if rid in BROWSER_IDS:channels.append('browser_candidate')
        channels.append('manual_agent_review')
        rules.append({'id':rid,'name':rule['name'],'channels':channels,'review_status':'pending'})
    return {'catalog_count':len(rules),'static_rule_count':sum('static_candidate' in x['channels'] for x in rules),
        'browser_rule_count':sum('browser_candidate' in x['channels'] for x in rules),
        'manual_review_required':len(rules),'rules':rules,
        'note':'Automated channels produce candidates, not verified fixes. Manual agent review applies to every rule.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path)
    args=p.parse_args()
    payload=json.dumps(build(),ensure_ascii=False,indent=2)+'\n'
    if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(payload,encoding='utf-8')
    else:print(payload)

if __name__=='__main__':main()
