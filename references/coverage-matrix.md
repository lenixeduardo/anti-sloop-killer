# Cobertura por canal de auditoria

Todos os 228 IDs estão no inventário e devem ser classificados em uma auditoria abrangente. **Não confundir 228 regras com 228 verificações automáticas executadas.**

| Canal | Ferramenta | Escopo | Status |
| --- | --- | --- | --- |
| Código estático | `scripts/audit_slop.py` | padrões de Tailwind/CSS, links, handlers, imagens, iframes, elementos clicáveis | automatizado parcial; requer triagem |
| DOM real e compatibilidade | `scripts/browser_audit.py` | viewport, overflow, imagens quebradas, alt, controles sem nome, links placeholders, erros JS | automatizado parcial; requer navegador |
| Qualidade visual | agente + screenshot + baseline aprovado | hierarquia, identidade, legibilidade, fidelidade, layout, texto, paletas | julgamento contextual obrigatório |
| Funcionalidade de negócio | testes específicos do projeto | pagamentos, autenticação, APIs, estados, formulários, permissões | fora da automação genérica |
| Performance/motion | ferramentas da aplicação | Web Vitals, GSAP/Three.js, redução de movimento, responsividade | testes específicos |

Os IDs não cobertos automaticamente não são considerados aprovados: recebem `pending_manual_review` e explicação. Um detector pode apontar múltiplos IDs equivalentes, e um ID pode exigir mais de uma estratégia de evidência.

## Contrato da avaliação

Cada candidato possui `status=candidate_not_verified`. Um agente deve registrar `confirmed`, `intentional`, `false_positive`, `not_applicable` ou `pending` junto à evidência antes de corrigir. Deve utilizar um teste de aceitação que falhe antes e passe após a mudança. É proibido alterar uma decisão aprovada da marca apenas para reduzir contagens.

## Tratamento seguro de arquivos

O scanner ignora symlinks e diretórios de build/dependências, limita arquivos a 2 MB e não altera código. A etapa de correção cabe ao agente externo, deve gerar diffs revisáveis e ter rollback por Git, preservando dados e alterações preexistentes. A skill não executa scripts de correção a partir do código escaneado.
