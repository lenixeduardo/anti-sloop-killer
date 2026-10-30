# Anti-AI-Slop — Evidência incremental de detecção e correção (v1.8)

Data: 30/10/2026. Commit: a determinar na publicação.

## Detector: cinco formatos, casos positivos e negativos

- Novos tipos objetivos de detecção: `POSITIVE_TABINDEX`, `UNLABELED_SELECT`, `UNLABELED_TEXTAREA`.
- Formatos: HTML, TSX/React, Vue, Astro e Svelte.
- Conjunto de teste: 10 arquivos, 15 achados positivos rotulados, 5 arquivos sem defeitos desses tipos.
- **AST:** TP=15, FP=0, FN=0; precisão=100%, recall=100% **na amostra sintética**.
- **Fallback sem AST:** TP=12, FP=0, FN=3; precisão=100%, recall=80% na mesma amostra. A diferença é explícita.
- O benchmark anterior permanece com 39/39 achados esperados e 0 FP na amostra anterior.

## Correção estrutural: cinco formatos controlados

- Duas correções estruturais por fonte: atualizar um `href` placeholder e substituir `div` clicável por `button` sem perder seu handler. **10/10 defeitos removidos em 5/5 propostas verificadas.**
- Cada cenário tem estado defeituoso inicial detectável, prévia sem mutação, modificação exata, teste de aceitação, varredura posterior sem o defeito e preservação de texto/marca.
- Testes negativos: rollback após falha da aceitação e rejeição de baseline SHA-256 adulterado, 2/2.
- HTML puro: clique com handler original preservado e navegação para âncora real no Chromium em desktop (1440), tablet (768) e mobile (390), 3/3. As capturas reais são geradas pelo job `quality-audit` do CI como artefatos.
- Os demais quatro formatos recebem verificação estrutural em fonte, **não** build/deploy real do framework.

## Critérios de publicação

- A meta de 9,5/10 **não decorre** deste benchmark. Não são projetos externos, gabaritos não são revisados de forma independente e não há homologação autenticada das três IAs.
- Relatórios não provam automaticamente acessibilidade total, qualidade estética nem capacidade de correção generalizada.
- Para homologação de produção: testar Next/React, Vue/Astro e HTML reais sobre HTTPS, revisar defeitos/soluções independentemente e repetir métricas sem ajustar gabaritos após o resultado.

Arquivos: `quality-accessibility-v18.json`, `quality-structural-v18.json`; testes reproduzíveis em `tests/test_quality_benchmarks_v2.py`.
