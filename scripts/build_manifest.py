#!/usr/bin/env python3
"""Regenerate distribution manifest using exactly the files copied by install.py."""
from pathlib import Path
from hashlib import sha256
from install import PARTS, ignore_entries

ROOT=Path(__file__).resolve().parents[1]
rows=[]
for part in PARTS:
    path=ROOT/part
    files=sorted(path.rglob('*')) if path.is_dir() else [path]
    for file in files:
        if not file.is_file() or file.is_symlink():continue
        rel=file.relative_to(ROOT)
        if str(rel)=='MANIFEST.sha256':continue
        if any(item in {'__pycache__','.pytest_cache','.mypy_cache','.venv','node_modules','.git','.DS_Store'} or item.endswith(('.pyc','.pyo')) for item in rel.parts):continue
        rows.append((str(rel).replace('\\','/'), sha256(file.read_bytes()).hexdigest()))
(ROOT/'MANIFEST.sha256').write_text(''.join(f'{digest}  {path}\n' for path,digest in sorted(rows)),encoding='utf-8')
print(f'Wrote {len(rows)} file hashes')
