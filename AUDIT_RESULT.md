# Auditoria funcional — Anti-AI-Slop v1.3

Data: 30/10/2026. Escopo: skill no repositório, scanner de pré-varredura, instaladores, patch transacional, browser audit, gate de evidências, testes unitários e E2E sintéticos.

## Resultado: **8,4/10 — meta 9,5 não homologada**

A skill evoluiu de documentação + scanner parcial para um workflow executável e reversível. A nota não deve ser inflada por testes sintéticos: falta avaliação independente de agentes Codex/Claude/Cursor em repositórios externos com critérios humanos de identidade visual e fluxos reais.

| Pilar | Peso | Avaliação | Evidência |
|---|---:|---:|---|
| Instalação e distribuição | 15% | 9,5 | integração local, backup, SHA-256 |
| Catálogo e rastreabilidade | 10% | 9,0 | 228 regras e 14 paletas inventariadas |
| Instruções e preservação | 15% | 9,2 | SKILL.md + playbook + aplicação explícita |
| Detecção automática | 25% | 7,0 | 29 IDs estáticos, 7 IDs DOM, heurísticas restantes manuais |
| Correção comprovada | 15% | 8,0 | preview, SHA baseline, testes de aceitação e rollback; fixture sintética |
| Browser/UX | 10% | 8,5 | Chromium, 3 viewports, interações, overflow, labels, contrastes e headings |
| Segurança e regressões | 10% | 9,0 | testes unitários, CI, proteção de symlinks, gate de evidências |
| **Ponderada** | **100%** | **8,4** | **Não atende à meta 9,5/10** |

## O que está comprovado

- `python -m unittest discover -s tests -v` executa a suíte inteira, incluindo instalação e o fluxo real de correção em Chromium quando Playwright está disponível.
- `python scripts/validate_catalog.py` verifica os 228 IDs, 14 paletas e sincronização dos índices.
- `python scripts/verify_manifest.py` verifica hashes e a integridade do pacote.
- `python scripts/apply_changes.py` usa mudanças pontuais propostas por agente: primeiro preview, depois aplicação com autorização e testes; falhas de teste restauram os bytes originais.
- `python scripts/browser_audit.py` fornece capturas em desktop, tablet e mobile, interações controladas, candidatos de contraste e heading sem autoaprovação.
- `python scripts/evaluate_gate.py` exige artefatos com SHA-256 e registro de status dos 228 IDs por padrão; não considera apenas booleanos.

## Lacunas objetivas para 9,5

1. Testar agente real em pelo menos três stacks externas (Next/React, Vue/Astro, HTML) e dois sites de produção/preview com funcionalidades não simuladas. Cada teste deve ter baseline, aceitação, screenshots, integração e regressões.
2. Ampliar a cobertura de detecção com parsers estruturados onde necessário. Regex/AST parcial e DOM genérico **não cobrem os 228 padrões automaticamente**; medir precisão e recall em amostra representativa de sites.
3. Exigir revisão independente de identidade, contraste com fundo complexo, animações, acessibilidade WCAG e qualidade de conteúdo, que não são decidíveis apenas por scanner.
4. Verificar publicamente o workflow de GitHub Actions verde depois do push, não somente testes locais.

## Observação

O teste E2E usa site sintético e Chromium real, não um caso de cliente. O fluxo de patch altera apenas conteúdo explicitamente aprovado, não redesenha interfaces automaticamente. Não criar ou alterar imagens de marca ao executar esta skill sem autorização explícita.

## Atualização v1.4 — benchmark de detecção

Foi criado um corpus local rotulado com 10 arquivos em 5 stacks e candidatos estáticos ampliados de 29 para 32 IDs. No modo TypeScript AST, o corpus sintético apresentou 39 TP, 0 FP e 0 FN (precisão e recall 100% **apenas nessa amostra**); sem AST, 34 TP e 5 FN. A suíte local possui 58 testes; consulte `BENCHMARK_RESULT.md` e `evidence/benchmark-v14.json`. O benchmark é transparente e não constitui avaliação externa independente. **A nota geral permanece 8,4/10 até validação de projetos externos e agentes reais.**

## Atualização de segurança v1.7 — 30/10/2026

**Correção da vulnerabilidade adversarial:** o gate v1.6 aprovava pontuação 10/10 com JSONs, transcrições inventadas e PNGs brancos com SHA-256 correto. O caso foi incorporado em `tests/test_gate_forgery_regression.py`. O teste exige que o resultado permaneça reprovado, com bloqueio específico de proveniência.

O gate estrito v1.7 exige uma **atestação criptográfica GitHub/Sigstore** de um manifesto que contenha exatamente os hashes de todos os comprovantes, vinculado ao commit SHA, repositório, ref e identidade de um workflow **independente**. Ausência da CLI `gh`, falta de atestado, assinatura inválida, artefato não correspondente ou workflow não autorizado produzem reprovação. O modo legado continua sem poder emitir aprovação.

O CI regular passa a gerar **proveniência assinada dos testes sintéticos**, deliberadamente marcados `real_agent_runtime=false` e `independent_validation=false`. Ela nunca é aceita como atestado final. Não foram executadas nem autenticadas sessões reais de Codex, Claude Code e Cursor; o workflow independente ainda precisa ser implantado em infraestrutura autorizada, incluindo revisão humana e testes em projetos externos.

**Validação local:** 91 testes executados, 89 aprovados e 2 ignorados por dependências opcionais; verificação do manifesto e catálogo aprovadas. **Verificação remota:** pendente após publicação deste commit. **Nota global 9,5:** ainda não homologada.
