<p align="center">
  <img src="assets/cover.png" alt="Capa Anti-AI-Slop: interfaces genéricas passam por um filtro e se tornam interfaces refinadas" width="100%" />
</p>

# Anti-AI-Slop

**Audit → Propose → Preview → Fix → Verify.** Skill reutilizável para detectar e corrigir padrões genéricos de websites gerados com IA, sem sacrificar a identidade da marca, as funcionalidades existentes nem a acessibilidade.

> A skill não considera uma cor, fonte, biblioteca ou efeito visual um erro isoladamente. Detecta problemas **contextuais e demonstráveis**, orienta correções e exige evidências de homologação. A meta de 9,5/10 é um critério de qualidade condicionado a testes reais, não uma promessa automática.

## O que está incluído

- **228 verificações catalogadas:** 87 Sailop, 37 Impeccable, 13 tópicos Unslop UI, 35 sinais complementares e 56 verificações adicionais. São identificadores do catálogo; parte dos conceitos se sobrepõe entre fontes.
- **14 paletas de referência:** roxo, índigo, laranja, pêssego, coral, âmbar, terracota, bege e outras composições. São heurísticas, **não cores proibidas**.
- **Scanner estático v2:** cobertura identificada por regra; reconhece Astro, Next Image, JSX, Vue, Svelte, HTML e CSS, filtra comentários e ignora symlinks. **Não automatiza todas as 228 verificações.**
- **Correção estrutural controlada:** opera por ID literal de elemento em HTML, Vue, Astro, Svelte e JSX/TSX, com `set_attribute`, `remove_attribute` ou `replace_element` e rollback por testes. Não cria layouts automaticamente.
- **axe-core, Lighthouse e diff visual:** acessibilidade real no Chromium, indicadores de performance em uma URL HTTP(S) de teste e comparações de screenshots contra baseline aprovado (ferramentas opcionais).
- **Aplicador de patches auditáveis:** edição exata com SHA-256 do baseline, preview diff, testes de aceitação e rollback ao falhar; o agente propõe as mudanças e o operador aprova `--apply`.
- **Gate rigoroso de evidências:** bloqueia pontuações ≥9,5 quando faltam artefatos verificáveis, revisão dos 228 IDs ou comprovantes de execução.
- **Playbook para agentes:** levantamento do baseline, triagem por severidade, correção contextual, validação em navegador e relatório com evidências.
- **Preservação obrigatória:** mantém logotipos, fotos, tokens, fontes e layouts aprovados; não inventa imagens, depoimentos ou integrações.
- **Instalação por projeto ou usuário:** Codex, Claude Code, Cursor e diretório genérico `.agents/skills/`.

## Benchmark adicional de detecção e correção (v1.8)

Três tipos objetivos de problemas foram incluídos nos detectores estáticos:
`POSITIVE_TABINDEX`, `UNLABELED_SELECT` e `UNLABELED_TEXTAREA`.
Há dez arquivos de benchmark rotulados em cinco frameworks, sendo cinco
negativos; um benchmark separado testa correção estrutural com verificação
pré/pós, preservação da marca, rollback e navegação real em Chromium (HTML).

```bash
python scripts/run_accessibility_benchmark.py --out reports/benchmark-accessibility.json
python scripts/run_structural_benchmark.py --out reports/benchmark-structural.json
# Opcional: requer Playwright e Chromium instalados
python scripts/run_structural_benchmark.py --browser --out reports/structural-browser.json
```

**Os resultados são específicos de casos sintéticos**, não comprovam desempenho
em sites externos nem cobertura completa dos 228 IDs. A execução JSX completa
requer TypeScript AST; o modo sem AST possui métricas separadas.

## Requisitos

- **Python 3.9+** para o instalador e scanner. O instalador usa exclusivamente a biblioteca padrão.
- Um agente compatível com **Agent Skills** para seguir `SKILL.md`.
- Um navegador/ambiente de execução, ferramentas de build e dependências do seu projeto para auditoria funcional e visual completa.

## Instalação rápida

Baixe o ZIP da release, extraia-o e abra um terminal **dentro da pasta `anti-ai-slop/`**, onde estão `SKILL.md` e `scripts/`.

### Windows — PowerShell

**Neste projeto (Codex):**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Agent codex -Scope project -ProjectPath "C:\caminho\do\meu-site"
```

**Para todos os projetos do usuário (Codex):**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Agent codex -Scope global
```

**Nos três agentes (Codex, Claude Code e Cursor):**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Agent all -Scope project -ProjectPath "C:\caminho\do\meu-site"
```

> No PowerShell 7, substitua `powershell` por `pwsh`. A opção `-ExecutionPolicy Bypass` é aplicada apenas a esse processo e não altera a política persistente do computador. Como alternativa, execute `py -3 .\scripts\install.py --agent codex --scope project --project "C:\caminho\do\meu-site"`.

### macOS / Linux — Bash

**Neste projeto (Codex):**

```bash
bash scripts/install.sh --agent codex --scope project --project /caminho/do/meu-site
```

**Para todos os projetos do usuário (Codex):**

```bash
bash scripts/install.sh --agent codex --scope global
```

**Para os três agentes, no projeto atual:**

```bash
bash scripts/install.sh --agent all --scope project --project .
```

### Instalador universal (Python)

Também funciona no Windows, Linux e macOS, sem executar o wrapper:

```bash
python3 scripts/install.py --agent codex --scope project --project .
python3 scripts/install.py --agent claude --scope global
python3 scripts/install.py --agent cursor --scope global
```

No Windows, se `python3` não estiver disponível, use `py -3`.

### Localização dos arquivos

| Agente | Projeto | Global (usuário local) |
|---|---|---|
| Codex | `<projeto>/.agents/skills/anti-ai-slop/` | `~/.agents/skills/anti-ai-slop/` |
| Claude Code | `<projeto>/.claude/skills/anti-ai-slop/` | `~/.claude/skills/anti-ai-slop/` |
| Cursor | `<projeto>/.cursor/skills/anti-ai-slop/` | `~/.cursor/skills/anti-ai-slop/` |
| Diretório genérico | `<projeto>/.agents/skills/anti-ai-slop/` | `~/.agents/skills/anti-ai-slop/` |

**Global** significa disponível ao usuário no computador local, não instalação administrativa para todos os usuários. Um único diretório `~/.agents/skills` pode ser reconhecido por Codex e Cursor; não é obrigatório duplicar a skill nesses dois agentes. Instalações globais locais não são automaticamente sincronizadas com todos os ambientes em nuvem.

### Opções de instalação e segurança

```bash
# Visualizar os destinos, sem fazer alterações
python3 scripts/install.py --agent all --scope project --project . --dry-run

# Confirmar que os arquivos obrigatórios estão instalados
python3 scripts/install.py --agent codex --scope project --project . --verify

# Atualizar uma skill existente (faz backup da versão anterior)
python3 scripts/install.py --agent codex --scope project --project . --force

# Instalar no caminho genérico, sem especificar um agente
python3 scripts/install.py --agent agents --scope global
```

O instalador **não sobrescreve instalações existentes** sem `--force`. Em uma atualização, a versão anterior é renomeada para `anti-ai-slop.backup-AAAAMMDDTHHMMSSZ` antes da nova instalação. A cópia é preparada e conferida antes da substituição. O instalador **não executa código remoto** nem realiza deploy ou push.

## Como usar com a IA

**Codex CLI ou IDE:** selecione a skill em `/skills` ou use:

```text
$anti-ai-slop Audite este frontend, corrija os problemas confirmados e homologue desktop, tablet e mobile. Preserve integralmente a identidade aprovada.
```

**Claude Code e Cursor:** digite `/anti-ai-slop` no chat do agente, caso a skill apareça entre as opções. Alternativamente, peça explicitamente para usar a skill `anti-ai-slop`.

**Prompt recomendado:**

```text
Use a skill anti-ai-slop neste repositório.
1. Registre o baseline real e o estado atual do Git.
2. Avalie as regras aplicáveis e diferencie defeitos de escolhas intencionais.
3. Corrija achados confirmados, priorizando fluxos quebrados e acessibilidade.
4. Preserve cores, tipografia, logotipos, fotos, componentes e animações aprovados.
5. Rode lint, testes, build e navegação real; compare desktop, tablet e mobile.
6. Apresente screenshots e evidências, pendências e nota ponderada.
7. Não declare 9,5/10 sem evidências e sem eliminar falhas críticas.
```

## Ferramentas de auditoria e homologação

O kit inclui a matriz de cobertura por regra, plano revisável de correções e um **gate que reprova evidências incompletas**, além do scanner de código. As ferramentas não fazem alterações automáticas na aplicação.

```bash
# Inventário de todas as regras e canais de detecção
python3 scripts/coverage_report.py --out reports/coverage.json
# Pré-varredura segura
python3 scripts/audit_slop.py /caminho/do/site --format json --out reports/static.json
# Plano que exige confirmação e testes de aceitação
python3 scripts/remediation_plan.py reports/static.json --out reports/fix-plan.md
# Validar nota apenas após preencher o template com evidências verdadeiras
python3 scripts/evaluate_gate.py reports/gate-input.json --out reports/gate-result.json
```

Auditoria no navegador (dependência **opcional**, fora do instalador):

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
python3 scripts/browser_audit.py http://localhost:3000 --out reports/browser --interaction-spec tests/fixtures/interaction-spec.json
# Fixture offline apenas para teste do próprio auditor, não prova de app em produção
python3 scripts/browser_audit.py --html tests/fixtures/site/index.html --out reports/fixture
```

O auditor registra capturas desktop/tablet/mobile, erros JavaScript, overflow, imagens quebradas, controles sem rótulo e links placeholders. O parâmetro `--interaction-spec` executa **somente** ações descritas explicitamente pelo usuário e reprova o comando quando as verificações falham; adapte o JSON ao fluxo do projeto (o exemplo é para a fixture). Não opera ações destrutivas nem submete formulários. Quando o navegador não conseguir abrir a URL, a auditoria fica incompleta. Para homologar processos específicos (login, pagamento, APIs), acrescente testes do sistema-alvo.

## Correção estrutural e homologação visual (v1.5)

A correção estrutural precisa de um elemento com `id` literal único, SHA-256 do arquivo original e um `finding_id`. O agente fornece a proposta explícita em JSON; a skill **não inventa alterações automaticamente**.

```json
{
  "edits": [{
    "path": "src/index.html",
    "id": "contact-cta",
    "finding_id": "NX-021",
    "expected_sha256": "<SHA-256 atual do arquivo>",
    "operation": "set_attribute",
    "attribute": "href",
    "value": "/contato"
  }]
}
```

```bash
# Pré-visualização sem escrita
python scripts/structural_fix.py /caminho/do/projeto proposta.json
# Aplicação SOMENTE após revisão, com testes reais para habilitar applied_verified
python scripts/structural_fix.py /caminho/do/projeto proposta.json --apply --check "python -m unittest discover -s tests"
```

`remove_attribute` requer atributo estático existente. `replace_element` exige markup completo e preservação do ID. JSX/TSX depende de TypeScript; atributos dinâmicos não são reescritos com segurança. Editar a composição inteira exige revisão do agente e testes de regressão adicionais.

### Testes de acessibilidade reais com axe-core

```bash
npm install --no-audit --no-fund --no-package-lock
python -m pip install playwright Pillow
python -m playwright install chromium
python scripts/browser_audit.py https://seu-preview.example --axe --fail-on-axe --out reports/axe-browser
```

O relatório inclui violações do axe por viewport, seus seletores e impacto. Violações críticas ou graves bloqueiam o gate com `--fail-on-axe`. A análise não comprova sozinha conformidade integral com WCAG.

### Lighthouse

```bash
python scripts/lighthouse_audit.py https://seu-preview.example --out reports/lighthouse
```

O Lighthouse utiliza a instalação **local** em `node_modules/.bin/lighthouse` e Chrome/Chromium. Exige HTTP(S); para HTML local, publique em servidor de teste antes. Os limiares padrão são: performance 80, acessibilidade 90, boas práticas 90 e SEO 80. As notas são medidas pela ferramenta, não pela skill.

### Comparação visual por screenshots

```bash
# Primeiro execute browser_audit.py duas vezes, em baseline e versão atual
python scripts/visual_compare.py --before reports/baseline --after reports/atual --out reports/diff --max-changed-ratio 0.01
```

São comparadas as imagens `desktop.png`, `tablet.png` e `mobile.png` e produzidos mapas de diferença. O limite de alteração é **um alerta de regressão**, não uma avaliação estética; mudanças aprovadas podem alterar muitos pixels legitimamente. Baselines ausentes, dimensões incompatíveis ou mudanças acima do limite não passam automaticamente.

**Dependências:** Python 3.9+, Node 22+ para Lighthouse 13.5.0, pacote npm `axe-core`, pacote `lighthouse`, Playwright Python e Pillow. O instalador da skill não instala essas dependências automaticamente e não executa downloads ao auditar um projeto.

## Auditoria estática — execução manual

Se estiver na pasta da skill baixada:

```bash
python3 scripts/validate_catalog.py
python3 scripts/audit_slop.py /caminho/do/site --format md --out reports/static.md
python3 scripts/audit_slop.py /caminho/do/site --format json --out reports/static.json
python3 -m unittest discover -s tests -v
```

Se instalou em um projeto Codex, execute **a partir da raiz desse projeto**:

```bash
python3 .agents/skills/anti-ai-slop/scripts/audit_slop.py . --format md --out reports/static.md
```

A ausência de alertas no scanner não comprova ausência de AI Slop. A auditoria integral também exige revisão da estrutura, UX, acessibilidade, conteúdo, design aprovado, DOM e fluxos funcionais.

## Processo e critérios de aprovação

| Fase | Entrega esperada |
|---|---|
| 0 — Baseline | Repositório, referências, assets, rotas e capturas originais |
| 1 — Detectar | Achados com IDs, evidências, gravidade e falsos positivos |
| 2 — Priorizar | P0 funcional, P1 acessibilidade, P2 identidade, P3 refinamentos |
| 3 — Corrigir | Mudanças mínimas e justificadas, sem alterar identidade aprovada |
| 4 — Homologar | Build, testes, navegação, motion, responsividade e capturas |
| 5 — Pontuar | Nota ponderada e gates bloqueantes para regressões críticas |
| 6 — Entregar | Relatório completo com correções, limitações e evidências |

As verificações visuais consideram no mínimo **390×844 (mobile)**, **768×1024 (tablet)** e **1440×900 (desktop)**. O objetivo é atingir **9,5/10**, mas falhas P0/P1, testes não executados ou evidências ausentes bloqueiam a homologação independentemente da nota visual.

## Estrutura do projeto

```text
anti-ai-slop/
├── SKILL.md                       # instruções do agente
├── README.md                      # instalação e documentação
├── ABOUT.md                       # GitHub About e topics
├── agents/
│   └── openai.yaml                # metadados opcionais de apresentação
├── assets/
│   ├── cover.png                  # capa do projeto
│   ├── icon.png                   # ícone em alta resolução
│   └── icon-small.png             # ícone reduzido
├── references/
│   ├── coverage-matrix.md
│   ├── catalogo-completo.md
│   ├── rules.json
│   └── criterios-e-correcao.md
├── scripts/
│   ├── install.py                 # instalação multiagente
│   ├── install.sh                 # atalho Bash
│   ├── install.ps1                # atalho PowerShell
│   ├── audit_slop.py              # scanner estático parcial v2
│   ├── browser_audit.py           # auditor Playwright opcional
│   ├── coverage_report.py         # inventário dos 228 IDs
│   ├── remediation_plan.py        # plano revisável de alterações
│   ├── evaluate_gate.py           # bloqueio de aprovação sem evidências
│   ├── validate_catalog.py
│   └── generate_rules.py
├── templates/
│   ├── RELATORIO_AUDITORIA.md
│   └── GATE_INPUT.example.json
└── tests/
    ├── test_skill.py
    └── test_installer.py
```

## Integridade, privacidade e limitações

A skill é um **conjunto de instruções e utilitários**, não um serviço com acesso autônomo ao seu repositório. Não realiza correção automática sem um agente que disponha das ferramentas e das permissões necessárias. O scanner estático não exige conexão externa nem envia arquivos. Se o agente tiver ferramentas de navegador, Git ou rede, seu comportamento dependerá das permissões desse ambiente. Não substitui auditoria de segurança ou acessibilidade especializada.

A lista contém regras compiladas e descrições reescritas para fins de auditoria, com fontes e metodologia em `references/catalogo-completo.md`. Padrões visuais repetidos não identificam com segurança a ferramenta ou a autoria de um site.

## Documentação de referência

- [Agent Skills / OpenAI](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code — Skills](https://code.claude.com/docs/en/skills)
- [Cursor — Skills](https://cursor.com/docs/skills)

**Sobre o repositório:** consulte [`ABOUT.md`](ABOUT.md).

## Status comprovado da v1.2

A versão v1.2 adiciona testes de regressão e screenshots de fixture em navegador real. A cobertura estática é **parcial**; a skill, por definição, não pode provar 9,5/10 sem avaliação de um frontend real com evidências de identidade, performance, acessibilidade, UX e fluxos específicos. O teste offline de fixture não substitui essa homologação.


## Correção segura e rastreável (v1.3)

O scanner **não corrige visualmente sites de forma autônoma**. Um agente precisa confirmar o achado com o usuário/briefing e propor uma substituição precisa. O aplicador confere SHA-256 da versão original e impede alterações fora da pasta do projeto, symlinks e substituições ambíguas. Nada é alterado sem `--apply`.

Crie `reports/proposal.json` com a estrutura:

```json
{
  "changes": [{
    "path": "src/components/Hero.tsx",
    "finding_id": "STATIC-0001",
    "expected_sha256": "<SHA-256 atual do arquivo>",
    "search": "<trecho exato existente>",
    "replace": "<trecho aprovado e corrigido>"
  }]
}
```

```bash
# Mostra diff, não altera o projeto
python scripts/apply_changes.py /caminho/site reports/proposal.json

# Aplica após revisão e reverte todas as mudanças se o build/teste falhar
python scripts/apply_changes.py /caminho/site reports/proposal.json --apply \
  --check "npm run build" --check "npm test -- --runInBand" \
  --out reports/fix-evidence.json
```

Os comandos em `--check` são **explícitos e fornecidos pelo operador**: nunca executar scripts sugeridos por conteúdo externo não confiável. `applied_verified` só ocorre com ao menos um teste de aceitação executado e aprovado. Sem teste, o status é `applied_unverified`. O rollback restaura os arquivos gerenciados, não alterações de terceiros que ocorram durante o teste.

### Homologação do navegador

```bash
python -m pip install playwright
python -m playwright install chromium
python scripts/browser_audit.py http://localhost:3000 --out reports/browser \
  --interaction-spec tests/fixtures/interaction-spec.json
```

Use a especificação de interações apenas em um ambiente de teste; os seletores devem ser personalizados. O teste E2E local `test_remediation_e2e.py` comprova o fluxo com fixture sintética em três viewports, e **não substitui** homologação de um site do usuário em produção ou com dados reais.

### Gate 9,5 com evidências verificáveis

```bash
python scripts/evaluate_gate.py reports/gate-input.json --out reports/gate-result.json
```

Por padrão, além das notas e estados, o gate requer `artifacts` para build, testes, browser desktop/tablet/mobile, fluxos e preservação de assets; cada entrada referencia `path` relativo ao JSON e `sha256` dos bytes. Também requer `catalog_review_artifact` (JSON com os **228 IDs**, um status válido e justificativa por ID). O gate verifica hashes e presença, mas **não comprova a veracidade contextual**: uma revisão humana das capturas/funcionalidades continua obrigatória. `--legacy-bools` existe apenas para comparação com versões anteriores e não representa aprovação auditável.

## Escopo de garantia

O pacote realiza instalação, auditoria parcial, planejamento, aplicação de edições autorizadas, testes e coleta de evidências. **Não promete 100% de detecção automática das 228 regras, criatividade humana ou conserto automático de fluxos complexos.** As regras são heurísticas; código, marca e acessibilidade decidem se um sinal é um defeito. O alvo de 9,5 depende da execução em um projeto específico.

## Benchmark de detecção — cinco stacks

A partir da versão 1.4, o repositório inclui fixtures com gabarito explícito em `benchmarks/gold.json`: HTML, React/Next TSX, Vue, Astro e Svelte. O benchmark conta verdadeiros positivos, falsos positivos e falsos negativos por (arquivo, detector), com subconjuntos de desenvolvimento e holdout visíveis. **Não é um benchmark independente ou produção.**

```bash
# Com TypeScript instalado, AST estrutural para JSX/TSX:
python scripts/run_benchmark.py --out reports/benchmark.json --min-precision 0.90 --min-recall 0.85

# Modo lexical sem AST (resultado e limitações separados):
python scripts/run_benchmark.py --no-ast --out reports/benchmark-fallback.json

# Testes de regressão e benchmark:
python -m unittest discover -s tests -v
```

Os detectores estruturais de templates têm natureza de **pré-varredura**, não substituem avaliação de conteúdo dinâmico, DOM renderizado ou revisão visual. A expansão de 29 para 32 IDs com candidatos estáticos não equivale a automatizar o catálogo de 228 padrões. O status das verificações está em `references/coverage-matrix.md`.

## Compatibilidade de agentes e evidências auditáveis (v1.6)

```bash
python scripts/agent_compat.py --agent all --out reports/agent-compat.json
```

Testa instalação por projeto e por usuário, descoberta de `SKILL.md`, manifesto e scanner instalado para **Codex, Claude Code e Cursor**. O relatório diferencia explicitamente `compatible_not_executed` de execução autêntica do modelo; este teste **não comprova** que qualquer agente tenha carregado a skill em uma sessão autenticada. Guia de homologação real: [`references/AGENT_RUNTIME_VALIDATION.md`](references/AGENT_RUNTIME_VALIDATION.md).

O gate estrito `scripts/evaluate_gate.py` passou a exigir relatórios JSON semânticos dos testes e browser (incluindo captura PNG vinculada por SHA-256), revisão contextual dos 228 IDs, revisão visual e transcrições de execução **real** dos três agentes. Um arquivo arbitrário, um `true` e um falso relatório de compatibilidade não podem aprovar uma nota 9,5. O modo `--legacy-bools` existe apenas para diagnóstico e sempre retorna reprovação na CLI.

```bash
# O exemplo sem evidências DEVE ser reprovado (exit 1)
python scripts/evaluate_gate.py templates/GATE_INPUT.example.json

# Publicação de logs e atestações no GitHub Actions, sem secretos
python scripts/ci_evidence.py --kind unit_tests --out reports/ci -- python -m unittest tests.test_gate_hardening -v
```

O workflow publica artefatos `agent-compat-*`, `gate-contract-evidence`, além dos resultados do benchmark e das ferramentas de qualidade. **CI verde significa que a compatibilidade e as salvaguardas foram verificadas, não que agentes autenticados tenham executado o processo nem que a nota 9,5 foi atingida.**

## Proveniência de evidências e proteção contra relatórios fabricados (v1.7)

O comando de homologação estrita **não aceita** mais relatórios JSON, logs e capturas PNG apenas porque seus hashes SHA-256 conferem. Esses arquivos podem ser fabricados localmente. Agora requer `signed_evidence_manifest`, um manifesto que enumera exatamente os 12 tipos de comprovação (incluindo logs de execução dos três agentes), e uma **atestado GitHub/Sigstore** verificado pela CLI `gh` com repositório, commit, `refs/heads/main`, workflow assinante e SHA-256 do manifesto. O verificador é `scripts/attested_evidence.py` e **falha fechado** quando a CLI, credenciais, assinatura ou proveniência não estão disponíveis.

```bash
python scripts/evaluate_gate.py reports/gate-input.json --out reports/gate-result.json
```

O workflow normal do GitHub Actions agora publica **um manifesto com atestado de CI sintético**, que comprova apenas os testes executados no pipeline. O campo `real_agent_runtime=false` é obrigatório, e o manifesto desse job **não é aceito como homologação de 9,5/10**. O gate requer um workflow **separado de validação independente**, identificado em `scripts/attested_evidence.py` como `.github/workflows/independent-validation.yml`; esse workflow deve rodar os três agentes autenticados, auditar aplicações externas e passar por revisão independente antes de assinar qualquer artefato. Até isso acontecer, o gate recusa qualquer alegação final.

Para reproduzir os testes adversariais locais:

```bash
python -m unittest tests.test_provenance tests.test_gate_hardening -v
```

**Limitação consciente:** atestados verificam a identidade do workflow e a integridade dos bytes, não o mérito artístico, a honestidade dos avaliadores nem a existência de correção real nos sites. Revisão independente e testes de negócio continuam necessários. Nenhum relatório local autoassinado pode substituir essa revisão.
