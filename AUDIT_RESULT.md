# Auditoria funcional Anti-AI-Slop v1.2 — 2026-10-30

## Evidências disponíveis

- `python -m unittest discover -s tests -v`: suíte local incluindo instalação, scanner léxico/AST, gate e screenshot de fixture.
- `python scripts/verify_manifest.py`: valida integridade dos arquivos distribuídos.
- `python scripts/coverage_report.py`: 228 IDs inventariados; apenas subconjunto com suporte a detecção estática e navegador. Os demais IDs exigem agente/revisão.
- `python scripts/browser_audit.py --html tests/fixtures/site/index.html`: capturas reais de Chromium em 390×844, 768×1024 e 1440×900, com inspeção de DOM e interação por especificação.
- `python scripts/evaluate_gate.py templates/GATE_INPUT.example.json`: **deve falhar** sem evidências (controle negativo).

## Mudanças

1. Scanner inclui suporte a `.astro`, `.mdx`, comentários filtrados e diretórios/symlinks isolados.
2. Parser AST de TypeScript opcional (`--ast`) melhora precisão de imagens, eventos e links JSX/TSX.
3. Matriz rastreável de regras e plano de correção por achado com testes de aceitação.
4. Auditor Playwright opcional: capturas, overflow, acessibilidade básica, erros JS, links, imagens e testes de interação explicitamente configurados.
5. Gate programático bloqueia declaração de ≥9,5/10 com evidência ausente, P0/P1 aberto, regressão ou pendências.
6. CI com Python 3.9/3.11/3.13, teste Playwright e regressão TypeScript AST.

## Limitações de homologação

Os resultados de browser são de uma **fixture local**, não de um site de produção. O sandbox atual bloqueia navegação HTTP pelo Chromium (`ERR_BLOCKED_BY_ADMINISTRATOR`); por isso a execução de URL real permanece sem comprovação neste ambiente. Os 228 itens são catalogados mas nem todos são automatizáveis; uma correção visual ou comportamental exige análise contextual por agente com acesso ao projeto e execução de testes próprios.

**Gate de 9,5/10: não aprovado automaticamente para a skill no ecossistema inteiro.** Não há evidência de remediação comprovada num projeto externo completo, com regressão visual e testes de fluxos de negócio. A skill ficou mais robusta, mas atribuir 9,5/10 agora seria falsificar o critério de aprovação que ela própria estabelece.
