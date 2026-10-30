# Regressão de proveniência — Anti-AI-Slop v1.7

## Falha observada na versão anterior

O gate foi convencido a emitir `approved: true`, `score: 10.0` para um conjunto inteiramente falso: logs simulados, JSONs sem execução, capturas PNG em branco e identidades inventadas de revisores/CLIs. A validade dos SHA-256 só atestava que os arquivos não tinham mudado depois de criados.

## Correção implementada

O script `scripts/attested_evidence.py` exige que o manifesto contenha os doze hashes exigidos pela avaliação, o commit e o nome do projeto HTTPS auditado. Depois usa `gh attestation verify` sem shell para verificar a atestação Sigstore do manifesto, com repositório, nome do workflow assinante, ref de origem e commit SHA fixados. Também compara o digest do artefato assinado ao manifesto apresentado. Verificação ausente é reprovação, sem exceção por variável de ambiente ou relatório local.

## CI assinado não é execução de agente

`scripts/ci_provenance.py` associa os artefatos do CI ao SHA do commit e ao ID da execução. O workflow `ci.yml` emite e verifica um atestado de origem GitHub OIDC/Sigstore para esse manifesto em commits na branch `main` **somente após todos os testes passarem**. O arquivo declara expressamente `real_agent_runtime: false` e `independent_validation: false`; não consegue satisfazer o gate 9,5.

## Regressões

- `tests/test_gate_forgery_regression.py` reproduz as evidências aparentemente completas e falsas com PNGs de formato válido; o gate deve reprovar exclusivamente devido à falta de atestação independente.
- `tests/test_provenance.py` cobre ausência de CLI, falha do verificador, assinatura de artefato errado, vínculos a SHA de commit incorretos e detecção de registros de compatibilidade que tentam se apresentar como runtime.
- Atestados **não comprovam conteúdo verdadeiro nem qualidade visual**; atestação independente precisa vir de workflow protegido, executando CLIs autenticadas sobre projetos reais, e de revisão humana. Não usar o CI sintético como substituto.

## Pendências incontornáveis para 9,5

1. Disponibilizar um workflow de validação independente com ambiente protegido e runner isolado, capaz de executar as três CLIs autenticadas e coletar provas de alterações em três stacks externas.
2. Avaliar dois projetos HTTPS reais, com baseline, fluxos de negócio, comparações visuais e critérios de aceite independentes.
3. Ativar a assinatura somente depois de o workflow registrar as evidências do próprio runner e revisão humana, nunca sobre uploads JSON arbitrários.
4. Conferir o atestado via GitHub CLI e repetir o gate com esses resultados reais.
