#!/usr/bin/env python3
"""Produce a deterministic manifest of *synthetic CI* evidence for GitHub Attest.

Never label agent compatibility as an authenticated agent run, and never claim
this bundle is an independent 9.5/10 validation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REQUIRED = ('agent-compat-codex','agent-compat-claude',
            'agent-compat-cursor','gate-contract-evidence','synthetic-benchmark-reports')


def build(source: Path, sha: str, run_id: str) -> dict:
    if len(sha) != 40 or any(c not in '0123456789abcdef' for c in sha):
        raise ValueError('Source commit SHA is required')
    if not run_id.isdigit() or int(run_id) <= 0:
        raise ValueError('GitHub Actions run id required')
    items=[]
    for dirname in REQUIRED:
        folder=source/dirname
        if not folder.is_dir() or folder.is_symlink():
            raise ValueError(f'Missing uploaded CI artifact: {dirname}')
        files=sorted(p for p in folder.rglob('*') if p.is_file() and not p.is_symlink())
        if not files: raise ValueError(f'Empty CI artifact: {dirname}')
        for p in files:
            if source.resolve() not in p.resolve().parents:
                raise ValueError('Unsafe path')
            items.append({'path':p.relative_to(source).as_posix(),
                          'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                          'size_bytes':p.stat().st_size})
        if dirname.startswith('agent-compat-'):
            agent=dirname.removeprefix('agent-compat-')
            reports=[json.loads(p.read_text(encoding='utf-8')) for p in files if p.name==f'agent-{agent}.json']
            if len(reports) != 1:
                raise ValueError(f'Missing or duplicated compatibility report: {agent}')
            record=reports[0]
            matches=record.get('results',[])
            if (record.get('schema') != 'anti-ai-slop/agent-compat-report/v1' or
                record.get('approved_for_compatibility') is not True or
                record.get('approved_for_real_agent_runtime') is not False or
                not isinstance(matches,list) or len(matches) != 1 or
                matches[0].get('agent') != agent or
                matches[0].get('status') != 'compatible_not_executed' or
                matches[0].get('runtime_executed') is not False):
                raise ValueError(f'Compatibility must be marked as unexecuted: {agent}')
    return {'schema':'anti-ai-slop/ci-evidence-manifest/v1',
            'scope':'synthetic-regressions-and-agent-installation-only',
            'real_agent_runtime':False,
            'independent_validation':False,
            'commit_sha':sha,'run_id':run_id,
            'files':items}


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--sha',default=os.getenv('GITHUB_SHA',''))
    p.add_argument('--run-id',default=os.getenv('GITHUB_RUN_ID',''))
    args=p.parse_args()
    try:
        result=build(args.source,args.sha,args.run_id)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(f'Manifested {len(result["files"])} synthetic CI artifacts; runtime_executed=false')
        return 0
    except (ValueError,OSError,json.JSONDecodeError) as exc:
        print(str(exc),file=sys.stderr)
        return 1

if __name__=='__main__':sys.exit(main())
