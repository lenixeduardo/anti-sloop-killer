# False Positive Guard — política de evidência

## Objetivo
Evitar que heurísticas (roxo, Inter, bento, glow ou cards) sejam tratadas como defeitos objetivos. O scanner é pré-varredura read-only, não uma prova de autoria IA, nem autoridade para alterar código.

## Contrato
- Cada finding permanece no JSON, inclusive os classificados como intencional/falso positivo.
- O valor inicial é `candidate_not_verified`; `autofix_permitted` é sempre `false`.
- Um registro estático referencia ID(s) do catálogo `references/rules.json` apenas se a associação detector→regra for semanticamente correta; caso contrário, `source_rules: []` é preferível a atribuição inventada.
- As regras UH-013 de *exclusão* jamais são alertas. Falhas do registro de mapeamentos interrompem a análise (*fail closed*).
- Duplicatas de mesmo detector, arquivo e linha são consolidadas; sinais distintos não são fundidos indiscriminadamente.
- `intentional` só é aplicável a candidato P2/P3. P0/P1 exige teste funcional/acessibilidade; só aceita `false_positive` com `runtime_verified: true` e revisão documentada. O booleano é declaração do revisor, **não comprovação automática**.
- Cada exceção precisa de `id`, `decision`, `path` relativo específico, `reviewed_by`, `rationale`, `evidence` e ao menos um `finding_keys` ou `rule_ids`. Pode ter `expires_on` ISO. Não usar glob de projeto inteiro, nem ocultar erros de build.
- O guard não aplica nenhuma correção e não transforma candidatos restantes em defeitos confirmados.

## Configuração
O scanner procura automaticamente `<projeto>/.anti-ai-slop/false-positive-guard.json`. Exemplo em `examples/false-positive-guard.policy.example.json` (**substitua** valores fictícios e só registre decisões realmente aprovadas).

```bash
python3 scripts/audit_slop.py . --format json --out reports/static.json
python3 scripts/audit_slop.py . --format json --policy ./minhas-excecoes.json
python3 scripts/false_positive_guard.py reports/static.json --policy ./minhas-excecoes.json --out reports/triage.json
python3 -m unittest tests.test_false_positive_guard -v
```

## Critérios de aceitação
1. Candidatos sem evidência continuam pendentes e visíveis.
2. Exceções são limitadas a arquivos e regras aplicáveis.
3. Falsos positivos P0/P1 precisam de comprovação de runtime e revisão.
4. IDs inexistentes, associações semânticas conhecidamente incorretas e UH-013 como violação falham.
5. O benchmark sintético não autoriza alegação de precisão real de 98%, nem nota 9,5; medir TP/FP/FN em aplicações externas com gabarito independente.

## Limitações
Uma aprovação na policy não demonstra por si que a identidade visual está correta. O avaliador deve examinar capturas, DOM real, navegador, flows, brand book e testes, e registrar versão/commit revisados. O motor não automatiza os 228 critérios nem aprova automaticamente um projeto.
