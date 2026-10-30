#!/usr/bin/env python3
"""Fail-closed 9.5 gate: checks evidence bytes, semantics and agent-runtime provenance.

This validator is NOT a substitute for independently reviewing real browser logs,
visual quality and the actions of authenticated agents. Legacy boolean mode only
exists for old integrations and cannot produce an auditable approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

WEIGHTS = {'identity':25,'layout':20,'functionality':20,'accessibility':15,'motion':10,'content':10}
REQUIRED_EVIDENCE = ('build','unit_tests','browser_desktop','browser_tablet','browser_mobile','functional_flows','assets_preserved')
REQUIRED_AGENTS = ('codex','claude','cursor')
STATUSES = {'confirmed','fixed_verified','intentional','false_positive','not_applicable','pending'}
SHA_RE = re.compile(r'^[0-9a-f]{40}$')
DIGEST_RE = re.compile(r'^[0-9a-f]{64}$')


def _safe_read(artifact: dict, base: Path) -> bytes | None:
    if not isinstance(artifact, dict) or not isinstance(artifact.get('path'), str):
        return None
    rel = Path(artifact['path'])
    digest = artifact.get('sha256')
    if rel.is_absolute() or '..' in rel.parts or not isinstance(digest,str) or not DIGEST_RE.fullmatch(digest):
        return None
    candidate = base / rel
    if candidate.is_symlink() or not candidate.is_file() or base not in candidate.resolve().parents:
        return None
    if candidate.stat().st_size > 10_000_000:
        return None
    contents = candidate.read_bytes()
    return contents if hashlib.sha256(contents).hexdigest() == digest else None


def validate_artifact(path: Path, digest: str, base: Path) -> bool:
    return _safe_read({'path': str(path), 'sha256': digest}, base.resolve()) is not None


def _json_artifact(item: dict, base: Path) -> dict | None:
    contents = _safe_read(item, base)
    if contents is None:
        return None
    try:
        data = json.loads(contents.decode('utf-8'))
        return data if isinstance(data, dict) else None
    except (ValueError, UnicodeDecodeError):
        return None


def _artifact_json_valid(key: str, artifact: dict, base: Path, common_commit: str | None) -> bool:
    obj = _json_artifact(artifact, base)
    if not obj or obj.get('kind') != key or obj.get('status') != 'passed':
        return False
    if common_commit and obj.get('commit_sha') != common_commit:
        return False
    if key in ('build','unit_tests','functional_flows'):
        if obj.get('schema') != 'anti-ai-slop/test-result/v1' or obj.get('exit_code') != 0:
            return False
        if not isinstance(obj.get('command'), str) or len(obj['command']) < 5:
            return False
        counts = obj.get('tests', {})
        if not isinstance(counts,dict) or type(counts.get('passed')) is not int or counts['passed'] < 1 or counts.get('failed') != 0:
            return False
        # Distinct external log captured by the runner, not a copied boolean.
        log = obj.get('log')
        if not isinstance(log, dict) or not _safe_read(log, base):
            return False
        return True
    if key.startswith('browser_'):
        if obj.get('schema') != 'anti-ai-slop/browser-result/v1':
            return False
        expected = {'browser_mobile':390,'browser_tablet':768,'browser_desktop':1440}[key]
        viewport = obj.get('viewport', {})
        checks = obj.get('checks', {})
        shot = _safe_read(obj.get('screenshot', {}), base)
        if (not isinstance(viewport, dict) or viewport.get('width') != expected or
            not isinstance(checks, dict) or checks.get('js_errors') != 0 or
            checks.get('horizontal_overflow') is not False or not shot or len(shot) < 24 or
            shot[:8] != b'\x89PNG\r\n\x1a\n' or shot[12:16] != b'IHDR'):
            return False
        width = int.from_bytes(shot[16:20], 'big')
        height = int.from_bytes(shot[20:24], 'big')
        return width == expected and height >= 300
    if key == 'assets_preserved':
        if obj.get('schema') != 'anti-ai-slop/asset-integrity/v1':
            return False
        assets = obj.get('assets', [])
        if not isinstance(assets,list):
            return False
        if not assets:
            return obj.get('no_assets') is True and len(str(obj.get('reason',''))) >= 20
        return all(isinstance(a,dict) and DIGEST_RE.fullmatch(str(a.get('before_sha256','')))
                   and a.get('before_sha256') == a.get('after_sha256') for a in assets)
    return False


def _catalog_review_valid(item: dict, base: Path) -> bool:
    catalog = _json_artifact(item, base)
    if not catalog:
        return False
    try:
        ids = {r['id'] for r in json.loads((Path(__file__).resolve().parents[1]/'references'/'rules.json').read_text(encoding='utf-8'))['rules']}
        entries = catalog.get('reviews', [])
        if not isinstance(entries,list) or len(entries) != len(ids) or {e.get('id') for e in entries} != ids:
            return False
        allowed = {'not_applicable','intentional','fixed_verified','false_positive'}
        return all(isinstance(e,dict) and e.get('status') in allowed
                   and len(str(e.get('reason','')).strip()) >= 20
                   and isinstance(e.get('evidence_refs'),list) and len(e['evidence_refs']) > 0
                   for e in entries)
    except (OSError, TypeError, ValueError, KeyError, AttributeError):
        return False


def _agent_runtime_valid(entry: dict, agent: str, base: Path, sha: str | None) -> bool:
    report = _json_artifact(entry, base)
    if not report or report.get('schema') != 'anti-ai-slop/agent-runtime/v1':
        return False
    if (report.get('agent') != agent or report.get('runtime_executed') is not True
        or report.get('exit_code') != 0 or report.get('status') != 'passed'
        or (sha and report.get('commit_sha') != sha)
        or not report.get('invocation')):
        return False
    transcript = report.get('transcript')
    if not isinstance(transcript,dict):
        return False
    log = _safe_read(transcript, base)
    return bool(log and len(log) >= 80 and agent.encode('ascii') in log.lower())


def evaluate(data:dict, *, strict:bool=False, base_dir:Path|None=None)->dict:
    errors = []
    scores = data.get('scores', {})
    if not isinstance(scores, dict) or set(scores) != set(WEIGHTS):
        errors.append('São obrigatórias seis notas de dimensão.')
        scores = scores if isinstance(scores,dict) else {}
    for key,value in scores.items():
        if key not in WEIGHTS:
            errors.append(f'Dimensão desconhecida: {key}')
        elif type(value) not in (float,int) or not 0 <= value <= 10:
            errors.append(f'Nota fora de 0..10: {key}')
    checks = data.get('evidence', {})
    checks = checks if isinstance(checks,dict) else {}
    for key in REQUIRED_EVIDENCE:
        if checks.get(key) is not True:
            errors.append(f'Evidência obrigatória ausente ou reprovada: {key}')
    if strict:
        base = (base_dir or Path.cwd()).resolve()
        repo_commit = data.get('commit_sha')
        if not isinstance(repo_commit,str) or not SHA_RE.fullmatch(repo_commit):
            errors.append('Commit SHA obrigatório para vincular evidências ao projeto.')
            repo_commit = None
        if os.getenv('GITHUB_SHA') and repo_commit != os.getenv('GITHUB_SHA'):
            errors.append('Commit não corresponde ao GITHUB_SHA do CI.')
        artifacts = data.get('artifacts', {})
        if not isinstance(artifacts,dict):
            artifacts = {}
        for key in REQUIRED_EVIDENCE:
            if not _artifact_json_valid(key, artifacts.get(key), base, repo_commit):
                errors.append(f'Evidência com semântica, hash ou resultado inválido: {key}')
        if not _catalog_review_valid(data.get('catalog_review_artifact'), base):
            errors.append('Revisão dos 228 IDs não possui referências e justificativas verificáveis.')
        visual = _json_artifact(data.get('manual_visual_review_artifact'), base)
        if (not visual or visual.get('schema') != 'anti-ai-slop/visual-review/v1'
            or visual.get('status') != 'approved' or len(str(visual.get('reviewer',''))) < 3
            or not isinstance(visual.get('notes'),list) or not visual['notes']):
            errors.append('Revisão visual independente não comprovada por artefato.')
        agent_runs = data.get('agent_runs', {})
        if not isinstance(agent_runs,dict):
            agent_runs = {}
        for agent in REQUIRED_AGENTS:
            if not _agent_runtime_valid(agent_runs.get(agent),agent,base,repo_commit):
                errors.append(f'Execução real autenticada não comprovada: {agent}')
    findings = data.get('findings',[])
    if not isinstance(findings,list):
        errors.append('findings deve ser uma lista')
        findings = []
    for finding in findings:
        if not isinstance(finding,dict) or finding.get('status') not in STATUSES:
            errors.append('Status inválido de achado')
            continue
        if strict and finding.get('status') in ('confirmed','pending'):
            errors.append(f"Achado não resolvido: {finding.get('id','unknown')}")
        elif finding.get('status') in ('confirmed','pending') and str(finding.get('severity','P2')).startswith(('P0','P1')):
            errors.append(f"P0/P1 não resolvido: {finding.get('id','unknown')}")
        if finding.get('status') == 'fixed_verified' and not finding.get('test_evidence'):
            errors.append(f"Correção sem teste comprovado: {finding.get('id','unknown')}")
    if data.get('catalog_review_complete') is not True:
        errors.append('Revisão contextual dos IDs aplicáveis pendente.')
    if data.get('manual_visual_review') is not True:
        errors.append('Revisão visual comparativa pendente.')
    if data.get('unreviewed_candidates',0) != 0:
        errors.append('Há candidatos da varredura sem triagem.')
    valid_scores = len(scores) == len(WEIGHTS) and all(type(scores.get(k)) in (int,float) and 0 <= scores[k] <= 10 for k in WEIGHTS)
    score = round(sum(scores[k]*weight/100 for k,weight in WEIGHTS.items()),2) if valid_scores else None
    if score is None or score < 9.5:
        errors.append('Nota ponderada abaixo de 9,5 ou ausente.')
    return {'score':score,'approved':not errors,'blockers':errors,'weights':WEIGHTS,
            'warning':'Hashes provam integridade, não veracidade. Requer revisão independente de logs, agentes e imagens.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--legacy-bools',action='store_true', help='Legacy untrusted evaluation, NEVER a valid final 9.5 approval')
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8'))
    result = evaluate(data, strict=not args.legacy_bools, base_dir=args.input.resolve().parent)
    if args.legacy_bools:
        result['legacy_only'] = True
        result['approved'] = False
        result['blockers'].append('Modo de compatibilidade não permite aprovação auditável.')
    output = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding='utf-8')
    else:
        print(output)
    return 0 if result['approved'] else 1

if __name__=='__main__':
    sys.exit(main())
