#!/usr/bin/env python3
"""Fail-closed GitHub/Sigstore provenance for an independent runtime audit.

Hashes only attest to bytes. This layer verifies signer identity, source commit and
that the signed manifest references *all* evidence used to award a high score.
The signer workflow must execute authentic provider sessions and be independently
reviewed. CI synthetic fixtures must never use that workflow identity.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

REPO = 'lenixeduardo/anti-sloop-killer'
SIGNER = f'{REPO}/.github/workflows/independent-validation.yml'
MANIFEST_SCHEMA = 'anti-ai-slop/independent-evidence-manifest/v1'
MANDATORY = ('build','unit_tests','browser_desktop','browser_tablet','browser_mobile',
             'functional_flows','assets_preserved','catalog_review','visual_review',
             'agent_codex','agent_claude','agent_cursor')
HEX40 = re.compile(r'^[0-9a-f]{40}$')
HEX64 = re.compile(r'^[0-9a-f]{64}$')


def read_ref(item: dict, base: Path) -> bytes | None:
    if not isinstance(item, dict) or not isinstance(item.get('path'), str):
        return None
    try:
        rel = Path(item['path'])
        if rel.is_absolute() or '..' in rel.parts or not HEX64.fullmatch(str(item.get('sha256',''))):
            return None
        path = base / rel
        if path.is_symlink() or not path.is_file() or base not in path.resolve().parents or path.stat().st_size > 10_000_000:
            return None
        content = path.read_bytes()
        return content if hashlib.sha256(content).hexdigest() == item['sha256'] else None
    except (OSError, ValueError):
        return None


def evidence_hashes(data: dict) -> dict[str, str] | None:
    """Every claim's exact digest; a signed list must match every referenced artifact."""
    result = {}
    mapping = dict(data.get('artifacts') or {})
    mapping['catalog_review'] = data.get('catalog_review_artifact')
    mapping['visual_review'] = data.get('manual_visual_review_artifact')
    for agent in ('codex','claude','cursor'):
        mapping[f'agent_{agent}'] = (data.get('agent_runs') or {}).get(agent)
    for key in MANDATORY:
        item = mapping.get(key)
        if not isinstance(item, dict) or not HEX64.fullmatch(str(item.get('sha256', ''))):
            return None
        result[key] = item['sha256']
    return result


def verify_attestation(data: dict, base: Path, commit_sha: str | None,
                       *, runner=subprocess.run, which=shutil.which) -> tuple[bool, str]:
    """Independent verification via gh CLI; no local trust toggles or offline bypass."""
    item = data.get('signed_evidence_manifest')
    if not commit_sha or not HEX40.fullmatch(commit_sha) or not isinstance(item, dict):
        return False, 'Manifesto atestado ausente ou commit inválido.'
    raw = read_ref(item, base)
    if raw is None:
        return False, 'Manifesto assinado ausente, inválido ou adulterado.'
    try:
        manifest = json.loads(raw)
    except (UnicodeDecodeError, ValueError):
        return False, 'Manifesto de proveniência não é JSON válido.'
    hashes = evidence_hashes(data)
    if (not isinstance(manifest,dict) or manifest.get('schema') != MANIFEST_SCHEMA or
        manifest.get('commit_sha') != commit_sha or manifest.get('repository') != REPO or
        manifest.get('signer_workflow') != SIGNER or hashes is None or
        manifest.get('artifact_sha256') != hashes or
        not isinstance(manifest.get('project_url'),str) or
        not manifest['project_url'].startswith('https://')):
        return False, 'Manifesto não vincula os artefatos, commit, projeto HTTPS e workflow esperados.'
    gh = which('gh')
    if not gh:
        return False, 'GitHub CLI ausente; não é possível verificar atestado Sigstore.'
    command = [gh, 'attestation', 'verify', str((base / item['path']).resolve()),
               '--repo', REPO, '--signer-workflow', SIGNER,
               '--source-digest', commit_sha, '--source-ref', 'refs/heads/main',
               '--format', 'json']
    try:
        proc = runner(command, capture_output=True, text=True, timeout=60, check=False)
        if proc.returncode:
            return False, 'Assinatura ou identidade do workflow não passou na verificação GitHub.'
        verified = json.loads(proc.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError):
        return False, 'Resposta do verificador de atestados ausente ou inválida.'
    if not isinstance(verified,list):
        return False, 'Verificador não forneceu atestados verificáveis.'
    digest = hashlib.sha256(raw).hexdigest()
    basename = Path(item['path']).name
    for record in verified:
        result = record.get('verificationResult',{}) if isinstance(record,dict) else {}
        statement = result.get('statement',{}) if isinstance(result,dict) else {}
        subjects = statement.get('subject',[]) if isinstance(statement,dict) else []
        if statement.get('predicateType') != 'https://slsa.dev/provenance/v1':
            continue
        if any(isinstance(subject,dict) and subject.get('name','').split('/')[-1] == basename
               and subject.get('digest',{}).get('sha256') == digest for subject in subjects):
            return True, 'Atestado GitHub/Sigstore verificado, vinculado à evidência e ao commit.'
    return False, 'Atestado não corresponde ao SHA-256 do manifesto submetido.'
