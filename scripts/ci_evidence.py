#!/usr/bin/env python3
"""Run a CI check and record exact argv, exit status, log bytes and SHA-256.

No shell evaluation; no fabricated pass on missing commands. Logs should contain
only non-secret, synthetic fixtures when uploaded to public repositories.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_command(kind: str, command: list[str], out: Path, *, timeout: int = 300) -> dict:
    if kind not in ('build','unit_tests','functional_flows','agent_compatibility','gate_contract'):
        raise ValueError('Unsupported evidence kind')
    if not command or any('\x00' in arg for arg in command):
        raise ValueError('Command argv required')
    out.mkdir(parents=True,exist_ok=True)
    try:
        run = subprocess.run(command,capture_output=True,text=True,timeout=timeout,
                             encoding='utf-8',errors='replace')
        log = run.stdout + ('\nSTDERR:\n' + run.stderr if run.stderr else '')
        exit_code = run.returncode
    except subprocess.TimeoutExpired as exc:
        exit_code=124
        log=f'Timeout: {timeout} seconds\n{str(exc)}'
    log_path=out/f'{kind}.log'
    log_path.write_text(log,encoding='utf-8')
    artifact={"schema":"anti-ai-slop/test-result/v1", "kind":kind,
              "status":"passed" if exit_code == 0 else "failed", "exit_code":exit_code,
              "command":subprocess.list2cmdline(command),
              "tests":{"passed":1 if exit_code == 0 else 0,"failed":0 if exit_code == 0 else 1},
              "commit_sha":os.getenv('GITHUB_SHA'),
              "timestamp_utc":datetime.now(timezone.utc).isoformat(),
              "log":{"path":log_path.name,'sha256':hashlib.sha256(log_path.read_bytes()).hexdigest()}}
    result_path=out/f'{kind}.json'
    result_path.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return artifact


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind',required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--timeout',type=int,default=300)
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    argv=args.command[1:] if args.command and args.command[0]=='--' else args.command
    result=run_command(args.kind,argv,args.out,timeout=args.timeout)
    print(json.dumps({'kind':result['kind'],'status':result['status'],'exit_code':result['exit_code'],'output':str(args.out)}))
    return 0 if result['status']=='passed' else 1

if __name__=='__main__':
    sys.exit(main())
