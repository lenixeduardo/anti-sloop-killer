# Agentes: compatibilidade ≠ execução real

Este documento separa **descoberta/instalação** de **invocação autenticada do modelo**. Apenas a segunda, com transcrição e revisão, conta como validação funcional dos agentes.

## Compatibilidade reproduzível sem contas de terceiros

```bash
python scripts/agent_compat.py --agent all --out reports/agent-compat.json
```

O comando cria **diretórios temporários separados** para Codex (`.agents/skills`), Claude Code (`.claude/skills`) e Cursor (`.cursor/skills`), simula instalação local e global, valida o `SKILL.md`, valida SHA-256 e executa o scanner **do pacote instalado** sobre um caso do benchmark. Não modifica o HOME do usuário. `runtime_executed=false` é uma declaração obrigatória no JSON.

O comando `--require-runtime` retorna erro enquanto não houver execução real comprovada; não existe bypass pelo fato de a CLI estar instalada.

## Homologação real — somente em ambiente autorizado

1. Fazer um clone de teste do frontend, sem segredos e sem acesso a produção. Fazer backup e registrar SHA do commit.
2. Instalar a skill por projeto (`python scripts/install.py --agent <agente> --scope project --project <pasta>`).
3. Com a CLI oficial **já instalada e autenticada pelo responsável**, executar um prompt de avaliação limitado ao clone. Não usar opções de execução irrestrita. Verificar se a CLI efetivamente descobriu e leu `SKILL.md`.
4. Executar novamente os testes estáticos e browser da skill; salvar logs de execução, `git diff`, relatório de achados, prints e casos de aceitação antes/depois.
5. Registrar o comando utilizado, status e versão da CLI, commit testado, revisão humana e evidências locais com SHA-256. **Sanitizar segredos, caminhos pessoais e dados de clientes antes de publicar qualquer transcrição.**
6. Só então gerar atestado `anti-ai-slop/agent-runtime/v1`; a CLI de gate exige um para cada agente.

Exemplos de invocação **não executados aqui** (verificar flags da versão instalada):

```bash
codex exec 'No clone de teste, carregue a skill anti-ai-slop, audite e produza um relatório. Não altere arquivos sem revisão.'
claude -p 'Carregue a skill anti-ai-slop e audite este clone de teste, sem modificar dados.'
agent -p 'Audite este clone de teste com a skill anti-ai-slop e entregue evidências, sem modificar dados.'
```

Cursor CLI também pode aparecer como `cursor-agent` em certas instalações; seguir a documentação e o comando real detectado. A confirmação de leitura da skill deve vir do registro do agente, **não do texto gerado pelo instalador**.

## Limitação importante

CI público não possui login/autorização para esses agentes. Os jobs `agent-compatibility` fazem somente testes de formato e execução dos scripts. Qualquer relatório que atribua sucesso de execução real de Codex, Claude Code ou Cursor com base nesses jobs é inválido. Um arquivo SHA-256 garante apenas integridade, não legitimidade externa do conteúdo.

## Atestação de homologação final (v1.7)

O gate exige um manifesto de evidências assinado por **um workflow diferente do CI de regressão**, com execução comprovada dos três provedores e revisão independente. O workflow gerador deve residir em `.github/workflows/independent-validation.yml` no mesmo commit auditado, usar um runner confiável com CLIs autenticadas, produzir os relatórios e os screenshots durante a execução, e usar `actions/attest@v4` para atestar somente o manifesto gerado dessa execução. Publicar artefatos arbitrários preexistentes como se fossem resultados do runner é proibido.

A verificação obrigatória usa a CLI GitHub:

```bash
gh attestation verify reports/independent-evidence-manifest.json \
  --repo lenixeduardo/anti-sloop-killer \
  --signer-workflow lenixeduardo/anti-sloop-killer/.github/workflows/independent-validation.yml \
  --source-digest "$AUDITED_SHA" --source-ref refs/heads/main --format json
```

O CI regular pode produzir atestados **somente para testes sintéticos e compatibilidade**, explicitamente marcados como não sendo execução real de agentes. Mesmo um atestado válido dessa origem **não** libera 9,5/10. Até o workflow independente e as sessões autenticadas estarem implantados, o estado obrigatório é `not_verified`.
