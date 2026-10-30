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

## Atualização v1.4 — etapas 1 e 2 do plano (30/10/2026)

- **Benchmark sintético de cinco stacks**: dez arquivos rotulados (HTML, Next/React, Vue, Astro, Svelte), com divisão development/holdout explícita, 39 pares positivos testados e cinco negativos; métricas em `evidence/benchmark-stacks-v14.json`.
- **Benchmark de cinco cenários de produto**: portfólio, Next/React, Vue/Astro, e-commerce e dashboard; 29 candidatos objetivos rotulados, controles seguros e métricas em `evidence/benchmark-scenarios-v14.json`.
- **Ampliação do scanner**: analisadores estruturados de markup, JSX via TypeScript AST, CSS com contraste literal de primeiro nível e foco sem alternativa; deduplicação e validação contra falsos positivos em código comentado e templates. Cobertura candidata do inventário atualizada em `evidence/coverage-v14.json`.
- **Testes**: 63 testes locais aprovados, integridade SHA-256 confirmada; job de benchmark adicionado ao CI.
- **PENDÊNCIAS**: os dois sites HTTPS não foram publicados nem testados; os gabaritos não têm avaliação independente; nenhum resultado representa eficácia sobre todas as 228 regras. A nota global de 9,5/10 **não está homologada** por esses testes.
