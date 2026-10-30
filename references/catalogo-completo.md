# Catálogo consolidado Anti-AI-Slop para websites

**Edição:** 29/10/2026 (ampliada em pesquisa complementar)  ·  **Idioma:** pt-BR  ·  **Formato:** Markdown

> Documento autoral de síntese técnica e auditoria, não uma reprodução integral dos artigos originais. Os nomes foram traduzidos ou condensados, e as descrições/diretrizes foram reescritas. Preserve os links abaixo para consultar os conteúdos completos.

**Atualização:** +56 verificações adicionais específicas (`NX-001`–`NX-056`) e duas composições cromáticas (`P13`–`P14`). Mantidos todos os identificadores originais e suas referências.

## Escopo e metodologia

- **Sailop:** 87 padrões distribuídos nas sete dimensões do catálogo publicado; identificadores `SA-001` a `SA-087`.
- **Impeccable:** 37 regras nas oito categorias do catálogo; `IM-001` a `IM-037`, mantendo a distinção entre *AI slop* e *Qualidade* e o modo de detecção (`CLI`, `Browser`, `LLM`).
- **Unslop UI (Herbert-Labs):** 13 tópicos do índice (`UH-001` a `UH-013`), sendo um deles **exclusão explícita de detecção**, não falha.
- **Unslop UI (claudiusararu):** 35 sinais complementares selecionados do `TELLS.md` (`UC-001` em diante); seleção não equivale à íntegra do repositório.
- **Paletas adicionais de auditoria:** 12 composições cromáticas (`P01`–`P12`), incluindo as quatro variantes laranjas. São exemplos operacionais criados neste documento, **não** entradas oficiais de um dos três catálogos.
- **Duplicatas:** fontes permanecem separadas para auditoria rastreável; não se deve somar os números como quantidade de defeitos únicos.
- **Precisão:** a Sailop informa 87 entradas; o catálogo consolidado está organizado pelas 87 posições/títulos da publicação. As recomendações são interpretações e não comandos universais. Pesquisas e porcentagens alegadas pelas fontes não foram verificadas de forma independente.

### Fontes primárias

1. [Impeccable — Slop (37 regras)](https://subclaude.com/slop/)
2. [Sailop — AI Slop Encyclopedia (87 padrões)](https://www.sailop.com/blog/ai-slop-encyclopedia)
3. [Herbert-Labs — Unslop UI skill](https://github.com/Herbert-Labs/vibecoded-design-tells/blob/main/skill/SKILL.md) e [catálogo de tells](https://github.com/Herbert-Labs/vibecoded-design-tells/blob/main/skill/references/tells.md)
4. [claudiusararu — Unslop UI TELLS.md](https://github.com/claudiusararu/unslop-ui-skill/blob/main/TELLS.md)

## Princípios obrigatórios antes de aplicar correções

- **Não proibir cores ou fontes.** Paletas roxas, laranjas, pretas e bege só entram como sinais quando são defaults não justificados e combinados a composição genérica.
- **Respeitar assets aprovados.** Não refazer logotipo, ilustração, fotografia, tipo ou paleta sem necessidade demonstrada e escopo autorizado.
- **Separar aparência de defeito.** Falhas WCAG, navegação, responsividade e ações quebradas são defeitos mesmo quando o design é original.
- **Verificar visualmente.** Uma varredura textual nunca comprova que a UI renderiza, anima e responde corretamente.
- **Não substituir um default por outro.** Roxo/azul não deve virar automaticamente creme/sálvia/serifa, laranja/coral ou preto/neon.
- **Exceção documentada.** Permitir registrar uma escolha intencional (por exemplo `unslop-ignore`) e sua justificativa.

---

## A. Sailop — 87 padrões

### A.1 Cores (15)

#### SA-001 — Azul Tailwind como primária
- **Sinal:** A cor predominante coincide com blue-600 / #2563EB sem decisão de marca.
- **Correção sugerida:** Defina uma cor de identidade e tokens próprios; preserve o azul quando for institucional.

#### SA-002 — Índigo em excesso
- **Sinal:** indigo-500/600 domina CTAs, links e fundos por inércia.
- **Correção sugerida:** Reveja a paleta completa e use tons intencionais.

#### SA-003 — Violeta como acento automático
- **Sinal:** Azul combinado ao violeta como reflexo de template.
- **Correção sugerida:** Exija justificativa do acento e variedade cromática coerente.

#### SA-004 — Texto em preto puro
- **Sinal:** Corpo usa #000000 de forma indiscriminada.
- **Correção sugerida:** Ajuste o preto conforme superfície, contraste e marca; não o proíba genericamente.

#### SA-005 — Fundos brancos puros por padrão
- **Sinal:** Toda superfície usa bg-white sem níveis visuais.
- **Correção sugerida:** Introduza hierarquia de superfícies quando pertinente.

#### SA-006 — Domínio de cinzas slate
- **Sinal:** Todos os neutros saem da escala slate do Tailwind.
- **Correção sugerida:** Estabeleça rampa neutra vinculada à marca e necessidades de contraste.

#### SA-007 — Uma única cor de destaque
- **Sinal:** Todos os elementos ativos compartilham exatamente o mesmo tom.
- **Correção sugerida:** Projete uma escala tonal e cores secundárias somente quando necessárias.

#### SA-008 — Ausência de cor secundária
- **Sinal:** Há uma cor primária e somente neutros sem distinção semântica.
- **Correção sugerida:** Avalie se uma cor secundária melhora navegação ou identidade.

#### SA-009 — Neutros sem temperatura
- **Sinal:** Cinzas sem matiz de marca dão aparência genérica.
- **Correção sugerida:** Defina neutros frios ou quentes de modo deliberado.

#### SA-010 — Sem variáveis CSS para cor
- **Sinal:** Cores espalhadas em classes e valores repetidos.
- **Correção sugerida:** Centralize tokens --color-* e documente usos.

#### SA-011 — Hexadecimais rígidos por todo o código
- **Sinal:** Valores hex são replicados sem sistema de tokens.
- **Correção sugerida:** Converta repetições para tokens; HEX não é erro por si só.

#### SA-012 — Sem tratamento de seleção de texto
- **Sinal:** ::selection fica no estilo padrão quando deveria integrar a identidade.
- **Correção sugerida:** Considere um estilo de seleção acessível e consistente.

#### SA-013 — Gradiente azul para roxo recorrente
- **Sinal:** linear-gradient azul→violeta em hero, títulos e CTA.
- **Correção sugerida:** Limite gradientes ao que tem propósito; adote linguagem cromática própria.

#### SA-014 — Direção de gradiente sempre para a direita
- **Sinal:** Uso repetido de bg-gradient-to-r em contextos variados.
- **Correção sugerida:** Ajuste direção à composição, em vez de mudar ângulo apenas por novidade.

#### SA-015 — Sem consideração por tema escuro
- **Sinal:** Ausência de estratégia para superfícies e preferências de tema.
- **Correção sugerida:** Defina política de temas conforme público, produto e acessibilidade.

### A.2 Tipografia (12)

#### SA-016 — Inter como escolha automática
- **Sinal:** Inter aparece como única família sem especificação de marca.
- **Correção sugerida:** Justifique a tipografia e desenvolva hierarquia própria; não substitua por outra moda.

#### SA-017 — Roboto como fallback estético
- **Sinal:** Roboto vira escolha estética automática sem conexão com o produto.
- **Correção sugerida:** Use pilha tipográfica coerente e fallback apropriado.

#### SA-018 — Poppins para parecer amigável
- **Sinal:** Poppins é usada porque o briefing diz somente “moderno e friendly”.
- **Correção sugerida:** Valide a personalidade tipográfica com referências concretas.

#### SA-019 — Ausência de fonte display
- **Sinal:** Títulos e corpo têm a mesma textura quando pedem contraste.
- **Correção sugerida:** Avalie uma família de exibição ou variações internas, sem impor duas fontes sempre.

#### SA-020 — Pouca variação de pesos
- **Sinal:** Interface alterna só 400 e 700 sem gradação.
- **Correção sugerida:** Ajuste pesos segundo funções, contraste e legibilidade.

#### SA-021 — Sem ajuste de tracking
- **Sinal:** Tracking uniforme em grandes títulos, labels e corpo.
- **Correção sugerida:** Ajuste espaçamento por tamanho e desenho de fonte.

#### SA-022 — Sem text-wrap balance em títulos adequados
- **Sinal:** Títulos apresentam linhas desequilibradas.
- **Correção sugerida:** Use balance quando ajudar; evite uso indiscriminado.

#### SA-023 — Escala tipográfica Tailwind intacta
- **Sinal:** Todos os tamanhos seguem exatamente presets sem ajuste editorial.
- **Correção sugerida:** Crie escala coerente com densidade e objetivos do site.

#### SA-024 — Carregamento de fontes sem font-display
- **Sinal:** Texto some durante a carga de @font-face.
- **Correção sugerida:** Empregue estratégia de carregamento adequada, geralmente swap.

#### SA-025 — Sem pilha de fallback
- **Sinal:** font-family informa uma família sem substitutas.
- **Correção sugerida:** Configure fallbacks métricos quando possível.

#### SA-026 — Fontes variáveis não consideradas
- **Sinal:** Múltiplos arquivos estáticos quando variável seria vantajosa.
- **Correção sugerida:** Avalie fonte variável por peso de download e suporte real.

#### SA-027 — Ausência de itálico quando útil
- **Sinal:** Ênfase e títulos não exploram variações disponíveis.
- **Correção sugerida:** Use itálico semanticamente quando contribuir; não como decoração automática.

### A.3 Layout (15)

#### SA-028 — Hero centralizada com slogan
- **Sinal:** Abertura em coluna única, H1 central, texto e dois botões.
- **Correção sugerida:** Estruture hero a partir de conteúdo, objetivo e imagem disponíveis.

#### SA-029 — Grid de três colunas em todo lugar
- **Sinal:** grid-cols-3 repetido para recursos, preços e depoimentos.
- **Correção sugerida:** Adote agrupamentos ditados pelo conteúdo.

#### SA-030 — Metades iguais para qualquer composição
- **Sinal:** grid-template-columns: 1fr 1fr mesmo quando há foco dominante.
- **Correção sugerida:** Experimente proporções orientadas à prioridade, sem assimetria forçada.

#### SA-031 — Container max-w-7xl universal
- **Sinal:** Todas as seções têm largura idêntica e conteúdo pouco aproveitado.
- **Correção sugerida:** Diferencie medidas de leitura, mídia e grids.

#### SA-032 — Sequência hero-features-pricing
- **Sinal:** Mesma ordem de seções de landing page SaaS.
- **Correção sugerida:** Organize a narrativa conforme jornada real de compra/uso.

#### SA-033 — Padding igual em todas as seções
- **Sinal:** py-20 ou py-24 em sequência mecânica.
- **Correção sugerida:** Use espaçamento por função, densidade e ritmo.

#### SA-034 — HTML pouco semântico
- **Sinal:** Divs substituem header, nav, main, section e article.
- **Correção sugerida:** Empregue elementos com função semântica adequada.

#### SA-035 — Ausência de grids assimétricos
- **Sinal:** Tudo ocupa células idênticas mesmo havendo diferenças importantes.
- **Correção sugerida:** Reserve assimetria para evidenciar prioridades reais.

#### SA-036 — Nenhum deslocamento da grade
- **Sinal:** Nenhum elemento quebra o alinhamento nem para efeitos editoriais.
- **Correção sugerida:** Permita exceções ópticas e transbordamento controlado quando úteis.

#### SA-037 — Raio único para todos os cantos
- **Sinal:** Todos os componentes compartilham o mesmo rounded-lg/2xl.
- **Correção sugerida:** Crie escala de raios por papel funcional, incluindo cantos retos.

#### SA-038 — CSS Grid sem áreas nomeadas
- **Sinal:** Layouts complexos montados sem clareza de regiões.
- **Correção sugerida:** Considere grid-template-areas onde melhorar legibilidade e adaptação.

#### SA-039 — Subgrid nunca considerado
- **Sinal:** Cards deixam textos e CTAs desalinhados apesar do mesmo grid.
- **Correção sugerida:** Use subgrid onde suportado e útil, sem obrigatoriedade.

#### SA-040 — Sem container queries
- **Sinal:** Componentes reagem só ao viewport mesmo dentro de contêineres diferentes.
- **Correção sugerida:** Empregue @container em componentes independentes quando apropriado.

#### SA-041 — Tudo é div
- **Sinal:** Hierarquia visual não corresponde a elementos HTML adequados.
- **Correção sugerida:** Corrija semântica e fluxo de teclado/leitores.

#### SA-042 — CSS columns ignorado
- **Sinal:** Conteúdo editorial flui em blocos indiferenciados.
- **Correção sugerida:** Avalie colunas de texto quando a leitura se beneficiar.

### A.4 Animação (12)

#### SA-043 — Fade-up em todos os elementos
- **Sinal:** Tudo entra com translateY + opacity.
- **Correção sugerida:** Animar só transições relevantes, com repertório de movimento coerente.

#### SA-044 — Pulse para todo loading
- **Sinal:** animate-pulse usado indiscriminadamente.
- **Correção sugerida:** Diferencie carregamento, atividade e atenção com estados claros.

#### SA-045 — Duração fixa de 300 ms
- **Sinal:** Toda transição é duration-300.
- **Correção sugerida:** Calibre duração por distância, dimensão e objetivo da ação.

#### SA-046 — Apenas ease-in-out
- **Sinal:** Todas as animações usam a mesma curva.
- **Correção sugerida:** Defina curvas por entrada, saída e interatividade.

#### SA-047 — Ausência de keyframes próprios
- **Sinal:** Somente presets de biblioteca, sem linguagem de movimento.
- **Correção sugerida:** Use animação específica quando a direção de arte exigir.

#### SA-048 — Stagger linear repetitivo
- **Sinal:** Sequências 0, 100, 200, 300 ms em todas as listas.
- **Correção sugerida:** Ajuste cascatas por quantidade e contexto; evite excessos.

#### SA-049 — Navegação sempre com backdrop-blur
- **Sinal:** Header fixo translúcido copiado de templates.
- **Correção sugerida:** Escolha comportamento do header pelo contexto de rolagem.

#### SA-050 — Ausência de :active
- **Sinal:** Botões têm hover, mas sem feedback de acionamento.
- **Correção sugerida:** Inclua estados pressed, foco e disabled adequados.

#### SA-051 — Cards sem feedback quando clicáveis
- **Sinal:** Cards interativos parecem inertes.
- **Correção sugerida:** Acrescente feedback discreto se houver ação real.

#### SA-052 — transition-all como padrão
- **Sinal:** Todas as propriedades animadas gerando custos de layout.
- **Correção sugerida:** Anima apenas propriedades necessárias, preferindo transform/opacity.

#### SA-053 — Sem prefers-reduced-motion
- **Sinal:** Movimento é imposto mesmo com preferência por redução.
- **Correção sugerida:** Respeite preferências do sistema e acessibilidade.

#### SA-054 — Nenhuma animação vinculada à rolagem considerada
- **Sinal:** Casos realmente baseados em progresso são implementados com soluções genéricas.
- **Correção sugerida:** Avalie recursos modernos quando houver suporte e ganho concreto.

### A.5 Componentes (15)

#### SA-055 — Terminal falso com três bolinhas
- **Sinal:** Mockup de terminal escuro com círculos coloridos e código genérico.
- **Correção sugerida:** Mostre captura, comandos e resultados reais.

#### SA-056 — Feature cards idênticos
- **Sinal:** Três ou quatro cartões de mesmo tamanho e estrutura.
- **Correção sugerida:** Dê destaque à função principal e adapte os demais ao conteúdo.

#### SA-057 — Faixa de estatísticas genéricas
- **Sinal:** Números grandes de clientes, velocidade e uptime sem fonte.
- **Correção sugerida:** Use métricas verificáveis e contextualizadas.

#### SA-058 — FAQ em acordeão automático
- **Sinal:** Todo conjunto de dúvidas vira um componente de expandir.
- **Correção sugerida:** Escolha apresentação conforme quantidade e necessidade de leitura.

#### SA-059 — CTA genérico Get Started
- **Sinal:** Botões sem verbo específico da operação.
- **Correção sugerida:** Dê nome ao resultado esperado do clique.

#### SA-060 — Botões sempre pill
- **Sinal:** rounded-full aplicado a todos os botões.
- **Correção sugerida:** Defina geometria de controles coerente com a marca.

#### SA-061 — Cards sempre rounded-2xl
- **Sinal:** Mesmo raio generoso em toda superfície.
- **Correção sugerida:** Ajuste raios por componente e composição.

#### SA-062 — Seção de passos numerados genérica
- **Sinal:** “Como funciona” sempre representado em 1-2-3.
- **Correção sugerida:** Use demonstração real, sequência funcional ou texto direto.

#### SA-063 — Três testemunhos em grid
- **Sinal:** Depoimentos idênticos com avatar, cargo e citação vaga.
- **Correção sugerida:** Priorize provas reais e varie apresentação quando necessário.

#### SA-064 — Badge pulsante sobre a hero
- **Sinal:** Pill “New/AI-powered” com ponto animado sem importância.
- **Correção sugerida:** Remova ou troque por atualização realmente relevante.

#### SA-065 — Rodapé Built with Love
- **Sinal:** Mensagem genérica substitui links e informações úteis.
- **Correção sugerida:** Mostre contato, políticas e caminhos reais.

#### SA-066 — Cards de ícone-título-frase
- **Sinal:** Cards com ícone de biblioteca e slogan superficial.
- **Correção sugerida:** Revele funcionamento, capturas ou evidências.

#### SA-067 — Dashboard de demonstração fictício
- **Sinal:** Valores e gráficos inventados usados como prova.
- **Correção sugerida:** Utilize dados rotulados como demo ou capturas de produto real.

#### SA-068 — Três planos de preço idênticos
- **Sinal:** Free/Pro/Enterprise, plano central em destaque automaticamente.
- **Correção sugerida:** Modele estrutura comercial real, sem inventar planos.

#### SA-069 — Barra de logos de clientes fictícios
- **Sinal:** Seção “Trusted by” exibe logos genéricos ou não autorizados.
- **Correção sugerida:** Use apenas parcerias comprovadas e assets oficiais.

### A.6 Estrutura (10)

#### SA-070 — Div soup
- **Sinal:** Muitas divs e poucos elementos semânticos.
- **Correção sugerida:** Empregue HTML semântico e landmarks.

#### SA-071 — Sem ::selection
- **Sinal:** Estilo de seleção não dialoga com o design.
- **Correção sugerida:** Avalie seleção acessível quando apropriado.

#### SA-072 — Sem :focus-visible
- **Sinal:** Falta indicação clara para teclado.
- **Correção sugerida:** Adicione estilo visível e com contraste.

#### SA-073 — Sem respeito a reduced motion
- **Sinal:** Não existe condição para reduzir movimento.
- **Correção sugerida:** Forneça alternativa para usuários sensíveis.

#### SA-074 — Sem CSS custom properties
- **Sinal:** Não há tokens reutilizáveis para cores e layout.
- **Correção sugerida:** Centralize sistema visual em variáveis.

#### SA-075 — Elemento HTML errado para função
- **Sinal:** Div clicável, span imitando botão ou tags indevidas.
- **Correção sugerida:** Substitua por elemento semântico correto.

#### SA-076 — Sem aria-labels onde necessários
- **Sinal:** Botões só com ícone sem nome acessível.
- **Correção sugerida:** Nomeie controles e defina alt adequadamente.

#### SA-077 — Sem skip link
- **Sinal:** Navegação por teclado exige percorrer menu repetidamente.
- **Correção sugerida:** Adicione pulo para conteúdo principal.

#### SA-078 — Somente className, sem abstração de estilo
- **Sinal:** Grandes cadeias de utilitários repetidas em todo o projeto.
- **Correção sugerida:** Extraia tokens/variantes, mantendo Tailwind onde adequado.

#### SA-079 — Sem text-wrap moderno onde ajuda
- **Sinal:** Títulos e corpo com quebras ruins em vários breakpoints.
- **Correção sugerida:** Use propriedades modernas de texto criteriosamente.

### A.7 Espaçamento (8)

#### SA-080 — py-20 em todas as seções
- **Sinal:** Espaçamento vertical constante e mecânico.
- **Correção sugerida:** Crie ritmo por hierarquia de conteúdo.

#### SA-081 — Grade de 4 px aplicada rigidamente
- **Sinal:** Alinhamento matemático prevalece sobre ajustes ópticos.
- **Correção sugerida:** Permita pequenos ajustes justificados.

#### SA-082 — Ausência total de valores ópticos
- **Sinal:** Jamais há valores intermediários onde a percepção pediria.
- **Correção sugerida:** Faça ajustes direcionados sem virar caos de medidas.

#### SA-083 — Mesmo gap em todos os componentes
- **Sinal:** gap-4 e gap-6 uniformes, independentes de relação semântica.
- **Correção sugerida:** Aproxime elementos relacionados e separe grupos distintos.

#### SA-084 — Padding de seção sem variação
- **Sinal:** Seções densas e leves recebem mesmo espaço.
- **Correção sugerida:** Modifique padding segundo densidade e prioridade.

#### SA-085 — Sem clamp() para espaço fluido
- **Sinal:** Medidas saltam abruptamente entre breakpoints.
- **Correção sugerida:** Avalie clamp() quando tiver faixa responsiva clara.

#### SA-086 — Sem estratégia de espaçamento responsivo
- **Sinal:** Valores desktop persistem no celular ou só um breakpoint altera.
- **Correção sugerida:** Defina tokens e comportamento por viewport/contexto.

#### SA-087 — px-4 para tudo no mobile
- **Sinal:** Todas as bordas seguem 16px sem diferenciação.
- **Correção sugerida:** Alinhe por ritmo visual, admitindo exceções intencionais.

---

## B. Impeccable — 37 regras

### B.1 Detalhes visuais (6)

#### IM-001 — Borda de acento em elemento arredondado
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Faixa colorida espessa conflita visualmente com cantos curvos.
- **Correção sugerida:** Reduzir faixa ou remover arredondamento.

#### IM-002 — Glassmorphism por toda parte
- **Classe:** AI slop. **Método:** LLM.
- **Sinal:** Vidro, blur e borda luminosa em locais sem necessidade de camadas.
- **Correção sugerida:** Usar vidro apenas onde estrutura justificar.

#### IM-003 — Modais como padrão de solução
- **Classe:** AI slop. **Método:** LLM.
- **Sinal:** Diálogo interrompe fluxos que caberiam na própria página.
- **Correção sugerida:** Reservar modal a decisões contextuais curtas.

#### IM-004 — Retângulos arredondados e sombras genéricas
- **Classe:** AI slop. **Método:** LLM.
- **Sinal:** Todas as superfícies usam mesmo card e sombra suave.
- **Correção sugerida:** Definir tratamentos específicos por função.

#### IM-005 — Borda lateral tipo aba
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Faixa grossa em um lado de card, estilo template.
- **Correção sugerida:** Substituir por hierarquia mais discreta.

#### IM-006 — Sparklines puramente decorativos
- **Classe:** AI slop. **Método:** LLM.
- **Sinal:** Minigráficos não possuem escala, informação nem contexto.
- **Correção sugerida:** Mostrar dados reais ou eliminar decoração.

### B.2 Tipografia (6)

#### IM-007 — Hierarquia tipográfica achatada
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Título, subtítulo e corpo em tamanhos quase iguais.
- **Correção sugerida:** Aumentar contraste proporcional e semântico.

#### IM-008 — Ícone empilhado acima do título
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Ícone num quadrado arredondado acima do texto de feature.
- **Correção sugerida:** Reorganizar conteúdo e questionar necessidade do ícone.

#### IM-009 — Monoespaçada usada só para parecer técnica
- **Classe:** AI slop. **Método:** LLM.
- **Sinal:** Mono em rótulos genéricos para simular devtool.
- **Correção sugerida:** Usar quando houver necessidade técnica/editorial.

#### IM-010 — Fonte superutilizada sem decisão
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Inter, Roboto, Fraunces, Geist, Plus Jakarta Sans ou Space Grotesk no automático.
- **Correção sugerida:** Selecionar sistema tipográfico por marca.

#### IM-011 — Fonte única para todas as funções
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Mesma família, sem contraste de estilo ou peso.
- **Correção sugerida:** Definir hierarquia por família, variações ou ambos.

#### IM-012 — Corpo de texto em caixa alta
- **Classe:** Qualidade. **Método:** CLI.
- **Sinal:** Parágrafos inteiros em uppercase prejudicam leitura.
- **Correção sugerida:** Reservar caixa alta a rótulos curtos.

### B.3 Cores e contraste (6)

#### IM-013 — Paleta cromática de IA
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Violeta/roxo em gradiente e ciano sobre preto por reflexo.
- **Correção sugerida:** Escolher cores referenciadas à marca.

#### IM-014 — Dark mode com brilhos coloridos
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Glows luminosos recorrentes sobre fundos escuros.
- **Correção sugerida:** Reduzir luz a pontos com propósito.

#### IM-015 — Dark mode escolhido por segurança
- **Classe:** AI slop. **Método:** LLM.
- **Sinal:** Tema escuro ou claro decidido sem relação com contexto.
- **Correção sugerida:** Tomar decisão explícita por público e ambiente.

#### IM-016 — Texto com gradiente
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** H1 ou KPI coloridos por background-clip.
- **Correção sugerida:** Usar texto sólido quando legibilidade for melhor.

#### IM-017 — Texto cinza sobre superfície colorida
- **Classe:** Qualidade. **Método:** CLI.
- **Sinal:** Contraste insuficiente e aparência apagada.
- **Correção sugerida:** Selecionar cor de texto calculada para o fundo.

#### IM-018 — Fundo preto puro
- **Classe:** Qualidade. **Método:** CLI.
- **Sinal:** Superfície #000000 usada sem justificativa visual.
- **Correção sugerida:** Avaliar preto tonal e camadas de superfície.

### B.4 Layout e espaço (7)

#### IM-019 — Tudo centralizado
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Textos e seções centralizados indiscriminadamente.
- **Correção sugerida:** Conduzir alinhamento pelo conteúdo e leitura.

#### IM-020 — Hero de métricas genéricas
- **Classe:** AI slop. **Método:** LLM.
- **Sinal:** Números enormes e pequenas estatísticas com gradiente.
- **Correção sugerida:** Substituir por evidências verificáveis.

#### IM-021 — Grades de cards idênticos
- **Classe:** AI slop. **Método:** LLM.
- **Sinal:** Vários ícones/títulos/textos clonados em cartões iguais.
- **Correção sugerida:** Variar a apresentação de acordo com prioridade.

#### IM-022 — Espaçamento monótono
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Mesmos gaps e paddings em todas as regiões.
- **Correção sugerida:** Criar ritmo e agrupamento consistente.

#### IM-023 — Cards dentro de cards
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Aninhamento excessivo de bordas e sombras.
- **Correção sugerida:** Simplificar níveis de contêiner.

#### IM-024 — Tudo dentro de cards
- **Classe:** AI slop. **Método:** LLM.
- **Sinal:** Qualquer conteúdo ganha retângulo com borda.
- **Correção sugerida:** Usar espaço e tipografia sem caixa quando cabível.

#### IM-025 — Linhas de texto compridas demais
- **Classe:** Qualidade. **Método:** Browser.
- **Sinal:** Parágrafos ultrapassam ~80 caracteres por linha.
- **Correção sugerida:** Limitar medida do texto (aprox. 65–75ch).

### B.5 Movimento (2)

#### IM-026 — Bounce e easing elástico automático
- **Classe:** AI slop. **Método:** CLI.
- **Sinal:** Saltos exagerados em interações comuns.
- **Correção sugerida:** Usar curvas adequadas ao comportamento e à identidade.

#### IM-027 — Animação de propriedades de layout
- **Classe:** Qualidade. **Método:** CLI.
- **Sinal:** Animar width, height, padding e margin gera instabilidade.
- **Correção sugerida:** Preferir transform/opacity ou técnica apropriada.

### B.6 Interação (2)

#### IM-028 — Todos os botões são primários
- **Classe:** Qualidade. **Método:** LLM.
- **Sinal:** CTAs com mesma saliência e cor.
- **Correção sugerida:** Separar ação principal e secundárias.

#### IM-029 — Informação redundante
- **Classe:** Qualidade. **Método:** LLM.
- **Sinal:** Subtítulo, título e legendas repetem ideia.
- **Correção sugerida:** Eliminar conteúdo duplicado.

### B.7 Responsividade (1)

#### IM-030 — Cortar recursos essenciais do mobile
- **Classe:** Qualidade. **Método:** LLM.
- **Sinal:** Funcionalidade desaparece por falta de adaptação.
- **Correção sugerida:** Adaptar interface sem reduzir capacidades essenciais.

### B.8 Qualidade geral (7)

#### IM-031 — Padding apertado
- **Classe:** Qualidade. **Método:** Browser.
- **Sinal:** Conteúdo encosta em borda/recipiente.
- **Correção sugerida:** Aumentar respiro segundo tamanho e densidade.

#### IM-032 — Texto justificado inadequado
- **Classe:** Qualidade. **Método:** CLI.
- **Sinal:** Rios de espaços em colunas web.
- **Correção sugerida:** Preferir alinhamento à esquerda, avaliar hifenização.

#### IM-033 — Contraste textual baixo
- **Classe:** Qualidade. **Método:** CLI.
- **Sinal:** Texto falha nos limiares WCAG.
- **Correção sugerida:** Verificar contraste normal ≥4,5:1 e grande ≥3:1.

#### IM-034 — Pulo de nível em headings
- **Classe:** Qualidade. **Método:** CLI.
- **Sinal:** h1 seguido de h3 sem h2 correspondente.
- **Correção sugerida:** Restaurar hierarquia de títulos lógica.

#### IM-035 — Entrelinha comprimida
- **Classe:** Qualidade. **Método:** CLI.
- **Sinal:** Corpo em múltiplas linhas com line-height menor que ~1,3.
- **Correção sugerida:** Ajustar line-height à tipografia e idioma.

#### IM-036 — Texto de corpo minúsculo
- **Classe:** Qualidade. **Método:** CLI.
- **Sinal:** Texto importante abaixo de ~12px.
- **Correção sugerida:** Manter tamanho legível, geralmente ≥14–16px.

#### IM-037 — Letter-spacing excessivo no corpo
- **Classe:** Qualidade. **Método:** CLI.
- **Sinal:** Tracking amplo torna frases lentas para ler.
- **Correção sugerida:** Conservar tracking amplo só em títulos/rótulos curtos.

**Nota:** O catálogo Impeccable informa 25 verificações determinísticas e 12 revisões por LLM. A classificação `CLI`/`Browser`/`LLM` foi preservada por entrada, mas a eficácia efetiva do detector depende da implementação e do ambiente.

---

## C. Unslop UI (Herbert-Labs) — catálogo priorizado

### UH-001 — Novo default “sofisticado” creme + serifa + verde sálvia
- **Prioridade:** alto.
- **Sinal:** Combinação #faf8f5 + Instrument Serif/Fraunces + verde-escuro sem justificativa.
- **Orientação:** Ancorar paleta, fonte e composição em identidade real; respeitar exceção intencional.

### UH-002 — shadcn e Tailwind sem personalização
- **Prioridade:** alto.
- **Sinal:** Cards, tokens e sombras iguais aos exemplos padrão.
- **Orientação:** Customizar tokens, componentes e ritmos antes de construir.

### UH-003 — Roxo/índigo de IA
- **Prioridade:** alto.
- **Sinal:** Violeta padrão em ação primária e links.
- **Orientação:** Revisar escolha pela marca, sem proibir roxo intencional.

### UH-004 — Gradientes e texto em gradiente
- **Prioridade:** alto.
- **Sinal:** Azul-violeta, letras transparentes com clip e múltiplos gradientes.
- **Orientação:** Reservar efeitos apenas para casos relevantes.

### UH-005 — Animação excessiva
- **Prioridade:** médio.
- **Sinal:** Fade-up, scale hover e scrolljacking repetidos.
- **Orientação:** Reduzir movimento e testar preferências de acessibilidade.

### UH-006 — Arredondamento universal
- **Prioridade:** médio.
- **Sinal:** rounded-2xl/3xl/full por toda a UI.
- **Orientação:** Escalonar raios segundo função.

### UH-007 — Neon e glow não solicitados
- **Prioridade:** médio.
- **Sinal:** Sombra colorida forte em dark mode genérico.
- **Orientação:** Desligar glow sem propósito; escuro por si só é permitido.

### UH-008 — Emojis como ícones de interface
- **Prioridade:** médio.
- **Sinal:** Emoji substitui ícone SVG em navegação e features.
- **Orientação:** Usar sistema consistente de ícones SVG ou nenhum.

### UH-009 — Fontes genéricas automáticas
- **Prioridade:** médio.
- **Sinal:** Inter/Geist e a nova moda Instrument Serif/Fraunces sem decisão de marca.
- **Orientação:** Estabelecer escolha tipográfica justificada.

### UH-010 — Esqueleto hero + três cards + CTA
- **Prioridade:** médio.
- **Sinal:** Estrutura simétrica copiada para todo tipo de produto.
- **Orientação:** Redesenhar jornada e distribuição conforme caso.

### UH-011 — Problemas reais de layout
- **Prioridade:** qualidade.
- **Sinal:** Overflow, alinhamento e espaço insuficiente em telas menores.
- **Orientação:** Revisar tamanhos reais com screenshots.

### UH-012 — Sinais de texto e baixa confiança
- **Prioridade:** contextual.
- **Sinal:** Clichês, fake reviews, conteúdo implausível e exemplos vazios.
- **Orientação:** Substituir por texto específico e evidência verificável.

### UH-013 — Sinais pouco comprovados (não penalizar automaticamente)
- **Prioridade:** exclusão.
- **Sinal:** Bento, glassmorphism e aurora/mesh têm evidência contestada ou fraca no estudo.
- **Orientação:** Registrar apenas quando prejudicarem a experiência ou identidade.

**Importante:** UH-013 registra padrões que o projeto aconselha **não detectar como erro automático**: *bento grids*, *glassmorphism* e fundos *mesh/aurora*, em razão de baixa robustez ou controvérsia dos sinais nos dados analisados. Isso conflita com detectores mais agressivos e deve prevalecer como critério de falso positivo, salvo defeitos objetivos de UX.

### Procedimento do Unslop UI

1. Definir briefing específico: referência, objetivo da página, paleta, tipografia e layout.
2. Rodar análise estática do repositório; registrar arquivos e linhas de evidência.
3. Classificar ocorrências em `default não solicitado`, `decisão intencional` e `defeito de qualidade`.
4. Corrigir os maiores riscos preservando a identidade e adicionar justificativas para exceções.
5. Validar no browser real e documentar capturas, breakpoints, interações e regressões.

Exemplo do projeto original:

```bash
python3 scripts/devibe_scan.py ./src --severity high
python3 scripts/devibe_scan.py ./src --json
```

Repositório de referência: https://github.com/Herbert-Labs/vibecoded-design-tells

---

## D. Complemento Unslop UI (claudiusararu) — 35 sinais selecionados

### D.1 Tipografia e copy

#### UC-001 — Mistura Space Grotesk + serif itálica + Inter
- **Sinal:** Trio de fontes da moda empregado sem briefing.
- **Correção sugerida:** Evitar o conjunto padronizado; definir escolhas justificadas.

#### UC-002 — Palavra única em itálico no H1
- **Sinal:** Um termo em serif-itálica só para parecer editorial.
- **Correção sugerida:** Criar sistema tipográfico real, não efeito isolado.

#### UC-003 — Tracking negativo aplicado ao corpo
- **Sinal:** tracking-tight em texto de 14–16px.
- **Correção sugerida:** Restituir espaçamento de leitura adequado.

#### UC-004 — Quebra artificial com br em títulos
- **Sinal:** Quebra fixa estoura em outros breakpoints.
- **Correção sugerida:** Controlar largura com medidas fluidas e testar responsividade.

#### UC-005 — Eyebrow em todas as seções
- **Sinal:** Rótulo uppercase em cada bloco sem informação nova.
- **Correção sugerida:** Remover rótulos redundantes.

#### UC-006 — Numerais não tabulares em tabelas
- **Sinal:** Preços e colunas numéricas desalinhados.
- **Correção sugerida:** Aplicar font-variant-numeric: tabular-nums.

#### UC-007 — Títulos longos e órfãos
- **Sinal:** H1 de quatro linhas com última linha de uma palavra.
- **Correção sugerida:** Editar copy e medida tipográfica.

#### UC-008 — Texto sem dados concretos
- **Sinal:** Slogans vagos e marketing inflado.
- **Correção sugerida:** Dar valores, exemplos e ações reais.

### D.2 Paleta e fundo

#### UC-009 — Gradiente quente âmbar-rosa como novo default
- **Sinal:** Depois de eliminar violeta, template passa a from-amber-400 to-pink-500.
- **Correção sugerida:** Evitar substituir um padrão pelo outro; usar direção cromática própria.

#### UC-010 — Paleta sem dominante
- **Sinal:** Quatro ou cinco tons em intensidades iguais.
- **Correção sugerida:** Criar hierarquia de neutros e acentos segundo a marca.

#### UC-011 — Faixa cromática sem âncoras
- **Sinal:** Todas as cores ficam em valores intermediários e pouco contraste.
- **Correção sugerida:** Introduzir contraste adequado e gradação de superfícies.

#### UC-012 — Tons de status diretos do framework
- **Sinal:** red-500/green-500/yellow-500 em todas as mensagens.
- **Correção sugerida:** Separar funções semânticas e harmonizar tokens sem comprometer significado.

#### UC-013 — Focus ring de cor fora da marca
- **Sinal:** ring-indigo-500 permanece após personalizar restante.
- **Correção sugerida:** Personalizar token de foco com contraste adequado.

#### UC-014 — Fundo aurora/blobs automático
- **Sinal:** Manchas radiais como preenchimento de hero vazia.
- **Correção sugerida:** Usar imagem real, textura com propósito ou espaço negativo.

#### UC-015 — Grade pontilhada escura decorativa
- **Sinal:** Grid.svg em opacidade mínima sobre hero sem função.
- **Correção sugerida:** Eliminar ou relacionar a linguagem visual ao conteúdo.

#### UC-016 — Sombras homogêneas sem elevação
- **Sinal:** Todo card repete shadow-md com mesma opacidade.
- **Correção sugerida:** Construir níveis de superfície por função.

#### UC-017 — Separadores wave em toda transição
- **Sinal:** Ondas SVG entre cada seção.
- **Correção sugerida:** Conectar seções por narrativa e hierarquia visual.

### D.3 Layout e componentes

#### UC-018 — Rodapé SaaS inchado
- **Sinal:** Quatro colunas, newsletter e redes apesar de site pequeno.
- **Correção sugerida:** Incluir apenas navegação e links existentes.

#### UC-019 — CTA final espelha a hero
- **Sinal:** Mesmo título e botões ao final da página.
- **Correção sugerida:** Encerrar a narrativa com ação específica.

#### UC-020 — Zigue-zague 50/50 obrigatório
- **Sinal:** Imagem alterna lado a cada seção com proporção igual.
- **Correção sugerida:** Compor por conteúdo em vez de alternância mecânica.

#### UC-021 — Mobile vira fila infinita de cards
- **Sinal:** Todas as grades viram lista única idêntica.
- **Correção sugerida:** Projetar densidade e interação mobile adequadas.

#### UC-022 — Badge “Now with AI” sem notícia real
- **Sinal:** Selo decorativo com ponto luminoso no topo.
- **Correção sugerida:** Usar anúncio verificável ou remover.

#### UC-023 — Pricing com scale-105 no plano central
- **Sinal:** Plano médio ampliado por reflexo de template.
- **Correção sugerida:** Destaque planos conforme proposta comercial real.

#### UC-024 — Estado vazio sem orientação
- **Sinal:** Ícone grande e “No data yet” sem informar ação.
- **Correção sugerida:** Explicar próximo passo e estado real.

#### UC-025 — Toast padrão para qualquer evento
- **Sinal:** Sonner com aparência de instalação em toda interação.
- **Correção sugerida:** Adequar feedback e priorizar estados embutidos.

#### UC-026 — Hover lift em todos os cards
- **Sinal:** Cartões sem ação também sobem no mouse.
- **Correção sugerida:** Somente interativos recebem affordance apropriada.

#### UC-027 — Card com tira colorida lateral
- **Sinal:** border-l-4 por padrão em vários módulos.
- **Correção sugerida:** Definir sinalização por contexto real.

### D.4 Imagens e ícones

#### UC-028 — Pessoas sintéticas com artefatos
- **Sinal:** Mãos, pele, dentes e acessórios incoerentes.
- **Correção sugerida:** Preferir imagens reais; validar cada geração visualmente.

#### UC-029 — Texto ilegível dentro de imagem
- **Sinal:** UI ou anúncios gerados com letras irreconhecíveis.
- **Correção sugerida:** Compor texto real sobre a imagem ou capturar UI real.

#### UC-030 — Depoimentos com avatares falsos
- **Sinal:** Rostos ou iniciais de clientes inexistentes.
- **Correção sugerida:** Usar autorização e fontes reais ou não exibir prova.

#### UC-031 — Arte 3D genérica de esfera cromada
- **Sinal:** Orb, cubo iridescente e blur substituem demonstração.
- **Correção sugerida:** Usar imagens que expliquem produto.

#### UC-032 — Mockup de navegador inclinado em gradiente
- **Sinal:** Frames flutuantes e ilegíveis no topo.
- **Correção sugerida:** Exibir recorte real de interface e estados funcionais.

#### UC-033 — Logos de terceiros distorcidos
- **Sinal:** Marcas reconstituídas incorretamente em seção social proof.
- **Correção sugerida:** Utilizar assets oficiais, com direitos e verificação.

#### UC-034 — Emojis simulando ícones
- **Sinal:** Rocket/sparkle/lightning em interface funcional.
- **Correção sugerida:** Usar SVGs consistentes; não usar emojis como ícones.

#### UC-035 — Lucide universal com chips
- **Sinal:** Ícones monoline copiados em caixas coloridas.
- **Correção sugerida:** Customizar conjunto, peso e apresentação sem sacrificar consistência.

Este subconjunto ressalta detalhes que não ficam explícitos em todos os índices acima. Para o catálogo original completo, consulte o `TELLS.md` na fonte primária, pois o repositório se apresenta como coleção de aproximadamente 100 observações, não como número fechado de regras.

---

## E. Paletas cromáticas — 12 exemplos operacionais

**Alerta:** as faixas HEX abaixo são combinações ilustrativas para inspeção e não prova de origem por IA. Não penalize cor isolada. O risco cresce quando há repetição de framework defaults, glows, gradientes decorativos, falta de identidade e contraste ruim.

| ID | Estilo | Cores HEX | Condição de alerta |
|---|---|---|---|
| P01 | AI Purple Gradient | `#0F172A`, `#2563EB`, `#6366F1`, `#8B5CF6`, `#A855F7` | Azul → violeta → roxo em landing SaaS; alto quando acompanhado de gradient text e glows. |
| P02 | Cyber Neon AI | `#050816`, `#00D4FF`, `#7C3AED`, `#FF3CAC`, `#EDE9FE` | Ciano/violeta/rosa fluorescentes e efeitos glow no fundo escuro. |
| P03 | Lavender SaaS | `#F8FAFC`, `#EEF2FF`, `#C7D2FE`, `#8B5CF6`, `#1F2937` | Lavanda clara, botões violetas e cards arredondados. |
| P04 | Tailwind Default Blue | `#FFFFFF`, `#EFF6FF`, `#3B82F6`, `#2563EB`, `#0F172A` | Azuis de preset sem sistema cromático próprio. |
| P05 | Beige Editorial | `#F5EFE6`, `#E7D6C1`, `#C5AD8B`, `#8B735B`, `#28241F` | Bege editorial repetitivo sem vínculo à marca. |
| P06 | Pastel AI Friendly | `#FFF7ED`, `#FBCFE8`, `#DDD6FE`, `#BBF7D0`, `#6D28D9` | Pêssego, rosa, lavanda e menta com aparência de template. |
| P07 | Fake Luxury Gold | `#111110`, `#383024`, `#C29B5B`, `#EDE0C7`, `#F5F2EB` | Preto/champanhe/dourado usados para sugerir luxo sem direção de arte. |
| P08 | Dark Neon Minimal | `#09090B`, `#18181B`, `#27272A`, `#A3E635`, `#FAFAFA` | Off-black e lima neon; risco sobretudo quando há glow e visual genérico. |
| P09 | Orange SaaS Gradient | `#FFF7ED`, `#FDBA74`, `#FB923C`, `#F97316`, `#EA580C` | Escala laranja Tailwind, CTA saturado e fundo creme. |
| P10 | Peach & Coral AI | `#FFF1E6`, `#FFD6BA`, `#FFB38A`, `#FF805C`, `#F45D48` | Pêssego/coral em superfícies suaves e cards arredondados. |
| P11 | Warm Amber & Beige | `#FAF6EF`, `#FDE68A`, `#F59E0B`, `#D97706`, `#78350F` | Âmbar e bege usados para substituir o gradiente roxo automaticamente. |
| P12 | Dark Orange Glow | `#09090B`, `#27211E`, `#9A3412`, `#F97316`, `#FFEDD5` | Preto com sombra brilhante laranja, estética tech de template. |

### Regras específicas para paletas laranjas

- Orange SaaS Gradient (`P09`): identificar cópia da escala `orange-50...orange-600`, sobretudo com cards e CTAs genéricos.
- Peach & Coral AI (`P10`): procurar superfícies pêssego/coral sem identificação de marca e excesso de blur.
- Warm Amber & Beige (`P11`): detectar paleta creme+âmbar como possível substituto automático para o roxo; não classificar qualquer fundo quente como erro.
- Dark Orange Glow (`P12`): avaliar se glow laranja em fundo preto tem intenção de marca e se não prejudica contraste/legibilidade.
- Acrescentar a combinação `creme + serif + sálvia` como alerta composto de alta prioridade, conforme Unslop 2026, ainda que não corresponda a uma das 12 paletas anteriores.

---

## F. Critérios de priorização e homologação 9,5/10 (proposta do catálogo consolidado)

### Severidade

| Classe | Significado | Exemplo | Tratamento |
|---|---|---|---|
| P0, funcional | Função inacessível/quebrada ou bloqueio ao uso | CTA sem ação, menu inacessível, erro de scroll | Corrigir antes de publicar |
| P1, acessibilidade | Obstáculo significativo de uso/contraste | foco invisível, texto baixo contraste, reduced-motion ignorado | Corrigir antes de homologar |
| P2, identidade genérica | Evidência combinada de defaults não escolhidos | hero + 3 cards + roxo + icon chips | Redesenhar com brief e preservar assets |
| P3, estilo discutível | Preferência estética sem defeito comprovado | bento, glassmorphism, dark mode intencional | Não penalizar sozinho |

### Pontuação proposta (diferente da escala Sailop)

| Pilar | Peso |
|---|---:|
| Identidade e originalidade | 25% |
| Layout e tipografia | 20% |
| UX e funções reais | 20% |
| Responsividade e acessibilidade | 15% |
| Animações e interações | 10% |
| Conteúdo e provas reais | 10% |

**Meta:** ≥9,5/10 após revisão visual e testes, não apenas ao passar o scanner.

### Checklist mínimo de evidências

- [ ] Captura da referência aprovada versus render atual em desktop, lado a lado.
- [ ] Capturas mobile e tablet lado a lado e legíveis, preservando os assets.
- [ ] Comparação do fundo, tipografia, cores, margens, recortes e iconografia.
- [ ] Cliques em CTAs, navegação, pesquisa, modais, carrosséis e links.
- [ ] Scroll, animações reais, fallback e prefers-reduced-motion.
- [ ] Sem overflow horizontal, elementos cortados ou cards vazios.
- [ ] Contraste mínimo WCAG para texto normal e grande, com evidência.
- [ ] Validação de imagem/asset sem adulteração e de logos não cortados.
- [ ] Relatório dos achados, com regra ID, severidade, arquivo/linha ou screenshot, correção e reteste.
- [ ] Build/testes automatizados e acesso por HTTPS quando APIs do navegador assim exigirem.

### Modelo de achado para agentes

```yaml
id: AUD-001
source_rules: [IM-013, SA-013, UH-004]  # exemplo ilustrativo
category: color
severity: P2
status: open
evidence:
  file: src/app/page.tsx
  lines: [18, 45]
  screenshot: evidence/desktop-before.png
  rationale: "Gradiente sem vínculo com o brand kit aprovado"
action: "Aplicar tokens da identidade existente sem redesenhar assets"
validation:
  desktop: pending
  tablet: pending
  mobile: pending
  interaction: pending
```

> Nota sobre IDs acima: em achados reais, referenciar sempre a entrada correta do catálogo. A referência YAML é demonstrativa e deve ser conferida antes da automação.

## Limitações e divergências entre fontes

- **Glassmorphism, aurora e bento:** alguns catálogos consideram sinais estéticos; o estudo Unslop UI prefere não detectar automaticamente. Tratar como contexto, não prova.
- **Fonte única versus combinação:** duas famílias não são requisito universal. Uma família variável bem trabalhada pode formar excelente hierarquia.
- **Dark mode:** ausência de modo escuro pode ser opção legítima do produto; a obrigatoriedade defendida pela Sailop não deve ser imposta sem contexto.
- **Regra de cor específica:** nome Tailwind não comprova uso de IA. É escolha não justificada combinada com outros padrões que tem valor diagnóstico.
- **Seleção e CSS modernos:** falta de `::selection`, `subgrid` ou `text-wrap: balance` não deve gerar falha bloqueante sozinha.
- **Contagem:** 87 Sailop + 37 Impeccable + catálogo priorizado Unslop + sinais complementares contêm muitas sobreposições; este material não afirma um total de sinais únicos.

## Registro de fontes

- Impeccable: https://subclaude.com/slop/
- Sailop: https://www.sailop.com/blog/ai-slop-encyclopedia
- Herbert Labs skill: https://github.com/Herbert-Labs/vibecoded-design-tells/blob/main/skill/SKILL.md
- Herbert Labs tells: https://github.com/Herbert-Labs/vibecoded-design-tells/blob/main/skill/references/tells.md
- Unslop UI TELLS: https://github.com/claudiusararu/unslop-ui-skill/blob/main/TELLS.md

---
**Inventário gerado:** Sailop 87 · Impeccable 37 · Herbert-Labs 13 · complementos 35 · paletas 12.

---

## G. Expansão por pesquisa web — novos sinais não explicitados na edição original

**Pesquisa complementar:** 29/10/2026. Os identificadores `NX-001` em diante descrevem sinais específicos adicionais encontrados em fontes externas e confrontados com os títulos e descrições do arquivo original. Esta seção **não** renomeia nem reconta as 87 entradas Sailop ou as 37 Impeccable. Relações parciais com padrões já existentes são explicadas em cada item.

**Leitura rigorosa:** isto é um catálogo de *indícios de design genérico* e de *falhas de qualidade*; nenhuma regra isolada comprova uso de IA. Registre sempre local, impacto, evidência visual/DOM, ambiente e exceções de marca. O peso 'Alta' indica prioridade de correção quando o problema é confirmado no contexto, não probabilidade de autoria por IA.

**Novos conjuntos de evidência:** além dos três catálogos iniciais, esta rodada consultou SiteBlob (pesquisa-piloto em 131 páginas atribuídas a builders de IA e 10 controles, sem generalização populacional), Falia (análise histórica), SlopFix (34 checks), Design Slop, antislop-master, Web AI Slop e diretrizes técnicas Google Chrome e Google Search.

### G.1 Composição, superfícies e paleta

#### NX-001 — Editorial de jornal sem justificativa
- **Evidência/detecção:** Seções densas em colunas, réguas finas, cantos totalmente quadrados e tipografia de jornal aplicados a qualquer negócio.
- **Correção sugerida:** Usar estrutura editorial apenas quando leitura, conteúdo e marca sustentarem a estética.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Não equivale ao beige editorial: aqui a assinatura é a composição de jornal.
- **Fonte:** [FALIA](https://falia.co/en/insights/web-design/spot-ai-built-website/).

#### NX-002 — Serifa de alto contraste com destaque terracota
- **Evidência/detecção:** Hero com grande título serifado, texto de contraste elevado e único acento terracota semelhante ao branding de ferramentas de IA.
- **Correção sugerida:** Validar o par tipografia/cor contra o brand book e os concorrentes; não substituir por outro preset.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Diferente de P09–P12: avalia o par tipográfico específico, não o laranja sozinho.
- **Fonte:** [FALIA](https://falia.co/en/insights/web-design/spot-ai-built-website/).

#### NX-003 — Separadores com ponto médio como template
- **Evidência/detecção:** Metadados, categorias ou detalhes da página sempre separados por “·”, sem necessidade editorial ou semântica.
- **Correção sugerida:** Definir hierarquia e separadores apropriados à densidade real e ao idioma.
- **Prioridade contextual:** Baixa.
- **Por que é adicional:** Mais específico que eyebrow ou monospace genéricos.
- **Fonte:** [FALIA](https://falia.co/en/insights/web-design/spot-ai-built-website/).

#### NX-004 — Seta automática no fim de todos os links
- **Evidência/detecção:** Links e botões recebem → decorativo indiscriminadamente, inclusive onde não há indicação real de avanço.
- **Correção sugerida:** Reservar ícones direcionais para ações que mudam contexto ou navegação.
- **Prioridade contextual:** Baixa.
- **Por que é adicional:** Não consta como assinatura isolada em 87+37+Unslop.
- **Fonte:** [FALIA](https://falia.co/en/insights/web-design/spot-ai-built-website/).

#### NX-005 — Borda espessa combinada com cantos arredondados
- **Evidência/detecção:** Cards/callouts com borda ≥2px mais arredondamento, repetidos como padrão sem necessidade funcional.
- **Correção sugerida:** Preferir espaço, divisores finos e superfícies sólidas; preservar exceções intencionais como brutalismo e foco.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Vai além de “rounded everything” e bordas de acento lateral.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-006 — Borda, sombra, tint e glow acumulados no mesmo elemento
- **Evidência/detecção:** Card carrega simultaneamente contorno, sombra, fundo tingido e brilho, sem separar funções.
- **Correção sugerida:** Escolher apenas o tratamento necessário para hierarquia, estado ou elevação.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Empilhamento de tratamentos não estava explicitado como conjunto.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-007 — Cartões brancos sobre fundo cinza por inércia
- **Evidência/detecção:** Todas as seções viram cartões brancos sobre canvas cinza claro sem diferenciação de níveis.
- **Correção sugerida:** Agrupar por alinhamento/divisores; usar cartão apenas para entidades realmente independentes.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Não é só “cards dentro de cards”; identifica receita de superfícies.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-008 — Alternância mecânica de fundos seção a seção
- **Evidência/detecção:** Branco → cinza → branco → cor repetido com frequência fixa, sem relação com mudança de contexto.
- **Correção sugerida:** Organizar o ritmo pelo conteúdo, narrativa, contrastes e agrupamentos reais.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Diferente de mesmo padding/mesmo gap: sinal cromático estrutural.
- **Fonte:** [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md).

#### NX-009 — Hero 100vh vazia
- **Evidência/detecção:** Hero ocupa toda a altura da janela com título e botão, mantendo preço, demonstração ou informação central abaixo da dobra.
- **Correção sugerida:** Dimensionar a hero pelo conteúdo e antecipar evidências úteis.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Não é sinônimo de “hero centralizada”.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md); [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md).

#### NX-010 — Excesso de padrões de grid no background
- **Evidência/detecção:** Malhas low-poly triangulares, redes de partículas ou blueprint aplicados como decoração tecnológica padrão.
- **Correção sugerida:** Remover se não carregarem informação ou identidade; usar diagrama real se necessário.
- **Prioridade contextual:** Baixa.
- **Por que é adicional:** Complementa aurora/blobs e grade pontilhada, mas cobre rede/low-poly.
- **Fonte:** [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md); [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

### G.2 Tipografia e conteúdo

#### NX-011 — Headline com tríade de adjetivos desconectados
- **Evidência/detecção:** Título como “Rápido. Seguro. Inteligente.” repetido em três palavras sem evidências.
- **Correção sugerida:** Substituir por uma promessa verificável, com público e benefício específico.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Não é apenas buzzword isolada: é uma construção sintática.
- **Fonte:** [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md); [SLOPFIX](https://slopfix.getbags.app/checklist).

#### NX-012 — Oferta genérica “para X ou Y, funciona para todos”
- **Evidência/detecção:** Texto tenta incluir públicos incompatíveis em uma única frase sem detalhar necessidades específicas.
- **Correção sugerida:** Segmentar públicos e exemplos de uso reais em vez de slogan de abrangência.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Padrão de voz não especificado no catálogo anterior.
- **Fonte:** [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md).

#### NX-013 — Vocabulário do produto inconsistente entre seções
- **Evidência/detecção:** O mesmo recurso ou entidade recebe nomes diferentes na hero, FAQ, pricing, formulário e dashboard.
- **Correção sugerida:** Definir glossário; revisar textos de ponta a ponta com nomes reais de produto.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Erro de coerência distinto de copy abstrata.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-014 — Restrições e custos escondidos pela composição
- **Evidência/detecção:** Página comunica benefícios mas omite preço aplicável, limitações, pré-requisitos, exceções e público não adequado.
- **Correção sugerida:** Expor condições necessárias antes do CTA de conversão e próximos passos.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Vai além de estatística inventada: omissão material para decisão.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-015 — Narrativa empresarial autobiográfica automática
- **Evidência/detecção:** Seção Sobre segue sempre “percebemos um problema → fundamos → equipe apaixonada → missão” sem fatos concretos.
- **Correção sugerida:** Inserir histórico real, decisões, pessoas, marcos e documentos pertinentes.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Mais específico que missão genérica já citada.
- **Fonte:** [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md).

### G.3 Imagens e dados

#### NX-016 — Colagem de dashboard como papel de parede
- **Evidência/detecção:** Vários mini gráficos, números e tiles compõem textura decorativa sem produto operacional por trás.
- **Correção sugerida:** Usar captura autêntica de um fluxo, ou ilustração assumidamente abstrata sem simular dados.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Diferente do dashboard fictício individual da hero.
- **Fonte:** [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md).

#### NX-017 — Ilustração isométrica genérica de foguete ou laptop
- **Evidência/detecção:** Ícone/arte 3D isométrica mostra dispositivos, foguetes ou escritórios sem relação direta com o serviço.
- **Correção sugerida:** Trocar por fotografia, fluxo ou visual de produto relevante.
- **Prioridade contextual:** Baixa.
- **Por que é adicional:** O catálogo anterior cita esferas 3D, não a fórmula isométrica.
- **Fonte:** [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md).

#### NX-018 — Pessoas e produtos mudam entre imagens da mesma página
- **Evidência/detecção:** Galeria alterna aparência, iluminação, objetos ou proporções de um mesmo personagem/produto entre cenas.
- **Correção sugerida:** Estabelecer referência visual canônica, testar continuidade e preservar assets aprovados.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Diferente de artefato isolado em imagem sintética.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-019 — Stock photo escolhida só por harmonizar com a cor
- **Evidência/detecção:** Imagem parece coerente com a paleta, mas não demonstra o público, processo ou produto.
- **Correção sugerida:** Priorizar representatividade funcional e semântica antes do color grading.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Não é meramente foto de escritório genérica.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-020 — Fotografias com direção inconsistente
- **Evidência/detecção:** Uma seção usa luz dramática e ângulo editorial; outra tem foto plana de banco de imagem, sem coerência de enquadramento.
- **Correção sugerida:** Definir padrões de luz, crop, perspectiva e tratamento; comparar em mosaico apenas para QA.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Não era uma regra específica de direção fotográfica.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-021 — Texto alternativo descreve a IA e não a imagem
- **Evidência/detecção:** Alt como “imagem gerada por IA” ou “render 3D” onde seria necessário descrever o conteúdo/propósito.
- **Correção sugerida:** Usar alt funcional e factual; vazio em decoração; preservar a legenda quando método for relevante.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Difere de ausência genérica de rótulo acessível.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-022 — Gráfico inteiro ornamental sem relação com dados
- **Evidência/detecção:** Visualização de área, barras ou linhas sem eixo, unidade, fonte, período ou capacidade de resposta à pergunta.
- **Correção sugerida:** Exigir série/dado real, unidade, fonte e mensagem interpretável; caso contrário remover.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Mais amplo que sparklines decorativos de IM-006.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

### G.4 UX e estados

#### NX-023 — Ausência de estados de sucesso e permissões
- **Evidência/detecção:** A UI cobre o caminho feliz, mas não confirma sucesso ou representa explicitamente usuários sem autorização.
- **Correção sugerida:** Especificar estados success, unauthorized, forbidden, expired e recovery conforme produto.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** O antigo arquivo fala de botões fictícios, não cobre estados como conjunto.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md); [ANTISLOP-MASTER](https://raw.githubusercontent.com/muris11/anti-ai-slop/main/skills/antislop-master/SKILL.md).

#### NX-024 — Offline e perda de conexão sem tratamento
- **Evidência/detecção:** Uma aplicação conectada mantém loading infinito ou zera o conteúdo ao perder a rede.
- **Correção sugerida:** Definir modo desconectado, retry e persistência local quando apropriado.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Nova condição específica de operação.
- **Fonte:** [ANTISLOP-MASTER](https://raw.githubusercontent.com/muris11/anti-ai-slop/main/skills/antislop-master/SKILL.md).

#### NX-025 — Formulário com campos desnecessários
- **Evidência/detecção:** Cadastro solicita informações que não servem ao fluxo, simulando um formulário completo de template.
- **Correção sugerida:** Solicitar apenas dados necessários e explicar campos obrigatórios.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Não equivale à estilização visual dos formulários.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-026 — Erro sem instrução de recuperação
- **Evidência/detecção:** Mensagens como “Ocorreu um erro” não informam próxima ação, campo afetado ou canal de suporte.
- **Correção sugerida:** Apresentar mensagem contextual, tentativa de novo envio, preservação dos dados e contato quando preciso.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Mais específico que “erro silencioso”.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md); [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md).

#### NX-027 — Navegação do navegador Voltar quebra a tarefa
- **Evidência/detecção:** Voltar abandona modal/etapa de checkout de forma inesperada, apaga dados ou leva a rota inválida.
- **Correção sugerida:** Testar histórico, deep links, navegação progressiva e restauração de estado.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Falha de fluxo não citada na versão original.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-028 — Ação destrutiva sem desfazer ou confirmação contextual
- **Evidência/detecção:** Exclusão ou edição irreversível é disparada imediatamente, sem feedback nem undo quando cabível.
- **Correção sugerida:** Projetar confirmação proporcional ao risco, reversão quando possível e feedback visível.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Diferente de excesso de confirmação já discutido.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-029 — Cadastro obrigatório antes de demonstrar valor
- **Evidência/detecção:** Login impede acesso a informações públicas suficientes sobre preço, propósito e requisitos.
- **Correção sugerida:** Exibir amostra legítima de valor e condições antes de solicitar conta, quando aplicável.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Novo defeito de decisão/conversão.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-030 — Informações críticas escondidas só em tooltip
- **Evidência/detecção:** Preço, requisito, restrição ou estado fica inacessível sem hover/foco específico.
- **Correção sugerida:** Expor informações essenciais diretamente; reservar tooltip para ajuda suplementar.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Diferente de navegação hover-only.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-031 — Indicador de progresso artificial
- **Evidência/detecção:** Barrinha cresce sem evento real, ou o usuário espera uma animação arbitrária para concluir algo simples.
- **Correção sugerida:** Vincular progresso a etapas medíveis ou usar estado indeterminado honesto.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Novo sinal de interação simulada.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-032 — Carousel com autoplay não interrompível
- **Evidência/detecção:** Conteúdo começa a deslizar sem opção de parar/controle por teclado, escondendo informação essencial.
- **Correção sugerida:** Permitir pausar quando necessário e acesso manual às informações; considerar lista estática.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Marquee genérico já coberto, mas aqui o problema é controle.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

### G.5 Responsividade e acessibilidade

#### NX-033 — Tablet ignorado apesar de mobile/desktop aprovados
- **Evidência/detecção:** Em larguras intermediárias surgem vazios estranhos, cards apertados e navegação desconectada.
- **Correção sugerida:** Homologar 768–1024px e breakpoints baseados no conteúdo, não só no dispositivo.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** O catálogo antigo exige prints, mas não descreve o defeito tablet.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-034 — Orientação horizontal rompe a interface
- **Evidência/detecção:** Paisagem em smartphone/tablet oculta CTA, modal ou menu devido a medidas fixas.
- **Correção sugerida:** Testar landscape e alturas reduzidas com scroll e safe areas.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Novo caso de viewport.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-035 — Modal briga com teclado virtual
- **Evidência/detecção:** Ao focar input no celular, modal excede a área visível, esconde botões ou impede o scroll.
- **Correção sugerida:** Adaptar viewport dinâmico, focus/scroll-into-view e posicionamento do CTA.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Complementa modal abuse sem duplicá-lo.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-036 — Estado comunicado somente por cor
- **Evidência/detecção:** Erro, sucesso, status de pedido ou severidade usam cor sem rótulo ou texto acessível.
- **Correção sugerida:** Usar texto, rótulo, símbolo semântico e contraste além da cor.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Não equivale apenas a baixo contraste.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-037 — Ordem de foco diferente da ordem visual
- **Evidência/detecção:** Tab/Shift+Tab pula regiões ou segue DOM incompatível com a sequência vista na tela.
- **Correção sugerida:** Alinhar DOM e visual; testar teclado real em todos os estados.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** A falta de focus-visible já é coberta, mas ordem não.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-038 — Foco não restaurado ao fechar diálogo
- **Evidência/detecção:** Ao fechar modal o foco some, retorna para o topo ou cai em elemento oculto.
- **Correção sugerida:** Implementar gestão de foco na abertura/fechamento e preservar elemento disparador.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Distinto de falta de aria-label.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-039 — Zoom de texto provoca cortes e perda de ações
- **Evidência/detecção:** Ampliação do navegador, fonte do SO ou idioma com strings longas quebra altura fixa e esconde botões.
- **Correção sugerida:** Testar zoom e conteúdo real traduzido; usar layout fluido.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Distinto de px-4 responsivo e overflow mobile padrão.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-040 — ARIA decorativo sem comportamento correspondente
- **Evidência/detecção:** Componente anuncia papel/estado de controle acessível, mas não permite operar com teclado ou leitor de tela.
- **Correção sugerida:** Preferir HTML nativo; sincronizar ARIA, interação e estado real.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** O catálogo antigo cobre ausência de ARIA, não ARIA incorreto.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

### G.6 Código e build

#### NX-041 — HTML/CSS inline concentrado sem estrutura
- **Evidência/detecção:** Styles embutidos numerosos e trechos de marcação estrutural replicados deixam a página difícil de evoluir.
- **Correção sugerida:** Extrair componentes/tokens e inspecionar DOM final, sem exigir externalizar todo estilo inline legítimo.
- **Prioridade contextual:** Média.
- **Por que é adicional:** SiteBlob destaca o sinal estrutural combinado.
- **Fonte:** [SITEBLOB](https://siteblob.com/blog/we-scanned-131-ai-built-websites-ai-look-wasnt-the-tell).

#### NX-042 — Componentes chamados Section1/Card2 sem domínio
- **Evidência/detecção:** Nomes genéricos permanecem depois da geração, sem revelar responsabilidade ou conteúdo.
- **Correção sugerida:** Usar nomes de domínio, responsabilidades e design-system.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Mais específico que “component duplication”.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-043 — Framework/rotas placeholder publicados
- **Evidência/detecção:** Title “React App”, rotas locais ou links de exemplo e variáveis de ambiente falsas chegam à produção.
- **Correção sugerida:** Verificar metadata, rotas, environment e urls de integração em build de produção.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Não apenas conteúdo Lorem ipsum no texto.
- **Fonte:** [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md); [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-044 — Importações ou endpoints inventados
- **Evidência/detecção:** Build depende de pacote inexistente ou chama rota/API que não existe, embora mockup esteja pronto.
- **Correção sugerida:** Executar build, smoke tests, network inspector e testes de contrato.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Mais específico que placeholder integration.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-045 — Regras !important e z-index extremos em cascata
- **Evidência/detecção:** Z-index 9999/99999 e !important se multiplicam para remendar overlays sem sistema de camadas.
- **Correção sugerida:** Criar escala de camadas, corrigir stacking contexts e especificidade na origem.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Diferente de tokens de espaçamento/cores.
- **Fonte:** [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md).

#### NX-046 — Atraso artificial com setTimeout em vez de estado real
- **Evidência/detecção:** Interface usa temporizador para simular fetch, sucesso ou conclusão, confundindo o estado da operação.
- **Correção sugerida:** Vincular UI ao resultado real da promise e disponibilizar erro/timeout efetivo.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Novo cheiro de implementação funcional.
- **Fonte:** [WEB-AI-SLOP](https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md).

#### NX-047 — Tratador de erro amplo mascara defeito de integração
- **Evidência/detecção:** Catch retorna dado fake/array vazio e a interface diz estar bem mesmo com API indisponível.
- **Correção sugerida:** Sinalizar erro correto, registrar contexto e separar fallback explícito do comportamento normal.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Complementa erro silencioso mas detalha falso sucesso.
- **Fonte:** [FALIA](https://falia.co/en/insights/web-design/spot-ai-built-website/).

#### NX-048 — Código inchado para efeito visual simples
- **Evidência/detecção:** Biblioteca JS, export plugin ou runtime inteiro carregado só para efeito estático simples.
- **Correção sugerida:** Preferir CSS/SVG nativo quando suficientes e remover dependências redundantes.
- **Prioridade contextual:** Média.
- **Por que é adicional:** Mais específico que dependências excessivas genéricas.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

### G.7 Performance, SEO e confiança

#### NX-049 — Hero com loading lazy atrasa o LCP
- **Evidência/detecção:** Imagem principal visível recebe loading="lazy" ou só é descoberta depois da execução JS.
- **Correção sugerida:** Deixar a mídia de LCP descoberta cedo e priorizada; lazy-loading apenas quando abaixo da dobra.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Defeito técnico concreto verificável, não julgamento visual.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md); [CHROME](https://developer.chrome.com/docs/modern-web-guidance/guides/performance/performance).

#### NX-050 — Layout shift por mídia/font sem dimensões
- **Evidência/detecção:** Fonte, imagem ou widget desloca a página após primeiro paint; botões mudam de posição.
- **Correção sugerida:** Reservar medidas/aspect-ratio, controlar fontes e verificar CLS.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Não aparecia como regra específica de estabilidade visual.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md); [CHROME](https://developer.chrome.com/docs/modern-web-guidance/guides/performance/performance).

#### NX-051 — Mídia decorativa bloqueia conteúdo significativo
- **Evidência/detecção:** Vídeo de fundo, partículas e animações pesadas competem com LCP e interatividade inicial.
- **Correção sugerida:** Priorizar conteúdo essencial; postergar decorações e adaptar a capacidade do dispositivo.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Diferente de fade-up repetitivo sem propósito.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md); [CHROME](https://developer.chrome.com/docs/modern-web-guidance/guides/performance/performance).

#### NX-052 — Metadados ou Open Graph não correspondem à página
- **Evidência/detecção:** Canonical, imagem OG, title, descrição ou dados estruturados apontam para outro produto/rota.
- **Correção sugerida:** Verificar cada rota renderizada e templates dinâmicos com dados reais.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Diferente de title e metadata ausentes.
- **Fonte:** [SITEBLOB](https://siteblob.com/blog/we-scanned-131-ai-built-websites-ai-look-wasnt-the-tell); [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-053 — Páginas de confiança superficiais ou ausentes
- **Evidência/detecção:** Site comercial omite informação aplicável de contato, entrega, troca, reembolso, identidade do operador.
- **Correção sugerida:** Exibir as políticas realmente exigidas pelo contexto e fluxo comercial, com termos corretos.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Nova dimensão trust surface; considerar leis aplicáveis.
- **Fonte:** [SITEBLOB](https://siteblob.com/blog/we-scanned-131-ai-built-websites-ai-look-wasnt-the-tell); [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-054 — Provas de urgência ou escassez inventadas
- **Evidência/detecção:** Contadores regressivos, “X pessoas comprando agora” ou badge de disponibilidade não possuem backend real.
- **Correção sugerida:** Conectar afirmações a eventos medidos ou removê-las.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Vai além de depoimentos e métricas fictícias.
- **Fonte:** [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

#### NX-055 — Conteúdo massivo SEO sem valor novo
- **Evidência/detecção:** Centenas de páginas quase iguais, geradas para capturar termos de busca sem resolver a intenção do leitor.
- **Correção sugerida:** Publicar páginas originais, úteis e com finalidade clara; verificar política de abuso em escala.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Novo requisito de publicação; política não equivale a “todo texto IA é spam”.
- **Fonte:** [GOOGLE-SEARCH](https://developers.google.com/search/docs/essentials/spam-policies).

#### NX-056 — Página funcional apenas na captura, sem QA renderizado
- **Evidência/detecção:** Há prints bonitos, mas network console/links/estados em produção ou múltiplos viewports falham.
- **Correção sugerida:** Exigir execução em navegador real, capturas comparativas e evidência de rotas, interações e erros.
- **Prioridade contextual:** Alta.
- **Por que é adicional:** Refina princípio geral do arquivo como padrão de auditoria independente.
- **Fonte:** [SITEBLOB](https://siteblob.com/blog/we-scanned-131-ai-built-websites-ai-look-wasnt-the-tell); [DESIGN-SLOP](https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md).

### G.8 Duas paletas específicas de 2026 (novos exemplos, não cores proibidas)

| ID | Nome | Referência cromática operacional | Critério | Fonte |
|---|---|---|---|---|
| P13 | **Terracotta Editorial** | `#F5F0E9` `#D8B7A1` `#C46B45` `#743D2D` `#1E1C19` | Observar **combinação** de hero serifado, acento terracota e template editorial; não penalizar cor isolada. | [Falia](https://falia.co/en/insights/web-design/spot-ai-built-website/) |
| P14 | **Vermilion on Near-Black** | `#090909` `#242424` `#E34234` `#FF6A3D` `#FAF7F4` | Avaliar acento ácido monocromático em fundo muito escuro como default, quando não há brand rationale. | [Falia](https://falia.co/en/insights/web-design/spot-ai-built-website/) |

Esses HEX são **exemplos reconstruídos para avaliação**, não amostras oficiais extraídas de ferramentas de IA. A cor laranja da marca, quando aprovada, continua válida.

### G.9 Matriz de validação adicional

| Etapa | Instrumentação proposta | Prova mínima |
|---|---|---|
| Camada visual | captura desktop/tablet/mobile, comparação de identidade | imagem da tela real + anotações localizadas |
| Estrutural | inspeção DOM, CSS computado e semântica | seletor, nó, valores medidos e casos de quebra |
| Fluxo | Playwright ou navegador operado de ponta a ponta | clique, estado, resposta e evidência de erro/recuperação |
| Acessibilidade | teclado real, zoom, labels, foco, contraste | fluxo tab/shift-tab, diálogo e mensagens de campo |
| Conteúdo | conferência com dados/documentação do produto | origem, contexto, data, limitações e consistência de termos |
| Performance | DevTools/Lighthouse + métricas de campo quando disponíveis | LCP, CLS, recursos críticos e redes móveis simuladas |
| Produção | build de release, rotas, API, SEO e confiança | URL final, status HTTP, metadata e políticas aplicáveis |

### G.10 Fontes adicionais verificadas

- **FALIA:** https://falia.co/en/insights/web-design/spot-ai-built-website/
- **DESIGN-SLOP:** https://github.com/wpgaurav/design-slop/blob/main/references/slop-patterns.md
- **SITEBLOB:** https://siteblob.com/blog/we-scanned-131-ai-built-websites-ai-look-wasnt-the-tell
- **WEB-AI-SLOP:** https://github.com/sahilkargutkar/web-ai-slop/blob/master/docs/detecting-ai-slop.md
- **ANTISLOP-MASTER:** https://raw.githubusercontent.com/muris11/anti-ai-slop/main/skills/antislop-master/SKILL.md
- **SLOPFIX:** https://slopfix.getbags.app/checklist
- **GOOGLE-SEARCH:** https://developers.google.com/search/docs/essentials/spam-policies
- **CHROME:** https://developer.chrome.com/docs/modern-web-guidance/guides/performance/performance

> Nota de metodologia: fontes de ferramentas de detecção costumam descrever heurísticas próprias, não consenso científico. O estudo SiteBlob reporta um resultado exploratório de amostra pequena; não generalize percentuais para a web. Diretrizes Google Chrome tratam de performance técnica, enquanto a política Google Search trata de conteúdo abusivo — não identificam uso de IA isoladamente.
