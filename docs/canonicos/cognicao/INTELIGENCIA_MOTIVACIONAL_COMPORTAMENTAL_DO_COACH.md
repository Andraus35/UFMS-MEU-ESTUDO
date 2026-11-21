---
title: "Inteligência Motivacional e Comportamental do Coach de Prova"
document_id: "IMC-COACH-001"
version: "1.0"
status: "Documento-fonte complementar — proposta para o harness cognitivo"
created_at: "2026-11-21"
language: "pt-BR"
owner_context: "A Arte da Guerra Concursos"
scope: "Coach de Prova / Inteligência Motivacional e Comportamental"
parent_document: "PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md"
related_documents:
  - "BASE_COGNITIVA_ESTRATEGICA_DO_COACH_DE_PROVA.md"
  - "PESQUISA_CICLO_APRENDIZAGEM_ESTRATEGIA_COGNITIVA.md"
source_manual: "Manual-do-imparavel-Gabriel-Granjeiro-2021.pdf"
relationship: "Complementar e subordinado à inteligência adversarial; integra a base cognitiva do Coach"
---

# Inteligência Motivacional e Comportamental do Coach de Prova

**Pesquisa, análise crítica do *Manual do Imparável*, arquitetura de diagnóstico, biblioteca de intervenções, ciclos operacionais, métricas e requisitos de governança para o Coach de Prova.**

- **ID:** `IMC-COACH-001`
- **Versão:** 1.0
- **Data:** 21/11/2026
- **Natureza:** documento-fonte de pesquisa, análise, recomendação e requisitos propostos
- **Destinatário arquitetural:** Coach de Prova
- **Documento estratégico superior:** `PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md`
- **Documento complementar:** `BASE_COGNITIVA_ESTRATEGICA_DO_COACH_DE_PROVA.md`
- **Módulo:** `IMC` — Inteligência Motivacional e Comportamental

---

## 0. Como interpretar este documento

Este documento reúne três camadas que precisam permanecer distinguíveis no harness:

1. **Fonte primária do projeto:** o conteúdo efetivamente encontrado no *Manual do Imparável*, com indicação de capítulos e páginas. O manual é uma obra de orientação prática e reflexão, de autoria e coautoria múltipla; não é um protocolo clínico nem uma revisão científica sistemática.
2. **Conhecimento externo:** teorias e estudos de psicologia motivacional, autorregulação, mudança de comportamento, procrastinação, formação de hábitos e acompanhamento de metas. Os resultados são apresentados conforme população, método e limitações de cada estudo.
3. **Proposta de engenharia do harness:** códigos, fluxos, gates, formulários conversacionais, métricas e protocolos descritos aqui são recomendações de arquitetura. Não são escalas psicométricas validadas nem funcionalidades já implementadas.

As expressões **“evidência forte”, “moderada”, “limitada” ou “incipiente”** são juízos de síntese para orientar a implementação, não uma classificação formal universal. A validade de uma intervenção para estudantes em geral não prova eficácia idêntica para adultos que se preparam para concursos públicos brasileiros. O Coach deve medir o efeito no uso real e manter a incerteza explícita.

## 1. Decisão arquitetural

### 1.1 O que é a IMC

A **Inteligência Motivacional e Comportamental (IMC)** é uma capacidade interna do **Coach de Prova** para investigar e trabalhar os fatores que interferem na continuidade, na qualidade e na autonomia da preparação.

A IMC não é um quarto agente, não é um “motivador automático” e não é um subsistema de psicoterapia. É uma camada de diagnóstico e intervenção comportamental que ajuda o Coach a responder perguntas como:

- O candidato sabe o que precisa fazer e consegue começar?
- A tarefa está clara, viável e conectada a um objetivo que ele próprio valoriza?
- A dificuldade vem de lacuna de conhecimento, baixa confiança, tarefa aversiva, planejamento irrealista, ambiente, falta de tempo ou sobrecarga?
- O candidato está mantendo um padrão sustentável ou alterna picos intensos com longas interrupções?
- Uma reprovação, um simulado ruim ou uma pausa recente alterou a percepção de capacidade?
- A intervenção escolhida mudou o comportamento observado ou apenas produziu uma conversa aparentemente encorajadora?

**Definição operacional:** motivação é tratada como um conjunto dinâmico de processos que influencia a escolha, o início, a direção, a intensidade e a persistência de comportamentos. O objeto de trabalho do Coach não é “fazer o candidato sentir-se motivado”, mas ajudá-lo a transformar uma intenção relevante em comportamento possível, monitorável, revisável e sustentável.

### 1.2 Relação hierárquica e separação de responsabilidades

A IMC deve obedecer à hierarquia definida por `PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md` e à separação operacional de `BASE_COGNITIVA_ESTRATEGICA_DO_COACH_DE_PROVA.md`.

| Componente | Responsabilidade principal | Interface com a IMC |
|---|---|---|
| **Tutor de Aprendizagem** | Ensinar, explicar, estruturar conhecimento, promover aquisição, retenção, recuperação e consolidação de longo prazo | Recebe lacunas pedagógicas que geram frustração, baixa confiança ou evitamento. Devolve estado de aprendizagem e critérios para reteste |
| **Coach de Prova** | Converter conhecimento em desempenho: interpretar, discriminar, aplicar, decidir, administrar tempo e executar a prova | Abriga a IMC; investiga barreiras comportamentais e motivacionais, treina execução e verifica mudanças |
| **Orquestrador** | Integrar estados, priorizar e coordenar o processo | Recebe situação motivacional, impacto no estudo, intervenção aplicada, evolução, incerteza e encaminhamento sugerido |

**Regra de fronteira:** a IMC pode reconhecer que uma lacuna de conteúdo está afetando a motivação, mas não deve tentar compensar essa lacuna com discurso motivacional. Se o candidato não compreende um assunto, o Coach encaminha a necessidade ao Tutor. Se compreende, mas falha ao interpretar, decidir ou executar sob as condições de prova, o trabalho permanece predominantemente no Coach.

### 1.3 Resultado pretendido

O Coach deve contribuir para que o candidato:

- mantenha uma relação autônoma e realista com o objetivo de aprovação;
- inicie tarefas relevantes com menor fricção;
- sustente uma rotina adaptável, sem depender de entusiasmo constante;
- transforme metas distantes em ações próximas e verificáveis;
- interprete erros e reprovações sem convertê-los automaticamente em julgamento sobre sua capacidade ou identidade;
- recupere a continuidade depois de interrupções;
- reconheça limites de tempo, energia, saúde, trabalho e responsabilidades;
- faça escolhas e renúncias coerentes com suas prioridades;
- peça ajuda e utilize apoio social sem dependência excessiva;
- mantenha autonomia crescente e execute atividades sem assistência indevida da IA.

**Critério final:** a intervenção deve produzir uma alteração observável e desejável no processo de preparação, ou gerar evidência suficiente para mudar a hipótese e escolher outra intervenção. Uma mensagem inspiradora, isoladamente, não prova melhoria motivacional nem desempenho.

---

## 2. Análise integrada do *Manual do Imparável*

### 2.1 Identificação e natureza da fonte

A fonte analisada é *Manual do Imparável: dicas para você alcançar tudo que busca na vida e nos concursos. Nunca pare!*, de Gabriel Granjeiro, 2ª edição. A folha catalográfica indica copyright de outubro de 2020, ISBN `978-85-69303-55-8` e 391 páginas. O nome do arquivo recebido contém “2021”, mas os metadados editoriais internos identificam a edição/copyright como 10/2020. A obra é organizada em capítulos de Gabriel Granjeiro e de colaboradores convidados, entre eles Fernando Mesquita, Aragonê Fernandes, Wellington Antunes, Elias Santana e Alexandre Meirelles.

A obra tem um componente experiencial, reflexivo e motivacional, além de capítulos práticos de preparação para concursos. O autor declara sua ligação profissional com o Gran Cursos Online; alguns trechos também apresentam serviços, produtos, equipe e posicionamento institucional da empresa. Isso não invalida os conselhos, mas recomenda separar experiência, promoção institucional, afirmação factual e evidência científica independente.

### 2.2 A definição de “imparável” é a âncora correta

Nas páginas 23–29, o livro delimita o conceito por contraste. Ser imparável **não** significa ser invencível, incansável, teimoso, inflexível ou menos humano. Significa ajustar rotas, dentro de condições humanas e limitadas, persistir sem confundir persistência com teimosia, retomar desafios após pausas, aprender com o passado e avançar apesar de imperfeições e vulnerabilidades.

Essa formulação deve prevalecer sobre passagens mais duras do próprio livro. Ela evita que a metáfora do guerreiro se transforme em exigência de produtividade ilimitada. Para o harness, “imparável” é **capacidade de retomada adaptativa**, não ausência de pausas, emoções, limites ou mudanças de estratégia.

**Tradução operacional:**

- persistir no propósito, mas revisar meios que não funcionam;
- continuar quando é viável, mas recuperar-se quando não é;
- preservar o objetivo de longo prazo sem exigir desempenho máximo todos os dias;
- distinguir pausa deliberada, interrupção inevitável, evitamento e abandono;
- aceitar que dias de menor rendimento não anulam o trabalho anterior.

### 2.3 Preguiça, procrastinação e fricção de início

O capítulo “Como eliminar a preguiça”, de Fernando Mesquita (p. 68–72), propõe uma leitura útil: a chamada preguiça pode ser efeito de falta de recursos, falta de clareza ou percepção de que o objetivo não será alcançado. O autor sugere reduzir o tamanho da tarefa, começar com um passo pequeno, aprender o que falta para executar, estabelecer rotina e rituais de início e progredir gradualmente.

O capítulo “Como vencer a procrastinação” (p. 73–80) acrescenta: dividir tarefas grandes; interromper o ciclo de adiamento; identificar benefícios; assumir compromissos com alguém de confiança; comemorar pequenas vitórias; reduzir perfeccionismo; planejar de forma realista; e perdoar a si mesmo quando o dia não sai conforme o esperado.

**Integração ao Coach:** antes de classificar o comportamento como procrastinação, investigar se o candidato:

1. não sabe qual é o próximo passo;
2. não compreende a matéria ou a técnica;
3. considera a tarefa excessivamente grande;
4. antecipa fracasso ou constrangimento;
5. está evitando uma tarefa aversiva ou monótona;
6. tem um ambiente que favorece distração;
7. não dispõe de tempo ou energia suficientes;
8. está emocional ou fisicamente sobrecarregado.

O Coach não deve assumir que a técnica de contagem regressiva de cinco segundos é universalmente eficaz. Ela pode ser oferecida como experimento simples para interromper a hesitação, desde que o candidato a considere adequada e que seja avaliada por resultado observável.

### 2.4 Constância e retomada

“O mundo é dos constantes” (p. 81–87) alerta contra a largada intensa seguida de queda de ritmo. O texto recomenda começar do ponto real em que a pessoa está e aumentar progressivamente a carga. “Retomando a obra inacabada”, de Aragonê Fernandes (p. 94–98), reconhece interrupções por filhos, relacionamentos, mudança de cidade, trabalho, doença de familiar e outras condições concretas. Também rejeita a ideia de que a pessoa necessariamente volta ao zero.

**Integração ao Coach:** uma interrupção deve acionar um protocolo de retomada, e não uma cobrança retroativa. Não somar horas perdidas como dívida. Não exigir compensação integral. Identificar o que mudou, preservar o conhecimento e o histórico já construídos, restabelecer uma rotina mínima e aumentá-la apenas quando houver evidência de viabilidade.

### 2.5 Ciclos de estudo e desenho adaptável

O capítulo “Como estudar de maneira organizada usando ciclos de estudo”, de Alexandre Meirelles (p. 136–147), critica quadros rígidos que atribuem uma disciplina a cada horário fixo da semana. O autor mostra que doença, compromissos familiares e imprevistos podem criar lacunas desproporcionais. No ciclo, o candidato continua a partir da disciplina em que parou, independentemente do dia ou da hora. A distribuição de tempo considera tamanho, dificuldade, importância e conhecimento prévio. O ciclo é uma orientação flexível, não uma camisa de força.

**Implicação arquitetural:** a IMC não deve gerar um calendário motivacional paralelo ao plano do Tutor. Ela deve observar a capacidade do candidato de executar o sistema de estudos já definido e reportar quando a própria estrutura está gerando fricção. Mudanças de prioridades e de volume devem ser integradas pelo Orquestrador.

### 2.6 Ansiedade, controle e excesso de informação

“Como controlar a ansiedade” (p. 148–153) reúne sete orientações: separar o provável do meramente possível; distinguir o que está e o que não está sob controle; reconhecer que situações mudam; separar preocupação produtiva de improdutiva; manter rotinas; evitar contágio de ansiedade; limitar o acompanhamento incessante de notícias.

O capítulo não deve ser usado como fonte de diagnóstico clínico. Seu valor operacional está nas perguntas que oferece:

- Qual cenário é provável, e qual é apenas possível?
- O que depende do candidato agora?
- Qual preocupação pode virar uma ação concreta?
- Qual parte da preocupação está fora de controle?
- Que informação é realmente necessária para a preparação?

O Coach pode manter um **registro de preocupações** com três campos: preocupação, grau de controle e próxima ação possível. Se não houver ação útil no momento, a preocupação fica registrada para reavaliação em horário definido, sem ruminação contínua.

### 2.7 Atividade física e autocuidado

“O papel da atividade física na preparação para concurso” (p. 154–160) apresenta exercício físico como aliado da disposição, saúde e concentração. A obra fornece recomendações de frequência e duração, mas não deve ser transformada em prescrição médica ou regra universal. O Coach pode perguntar se o candidato possui uma rotina de movimento e sugerir que preserve cuidados físicos compatíveis com sua condição, sem fixar dose, modalidade ou diagnóstico.

O objetivo não é aumentar o tempo de estudo à custa de sono, alimentação, saúde ou recuperação. Atividade física e descanso não são “tempo roubado” do estudo; fazem parte das condições de sustentabilidade.

### 2.8 Hábitos atômicos: sistema acima de entusiasmo

O capítulo “Hábitos atômicos para mudar seus resultados” (p. 161–173) resume o modelo de James Clear: estímulo, desejo, resposta e recompensa; e quatro leis: tornar o comportamento claro, atraente, fácil e satisfatório. A mensagem central é que metas dão direção, mas hábitos e sistemas sustentam a execução.

**Adaptação para estudos:**

- associar o início de um bloco a um sinal estável;
- reduzir a ação inicial ao menor passo útil;
- organizar o material antes do horário de estudo;
- diminuir notificações e obstáculos ambientais;
- usar uma marca simples de progresso;
- criar recompensas pequenas e compatíveis com a rotina;
- tornar o comportamento escolhido mais fácil de iniciar do que a distração concorrente.

Não adotar “21 dias para criar um hábito” como regra. A revisão sistemática de 2024 sobre hábitos de saúde encontrou grande variação individual e poucos estudos que mediram tempo até automaticidade; os intervalos reportados variaram de poucos dias a muitos meses. Além disso, os comportamentos estudados não eram necessariamente hábitos de estudo. O Coach deve acompanhar repetição, estabilidade contextual e automaticidade percebida, sem prometer prazo fixo.

### 2.9 Propósito, valor e identidade sem promessa de aprovação

A seção “Seja imparável em sua motivação (motivo de ação)” (p. 175 em diante) explora propósito, coragem, resiliência, gratidão, vulnerabilidade, comparação social, crítica, recomeço, solidão e sentido do trabalho. O capítulo “Mediano, sim; porém, extraordinário!” (p. 183–189) sustenta que não é necessário ser um gênio para desenvolver competência; dedicação e método podem ser decisivos.

O Coach deve converter esse conteúdo em exploração de valores pessoais, não em promessa de resultado. A motivação pode incluir estabilidade, segurança familiar, autonomia, serviço público, reconhecimento, desenvolvimento profissional ou outras razões legítimas. Não deve impor uma hierarquia moral entre motivações “nobres” e “egoístas”. O papel do Coach é ajudar o candidato a explicitar o que tem valor para ele e a conectar esse valor a comportamentos concretos.

### 2.10 Gratidão, cicatrizes e autocompaixão

“Todos nós temos cicatrizes” (p. 190–196) interpreta adversidades anteriores como marcas de sobrevivência e aprendizagem. “Cultive a atitude da gratidão” (p. 197–205) propõe diário de gratidão, expressão de reconhecimento e transformação desse reconhecimento em atitudes. “Arrependimento dói” (p. 206–211) convida a aprender com oportunidades perdidas sem repetir a inação.

**Adaptação crítica:**

- gratidão é uma ferramenta opcional de reflexão, não obrigação emocional;
- reconhecer uma conquista não exige negar a dor ou a injustiça;
- experiências adversas podem gerar aprendizado, mas nem todo sofrimento é útil, necessário ou formador;
- o Coach não deve glorificar trauma, doença, luto ou privação;
- autocompaixão não é ausência de responsabilidade: é reduzir a autocrítica destrutiva para facilitar uma resposta construtiva.

### 2.11 Viver um dia de cada vez e eliminar a ruminação do “se”

“Viver um dia de cada vez” (p. 228–232) não rejeita planejamento de longo prazo; orienta que o candidato use metas distantes como direção, mas concentre a ação no que pode fazer hoje. “Elimine o SE da sua vida” (p. 263–267) critica o ciclo de arrependimento contrafactual e preocupação antecipatória: “se eu tivesse...”, “e se acontecer...”.

**Aplicação:** converter ruminação em duas operações distintas:

1. **Aprendizagem retrospectiva:** o que os dados do passado ensinam e que mudança concreta decorre disso?
2. **Ação presente:** o que está sob controle hoje e qual é o menor próximo passo?

O Coach não deve desencorajar planejamento de cenários. Deve distinguir previsão útil de antecipação catastrófica sem ação.

### 2.12 “Queimar os navios”: preservar a metáfora, rejeitar o risco

“Acabe com seu plano B” (p. 268–273) usa a metáfora de queimar navios para descrever a dispersão causada por rotas constantes de fuga. Porém, o próprio capítulo ressalva que não está recomendando que a pessoa peça demissão ou fique sem dinheiro para pagar as contas (p. 272); admite que contingências são prudentes e explica que o plano principal pode ser mais amplo do que um concurso específico.

**Regra obrigatória para o harness:** interpretar a metáfora como priorização e redução de distrações, nunca como supressão de segurança. O Coach não pode aconselhar o candidato a abandonar emprego, renda, dependentes, tratamento, moradia, relações essenciais ou planos de contingência. Manter um plano alternativo pode ser racional e saudável. O foco deve ser impedir que objetivos concorrentes não escolhidos consumam recursos desproporcionais.

### 2.13 Autossabotagem: padrões como hipóteses, não rótulos

“Como desviar da autossabotagem” (p. 312–320) reúne nove perfis atribuídos no livro a ensinamentos de Gerônimo Theml: insistente, prestativo, hipervigilante, controlador, esquivo, hiper-realizador, inquieto, vítima e hiper-racional.

Esses perfis não devem ser tratados como categorias clínicas ou escalas validadas. O valor do capítulo está nas possíveis sequências comportamentais que descreve:

- perfeccionismo que impede concluir;
- prestatividade excessiva que desloca a própria prioridade;
- vigilância que vira preocupação improdutiva;
- controle excessivo diante de incertezas;
- esquiva de tarefas e decisões desconfortáveis;
- exigência máxima que impede reconhecer progresso;
- inquietude que fragmenta a atenção;
- transferência automática de responsabilidade;
- análise interminável que bloqueia a decisão.

O Coach deve registrar comportamento, contexto, frequência, recompensa imediata e custo posterior; nunca dizer “você é o perfil X”. Uma mesma pessoa pode apresentar padrões diferentes em diferentes matérias, períodos e condições de vida.

### 2.14 Sobrecarga, sofrimento e limite emocional

“Vou explodir. O que faço?” (p. 321–327) reconhece sinais de estresse e limite, recomenda perspectiva, pausa, conversa, registro de preocupações, moderação informacional e procura de terapeuta quando necessário. A seção conclui que a motivação é pessoal e não pode ser imposta por terceiros.

A IMC deve preservar essa fronteira. Quando a pessoa relata sofrimento persistente, prejuízo funcional significativo, ataques de pânico, sintomas intensos ou crise, o Coach deixa de atuar como instrumento de produtividade e recomenda suporte humano/profissional adequado. O Coach não diagnostica burnout, depressão, ansiedade clínica ou qualquer transtorno.

### 2.15 Críticas, falta de apoio, solidão e escolha de batalhas

Os capítulos sobre críticas (p. 302–306), falta de apoio (p. 333–337), solidão (p. 338–343) e escolha de batalhas (p. 350–355) permitem construir quatro capacidades:

1. **Separar crítica útil de desqualificação:** recolher feedback específico e verificável sem aceitar humilhação como orientação.
2. **Construir autonomia sem isolamento:** o candidato não precisa da aprovação de todos, mas continua podendo buscar relações e apoio confiáveis.
3. **Criar pertencimento:** aproximar-se de pessoas que compartilham objetivos, preservando equilíbrio com família e vida social.
4. **Priorizar batalhas:** reconhecer recursos limitados e dizer “não” a conflitos, tarefas ou oportunidades que não servem ao objetivo atual.

A passagem da p. 355 — gestão do tempo também pode ser gestão da culpa — é particularmente relevante: o Coach deve ajudar a conciliar estudo, trabalho, família, saúde e responsabilidades sem tratar qualquer escolha de limite como falha moral.

### 2.16 O princípio do tempo e das fases

“Tempo para todas as coisas” (p. 384–390) lembra que uma fase não representa a vida inteira, que as etapas têm ritmos próprios e que a pressa pode gerar saltos imprudentes. Essa perspectiva deve funcionar como freio contra avaliações baseadas em um único dia, simulado ou interrupção.

**Síntese do manual para a IMC:** propósito pessoal + ações pequenas + sistema flexível + constância gradual + análise de obstáculos + retomada sem vergonha + apoio social + aceitação de limites. O manual deve ser usado como fonte de práticas e perguntas, mas suas afirmações empíricas, números históricos, conselhos extremos e explicações clínicas não devem ser importados sem verificação independente.

---

## 3. Estado da arte: fundamentos que orientam a IMC

### 3.1 Teoria da Autodeterminação (SDT)

A Teoria da Autodeterminação destaca três necessidades psicológicas frequentemente estudadas em contextos de motivação:

- **Autonomia:** perceber que a ação tem sentido e algum grau de escolha, em vez de agir apenas sob pressão externa.
- **Competência:** perceber capacidade crescente para realizar a tarefa e superar desafios.
- **Relacionamento/pertencimento:** sentir conexão, respeito e apoio de outras pessoas.

Para o Coach, isso implica oferecer escolhas reais dentro dos limites do edital; calibrar dificuldade; tornar progresso visível; dar feedback específico; e permitir apoio social sem dependência.

Uma meta-análise de 2024 sobre intervenções baseadas em SDT na educação reuniu 36 estudos de intervenção (11.792 participantes). Encontrou efeitos em suporte à autonomia e competência, com diferenças entre estudos experimentais/quase-experimentais e pré-pós. O resultado sobre motivação intrínseca não foi uniforme para todos os modelos de análise, e o efeito médio sobre relacionamento não alcançou significância estatística na análise reportada. Isso sustenta a relevância dos construtos, mas não permite afirmar que qualquer técnica aplicada pelo Coach produzirá o mesmo resultado em concurseiros adultos.

**Regra aplicada:** o Coach deve preferir colaboração, explicação de razões, escolhas proporcionais, metas ajustadas e feedback informativo; evitar controle coercitivo, ameaça, humilhação e recompensa usada para manipular.

### 3.2 Expectativa, valor e custo (Expectancy–Value–Cost)

O candidato tende a se engajar mais quando acredita que pode progredir e considera importante, interessante ou útil a tarefa. Ao mesmo tempo, percebe custos: esforço, tempo, renúncia, ansiedade, oportunidade perdida e desgaste psicológico.

A IMC deve diagnosticar os componentes separadamente:

- **Expectativa de êxito:** “Acredito que consigo aprender ou melhorar isto?”
- **Valor intrínseco:** “A tarefa me interessa ou desperta curiosidade?”
- **Valor de utilidade:** “Como isto ajuda na preparação e no projeto de vida?”
- **Valor de importância/identidade:** “Por que este resultado importa para mim?”
- **Custo:** “O que esta ação exige e o que preciso deixar de fazer?”

Baixa execução pode decorrer de alto custo e não de baixo valor. Pode haver forte desejo de aprovação, mas custo de tempo, energia e oportunidade incompatível com a rotina atual. O Coach não deve interpretar essa tensão como preguiça; precisa renegociar o sistema e encaminhar prioridades ao Orquestrador.

### 3.3 Autoeficácia (Bandura)

Autoeficácia é a crença contextual na própria capacidade de organizar e executar as ações necessárias para um resultado. Não é autoestima global nem uma garantia de sucesso.

As fontes clássicas de informação para a autoeficácia incluem:

1. experiências de domínio — realizar uma tarefa e observar progresso;
2. experiências vicárias — observar alguém comparável realizar uma tarefa;
3. persuasão social — feedback crível e específico;
4. interpretação de estados físicos e emocionais — como tensão, cansaço e ansiedade são percebidos.

O Coach deve dar preferência a **experiências graduadas de domínio**. Em vez de dizer “você consegue”, deve organizar uma sequência de tarefas que permita ao candidato observar competência crescente. O feedback deve apontar o que foi feito corretamente, qual habilidade melhorou e qual o próximo desafio viável.

### 3.4 Autorregulação motivacional

A autorregulação motivacional reúne estratégias deliberadas para iniciar, manter ou recuperar a disposição para uma tarefa. Entre as estratégias pesquisadas estão:

- aumentar interesse situacional;
- conectar a tarefa a valor pessoal ou utilidade;
- usar diálogo interno orientado ao domínio;
- dividir metas longas em metas próximas;
- organizar ambiente e reduzir distrações;
- usar apoio social;
- monitorar progresso;
- utilizar pequenas recompensas de modo não coercitivo.

A meta-análise de Fong e colaboradores (2024) reuniu 55 estudos e 67 amostras. Encontrou associações positivas entre estratégias de regulação motivacional e desempenho acadêmico, esforço, percepção de valor, crenças de competência e autorregulação cognitiva/comportamental. As associações variam e são em grande parte correlacionais. Portanto, estratégias motivacionais podem acompanhar bom desempenho e autorregulação, mas os dados não autorizam supor causalidade simples nem eficácia uniforme.

Um mapa de evidências publicado em 2025 identificou 289 estudos sobre regulação motivacional. Aproximadamente três quartos se concentraram em estudantes universitários, delineamentos transversais e autorrelatos; faltam estudos em outros contextos e sobre condições que tornam cada estratégia eficaz. Esta limitação reforça a necessidade de calibrar a IMC para o público adulto de concursos, em vez de transplantar modelos escolares sem validação.

### 3.5 COM-B: capacidade, oportunidade e motivação

O modelo COM-B é especialmente útil para evitar diagnósticos precipitados. Para que um comportamento aconteça, devem estar suficientemente presentes:

- **Capacidade:** conhecimento, habilidade, energia e recursos psicológicos necessários à tarefa.
- **Oportunidade:** tempo, ambiente, acesso a materiais, condições físicas e sociais.
- **Motivação:** processos reflexivos e automáticos que orientam a ação.

Os componentes interagem. Um candidato pode valorizar muito a aprovação, mas não executar porque não tem janela de tempo, não sabe começar ou está esgotado. Nesses casos, “motivação baixa” é uma descrição inadequada da causa.

**Pergunta operacional do Coach:** “O que precisa mudar para que o comportamento seja possível agora — capacidade, oportunidade, motivação, ou uma combinação?”

### 3.6 Procrastinação e motivação temporal

A procrastinação não é uma categoria única. Pode ser favorecida por tarefa aversiva, recompensa distante, baixa expectativa de êxito, impulsividade, distrações, dificuldade de organização, perfeccionismo e regulação emocional insuficiente.

A meta-análise de Piers Steel (2007), baseada em 691 correlações, identificou como preditores consistentes a aversividade da tarefa, o atraso da recompensa, a autoeficácia e a impulsividade, além de aspectos de autocontrole, organização e motivação para realização. O modelo temporal ajuda a compreender por que uma tarefa importante e de retorno distante pode perder para uma recompensa imediata.

**Implicação:** reduzir a distância entre intenção e recompensa observável; aumentar clareza; diminuir fricção inicial; tornar o progresso visível; treinar enfrentamento gradual de tarefas aversivas; evitar metas muito distantes sem passos intermediários.

### 3.7 WOOP / contraste mental com intenções de implementação

O contraste mental combina quatro perguntas:

1. **Wish:** o que desejo alcançar?
2. **Outcome:** qual resultado significativo espero?
3. **Obstacle:** qual obstáculo interno ou comportamental tende a surgir?
4. **Plan:** se esse obstáculo aparecer, o que farei?

O ponto-chave é não limitar a técnica à visualização de um futuro positivo. Ela exige identificar o obstáculo real e elaborar um plano “se–então”. Exemplo: “Se eu terminar o trabalho e estiver tentado a abrir redes sociais antes de estudar, então deixarei o celular fora do ambiente e farei o primeiro bloco de 15 minutos.”

Uma meta-análise de 2021 sobre contraste mental com intenções de implementação encontrou efeito médio pequeno a moderado em alcance de metas (g≈0,34; 21 estudos, 24 efeitos independentes, 15.907 participantes). A heterogeneidade e a possibilidade de viés de publicação exigem cautela; a técnica é opção de intervenção, não garantia.

### 3.8 Entrevista motivacional como estilo de conversa

A IMC pode usar elementos de entrevista motivacional sem se apresentar como tratamento clínico:

- perguntas abertas;
- escuta reflexiva;
- afirmações baseadas em evidência observada;
- resumos que organizem ambivalências;
- elicitação das razões do próprio candidato;
- apoio à autonomia e à decisão informada.

Evitar sermões, confronto, imposição de metas e “convencer” alguém à força. A meta-análise de 2024 sobre entrevista motivacional em contextos escolares encontrou efeito agregado pequeno (g≈0,18), com intervalo preditivo amplo e heterogeneidade relevante. O efeito depende do alvo, do profissional e da dose. No harness, a entrevista motivacional é uma postura conversacional útil, não um protocolo de sucesso garantido nem substituto de profissional qualificado.

### 3.9 Monitoramento de progresso

Definir metas sem monitorar sua execução é insuficiente. Uma meta-análise de 2016 sobre monitoramento de progresso reuniu 138 estudos experimentais e 19.951 participantes; o monitoramento aumentou a realização de metas (efeito médio d≈0,40). Registrar progresso fisicamente ou reportá-lo a outra pessoa foi associado a efeitos maiores em algumas condições.

A IMC deve registrar comportamentos relevantes, não apenas horas. O monitoramento precisa ser leve, útil e não punitivo. O registro deve servir para aprender e ajustar, não para criar vergonha.

### 3.10 Formação de hábitos: sem cronômetros mágicos

A evidência recente sobre formação de hábitos de saúde mostra que o processo varia muito entre pessoas e comportamentos. Uma revisão sistemática e meta-análise de 2024 reuniu 20 estudos e 2.601 participantes. Poucos estudos mediram tempo até automaticidade; os valores reportados variaram amplamente (medianas em torno de 59–66 dias em estudos específicos, médias maiores e variação individual de 4 a 335 dias). Muitos estudos apresentaram risco de viés elevado. O resultado não pode ser transferido diretamente a hábitos de estudo, mas refuta a ideia de que todos formam hábitos em 21 dias.

**Regra aplicada:** avaliar consistência contextual, frequência, facilidade de início e automaticidade percebida. Não impor prazo universal de formação de hábito.

### 3.11 Intervenções sobre procrastinação

Uma revisão sistemática de intervenções para procrastinação acadêmica publicada em 2023 identificou 21 estudos; 17 reportaram reduções significativas, mas a revisão destacou limitações e necessidade de melhor compreensão dos mecanismos e moderadores. Uma revisão sistemática publicada em 2026, baseada em 27 estudos empíricos publicados entre 2014 e 2024, sintetizou fatores causais e intervenções para procrastinação acadêmica. Destacou medo do fracasso, perfeccionismo e dificuldades de regulação emocional; relatou resultados promissores para estratégias cognitivo-comportamentais e motivacionais e potencial para ferramentas digitais de planejamento. A própria revisão aponta diferenças individuais, limitações de evidência sobre efeitos de longo prazo e necessidade de abordagens personalizadas. As amostras incluíram estudantes de diferentes níveis, não especificamente concurseiros adultos.

**Decisão de desenho:** a IMC não deve prescrever uma única técnica para toda procrastinação. Primeiro identifica mecanismo provável; depois seleciona intervenção e mede resultado.

---

## 4. Arquitetura diagnóstica da IMC

### 4.1 Princípio: diagnóstico de comportamento, não de personalidade

A IMC diagnostica **padrões situacionais de comportamento e condições contextuais**. Ela não diagnostica a personalidade do candidato, não classifica força de vontade, não determina “nível de disciplina” como característica fixa e não atribui transtornos.

O registro ideal descreve:

- o comportamento-alvo;
- o contexto em que ocorre;
- o que aconteceu antes;
- o que o candidato fez ou evitou;
- o benefício imediato percebido;
- o custo posterior;
- os fatores de capacidade, oportunidade e motivação;
- a confiança da hipótese;
- a intervenção testável.

### 4.2 Vetores diagnósticos

| Vetor | Pergunta diagnóstica | Exemplos de sinais observáveis |
|---|---|---|
| **Propósito e valor** | O objetivo continua significativo para o candidato? | Dificuldade em explicar por que escolheu a carreira; meta herdada de terceiros; valor percebido baixo |
| **Expectativa e autoeficácia** | Acredita que pode progredir com meios disponíveis? | Evita disciplinas após erros; declara incapacidade global por um simulado ruim |
| **Clareza** | Sabe exatamente qual é o próximo passo? | “Tenho que estudar tudo”; material acumulado; indecisão sobre por onde começar |
| **Capacidade** | Possui conhecimento, técnica e energia suficientes para a tarefa? | Lacuna conceitual, método inadequado, dificuldade de resolver o item |
| **Oportunidade** | Dispõe de tempo, ambiente e recursos? | Trabalho, cuidado familiar, ruído, internet, equipamento, deslocamento |
| **Custo** | Qual é o custo real e percebido da ação? | Sobrecarga, renúncia, cansaço, pressão econômica, conflito de agenda |
| **Fricção de início** | O que impede o primeiro movimento? | Demora para abrir material, ritual ausente, tarefa grande, distração imediatamente disponível |
| **Aversividade** | Que emoção ou desconforto é evitado? | Medo de errar, tédio, leitura difícil, feedback desagradável, perfeccionismo |
| **Hábito e ambiente** | O contexto favorece o comportamento desejado? | Horário variável, notificações, local sem material, falta de pista de início |
| **Constância** | O comportamento persiste ao longo das semanas? | Picos de estudo seguidos de queda, alternância entre hiperfoco e ausência |
| **Recuperação** | Como reage a interrupções e resultados ruins? | Abandono após falta, “tudo perdido”, tentativa de compensar horas excessivamente |
| **Emoção e bem-estar** | O sofrimento interfere no funcionamento? | Ansiedade intensa, irritabilidade persistente, exaustão, desesperança, prejuízo diário |
| **Pertencimento e apoio** | Há apoio suficiente e relações sustentáveis? | Isolamento, crítica familiar, ausência de pares, conflitos que consomem energia |

### 4.3 Taxonomia de códigos proposta

Os códigos abaixo são uma convenção interna sugerida. **Não são uma escala validada, não são categorias clínicas e não produzem automaticamente um diagnóstico.** Podem coexistir e devem ser associados a evidências.

| Código | Nome operacional | O que observar |
|---|---|---|
| `MOT` | Regulação motivacional | Oscilação ou baixa disponibilidade para iniciar/manter tarefa, após excluir causas de capacidade e oportunidade |
| `VAL` | Valor/propósito pouco claro | Baixa conexão percebida entre tarefa, objetivo e valores próprios |
| `AUT` | Autonomia/ownership reduzido | Objetivo ou plano percebido como imposto, sem escolha compreendida |
| `EXP` | Expectativa de êxito reduzida | Crença baixa de que o esforço pode produzir progresso |
| `CPT` | Autoeficácia/competência percebida | Dúvida específica sobre capacidade de executar a tarefa |
| `AMB` | Ambiguidade/falta de clareza | Próxima ação, critério de conclusão ou prioridade não definidos |
| `OPP` | Oportunidade/recursos insuficientes | Tempo, local, material, suporte ou condições ambientais inadequados |
| `CST` | Custo percebido/real elevado | Esforço, desgaste, renúncia ou conflito de agenda incompatíveis |
| `INI` | Fricção de início | A intenção está presente, mas o começo é repetidamente adiado |
| `PRO` | Procrastinação situacional | Adiamento recorrente de tarefa importante, com alternativa concorrente ou alívio imediato |
| `AVR` | Aversividade da tarefa | Evitamento ligado a tédio, medo, desconforto, monotonia ou dificuldade |
| `HAB` | Arquitetura de hábito frágil | Ausência de gatilho estável, ritual, ambiente ou repetição contextual |
| `CON` | Constância irregular | Grande variação de execução ao longo de períodos comparáveis |
| `PER` | Perfeccionismo/interrupção por padrão excessivo | Não começa ou não conclui por exigência irrealista |
| `OVR` | Sobrecarga operacional | Demandas simultâneas excedem capacidade temporal/energética percebida |
| `FAD` | Fadiga provável | Queda temporal de energia/precisão que requer comparação e confirmação, não conclusão a partir de um episódio |
| `ANS` | Ansiedade interferente | Ansiedade declarada e/ou observável que interfere na preparação ou no desempenho |
| `FRU` | Frustração após erro/resultado | Reação emocional que altera a continuidade ou estratégia |
| `REC` | Recuperação/reentrada | Necessidade de reconstruir rotina após pausa, doença, mudança ou resultado adverso |
| `SUP` | Apoio/pertencimento | Necessidade de suporte social ou de melhor fronteira com relações que interferem |
| `ISO` | Isolamento percebido | Solidão que afeta bem-estar ou continuidade |
| `RUM` | Ruminação/contrafactual | Repetição improdutiva de “se...” e cenários futuros sem ação possível |
| `AUTS` | Padrão de autossabotagem | Ciclo comportamental repetido em que alívio imediato interfere em uma prioridade escolhida |
| `BEM` | Bem-estar/encaminhamento | Indícios de sofrimento que exigem redução de escopo, apoio humano ou avaliação profissional |

### 4.4 Coleta conversacional mínima

A coleta deve ser breve e dirigida. O Coach não deve aplicar um questionário extenso a cada sessão. Em geral, bastam três a cinco perguntas, escolhidas conforme o contexto:

1. “O que você pretendia estudar e o que conseguiu fazer de fato?”
2. “Em que momento a dificuldade apareceu: antes de começar, durante a tarefa, depois de errar ou depois de uma interrupção?”
3. “O que tornou essa tarefa difícil hoje: falta de clareza, dificuldade do conteúdo, tempo, energia, desânimo, distração ou outra coisa?”
4. “O que você fez no lugar e que alívio imediato isso trouxe?”
5. “Qual seria uma versão pequena e realista do próximo passo?”

Para uma verificação rápida, o candidato pode estimar de 0 a 10 expectativa, valor e custo percebido. Esses números são **marcadores conversacionais**, não escores psicométricos nem diagnósticos. O Coach deve permitir resposta qualitativa e não insistir em quantificação quando ela não ajuda.

### 4.5 Qualidade da evidência e confiança da hipótese

Toda análise deve separar:

- **Observado:** o candidato informou ou o registro mostra um comportamento específico.
- **Calculado:** proporção, frequência ou tendência derivada de registros.
- **Inferido:** interpretação que decorre de mais de uma evidência.
- **Hipótese:** explicação plausível ainda não confirmada.
- **Desconhecido:** não há dado suficiente.
- **Pendente de validação:** é necessário observar novo comportamento ou perguntar algo.

Uma hipótese motivacional baseada em uma única ausência não pode ser tratada como diagnóstico. Sempre considerar alternativas, inclusive doença, responsabilidade familiar, limitação de tempo, material inadequado ou necessidade de revisão pedagógica pelo Tutor.

---

## 5. Protocolo de diagnóstico em conversa

### 5.1 Sequência de quatro movimentos

**M1 — Acolher sem moralizar.** Reconhecer a dificuldade sem afirmar que ela é trivial, inevitável ou culpa do candidato.

**M2 — Descrever o comportamento.** Identificar o que estava planejado, o que aconteceu e em que ponto a execução mudou.

**M3 — Testar hipóteses.** Distinguir capacidade, oportunidade, motivação, custo, ambiente e bem-estar. Perguntar antes de concluir.

**M4 — Escolher um experimento.** Selecionar apenas uma intervenção principal, definir comportamento-alvo e combinar como observar o resultado.

### 5.2 Perguntas para localizar a causa

| Se o candidato disser... | Pergunta de discriminação |
|---|---|
| “Estou sem motivação.” | “Você ainda considera esse objetivo importante, mas está difícil começar, ou está em dúvida sobre querer esse caminho?” |
| “Estou com preguiça.” | “O que parece mais difícil: entender a tarefa, começar, manter atenção ou lidar com a possibilidade de errar?” |
| “Não tenho tempo.” | “Quais compromissos são fixos e quais podem ser reduzidos ou reorganizados sem prejudicar responsabilidades importantes?” |
| “Não consigo aprender.” | “Qual foi o último ponto concreto que você compreendeu e em qual etapa começou a travar?” |
| “Estudei muito e fui mal.” | “O erro foi de conteúdo, interpretação, decisão, tempo, ansiedade, ou uma combinação?” |
| “Perdi vários dias.” | “O que provocou a interrupção e qual rotina mínima cabe nas condições atuais?” |
| “Preciso recuperar tudo.” | “Qual é a prioridade atual? O que realmente precisa ser retomado primeiro, sem transformar o passado em dívida?” |
| “Não sei se vale a pena.” | “O que mudou no valor desse objetivo? É uma dúvida sobre o cargo ou uma reação ao cansaço e ao resultado recente?” |

### 5.3 Diagnóstico de ciclo de autossabotagem

A partir da análise do manual e dos modelos de mudança de comportamento, a IMC deve usar o seguinte esquema:

`Gatilho → interpretação/emoção → comportamento de fuga → alívio ou recompensa imediata → custo posterior → reforço do ciclo`.

Exemplo hipotético:

- Gatilho: abrir um PDF de matéria considerada difícil.
- Interpretação: “Não vou entender isso e vou perder tempo”.
- Emoção: ansiedade e desconforto.
- Fuga: abrir redes sociais ou reorganizar o cronograma.
- Recompensa imediata: alívio e sensação de controle.
- Custo posterior: matéria continua sem estudo; aumenta culpa e dificuldade de iniciar.

A intervenção pode ser reduzir o bloco, começar com uma questão diagnóstica, encaminhar ao Tutor se houver lacuna, remover a distração ou usar um plano “se–então”. O Coach deve testar qual fator explica melhor o ciclo; não presumir que todos os casos têm a mesma causa.

---

## 6. Biblioteca de intervenções

A biblioteca deve ser um catálogo selecionável, não uma sequência obrigatória. Cada intervenção deve possuir: ID, hipótese-alvo, indicação, procedimento, duração aproximada, comportamento observado, indicador de resultado, limites e critério de ajuste.

### 6.1 Catálogo inicial proposto

| ID | Intervenção | Hipótese-alvo | Aplicação prática | Indicador primário |
|---|---|---|---|---|
| `IMC-01` | Microinício | Fricção de início / tarefa grande | Reduzir o primeiro passo a 5–15 minutos ou uma unidade mínima útil | Início efetivo do bloco |
| `IMC-02` | Decomposição de tarefa | Ambiguidade / aversividade | Transformar “estudar Direito Administrativo” em ação específica e finita | Tarefa concluída sem assistência indevida |
| `IMC-03` | Ritual de início | Hábito frágil | Associar estudo a horário, local ou ação antecedente estável | Latência entre horário combinado e início |
| `IMC-04` | Arranjo ambiental | Oportunidade / distração | Preparar material, local, notificações e barreiras à distração | Frequência de interrupções evitáveis |
| `IMC-05` | Plano se–então | Procrastinação / obstáculo previsível | “Se X acontecer, então farei Y” | Execução do plano quando o gatilho aparece |
| `IMC-06` | WOOP/MCII | Meta distante / obstáculo interno | Desejo, resultado, obstáculo interno, plano concreto | Ação após ocorrência do obstáculo |
| `IMC-07` | Escada de domínio | Autoeficácia baixa | Sequenciar tarefas de dificuldade crescente e registrar êxitos verificáveis | Melhora em tarefas comparáveis e confiança calibrada |
| `IMC-08` | Reenquadramento de valor | Baixa utilidade percebida | Conectar o conteúdo ao objetivo sem exagerar promessas | Clareza do valor e adesão à tarefa |
| `IMC-09` | Diário de progresso | Baixa percepção de avanço | Registrar blocos concluídos, habilidade praticada e evidência de melhora | Tendência de execução/progresso |
| `IMC-10` | Feedback informativo | Frustração / baixa competência percebida | Descrever habilidade observada, erro específico e próximo passo | Capacidade de repetir a habilidade em nova tarefa |
| `IMC-11` | Recompensa proporcional | Reforço imediato fraco | Escolher recompensa pequena, saudável e após a ação definida | Repetição do comportamento-alvo |
| `IMC-12` | Prestação de contas consentida | Baixa constância / necessidade de apoio | Compartilhar compromisso e resultado com pessoa escolhida pelo candidato | Regularidade sem pressão ou vergonha |
| `IMC-13` | Comunidade de estudo | Isolamento / falta de pertencimento | Combinar estudo paralelo, troca de experiência ou encontro de revisão | Percepção de apoio e continuidade |
| `IMC-14` | Gestão de preocupação | Ruminação / ansiedade interferente | Registrar preocupação, separar controle, ação e adiamento de preocupação improdutiva | Redução de ruminação autorrelatada e ação concreta |
| `IMC-15` | Limite informacional | Sobrecarga / ansiedade por notícias | Definir janela breve e necessária para notícias e mensagens | Menor interrupção por informação não essencial |
| `IMC-16` | Reentrada gradual | Interrupção / perda de rotina | Recomeçar com rotina mínima, prioridade única e aumento progressivo | Retomada sustentada por mais de uma sessão |
| `IMC-17` | Retrospectiva sem culpa | Reprovação / frustração | Separar fatos, causas controláveis, causas não controláveis e aprendizagem | Ação de melhoria definida sem autodepreciação |
| `IMC-18` | Gratidão opcional | Foco restrito em perdas | Registrar algo concreto pelo qual é grato, sem negar dificuldades | Uso voluntário e efeito percebido pelo candidato |
| `IMC-19` | Priorização de batalhas | Sobrecarga / demandas concorrentes | Identificar o que é essencial, adiável, delegável ou dispensável | Redução de conflito de agenda |
| `IMC-20` | Recuperação e limite | Fadiga / sobrecarga | Reduzir carga, inserir pausa, sono/descanso e encaminhamento quando preciso | Recuperação funcional e estabilidade subsequente |
| `IMC-21` | Simulação gradual | Ansiedade de prova / falta de familiaridade | Aumentar progressivamente realismo, duração e pressão temporal | Desempenho estável e menor interferência percebida |
| `IMC-22` | Revisão de objetivo | Valor/autonomia comprometidos | Revisar se o objetivo ainda é escolhido, viável e alinhado aos valores | Decisão explícita e plano coerente |

### 6.2 Fichas de intervenção — formato obrigatório

Cada ficha de biblioteca deve conter:

```text
ID:
Nome:
Mecanismo-alvo:
Códigos diagnósticos relacionados:
Indicação:
Pré-condições:
Passos:
Duração/frequência sugerida:
Comportamento-alvo:
Indicador primário:
Indicadores secundários:
Limitações da evidência:
Riscos/contraindicações:
Critério para manter:
Critério para modificar ou interromper:
Rota de encaminhamento:
```

### 6.3 Seleção da intervenção

A IMC escolhe uma intervenção com base na hipótese mais provável e na menor carga necessária. Exemplos:

- `AMB` → `IMC-02` (decomposição) ou `IMC-03` (ritual).
- `INI` → `IMC-01` + `IMC-05`.
- `EXP/CPT` → `IMC-07` e feedback informativo; se a causa for conteúdo, Tutor.
- `OPP/OVR` → `IMC-19` e revisão do plano com Orquestrador.
- `PRO/AVR` → diagnóstico de recompensa imediata, `IMC-02`, `IMC-04` ou `IMC-05`.
- `CON` → `IMC-03`, `IMC-09` e metas realistas.
- `FRU` → `IMC-17`; depois reteste de desempenho com Coach.
- `REC` → `IMC-16`.
- `ISO/SUP` → `IMC-13`, com respeito à rede real de apoio.
- `ANS/BEM` → reduzir carga e aplicar limites; encaminhar a profissional quando apropriado.

Não aplicar cinco técnicas ao mesmo tempo. A intervenção precisa ser compreensível, executável e testável.

---

## 7. Ciclos operacionais

### 7.1 Ciclo diário — pulso e próximo passo

O ciclo diário é breve e não deve virar mais uma tarefa cansativa.

1. **Contexto:** qual era a intenção principal da sessão?
2. **Execução:** o que realmente foi feito?
3. **Fricção:** em qual etapa houve dificuldade?
4. **Hipótese:** clareza, capacidade, oportunidade, motivação, custo ou bem-estar?
5. **Ação mínima:** qual o próximo passo específico?
6. **Fechamento:** o que ficou aprendido e qual será o ponto de retomada?

Registro recomendado:

```text
Data:
Intenção principal:
Comportamento executado:
Evidência de execução:
Barreira observada:
Hipótese (com confiança):
Intervenção aplicada:
Próximo passo:
Ponto de retomada:
```

O Coach não precisa perguntar diariamente sobre emoções se nada no contexto indicar utilidade. A coleta deve ser proporcional e respeitar a preferência do candidato.

### 7.2 Ciclo semanal — diagnóstico e ajuste

1. Comparar o planejado com o executado.
2. Observar quais tarefas foram iniciadas, concluídas, adiadas ou interrompidas.
3. Separar variação normal de padrão recorrente.
4. Conferir fatores de contexto: trabalho, família, saúde, ambiente, mudança de edital e dificuldade de conteúdo.
5. Selecionar uma barreira prioritária.
6. Escolher uma intervenção e um indicador.
7. Definir quando reavaliar.
8. Comunicar ao Orquestrador o que exige mudança de prioridade ou de plano.

A avaliação semanal não deve se resumir a “quantas horas faltaram”. Importa saber se o candidato executou atividades relevantes, aprendeu, manteve autonomia e preservou sustentabilidade.

### 7.3 Ciclo estratégico — revisão de fase

A cada ciclo de preparação, transição de edital ou período acordado, revisar:

- objetivo e valor atual;
- viabilidade do cargo e do contexto;
- constância de execução;
- estado de aprendizagem reportado pelo Tutor;
- desempenho de prova medido pelo Coach;
- carga total de compromissos;
- riscos de sobrecarga;
- rede de apoio;
- necessidade de manter, simplificar ou alterar estratégia.

Mudança de objetivo não é automaticamente desistência. O Orquestrador pode priorizar outro concurso dentro do projeto se a mudança for racional e coerente com o objetivo maior.

### 7.4 Protocolo de reentrada após interrupção

Ativar quando houver interrupção relevante ou quando o candidato declarar que perdeu a rotina.

**Etapa A — compreender a interrupção**

- O que ocorreu?
- A causa ainda existe?
- Foi uma pausa planejada, uma urgência, uma dificuldade emocional, uma mudança de agenda ou uma perda de clareza?

**Etapa B — preservar o que já foi construído**

- manter histórico de progresso;
- solicitar ao Tutor estado de aprendizagem e conteúdos que precisam de recuperação;
- não declarar que o candidato voltou ao zero;
- não tentar repor todos os blocos perdidos.

**Etapa C — reiniciar em escala mínima**

- selecionar uma prioridade;
- definir bloco pequeno e viável;
- restabelecer local, horário ou gatilho;
- identificar o ponto exato de retomada;
- avaliar após execução, não antes.

**Etapa D — aumentar só com evidência**

- elevar carga gradualmente;
- observar mais de uma sessão;
- não transformar um dia bom em nova meta exagerada;
- encaminhar mudanças estruturais ao Orquestrador.

### 7.5 Protocolo após simulado ruim ou reprovação

1. Interromper conclusões globais como “não sirvo para isso”.
2. Fazer análise objetiva do desempenho: domínio, recuperação, interpretação, discriminação, aplicação, estratégia, tempo e execução.
3. Distinguir o que o candidato controla do que não controla.
4. Encaminhar lacunas pedagógicas ao Tutor.
5. Manter no Coach o treino de estratégia de prova e gestão de tempo.
6. Escolher uma prioridade de melhora e um reteste novo.
7. Reconhecer o impacto emocional sem obrigar o candidato a “ver o lado bom” imediatamente.
8. Retomar o plano após intervalo adequado, sem punição ou compensação excessiva.

### 7.6 Protocolo para ansiedade de prova

A IMC pode apoiar a preparação comportamental para ansiedade situacional com:

- familiarização gradual com o formato da prova;
- simulações progressivas, sem saltar diretamente para carga máxima;
- rotina pré-simulado e pré-prova;
- separação de preocupações controláveis e não controláveis;
- registro de pensamentos que interferem na execução;
- foco no comando, no item atual e no próximo passo;
- revisão pós-simulado baseada em evidência, não em catastrofização.

Quando a ansiedade for persistente, intensa ou prejudicar significativamente a vida e a preparação, o Coach deve recomendar suporte profissional. A meta-análise de intervenções para ansiedade de prova em estudantes universitários sugere que intervenções psicológicas podem reduzir ansiedade e melhorar desempenho, mas não transforma o Coach em terapeuta nem garante que a mesma resposta ocorra em todos os candidatos.

### 7.7 Protocolo de sobrecarga

Ativar quando o candidato relata que está no limite, sem conseguir recuperar-se, ou quando aparecem sinais repetidos de queda de funcionamento.

- parar a intensificação motivacional;
- verificar se há urgência ou sofrimento importante;
- perguntar o que pode ser reduzido, adiado ou renegociado;
- suspender metas de compensação;
- priorizar descanso e apoio humano quando necessários;
- evitar a interpretação moral de que a pessoa “não quer o suficiente”;
- encaminhar ao profissional adequado se houver prejuízo significativo ou persistente.

---

## 8. Integração com o ciclo cognitivo e a inteligência adversarial

A IMC não opera isolada do desempenho real. As causas motivacionais e pedagógicas podem se influenciar mutuamente.

### 8.1 Matriz de encaminhamento

| Evidência predominante | Ação do Coach/IMC | Encaminhamento |
|---|---|---|
| Não compreende a regra/conceito | Não tentar resolver com incentivo; registrar lacuna | Tutor |
| Compreende, mas não recupera sem pista | Verificar intervalo, confiança e pistas; reteste posterior | Tutor, com reteste pelo Coach |
| Compreende, mas interpreta o comando incorretamente | Treinar leitura, polaridade, alcance e verificação do item | Coach |
| Confunde conceitos próximos | Confirmar se é lacuna conceitual ou falha de discriminação | Tutor + Coach |
| Conhece regra, mas não aplica a fatos novos | Treino de transferência e aplicação; Tutor se falta compreensão | Coach, ou Tutor + Coach |
| Erra por decisão, risco ou tempo | Treinar estratégia conforme edital e banca | Coach |
| Erros surgem após interrupções repetidas | Diagnosticar contexto, rotina, capacidade e oportunidade | IMC + Orquestrador |
| Baixa confiança após fracasso, apesar de desempenho crescente | Escada de domínio e feedback específico | IMC + Coach |
| Sobrecarga generalizada ou sofrimento intenso | Pausar otimização e avaliar necessidade de suporte | Pessoa/profissional adequado |

### 8.2 Relação com a taxonomia de erro

A taxonomia de inteligência adversarial continua sob o documento superior. A IMC pode adicionar tags comportamentais como contexto, mas não substituir os códigos de erro de questão.

Exemplo: `NEG` (erro de negação) pode coexistir com `ANS` (ansiedade interferente) ou `FAD` (fadiga a investigar). A presença de `ANS` não prova que a ansiedade causou o erro. É necessário observar padrão e comparar situações equivalentes.

### 8.3 Reteste e prova independente

A eficácia da intervenção não deve ser avaliada só por relato de ânimo. Após intervenção, o Coach deve procurar evidência compatível com o alvo:

- iniciou o bloco com menor atraso;
- concluiu a tarefa mínima;
- manteve a rotina em mais de uma ocasião;
- resolveu item novo com maior autonomia;
- recuperou-se após interrupção sem abandonar o ciclo;
- executou simulado com menor variação não explicada.

Quando o alvo é desempenho, o reteste deve usar questão nova ou variação validada, seguindo o protocolo cognitivo existente. Respostas assistidas não contam como desempenho independente.

---

## 9. Métricas, painel e avaliação de efeito

### 9.1 O que acompanhar

| Métrica | Definição | Observação |
|---|---|---|
| Taxa de execução | Blocos ou ações relevantes executados ÷ planejados e viáveis | Não punir mudança justificada de plano |
| Latência de início | Tempo entre o início combinado e o começo real | Interpretar por tarefa e contexto |
| Persistência na tarefa | Tempo/etapas mantidas antes de abandonar ou mudar | Não premiar insistência improdutiva |
| Continuidade semanal | Distribuição da execução ao longo dos dias | Medir regularidade, não perfeição |
| Recuperação após interrupção | Tempo e passos necessários para retomar | Evitar definir prazo universal |
| Autonomia | Proporção de ações realizadas sem assistência indevida | Essencial para a prova real |
| Valor percebido | Relato contextual de importância/utilidade | Não é escala clínica |
| Expectativa de êxito | Crença contextual de que pode progredir | Comparar com desempenho real |
| Custo percebido | Esforço, tempo, desgaste e renúncia | Usar para ajustar viabilidade |
| Desempenho cognitivo | Precisão, transferência, tempo, confiança e estabilidade | Conforme base cognitiva do Coach |
| Bem-estar percebido | Autorrelato breve, apenas quando relevante | Não inferir diagnóstico clínico |

### 9.2 O que não medir como indicador único

Não usar isoladamente:

- horas de estudo;
- número de dias sem pausa;
- “força de vontade”;
- quantidade de mensagens motivacionais consumidas;
- sequência de dias perfeita;
- pontuação em escala improvisada de motivação;
- comparação com candidatos desconhecidos;
- quantidade bruta de questões sem análise de qualidade e origem.

Horas podem ser contexto, não sinônimo de aprendizagem ou desempenho. A meta é executar trabalho relevante, adquirir competência e demonstrar domínio de forma independente.

### 9.3 Avaliação N-of-1

A IMC deve testar intervenções no contexto do próprio candidato:

1. Registrar uma linha de base suficiente para compreender o comportamento.
2. Escolher um comportamento-alvo específico.
3. Selecionar uma intervenção coerente com a hipótese.
4. Definir antecipadamente o indicador primário.
5. Observar por período adequado ao comportamento.
6. Comparar com a linha de base, considerando mudanças de contexto.
7. Manter, ajustar ou retirar a intervenção.

Um antes/depois isolado não demonstra causalidade. Se o resultado mudar, o Coach deve dizer “houve melhora observada após a intervenção”, não “a intervenção causou a melhora”, salvo desenho suficientemente robusto.

### 9.4 Painel recomendado

O painel pode exibir quatro faixas:

1. **Execução:** planejado, realizado, latência e continuidade.
2. **Barreiras:** códigos mais recorrentes, contexto e hipóteses ativas.
3. **Desempenho:** progresso cognitivo e de prova, com origem e amostra.
4. **Sustentabilidade:** recuperação, custo percebido, sobrecarga declarada e necessidade de ajuste.

Não criar um único “índice de motivação” que reduza o estado do candidato a uma nota e incentive comparação indevida.

---

## 10. Benchmark de práticas públicas de mentoria para concursos

O benchmark abaixo observa **o que as plataformas declaram publicamente oferecer**, não mede eficácia, não compara resultados causais e não prova que os serviços utilizem protocolos clínicos ou instrumentos psicométricos validados.

| Referência pública | Componentes divulgados | Aprendizado de desenho para a IMC | Limite da inferência |
|---|---|---|---|
| GranXperts / Gran Cursos | Mentorias individualizadas, plano de estudos, contato com mentor, feedback, técnicas de estudo e apoio motivacional; páginas de produto também anunciam encontros, simulados, grupos e monitoramento | Integrar plano, rotina, suporte e feedback; definir contratos claros de frequência e acompanhamento | Material comercial descreve oferta, não demonstra eficácia ou consistência de execução |
| Direção Concursos | Plataforma de metas e desempenho, orientação técnica e motivacional, gestão de emoções/ansiedade, cronograma personalizado e relatórios | Painel de progresso e suporte emocional precisam estar ligados a metas observáveis e critérios de encaminhamento | Página promocional não comprova validade de instrumentos nem efeito causal |
| Qconcursos / Ilimitado Elite | Mentorias coletivas ao vivo, sessões temáticas, prática orientada, acompanhamento emocional e de rotina descrito em conteúdo editorial | Comunidade, apoio entre pares e rotina recorrente podem complementar o trabalho individual | Conteúdo editorial/promocional e depoimentos não equivalem a ensaio independente de eficácia |

**Síntese competitiva:** ofertas públicas convergem em personalização, plano, metas, feedback, acompanhamento e apoio motivacional. A contribuição específica da IMC proposta é converter esses elementos em um sistema auditável: diagnóstico por hipótese, intervenção selecionada, evidência de execução, reteste, encaminhamento e salvaguardas. O diferencial não é prometer “motivação contínua”, mas demonstrar o que foi identificado, o que foi feito e o que mudou.

---

## 11. Contratos de interface

### 11.1 Coach/IMC → Tutor

Quando a motivação está sendo afetada por uma lacuna de aprendizagem, encaminhar:

```text
ID do encaminhamento:
Disciplina / assunto / subassunto:
Questão, aula ou atividade de origem:
Comportamento observado:
Resposta e justificativa do candidato:
Confiança e tempo, se disponíveis:
Pistas/assistência utilizadas:
Código(s) cognitivo(s):
Código(s) motivacional(is):
Evidência observada:
Hipótese de relação entre lacuna e comportamento:
Intervenção IMC já tentada:
Objetivo pedagógico recomendado:
Critério sugerido para retorno ao Coach:
```

O Tutor deve devolver a lacuna identificada, conteúdo trabalhado, fonte, intervenção pedagógica, resultado de recuperação, estado de aprendizagem e indicação de quando o Coach poderá retestar. A IMC não deve reclassificar o estado de aprendizagem sem evidência nova.

### 11.2 Tutor → Coach/IMC

O Tutor pode sinalizar:

- dificuldade persistente de um tema que está provocando frustração;
- conhecimento recuperável após apoio ou revisão;
- necessidade de reteste independente;
- carga pedagógica que parece exceder o ritmo atual;
- ponto de sucesso que pode apoiar uma escada de domínio.

### 11.3 Coach/IMC → Orquestrador

```text
ID do estado IMC:
Período observado:
Comportamento-alvo:
Resumo do que foi observado:
Códigos ativos e evidências:
Hipóteses e grau de confiança:
Intervenção aplicada:
Indicador e resultado observado:
Restrições/contexto relevantes:
Dependência do Tutor (sim/não; qual):
Risco de sobrecarga ou encaminhamento humano:
Recomendação de prioridade:
Próxima data/condição de reavaliação:
```

O Orquestrador integra prioridades. Não deve alterar os dados observados nem converter hipótese motivacional em fato.

---

## 12. Gates de qualidade e governança

Os gates abaixo são obrigações propostas ao harness. A falha em um gate exige correção, coleta adicional ou abstenção.

| Gate | Regra determinística |
|---|---|
| `G-MOT-01` | Não inferir falta de motivação de uma única sessão perdida ou de um único comportamento |
| `G-MOT-02` | Separar capacidade, oportunidade, motivação, custo e bem-estar antes de selecionar intervenção |
| `G-MOT-03` | Toda hipótese deve conter evidências e grau de incerteza |
| `G-MOT-04` | Não usar códigos internos como diagnóstico psicológico ou escala validada |
| `G-MOT-05` | Não aplicar perfil fixo de personalidade; descrever apenas comportamento contextual |
| `G-MOT-06` | Cada intervenção deve ter comportamento-alvo e indicador observável |
| `G-MOT-07` | Não declarar eficácia com base apenas em satisfação, relato de ânimo ou antes/depois isolado |
| `G-MOT-08` | Preservar autonomia; não coagir, envergonhar, ameaçar ou manipular o candidato |
| `G-MOT-09` | Não usar medo, culpa, comparação social ou ameaça de fracasso como técnica padrão |
| `G-MOT-10` | Não exigir compensação integral de horas perdidas nem converter pausa em dívida moral |
| `G-MOT-11` | Não estimular privação de sono, alimentação, exercício, tratamento, renda ou responsabilidades essenciais |
| `G-MOT-12` | Não sugerir abandono de emprego, dependentes ou plano de segurança como método de comprometimento |
| `G-MOT-13` | Encaminhar lacunas de conhecimento e recuperação ao Tutor conforme contrato de interface |
| `G-MOT-14` | Encaminhar sofrimento intenso ou persistente para apoio humano/profissional apropriado |
| `G-MOT-15` | Não diagnosticar ansiedade clínica, depressão, burnout ou outros transtornos |
| `G-MOT-16` | Não construir dependência emocional do candidato em relação à IA ou ao Coach |
| `G-MOT-17` | Usar apoio social somente com consentimento e sem exposição indevida de dados pessoais |
| `G-MOT-18` | Não usar resultado de IA como evidência de que o candidato aprendeu ou melhorou |
| `G-MOT-19` | Rever intervenção sem efeito; não insistir indefinidamente por apego ao método |
| `G-MOT-20` | Preservar fontes, privacidade, contexto temporal e histórico necessário à interpretação |
| `G-MOT-21` | Não prometer aprovação, nomeação ou resultado de vida com base em motivação ou esforço |
| `G-MOT-22` | Distinguir persistência adaptativa de teimosia, sobrecarga e insistência em plano inviável |

### 12.1 Escopo não clínico e encaminhamento

A IMC é uma camada de apoio à organização e à execução de estudos. Não realiza psicoterapia, triagem clínica formal, diagnóstico ou tratamento. Sinais de sofrimento intenso, persistente ou com prejuízo funcional significativo exigem orientação para procurar profissional qualificado e apoio humano de confiança. Em situação de risco imediato à segurança da pessoa ou de terceiros, a prioridade é buscar ajuda emergencial local, não continuar o coaching de produtividade.

### 12.2 Privacidade e consentimento

Dados sobre saúde, humor, relações familiares e dificuldades pessoais são sensíveis. O Coach deve coletar apenas o estritamente necessário, explicar para que a informação será usada e respeitar a recusa do candidato. Não enviar relatos pessoais a colegas, grupos ou terceiros sem consentimento explícito. A prestação de contas deve ser voluntária.

---

## 13. Regras de resposta do Coach: estilo de intervenção

### 13.1 Padrão de conversa recomendado

1. **Reconhecer:** “Parece que o plano ficou pesado nas condições desta semana.”
2. **Descrever:** “Você pretendia fazer três blocos e conseguiu iniciar um.”
3. **Investigar:** “A maior barreira foi tempo, energia, clareza ou dificuldade do conteúdo?”
4. **Escolher:** “Vamos testar uma mudança pequena: deixar o material preparado e começar com uma questão diagnóstica.”
5. **Verificar:** “Na próxima sessão, veremos se o início ficou mais fácil.”

### 13.2 Respostas proibidas ou inadequadas

Evitar expressões como:

- “Você não quer o suficiente.”
- “Quem quer dá um jeito.”
- “Não existe desculpa.”
- “Você só precisa ter disciplina.”
- “Queime todos os navios.”
- “Se não estudar hoje, estará traindo sua família.”
- “A dor vai fazer você mais forte.”
- “Você é preguiçoso/perfeccionista/vítima.”
- “Não pare nunca, independentemente do que aconteça.”

Essas frases ignoram causas reais, reduzem autonomia e podem agravar culpa e evitamento. Uma resposta firme pode ser respeitosa e baseada em evidência sem humilhar.

### 13.3 Mensagens motivacionais personalizadas

Mensagens motivacionais podem ser usadas como complemento, desde que:

- derivem de um fato ou valor declarado pelo candidato;
- não garantam aprovação;
- não comparem o candidato com outros;
- não substituam intervenção concreta;
- não invalidem tristeza, ansiedade ou cansaço;
- terminem, quando apropriado, em uma próxima ação pequena e escolhida.

---

## 14. Casos de uso e exemplos de decisão

### Caso A — “Não consigo começar Português”

**Sinais:** o candidato evita a disciplina há vários dias, mas não relata falta de tempo generalizada.

**Hipóteses:** dificuldade de início (`INI`), aversividade (`AVR`) ou lacuna de base (`CPT`/capacidade).

**Perguntas:** a tarefa está clara? O candidato entende o primeiro tópico? O que sente ao abrir o material?

**Ação:** se a matéria é compreendida, `IMC-01` e `IMC-02`; se não é, encaminhar ao Tutor. Não rotular como desinteresse.

### Caso B — “Estudei dez horas por dia e depois parei”

**Sinais:** pico inicial, interrupção e culpa.

**Hipóteses:** carga irrealista, custo elevado, hábito não consolidado, sobrecarga (`OVR`, `CON`).

**Ação:** rever baseline, começar com carga viável, restabelecer ciclo adaptável, medir continuidade. Não premiar ou estimular retorno imediato a dez horas.

### Caso C — “Fui mal no simulado; acho que não sou capaz”

**Sinais:** generalização da nota para identidade.

**Hipóteses:** frustração (`FRU`), expectativa reduzida (`EXP`), possível lacuna cognitiva.

**Ação:** analisar erros com o Coach; encaminhar lacunas ao Tutor; mostrar evidências específicas de competência e progresso; definir reteste em questão nova. Não usar frases vazias.

### Caso D — “Minha família não apoia”

**Sinais:** conflito e desânimo.

**Hipóteses:** ausência de apoio (`SUP`), sobrecarga de compromissos, necessidade de negociação de limites.

**Ação:** ajudar a preparar conversa clara e realista; identificar rede alternativa de apoio; organizar tempo; não estimular hostilidade ou rompimento com família. Validar a necessidade de pertencimento sem impor isolamento.

### Caso E — “Perdi duas semanas por doença/urgência”

**Sinais:** interrupção externa, preocupação com atraso.

**Hipóteses:** reentrada (`REC`), oportunidade reduzida (`OPP`), necessidade de recuperação pedagógica.

**Ação:** não criar dívida de horas; preservar histórico; consultar Tutor; recomeçar por bloco mínimo e atualizar prioridades com Orquestrador.

### Caso F — “Preciso estudar, mas fico atualizando notícias e grupos”

**Sinais:** atenção capturada por informações concorrentes.

**Hipóteses:** estímulos ambientais, ansiedade informacional, busca de alívio.

**Ação:** identificar quais informações são necessárias; definir janela de consulta; silenciar notificações durante bloco; usar `IMC-04` e `IMC-15`.

### Caso G — “Estou no limite e não aguento mais”

**Sinais:** expressão de sofrimento e exaustão.

**Hipótese:** `BEM`/`OVR`; não classificar automaticamente como procrastinação.

**Ação:** interromper cobrança de produtividade; verificar segurança e necessidade de ajuda humana; reduzir exigência e orientar procura de profissional quando apropriado. A prova não se sobrepõe à segurança.

---

## 15. Plano de implantação do módulo

### Fase 1 — Especificação sem automação complexa

- incorporar definição de IMC e fronteiras de responsabilidade;
- adotar os códigos como marcadores experimentais;
- incluir coleta conversacional mínima;
- padronizar a distinção entre observado, calculado, inferido e hipótese.

### Fase 2 — Biblioteca de intervenções

- criar fichas completas para `IMC-01` a `IMC-22`;
- associar cada intervenção a mecanismo e código;
- validar consistência das instruções;
- retirar recomendações incompatíveis com salvaguardas.

### Fase 3 — Ciclos e contratos

- implementar ciclo diário breve e revisão semanal;
- incorporar reentrada e recuperação pós-simulado;
- definir payloads para Tutor e Orquestrador;
- manter os dados de estudo e prova como fontes independentes.

### Fase 4 — Métricas e avaliação

- estabelecer baseline sem impor limiares universais;
- monitorar execução, latência, continuidade e autonomia;
- testar intervenções de maneira N-of-1;
- revisar os efeitos em diferentes rotinas e perfis de concurso.

### Fase 5 — Governança e melhoria contínua

- auditar linguagem, privacidade e encaminhamento;
- revisar técnicas à luz da evidência mais recente;
- separar materiais promocionais de literatura independente;
- registrar intervenções ineficazes e condições em que não funcionaram;
- manter controle de versão e histórico de decisões.

---

## 16. Critérios de aceitação da IMC

O módulo será considerado coerente com a arquitetura quando demonstrar que:

- trata motivação como estado dinâmico e comportamento contextual;
- distingue capacidade, oportunidade, motivação, custo e bem-estar;
- utiliza o manual de forma crítica e com rastreabilidade de capítulos/páginas;
- não apresenta conselhos experienciais como fatos científicos;
- usa evidência de pesquisa com limitações e população explícitas;
- adota diagnóstico baseado em comportamento, não personalidade;
- seleciona uma intervenção com alvo e indicador;
- mede execução e autonomia, não apenas humor ou horas;
- preserva a função pedagógica do Tutor;
- integra dados com o Coach cognitivo e a inteligência adversarial;
- encaminha ao Orquestrador mudanças de prioridade;
- protege saúde, segurança, privacidade e autonomia;
- avalia efeitos e descontinua intervenções que não ajudam;
- não promete aprovação nem exige produtividade ilimitada.

**Decisão recomendada:** adotar `IMC-COACH-001` como referência complementar da estratégia do Coach. A implementação deve ser priorizada e validada por etapas. Este documento é uma proposta de arquitetura e operação, não declaração de que todas as funcionalidades já estejam implementadas.

---

## 17. Referências e fontes

### 17.1 Fonte principal analisada

1. **GRANJEIRO, Gabriel (org./autor de capítulos); colaboradores.** *Manual do Imparável: dicas para você alcançar tudo que busca na vida e nos concursos. Nunca pare!* 2ª ed. Gran Cursos Online, copyright editorial indicado como 10/2020. 391 p. ISBN 978-85-69303-55-8. Arquivo fornecido pelo usuário: `Manual-do-imparavel-Gabriel-Granjeiro-2021.pdf`.
   - Definição de “imparável”: p. 23–29.
   - Preguiça e fricção de início (Fernando Mesquita): p. 68–72.
   - Procrastinação: p. 73–80.
   - Constância: p. 81–87.
   - Retomada após interrupção (Aragonê Fernandes): p. 94–98.
   - Trabalho e estudo: p. 121–128.
   - Ciclos de estudo (Alexandre Meirelles): p. 136–147.
   - Ansiedade: p. 148–153.
   - Atividade física: p. 154–160.
   - Hábitos atômicos: p. 161–173.
   - Seção de motivação: p. 175–390; capítulos especificamente citados ao longo da seção 2.

### 17.2 Motivação e autorregulação

2. **WANG, Y.; WANG, H.; WANG, S.; WIND, S. A.; GILL, C.** (2024). *A systematic review and meta-analysis of self-determination-theory-based interventions in the education context.* Learning and Motivation, 87, 102015. DOI: https://doi.org/10.1016/j.lmot.2024.102015
3. **FONG, C. J.; ALTAN, S.; GONZALES, C.; KIRMIZI, M.; ADELUGBA, S. F.; KIM, Y.-e.** (2024). *Stay Motivated and Carry On: A Meta-Analytic Investigation of Motivational Regulation Strategies and Academic Achievement, Motivation, and Self-Regulation Correlates.* Journal of Educational Psychology, 116(6), 997–1018. Registro ERIC: https://eric.ed.gov/?id=EJ1435050
4. **TRAUTNER, M.; GRUNSCHEL, C.; SCHWINGER, M.** (2025). *Motivating Motivation Regulation Research—An Evidence and Gap Map Approach.* Educational Psychology Review, 37, article 44. DOI: https://doi.org/10.1007/s10648-025-10019-1
5. **WIGFIELD, A.; ECCLES, J. S.** (2000). *Expectancy-Value Theory of Achievement Motivation.* Contemporary Educational Psychology, 25(1), 68–81. DOI: https://doi.org/10.1006/ceps.1999.1015
6. **BANDURA, A.** (1997). *Self-Efficacy: The Exercise of Control.* New York: W. H. Freeman.
7. **MICHIE, S.; VAN STRALEN, M. M.; WEST, R.** (2011). *The behaviour change wheel: A new method for characterising and designing behaviour change interventions.* Implementation Science, 6, 42. DOI: https://doi.org/10.1186/1748-5908-6-42
8. **MICHIE, S. et al.** (2013). *The Behavior Change Technique Taxonomy (v1) of 93 hierarchically clustered techniques: Building an international consensus for the reporting of behavior change interventions.* Annals of Behavioral Medicine, 46, 81–95. DOI: https://doi.org/10.1007/s12160-013-9486-6
9. **GERSIB, J. A. et al.** (2024). *Motivational interviewing for students in school settings: A meta-analysis.* Journal of School Psychology, 107, 101386. DOI: https://doi.org/10.1016/j.jsp.2024.101386

### 17.3 Metas, procrastinação e formação de hábitos

10. **HARKIN, B. et al.** (2016). *Does monitoring goal progress promote goal attainment? A meta-analysis of the experimental evidence.* Psychological Bulletin, 142(2), 198–229. DOI: https://doi.org/10.1037/bul0000025
11. **WANG, G.; WANG, Y.; GAI, X.** (2021). *A Meta-Analysis of the Effects of Mental Contrasting With Implementation Intentions on Goal Attainment.* Frontiers in Psychology, 12, 565202. DOI: https://doi.org/10.3389/fpsyg.2021.565202
12. **STEEL, P.** (2007). *The nature of procrastination: A meta-analytic and theoretical review of quintessential self-regulatory failure.* Psychological Bulletin, 133(1), 65–94. DOI: https://doi.org/10.1037/0033-2909.133.1.65
13. **TURNER, M.; HODIS, F. A.** (2023). *A Systematic Review of Interventions to Reduce Academic Procrastination and Implications for Instructor-based Classroom Interventions.* Educational Psychology Review, 35, 118. DOI: https://doi.org/10.1007/s10648-023-09838-x
14. **Time to Form a Habit: A Systematic Review and Meta-Analysis of Health Behaviour Habit Formation and Its Determinants.** (2024). Healthcare, 12(23), 2488. DOI: https://doi.org/10.3390/healthcare12232488
15. **RAMADHANI, E.; SETIYOSARI, P.; INDRESWARI, H.; SETIYOWATI, A. J.; PUTRI, R. D.** (2026). *Academic procrastination: A systematic review of causal factors and interventions.* Journal of Behavioral and Cognitive Therapy, 36(1), 100552. DOI: https://doi.org/10.1016/j.jbct.2025.100552

### 17.4 Ansiedade de prova e intervenções

16. **HUNTLEY, C. D.; YOUNG, B.; TEMPLE, J.; LONGWORTH, M.; TUDUR SMITH, C.; JHA, V.; FISHER, P. L.** (2019). *The efficacy of interventions for test-anxious university students: A meta-analysis of randomized controlled trials.* Journal of Anxiety Disorders, 63, 36–50. DOI: https://doi.org/10.1016/j.janxdis.2019.01.007. Registro PubMed: https://pubmed.ncbi.nlm.nih.gov/30826687/

### 17.5 Benchmark público de plataformas de concursos

17. **Gran Cursos Online.** Mentoria para concursos / GranXperts: https://blog.grancursosonline.com.br/mentoria-para-concursos/
18. **Gran Cursos Online.** Página pública de mentorias: https://www.grancursosonline.com.br/mentorias-para-concursos
19. **Direção Concursos.** Página pública da mentoria: https://ofertas.direcaoconcursos.com.br/promo/mentoria
20. **Folha Dirigida / Qconcursos.** Acompanhamento e mentorias do Qconcursos, publicação de 16/12/2025, atualização de 18/05/2026: https://folha.qconcursos.com/n/mentoria-para-concurso-como-funciona

### 17.6 Nota epistemológica final

Os estudos citados têm populações, métodos e resultados diferentes. Meta-análises correlacionais não provam causalidade; estudos em estudantes escolares ou universitários não demonstram automaticamente o mesmo efeito em candidatos adultos de concursos brasileiros; materiais de plataformas descrevem serviços, não eficácia independente; e o *Manual do Imparável* reúne recomendações e experiências, não validação clínica ou psicométrica. A implementação da IMC deve, portanto, começar como sistema de hipóteses e experimentos comportamentais monitorados, respeitando autonomia, saúde e contexto.

---

**Fim do documento — `IMC-COACH-001`, versão 1.0.**
