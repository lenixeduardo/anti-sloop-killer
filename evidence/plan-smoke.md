# Plano de correção Anti-AI-Slop

Todo achado é candidato até confirmação com DOM, testes e contexto da marca.

| ID | Origem | Prioridade | Local | Estado inicial |
|---|---|---|---|---|
| STATIC-0001 | PLACEHOLDER_HREF | P0_CANDIDATE | `index.html:1` | candidate_not_verified |

## Instruções obrigatórias para o agente

1. Antes da edição: salvar `git status --short`, hashes dos assets aprovados, comando de build e baseline de screenshots.
2. Por achado: confirmar reprodução, relacionar IDs de catálogo, identificar causa real e impacto; classificar intencional/falso positivo/não aplicável quando couber.
3. Criar teste de aceitação que falhe ANTES da alteração. Não corrigir defaults que sejam identidade aprovada.
4. Aplicar a menor mudança de código possível; gerar diff revisável. Não usar conteúdo, usuários ou métricas falsos.
5. Executar lint, testes, build, browser desktop/tablet/mobile, funções críticas e redução de movimento.
6. Confirmar hashes de assets e comportamentos preservados; reverter somente alterações da correção se houver regressão.
7. Preencher `templates/GATE_INPUT.example.json` com notas e EVIDÊNCIAS REAIS; executar `scripts/evaluate_gate.py`.
8. Se o gate não aprovar, manter o status pendente, documentar bloqueio e repetir; nunca declarar 9,5 sem homologação.

## Confirmação e testes de aceitação

### STATIC-0001 — PLACEHOLDER_HREF
- Referência: NX-043, NX-056
- Local: `index.html:1`
- Orientação: Link parece placeholder; # pode ser âncora de topo legítima.
- Status: `pending` (atualizar para confirmed/fixed_verified/intentional/false_positive/not_applicable)
- Prova antes/depois: **pendente**
- Teste de aceitação: **pendente**
