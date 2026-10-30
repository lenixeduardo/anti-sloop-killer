#!/usr/bin/env python3
"""Audit gate: evidence required; a static scan alone can NEVER pass a 9.5 score."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

WEIGHTS={'identity':25,'layout':20,'functionality':20,'accessibility':15,'motion':10,'content':10}
REQUIRED_EVIDENCE=('build','unit_tests','browser_desktop','browser_tablet','browser_mobile','functional_flows','assets_preserved')
STATUSES={'confirmed','fixed_verified','intentional','false_positive','not_applicable','pending'}


def validate_artifact(path: Path, digest: str, base: Path) -> bool:
    """Verify bytes on disk; never trust a path or a boolean without a digest."""
    if not isinstance(digest, str) or len(digest) != 64:
        return False
    if not isinstance(path, Path) or path.is_symlink() or path.is_absolute() or '..' in path.parts:
        return False
    candidate = base / path
    if not candidate.is_file() or candidate.is_symlink() or base not in candidate.resolve().parents:
        return False
    return hashlib.sha256(candidate.read_bytes()).hexdigest() == digest


def evaluate(data:dict, *, strict:bool=False, base_dir:Path|None=None)->dict:
    errors=[]
    scores=data.get('scores',{})
    if set(scores)!=set(WEIGHTS):errors.append('São obrigatórias seis notas de dimensão.')
    for key,value in scores.items():
        if key not in WEIGHTS:errors.append(f'Dimensão desconhecida: {key}')
        elif type(value) not in (float,int) or not 0<=value<=10:errors.append(f'Nota fora de 0..10: {key}')
    checks=data.get('evidence',{})
    for key in REQUIRED_EVIDENCE:
        if checks.get(key) is not True:errors.append(f'Evidência obrigatória ausente ou reprovada: {key}')
    if strict:
        base=(base_dir or Path.cwd()).resolve()
        artifacts=data.get('artifacts',{})
        for key in REQUIRED_EVIDENCE:
            item=artifacts.get(key) if isinstance(artifacts,dict) else None
            if not isinstance(item,dict) or not validate_artifact(Path(item.get('path','')),
                    item.get('sha256',''),base):
                errors.append(f'Comprovante inválido ou ausente: {key}')
        catalog=data.get('catalog_review_artifact')
        if not isinstance(catalog,dict) or not validate_artifact(Path(catalog.get('path','')),
                catalog.get('sha256',''),base):
            errors.append('Revisão do catálogo sem arquivo verificável.')
        else:
            try:
                review=json.loads((base/catalog['path']).read_text(encoding='utf-8'))
                ids={r['id'] for r in json.loads((Path(__file__).resolve().parents[1]/'references'/'rules.json').read_text(encoding='utf-8'))['rules']}
                entries=review.get('reviews',[])
                if not isinstance(entries,list) or {e.get('id') for e in entries}!=ids or len(entries)!=len(ids) or any(
                    e.get('status') not in {'not_applicable','intentional','fixed_verified','false_positive','confirmed'}
                    or len(str(e.get('reason','')).strip())<12 for e in entries):
                    errors.append('Revisão contextual incompleta: 228 IDs com status e justificativa obrigatórios.')
            except (OSError,ValueError,TypeError,KeyError):
                errors.append('Arquivo de revisão contextual ilegível ou inválido.')
    findings=data.get('findings',[])
    if not isinstance(findings,list):
        errors.append('findings deve ser uma lista')
        findings=[]
    for finding in findings:
        if finding.get('status') not in STATUSES:errors.append('Status inválido de achado')
        elif finding.get('status') in ('confirmed','pending') and finding.get('severity','P2').startswith(('P0','P1')):
            errors.append(f"P0/P1 não resolvido: {finding.get('id','unknown')}")
        if finding.get('status')=='fixed_verified' and not finding.get('test_evidence'):
            errors.append(f"Correção sem teste comprovado: {finding.get('id','unknown')}")
    if data.get('catalog_review_complete') is not True:
        errors.append('Revisão contextual dos IDs aplicáveis pendente.')
    if data.get('manual_visual_review') is not True:
        errors.append('Revisão visual comparativa pendente.')
    if data.get('unreviewed_candidates',0)>0:
        errors.append('Há candidatos da varredura sem triagem.')
    score=round(sum(scores[k]*weight/100 for k,weight in WEIGHTS.items()),2) if len(scores)==len(WEIGHTS) and all(type(scores.get(k)) in (int,float) and 0<=scores[k]<=10 for k in WEIGHTS) else None
    if score is None or score<9.5:errors.append('Nota ponderada abaixo de 9,5 ou ausente.')
    return {'score':score,'approved':not errors,'blockers':errors,'weights':WEIGHTS,
        'warning':'Somente evidências fornecidas; confirme links, logs e screenshots externamente antes de aceitar qualquer declaração.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path,help='JSON preenchido pelo avaliador humano/agente com evidências')
    p.add_argument('--out',type=Path)
    p.add_argument('--legacy-bools',action='store_true',help='Compatibilidade com score antigo, sem aprovação auditável')
    args=p.parse_args()
    data=json.loads(args.input.read_text(encoding='utf-8'))
    result=evaluate(data,strict=not args.legacy_bools,base_dir=args.input.resolve().parent)
    output=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.out:args.out.write_text(output,encoding='utf-8')
    else:print(output)
    return 0 if result['approved'] else 1

if __name__=='__main__':sys.exit(main())
