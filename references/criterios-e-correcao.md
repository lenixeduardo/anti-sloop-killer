# Rubrica de aplicação e correção

## Conceitos que não podem se confundir

- **Assinatura visual genérica:** cluster de decisões tipográficas, cromáticas, layout e microinteração não motivadas pela marca. Exige contexto; não é prova de geração por IA.
- **Defeito objetivo:** ação quebrada, overflow, contraste, fluxo enganoso, lentidão, dado fictício, fonte/asset faltante, alteração não autorizada. Pode ocorrer em qualquer site.
- **Escolha intencional de marca:** cor, fonte, glassmorphism, bento, hero, layout, motion ou estética que tem suporte no briefing/design system. Não deve ser penalizada.

## Matriz de status por achado

| Estado | Significado | Precisa alterar? |
|---|---|---|
| `confirmado` | Evidência + impacto demonstrado | Sim, com teste de aceitação |
| `corrigido` | Alteração implementada e retestada | Não, salvo regressão |
| `intencional` | Decisão aprovada pela marca, com justificativa | Não |
| `falso_positivo` | Heurística não descreve defeito real | Não |
| `nao_aplicavel` | Página/projeto não contém o padrão | Não |
| `pendente` | Necessita reparo ou validação | Sim |
| `nao_verificado` | Falta acesso/prova suficiente | Não afirmar sucesso |

## Nota por dimensão (0–10)

- **9,5–10:** funcionalidade, identidade, acabamento e evidência excelentes; nenhum bloqueio.
- **8–9,4:** qualidade boa, mas com irregularidades relevantes documentadas.
- **6–7,9:** lacunas visíveis ou funcionais importantes.
- **0–5,9:** riscos expressivos, baixa funcionalidade ou identidade inconsistente.

A nota final é ponderada: identidade 25%; layout 20%; UX 20%; responsividade/acessibilidade 15%; animação 10%; conteúdo 10%. **Gates obrigatórios**: zero P0/P1, build e fluxos críticos verificados, screenshots de desktop/tablet/mobile, nenhuma violação de brand/assets. Um gate que falhe impede a homologação mesmo com média alta.

## Playbook de remediação

1. **Paleta suspeita:** conferir brand kit, tokens, contrastes e contexto; só mudar se comprovadamente não for identidade. Não trocar automaticamente uma moda por outra. 14 exemplos `P01..P14` no catálogo, incluindo laranja/coral/terracota.
2. **Hero genérica:** escrever intenção central do visitante e confirmar oferta real, imagens disponíveis e CTA verdadeiro. Redistribuir composição conforme conteúdo; não gerar “hero diferente” só por estilo.
3. **Cards repetidos:** reclassificar conteúdo por função e prioridade. Usar tabela, texto, visual real, lista ou cards somente quando fizerem sentido.
4. **Fonte padrão:** preservar fonte aprovada; se não houver, selecionar com base no caráter e legibilidade do produto e validar fallback, escala, comprimento da linha e pesos.
5. **Motion genérico:** reduzir animações redundantes, priorizar estados informativos; inspecionar performance e reduced motion. Em Three.js validar render, câmera e interação nos devices.
6. **Ícones/logos:** usar apenas SVG/assets vetoriais autorizados; consistência de traço, caixa, escala e perspectiva; sem emojis como ícones.
7. **Falsa credibilidade:** eliminar métricas e depoimentos sem fonte; não substituir por novas estatísticas inventadas.
8. **UX incompleta:** inventariar estados default/loading/empty/success/error/offline, fluxos de teclado e viewport. Validar navegação real.
9. **Dívida de frontend:** remover duplicação relevante e placeholders; corrigir semântica, tipagem, imports e dependências; não refatorar indiscriminadamente.
10. **SEO/performance:** verificar metadata, hero LCP, dimensões da mídia, CLS, disponibilidade de rotas, cache/rede e políticas de publicação.

## Critérios de evidência

- Prova estática: caminho/linha e regra exata. Marcada como `suspeita` até revisão.
- Prova renderizada: URL, viewport, screenshot comparativa, data/hora e estado.
- Prova funcional: ação executada, resultado, console/network, browser/versão quando relevante.
- Prova de regressão: diff, build/testes e repetição do fluxo antes quebrado.
- Prova de marca: referência aprovada, tokens e assets checados (hash quando viável).

## Limites

Nenhum scanner cobre 228 heurísticas com precisão alta só por código-fonte. Não usar contagem de match como score. A biblioteca não substitui Playwright, DevTools, auditoria WCAG, inspeção humana ou o briefing real.
