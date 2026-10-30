---
name: anti-ai-slop
description: Audita, corrige e homologa websites e aplicações frontend para eliminar padrões genéricos de design produzidos sem intenção, defeitos de UX, conteúdo e código, usando catálogo rastreável de 228 verificações (Sailop, Impeccable, Unslop UI e extensões) e 14 paletas heurísticas. Preserva identidade visual aprovada, fontes, assets e funções existentes. Usar quando alguém pedir /anti-ai-slop, remover AI slop, corrigir landing page genérica, melhorar fidelidade do mockup, ou homologar um frontend com meta 9,5/10.
---

# Skill: Anti-AI-Slop · Audit → Fix → Verify

## Missão

Transformar **um projeto web existente** em uma interface distintiva, funcional, acessível e fiel à identidade aprovada. Detectar e eliminar **todos os problemas confirmados no contexto**, não banir indiscriminadamente cores, fontes, cards ou animações. Operar sobre código real, executar testes e apresentar evidência visual e funcional. Usar o catálogo integral em `references/catalogo-completo.md`; consultar `references/rules.json` para localizar os IDs.

**Regra absoluta:** nenhum padrão estético isolado prova autoria por IA. Um item do catálogo pode ser `confirmado`, `falso_positivo`, `intencional`, `nao_aplicavel` ou `pendente`. **Não remover** um item intencional/legítimo para satisfazer numericamente o detector. **Não alegar remoção total nem nota 9,5/10 sem testes**.

## Gatilhos de uso

- `/anti-ai-slop [caminho/URL/briefing]`
- “remova o AI slop”, “faça parecer menos site de IA”, “corrija a identidade visual genérica”
- “audite o frontend”, “homologue 9,5/10”, “garanta fidelidade ao mockup”
- Revisão de websites React, Next.js, Vue, Svelte ou HTML/CSS.

## Hierarquia e proteções inegociáveis

1. **Brand/brief aprovado > heurísticas anti-slop.** Preserve logotipo, paleta (inclusive laranja, roxo ou azul), fontes, fotos, assets, textos de marca e layout já aprovados. Nunca os reconstrua por IA por iniciativa própria. Registre hashes/caminhos antes e depois para assets sensíveis.
2. **Comportamento real > aparência de demonstração.** Nunca substituir componente funcional por placeholder, conteúdo simulado, botão decorativo, depoimento falso ou métrica inventada. Não enfraquecer auth, dados, integrações, permissões, segurança ou acessibilidade.
3. **Sem substituição de clichês.** Nunca trocar automaticamente roxo por laranja/bege, Inter por Instrument Serif, glow por brutalismo, todos os cards por bento, ou animação fade-up por parallax. A alternativa deve ser justificada pelo produto.
4. **Nenhum emoji como ícone de interface.** Usar SVG consistente, ícones vetoriais existentes ou texto, sem inventar logotipos.
5. **Escopo restrito.** Não apagar assets usados, dados, rotas ou código de domínio fora do escopo. Não publicar/deployar sem autorização de escrita apropriada.
6. **Não ocultar achados.** Quando não houver acesso ao código, navegador, HTTPS, testes, dados ou capturas, registrar `nao_verificado` e a razão. Não simular sucesso.
7. **Acessibilidade e função são bloqueantes.** Defeitos P0/P1 não podem ser ignorados por uma nota visual alta.

## Fluxo obrigatório

### Fase 0 — Levantar contexto e travar baseline

- Identificar repositório/caminho, framework, comandos de install/test/build, rotas importantes, referências (mockup, screenshots) e ambiente disponível. Se já houver informações, reutilizá-las; não pedir novamente.
- Inspecionar `git status`, branch, arquivos alterados, tokens, `package.json`, componentes compartilhados, assets, links e dependências.
- Registrar quais cores/fontes/layout/assets são aprovados e quais são desconhecidos; priorizar identidade comprovada no código ou briefing. **Sem briefing, preservar o existente e corrigir apenas defeitos evidentes.**
- Capturar baseline **real** quando houver navegador: desktop 1440×900, tablet 1024×768/768×1024, mobile 390×844, incluindo estados do produto. Guardar screenshot original/referência sem recriar elementos.
- Formar `baseline.md` com rotas, interações-chave, hashes de assets e riscos de regressão. Se não houver browser, marcar capturas pendentes.

### Fase 1 — Inventário integral e triagem

- Ler `references/catalogo-completo.md` por categoria e consultar `references/rules.json` para avaliar **todos os IDs aplicáveis**: `SA-001..087`, `IM-001..037`, `UH-001..013`, `UC-001..035`, `NX-001..056`, e paletas `P01..P14`.
- `UH-013` é **exceção contra falsos positivos**: bento, glassmorphism e aurora/mesh não são falhas automáticas.
- Rodar `python3 scripts/audit_slop.py <projeto> --format json --out reports/static.json` para **candidatos estáticos**, nunca como veredito. Quando Node.js e TypeScript estiverem disponíveis, repetir com `--ast` para análise estruturada de JSX/TSX, reduzindo falsos positivos de código comentado ou strings; o fallback léxico permanece parcial. Gerar `python3 scripts/coverage_report.py --out reports/coverage.json` para explicitar a cobertura por ID; a revisão manual contextual dos 228 IDs é mandatória. Ler `references/coverage-matrix.md`.
- Criar plano não destrutivo: `python3 scripts/remediation_plan.py reports/static.json --out reports/fix-plan.md` com teste de aceitação para cada achado confirmado. O scanner é deliberadamente parcial; os demais IDs exigem análise de código, DOM, screenshot, conteúdo e fluxo.
- Para cada achado, registrar regra(s), arquivo/linha ou URL/seletor, evidência, dano concreto, confiança, severidade e estado. Consolidar aliases: várias fontes podem descrever o mesmo defeito.
- Tratar paletas azul/roxo, laranja/coral/âmbar, terracota, bege, neon e dark como **sinais compostos**, nunca proibição por HEX. Um contraste WCAG insuficiente é problema objetivo; usar limiar 4,5:1 para texto normal e 3:1 para texto grande, salvo exceções normativas.
- Proibir alegações sem evidência: `muitos cards`, `fonte genérica`, `parece IA` não justificam alteração isoladamente.

### Fase 2 — Priorizar por impacto (ordem obrigatória)

1. **P0 — Fluxo quebrado:** CTA sem ação, UI que não abre, navegação, auth, APIs, dados, console, componentes invisíveis, erro de build, ações enganosas.
2. **P1 — Acessibilidade e responsividade:** foco/teclado, semântica, contraste, zoom, mobile/tablet, overflow, redução de movimento, estados de erro.
3. **P2 — Design sem identidade:** conjunto comprovado de presets sem relação com marca (hero + três cards + badges + gradiente + icon chips + spacing uniformizado etc.).
4. **P3 — Refinamento:** clichês localizados e escolhas estéticas discutíveis, preservando decisões intencionais.

Corrigir P0 e P1 antes dos ajustes cosméticos. Alocar a cada achado um `fix_id` e teste de aceitação. Selecionar soluções para a intenção real do site: e-commerce, portfolio, SaaS, mídia, serviço, dashboard etc.

### Fase 3 — Implementar com preservação

- Criar/normalizar tokens de design apenas quando necessário, sem mudar cores ou fontes aprovadas. Alterar o mínimo de arquivos para corrigir cada problema.
- Reformular narrativa, hierarquia, composição e densidade dos blocos repetitivos **sem inventar elementos**. Preferir exemplos, imagens e dados verdadeiros do produto.
- Remover efeitos decorativos quando atrapalharem legibilidade, LCP/CLS, orientação ou acesso. Manter animação intencional (Three.js, GSAP, CSS) quando tecnicamente correta; não desativar a experiência aprovada.
- Preservar ícones originais, marcas de terceiros e proporções; jamais recortar logotipos ou gerar em substituição assets existentes sem pedido explícito.
- Em React/Next/Vue, preferir correções sustentáveis em componentes/tokens reutilizáveis a exceções locais, `!important` em cascata e setTimeout simulando loading.
- Após cada grupo de alterações, conferir diff, integridade do conteúdo, hashes de assets e ausência de regressões. Não sobrescrever edições não relacionadas do usuário.

### Fase 4 — Validar em ambiente real

**Execução técnica:** `install` quando necessário; lint, typecheck, testes unitários/integrados, build de produção. Corrigir falhas causadas pelas mudanças. Não alegar execução de comando não rodado.

**Browser e interação:** `python3 scripts/browser_audit.py http://localhost:3000 --out reports/browser` com Playwright instalado para screenshots e inspeção de DOM nos três viewports. O comando de fixture offline `--html tests/fixtures/site/index.html` comprova somente HTML local, não navegação de produção. Os resultados são candidatos e não constituem teste de autenticação ou pagamento. Carregar cada rota sob HTTP/HTTPS apropriado, testar links/CTAs, menus, formulários, modais, autenticação quando houver conta de teste, carrosséis e scroll. Inspecionar erros JS, console/network, overlays, dimensões, overflow horizontal, fontes, fallbacks e estados vazio/erro/loading.

**Motion:** para GSAP/Three.js/parallax comprovar alteração de frames ou propriedades ao longo do tempo, checar interação touch e `prefers-reduced-motion`. Um screenshot único **não prova** que a animação funciona. Se recurso precisar HTTPS ou origem segura, testar sob contexto adequado antes de culpar código.

**Capturas obrigatórias:**
- Desktop: referência original e resultado lado a lado, com legendas.
- Mobile **e tablet**: apresentar juntos em prancha lado a lado, legível no celular.
- Mostrar capturas diretamente na conversa quando a ferramenta permitir, **além** dos arquivos; não responder apenas com caminhos.
- Testar no mínimo 390×844, 768×1024 e 1440×900; acrescentar pontos intermediários e estados de hover/foco/orientação relevantes.
- Capturar também modais, menus, página rolada e estados que mudaram.

Se não houver execução disponível, rotular evidência como `não validada` e não aprovar o gate.

### Fase 5 — Score e gate ≥ 9,5/10

Avaliar com critérios observáveis e pesos abaixo. Conferir rubrica em `references/criterios-e-correcao.md`.

| Pilar | Peso |
|---|---:|
| Identidade e originalidade | 25% |
| Layout e tipografia | 20% |
| UX e funções reais | 20% |
| Responsividade e acessibilidade | 15% |
| Animações e interações | 10% |
| Conteúdo e provas reais | 10% |

Fórmula: `nota = soma(peso × nota_da_dimensao) / 100`, com cada nota de 0 a 10. **Não declarar aprovação** se: houver P0/P1 aberto, testes críticos não executados, assets alterados sem autorização, capturas obrigatórias ausentes ou fluxo crítico quebrado. `≥9,5` somente com comprovantes e todos os gates satisfeitos. Uma nota subjetiva não compensa defeito real.

**Gate executável:** preencha uma cópia de `templates/GATE_INPUT.example.json` com notas, evidências de build, teste e browser, triagem dos achados e revisão visual, depois rode `python3 scripts/evaluate_gate.py reports/gate-input.json --out reports/gate-result.json`. O gate retorna código de erro se faltarem evidências, houver problemas P0/P1 ou a nota for menor que 9,5; ele valida o preenchimento, não autentica a veracidade dos anexos, que precisam ser revisados.

**Laço de melhoria:** se a nota ficar abaixo de 9,5/10, priorizar os achados remanescentes de maior impacto, repetir Fases 2–5, recalcular o score a partir de novas evidências e interromper apenas quando homologado ou quando existir um bloqueio externo documentado. Não forçar nota aumentando pontuações sem correções reais.

### Fase 6 — Relatar e entregar

Preencher `templates/RELATORIO_AUDITORIA.md`: baseline, planilha de achados com IDs do catálogo, mudanças com paths e commits quando houver, testes executados com saída, imagens antes/depois, status de todos os achados, exceções e nota ponderada. Registrar `corrigido`, `intencional`, `nao_aplicavel`, `pendente` ou `nao_verificado` sem fingir resolução.

**Formato conciso da resposta:** diagnóstico quantificado → correções implementadas → verificação feita → evidências visuais → pendências → nota/gate. Informar sem ambiguidade se o código foi modificado, se foi testado em navegador e se foi feito deploy; não anunciar deploy ou push inexistente.

## Critério de conclusão para “remova todo o AI Slop”

Interpretar como: **avaliar cada entrada aplicável do catálogo e corrigir 100% dos achados confirmados, respeitando a identidade, as exceções válidas e a segurança.** Não significa eliminar todos os gradientes, ícones, card layouts, cores específicas ou bibliotecas. Concluir somente após varredura, correção, rerun do scanner, build, validação visual e registro do status de cada achado. Quando etapas não forem possíveis, entregar o que foi feito e listar o restante como pendente.

## Utilitários incluídos

```bash
python3 scripts/validate_catalog.py
python3 scripts/audit_slop.py ./seu-projeto --format md --out reports/static.md
python3 scripts/audit_slop.py ./seu-projeto --format json --out reports/static.json
python3 -m unittest discover -s tests -v
```

A inspeção estática sinaliza apenas algumas heurísticas implementáveis por regex; **não cobre as 228 regras automaticamente**. Conferir `references/rules.json` e executar revisão manual e browser para a cobertura integral. Nunca inferir aprovação a partir da ausência de alertas.

## Segurança da automação

- O scanner v2 ignora symlinks e diretórios de dependências, limita tamanho, preserva código e não executa o conteúdo escaneado. `static_rule_count` informa somente o subconjunto com suporte; os demais permanecem pendentes.
- Não modificar arquivos sem primeiro confirmar o defeito e preservar backups/diffs. O scanner e os relatórios nunca alteram o projeto; a correção é feita por agente autorizado com testes reproduzíveis.
- Uma varredura estática sem achados nunca equivale a auditoria completa. Se navegador não estiver disponível, a evidência é `não executada` e o gate bloqueia.
