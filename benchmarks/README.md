# Benchmark estático Anti-AI-Slop — cinco formatos

## Objetivo

Estabelecer **rótulos explícitos e reproduzíveis** para o scanner antes da avaliação de sites reais. São dez arquivos (um defeituoso e um limpo por formato): HTML, Next.js/React TSX, Vue SFC, Astro e Svelte. Os casos limpos verificam falsos positivos (inclusive links âncora legítimos, texto com cor de marca, inputs com labels e comentários).

- Gabarito: `gold.json`. Unidade de avaliação: par **(arquivo, identificador de detector)**, não contagem de ocorrências.
- `development`: 5 arquivos para iteração de detectores.
- `holdout`: 5 arquivos com avaliação separada. **É um conjunto público e sintético**, não uma amostra oculta nem um teste de produção; não é independente do autor da implementação.
- Verificação: `python scripts/run_benchmark.py --out reports/benchmark.json --min-precision .90 --min-recall .85` (usa TypeScript AST quando disponível).
- Fallback sem AST: `python scripts/run_benchmark.py --no-ast`. Não apresentar o recall do fallback como cobertura AST.
- Nenhum arquivo é modificado pelo scanner nem pelo benchmark.

## Interpretação responsável

Precisão = TP/(TP+FP), recall = TP/(TP+FN), F1 = média harmônica, avaliados sobre defeitos **objetivos rotulados**. Não mede estética, qualidade de correções, segurança de produção, performance, semelhança entre projetos ou a cobertura integral das 228 heurísticas. Detectores P3 (ex.: `target=_blank` sem `rel`) são **candidatos**; navegadores modernos aplicam isolamento implícito.

### Próximas avaliações externas

Congelar os rótulos deste benchmark, adicionar projetos de terceiros com permissão de uso e gabaritos revisados por avaliadores diferentes; medir resultados por framework, severidade e detector; acompanhar casos de falso positivo com exemplos verdadeiros de marca e páginas dinâmicas. Não aumentar a nota geral da skill apenas por passar nestas fixtures.

## Extensão v1.8 — qualidade das correções estruturais e três novos detectores

Os arquivos `fixtures/accessibility-v2/` contêm cinco pares *broken/clean* rotulados
em `accessibility-gold.json`. Três problemas objetivos novos são avaliados:
`POSITIVE_TABINDEX`, `UNLABELED_SELECT`, `UNLABELED_TEXTAREA`.
A execução mede precisão e recall por **par (arquivo, tipo de defeito)**, incluindo
controles negativos: labels corretas, tabIndex zero/negativo/dinâmico e código comentado.

```bash
python scripts/run_accessibility_benchmark.py --out reports/benchmark-accessibility.json
python scripts/run_accessibility_benchmark.py --no-ast --min-recall 0.75 --out reports/benchmark-accessibility-fallback.json
python scripts/run_structural_benchmark.py --out reports/benchmark-structural.json
python scripts/run_structural_benchmark.py --browser --out reports/structural-browser.json
```

`structural/` é um conjunto separado de cinco fontes controladas (HTML, TSX,
Vue, Astro e Svelte). Cada teste deve apresentar falha inicial, proposta, diff
sem mutação, aplicação com teste de aceitação, ausência posterior do problema,
preservação literal da identidade e conteúdo, mais dois casos negativos de
hash desatualizado e rollback. Com `--browser`, só **HTML puro** recebe
navegação real no Chromium nas três resoluções; não afirmar execução de apps
compilados Vue/React/Astro/Svelte em navegador a partir desses resultados.

**Limitação metodológica:** todos os exemplos são sintéticos e rotulados pela
equipe implementadora. A ausência de falsos positivos *nesses arquivos* não
autoriza alegar falsos positivos zero em websites independentes. Testes HTTPS
externos e revisão humana continuam necessários para meta global de 9,5/10.
