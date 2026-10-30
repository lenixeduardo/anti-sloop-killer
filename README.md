<p align="center">
  <img src="assets/cover.png" alt="Capa Anti-AI-Slop: interfaces genéricas passam por um filtro e se tornam interfaces refinadas" width="100%" />
</p>

# Anti-AI-Slop

**Audit → Fix → Verify.** Skill reutilizável para detectar e corrigir padrões genéricos de websites gerados com IA, sem sacrificar a identidade da marca, as funcionalidades existentes nem a acessibilidade.

> A skill não considera uma cor, fonte, biblioteca ou efeito visual um erro isoladamente. Detecta problemas **contextuais e demonstráveis**, orienta correções e exige evidências de homologação. A meta de 9,5/10 é um critério de qualidade condicionado a testes reais, não uma promessa automática.

## O que está incluído

- **228 verificações catalogadas:** 87 Sailop, 37 Impeccable, 13 tópicos Unslop UI, 35 sinais complementares e 56 verificações adicionais. São identificadores do catálogo; parte dos conceitos se sobrepõe entre fontes.
- **14 paletas de referência:** roxo, índigo, laranja, pêssego, coral, âmbar, terracota, bege e outras composições. São heurísticas, **não cores proibidas**.
- **Scanner estático v2:** cobertura identificada por regra; reconhece Astro, Next Image, JSX, Vue, Svelte, HTML e CSS, filtra comentários e ignora symlinks; opcionalmente usa a AST do TypeScript para JSX/TSX. **Não automatiza todas as 228 verificações.**
- **Playbook para agentes:** levantamento do baseline, triagem por severidade, correção contextual, validação em navegador e relatório com evidências.
- **Preservação obrigatória:** mantém logotipos, fotos, tokens, fontes e layouts aprovados; não inventa imagens, depoimentos ou integrações.
- **Instalação por projeto ou usuário:** Codex, Claude Code, Cursor e diretório genérico `.agents/skills/`.

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
# Com Node.js + TypeScript instalado: análise AST precisa para JSX/TSX
python3 scripts/audit_slop.py /caminho/do/site --ast --format json --out reports/static-ast.json
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
│   ├── audit_jsx_ast.cjs           # parser JSX/TSX com TypeScript (opcional)
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
