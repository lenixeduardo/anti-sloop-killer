# Benchmark de detecção Anti-AI-Slop

## Escopo e limites (obrigatório antes de interpretar as métricas)

Este repositório contém **dois conjuntos sintéticos**, não cinco aplicações externas de produção:

1. `fixtures/` + `gold.json`: dez arquivos rotulados, cinco stacks (HTML, React/Next, Vue, Astro e Svelte), divididos em desenvolvimento e holdout público. Mede a presença de tipos de defeito por arquivo.
2. `cases/` + `ground-truth.json`: cinco **cenários de produto** (portfólio HTML, Next/React, Vue/Astro, e-commerce e dashboard), cada um com casos defeituosos e seguros. Mede pares `(caminho relativo, detector)`.

Os conjuntos não são estatisticamente independentes nem representam distribuição real de produção. O gabarito está versionado junto ao código; **ainda falta revisão humana externa, dois deployments HTTPS reais e casos de fluxos de negócio**. Os números de precisão/recall aqui reportados são somente sobre os defeitos objetivos rotulados nas fixtures, e **não medem** cobertura dos 228 padrões estéticos.

## Como reproduzir

Requisitos: Python 3.9+, Node.js e TypeScript resolvível pelo script `audit_jsx_ast.cjs`.

```bash
npm install --no-save --no-package-lock typescript@5.9.3
python scripts/run_benchmark.py --min-precision 0.90 --min-recall 0.85 --out reports/benchmark-stacks.json
python scripts/run_scenario_benchmark.py --out reports/benchmark-scenarios.json
python -m unittest discover -s tests -v
```

A avaliação de `gold.json` possui duas divisões: `development` e `holdout`; ambas são explícitas e podem ser inspecionadas. Não trate `holdout` como cego, privado ou coletado independentemente.

- **TP:** detector indicou defeito esperado no gabarito.
- **FP:** detector apontou defeito não rotulado (ainda pode ser defeito legítimo; revisar antes de alterar o gabarito).
- **FN:** o gabarito esperava algo que o detector não encontrou.
- **Precisão:** TP/(TP+FP). **Recall:** TP/(TP+FN).
- Casos legítimos em `clean.*` verificam que a skill não penaliza automaticamente fontes, paletas ou bibliotecas aprovadas.

## Para concluir o benchmark independente (pendente)

1. Selecionar cinco projetos **independentes** (HTML, Next/React, Vue/Astro, e-commerce HTTPS, dashboard HTTPS) com permissão de auditoria e commits imutáveis.
2. Criar inventário de defeitos por especialistas antes de executar o scanner; incluir casos negativos e justificar estética intencional.
3. Comparar resultados com análise cega por ao menos dois revisores. Reportar discordâncias, precisão, recall e intervalo por stack.
4. Registrar para os dois sites HTTPS: URL testada, SHA do commit, data, recursos críticos, screenshots, fluxos de autenticação e acesso permitido.
5. Executar a skill sem acesso ao gabarito, preservar referências, executar correção + regressão e publicar **evidências reais**. Não preencher como aprovado quando estiver indisponível.

O modelo para os sites externos fica em `external-targets.example.json` e não contém URLs inventadas.
