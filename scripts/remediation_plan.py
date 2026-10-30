#!/usr/bin/env python3
"""Generate a reviewable plan from a scanner JSON; does not edit the scanned project."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def make_plan(report:dict)->str:
    lines=['# Plano de correção Anti-AI-Slop','',
         'Todo achado é candidato até confirmação com DOM, testes e contexto da marca.','',
         '| ID | Origem | Prioridade | Local | Estado inicial |','|---|---|---|---|---|']
    for f in report.get('findings',[]):
        lines.append(f"| {f.get('id','?')} | {f['key']} | {f['severity']} | `{f['file']}:{f['line']}` | candidate_not_verified |")
    lines+=['','## Instruções obrigatórias para o agente','',
      '1. Antes da edição: salvar `git status --short`, hashes dos assets aprovados, comando de build e baseline de screenshots.',
      '2. Por achado: confirmar reprodução, relacionar IDs de catálogo, identificar causa real e impacto; classificar intencional/falso positivo/não aplicável quando couber.',
      '3. Criar teste de aceitação que falhe ANTES da alteração. Não corrigir defaults que sejam identidade aprovada.',
      '4. Aplicar a menor mudança de código possível; gerar diff revisável. Não usar conteúdo, usuários ou métricas falsos.',
      '5. Executar lint, testes, build, browser desktop/tablet/mobile, funções críticas e redução de movimento.',
      '6. Confirmar hashes de assets e comportamentos preservados; reverter somente alterações da correção se houver regressão.',
      '7. Preencher `templates/GATE_INPUT.example.json` com notas e EVIDÊNCIAS REAIS; executar `scripts/evaluate_gate.py`.',
      '8. Se o gate não aprovar, manter o status pendente, documentar bloqueio e repetir; nunca declarar 9,5 sem homologação.','',
      '## Confirmação e testes de aceitação','']
    for f in report.get('findings',[]):
        lines +=[f"### {f.get('id','?')} — {f['key']}",
                 f"- Referência: {', '.join(f.get('source_rules',[]))}",
                 f"- Local: `{f['file']}:{f['line']}`",
                 f"- Orientação: {f.get('note','Revisar o contexto.')}",
                 '- Status: `pending` (atualizar para confirmed/fixed_verified/intentional/false_positive/not_applicable)',
                 '- Prova antes/depois: **pendente**','- Teste de aceitação: **pendente**','']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('scanner_json',type=Path)
    p.add_argument('--out',type=Path)
    args=p.parse_args()
    text=make_plan(json.loads(args.scanner_json.read_text(encoding='utf-8')))
    if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text,encoding='utf-8')
    else:print(text)

if __name__=='__main__':main()
