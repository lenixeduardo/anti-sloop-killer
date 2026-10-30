#!/usr/bin/env python3
"""Apply agent-proposed exact edits safely, with dry run and rollback on test failure.

This tool does not propose fixes or interpret UI intent. The agent must confirm findings,
obtain approval, provide exact expected hashes and run project-specific acceptance checks.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path

MAX_FILE_BYTES = 2_000_000


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare(project: Path, proposal: dict) -> list[dict]:
    if project.is_symlink() or not project.is_dir():
        raise ValueError('Project root must be an existing non-symlink directory')
    root = project.resolve()
    changes = proposal.get('changes')
    if not isinstance(changes, list) or not changes:
        raise ValueError('Proposal requires a nonempty changes list')
    if len(changes) > 50:
        raise ValueError('Too many changes; split into batches <= 50')
    outputs = {}
    for item in changes:
        if not isinstance(item, dict):
            raise ValueError('Each change must be an object')
        raw = item.get('path')
        if not isinstance(raw, str) or not raw or '\\' in raw or '\0' in raw:
            raise ValueError('Invalid file path')
        rel = Path(raw)
        if rel.is_absolute() or any(x in ('.', '..') for x in rel.parts):
            raise ValueError(f'Path traversal forbidden: {raw}')
        candidate = root / rel
        if any(p.is_symlink() for p in (candidate, *candidate.parents) if p != root and root in p.parents):
            raise ValueError(f'Symlink forbidden: {raw}')
        if not candidate.is_file() or root not in candidate.resolve().parents:
            raise ValueError(f'File is outside project or missing: {raw}')
        data = candidate.read_bytes()
        if len(data) > MAX_FILE_BYTES:
            raise ValueError(f'File exceeds safe limit: {raw}')
        expected = item.get('expected_sha256')
        if not isinstance(expected, str) or expected != sha(data):
            raise ValueError(f'Baseline hash mismatch: {raw}')
        old, new = item.get('search'), item.get('replace')
        if not isinstance(old, str) or not old or not isinstance(new, str) or old == new:
            raise ValueError(f'Invalid exact replacement: {raw}')
        try:
            original = data.decode('utf-8')
        except UnicodeDecodeError as e:
            raise ValueError(f'Only UTF-8 source files supported: {raw}') from e
        stage = outputs.setdefault(raw, {'path': candidate, 'before': data, 'current': original, 'reason': []})
        # All replacements apply to one in-memory snapshot, never partially on disk.
        if stage['current'].count(old) != 1:
            raise ValueError(f'Exact match must occur once in {raw}: found {stage["current"].count(old)}')
        stage['current'] = stage['current'].replace(old, new, 1)
        stage['reason'].append(str(item.get('finding_id', 'unassigned')))
    return list(outputs.values())


def apply(project: Path, proposal: dict, *, approved: bool = False, checks: list[list[str]] | None = None) -> dict:
    edits = prepare(project, proposal)
    diffs = []
    for entry in edits:
        before = entry['before'].decode('utf-8')
        after = entry['current']
        rel = str(entry['path'].relative_to(project.resolve()))
        diffs.extend(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                         fromfile='a/'+rel, tofile='b/'+rel))
    result = {'status': 'preview', 'files': len(edits), 'diff': ''.join(diffs), 'checks': []}
    if not approved:
        return result
    try:
        for entry in edits:
            if sha(entry['path'].read_bytes()) != sha(entry['before']):
                raise ValueError(f'File changed between review and apply: {entry["path"]}')
        for entry in edits:
            entry['path'].write_bytes(entry['current'].encode('utf-8'))
        for argv in checks or []:
            if not argv or any(not isinstance(x, str) or not x for x in argv):
                raise ValueError('Verification command invalid')
            proc = subprocess.run(argv, cwd=project, capture_output=True, text=True, timeout=120, shell=False)
            check = {'command': argv, 'exit_code': proc.returncode,
                     'stdout_tail': proc.stdout[-3000:], 'stderr_tail': proc.stderr[-3000:]}
            result['checks'].append(check)
            if proc.returncode != 0:
                raise RuntimeError(f'Acceptance check failed: {argv[0]} (exit {proc.returncode})')
        result['status'] = 'applied_verified' if checks else 'applied_unverified'
        result['sha256_after'] = {str(e['path'].relative_to(project.resolve())):
                                  sha(e['path'].read_bytes()) for e in edits}
    except Exception as e:
        for entry in edits:
            entry['path'].write_bytes(entry['before'])
        result['status'] = 'rolled_back'
        result['error'] = str(e)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('proposal', type=Path)
    parser.add_argument('--apply', action='store_true', help='Actually modify files after human review')
    parser.add_argument('--check', action='append', default=[], help='Explicit verification argv (quoted string), repeatable')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    try:
        proposal = json.loads(args.proposal.read_text(encoding='utf-8'))
        result = apply(args.project, proposal, approved=args.apply,
                       checks=[shlex.split(command) for command in args.check])
        output = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output, encoding='utf-8')
        else:
            print(output)
        return 0 if result['status'] in ('preview','applied_verified','applied_unverified') else 1
    except (ValueError, OSError, json.JSONDecodeError, subprocess.SubprocessError) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
