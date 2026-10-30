#!/usr/bin/env python3
"""Verify integrity of manifest tracked files; returns a nonzero exit code on mismatch."""
import hashlib
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'MANIFEST.sha256'
failures=[]
for line in manifest.read_text(encoding='utf-8').splitlines():
    if not line.strip():continue
    try:expected,rel=line.split('  ',1)
    except ValueError:
        failures.append('Linha inválida'); continue
    path=(ROOT/rel).resolve()
    if ROOT.resolve() not in path.parents or not path.is_file():
        failures.append(f'{rel}: ausente/inseguro');continue
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:failures.append(f'{rel}: hash diferente')
if failures:
    print('\n'.join(failures),file=sys.stderr)
    sys.exit(1)
print('Integrity OK')
