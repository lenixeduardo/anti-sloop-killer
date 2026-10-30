#!/usr/bin/env python3
"""Audit gate: evidence required; a static scan alone can NEVER pass a 9.5 score."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

WEIGHTS={'identity':25,'layout':20,'functionality':20,'accessibility':15,'motion':10,'content':10}
STATUSES={'confirmed','fixed_verified','intentional','false_positive','not_applicable','pending'}


def evaluate(data:dict)->dict:
    errors=[]
    scores=data.get('scores',{})
    if set(scores)!=set(WEIGHTS):errors.append('São obrigatórias seis notas de dimensão.')
    for key,value in scores.items():
        if key not in WEIGHTS:errors.append(f'Dimensão desconhecida: {key}')
        elif type(value) not in (float,int) or not 0<=value<=10:errors.append(f'Nota fora de 0..10: {key}')
    checks=data.get('evidence',{})
    for key in ('build','unit_tests','browser_desktop','browser_tablet','browser_mobile','functional_flows','assets_preserved'):
        if checks.get(key) is not True:errors.append(f'Evidência obrigatória ausente ou reprovada: {key}')
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
    args=p.parse_args()
    data=json.loads(args.input.read_text(encoding='utf-8'))
    result=evaluate(data)
    output=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.out:args.out.write_text(output,encoding='utf-8')
    else:print(output)
    return 0 if result['approved'] else 1

if __name__=='__main__':sys.exit(main())
