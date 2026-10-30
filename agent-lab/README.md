# Laboratório reproduzível: Codex, Claude Code e Cursor Agent

Este laboratório instala **os programas oficiais**, não aliases, wrappers de simulação nem pacotes substitutos. Usa `ubuntu-latest`, Node 22 e Python 3.11. Não configura autenticação nem solicita credenciais.

## Executar no GitHub Actions

Abra **Actions > Install and verify three official coding CLIs > Run workflow**, ou envie um commit que altere os scripts e o workflow. A execução registra a versão real de cada CLI, confirma a descoberta do `SKILL.md` nas pastas próprias e roda o scanner do pacote instalado. Baixe o artifact `official-cli-install-lab` para os relatórios JSON.

Os runners do GitHub são **efêmeros**: a instalação desaparece ao final de cada job. Para um ambiente persistente, execute as mesmas instruções numa máquina/VM Linux com acesso à rede.

## Executar numa máquina Linux ou WSL

A partir da raiz do repositório:

```bash
bash scripts/setup_agent_clis.sh
bash scripts/probe_agent_clis.sh
cat .agent-cli-lab/reports/cli-versions.json
```

Defina `AGENT_LAB_ROOT=/caminho/isolado` para outro local de instalação. Os executáveis e configurações de HOME são guardados apenas nesse diretório. Para uma sessão interativa posterior, use `HOME="$AGENT_LAB_ROOT/home"` e inclua `"$AGENT_LAB_ROOT/npm-global/bin:$HOME/.local/bin:$HOME/.cursor/bin"` no `PATH`.

## Proveniência e permissões

- Codex: distribuição oficial `@openai/codex` no npm.
- Claude Code: instalador nativo de `https://claude.ai/install.sh`.
- Cursor Agent: instalador de `https://cursor.com/install`.
- As transferências do instalador nativo são feitas sobre HTTPS e o SHA-256 dos scripts baixados é registrado para auditoria; o valor não é apresentado como verificação de assinatura do fabricante.
- O workflow é **read-only**, não recebe secrets e não executa `login` nem prompts com modelo.
- `installed=true` e `--version=0` comprovam presença e execução do binário; **não** comprovam leitura da skill por um modelo, nem validação funcional de um agente.

## Bloqueios

Se a rede bloquear DNS/HTTPS, o job falhará explicitamente; o relatório não marcará a instalação como concluída. Se um serviço exigir autenticação ou conexão externa, será necessário autenticar **na máquina do usuário**, sem compartilhar credenciais no chat ou em artefatos.
