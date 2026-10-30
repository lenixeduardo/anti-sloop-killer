#!/usr/bin/env python3
"""Produce a CI evidence summary with a hard boundary between compatibility and runtime."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def summarize(paths: list[Path]) -> str:
    lines=['# Anti-AI-Slop: evidence summary','','| Evidence | Status | Meaning |','|---|---|---|']
    for path in paths:
        if not path.exists():
            lines.append(f'| {path.name} | missing | No evidence |')
            continue
        try:
            data=json.loads(path.read_text(encoding='utf-8'))
            if data.get('schema')=='anti-ai-slop/agent-compat-report/v1':
                results=data.get('results',[])
                for result in results:
                    lines.append(f"| {result.get('agent')} | {result.get('status')} | Installation / scanner only; NOT real agent execution |")
            elif data.get('schema')=='anti-ai-slop/test-result/v1':
                lines.append(f"| {data.get('kind')} | {data.get('status')} | exit_code={data.get('exit_code')}; source log in artifact |")
            else:
                lines.append(f'| {path.name} | unrecognized schema | Never assert successful completion |')
        except (OSError,ValueError,TypeError):
            lines.append(f'| {path.name} | invalid JSON | No evidence |')
    lines.extend(['','**Gate status:** NOT HOMOLOGATED for 9.5. Real authenticated Codex, Claude Code and Cursor invocations and independent review are required.'])
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('files',nargs='+',type=Path)
    p.add_argument('--out',type=Path,default=Path('reports/CI_EVIDENCE_SUMMARY.md'))
    args=p.parse_args()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    text=summarize(args.files)
    args.out.write_text(text,encoding='utf-8')
    print(text)

if __name__=='__main__':main()
