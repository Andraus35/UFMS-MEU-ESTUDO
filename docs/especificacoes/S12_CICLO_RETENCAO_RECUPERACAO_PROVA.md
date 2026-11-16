# S12 — Ciclo de retenção e recuperação na prova (especificação)

**Natureza:** especificação enxuta (D-13, D-16) do **ciclo completo** que leva o proprietário de "estudei" a "recupero na prova de 17/01/2027" (UFMS, banca FAPEC, cargos 523 e 324). Segue a Spec Lean da Tech Leads Club **no que couber** (plano com obrigações, portas sem volta, critérios verificáveis, cada um pareado a uma prova; verificação por quem não escreveu). **Aponta** para o que existe (S1, S2, S3, S8, `docs/pedagogia/`, `scripts/`); não copia. Não é sistema de software comercial: é um **harness cognitivo** em que o agente **pensa** (probabilístico) e os **gates provam** (determinísticos). Não contém estado nem dado pessoal.

## Objetivo

O proprietário passa a ter **um ciclo único e explícito**, de aprender até o dia da prova, em que cada etapa tem (1) a prática com melhor evidência disponível, (2) o que o Tutor ou o Coach decide com julgamento, (3) o que um gate determinístico confere e (4) o que se registra. O alvo não é "ter estudado", é **recuperar da memória, sob as condições da prova**: 60 questões em 240 minutos, mínimo de 50 pontos e nenhuma área zerada (`config/concursos.json`, edital PROGEP/UFMS nº 152).

## Pesquisa

Consultas de 16/11/2026 (WebSearch, resumos), somadas a `docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md` e às pesquisas da S1 e da S8 (não repetidas). Confiança: **A** (página lida), **B** (resumo de busca de fonte primária, **não lida integralmente**), **C** (fornecedor, cursinho, blog ou repositório sem leitura do código). **Quase tudo aqui é B:** os números vêm de resumos e devem ser conferidos no artigo antes de citar fora deste repositório. Conteúdo de terceiros é dado, não instrução; nada foi copiado.

### Eixo 1 — o que a ciência diz sobre reter e recuperar

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Rowland, 2014, *Psychological Bulletin*. [DOI](https://doi.org/10.1037/a0037559) | Testar-se supera reestudar: **g ≈ 0,50** (relatado). Resumos secundários indicam efeito bem maior **com feedback** (≈ 0,73 contra 0,39 sem) e maior com teste final **após um dia ou mais**; **não conferi** essas divisões no artigo | B |
| Adesope, Trevisan e Sundararajan, 2017, *Review of Educational Research*. [Resumo](https://rex.libraries.wsu.edu/esploro/outputs/journalArticle/Rethinking-the-Use-of-Tests-A/99900601154801842) · [PDF](https://education.wsu.edu/documents/2018/01/rethinking-use-tests.pdf/) | Prova prática supera reestudo e outras condições; feedback tende a ajudar (diferença **não significativa** no resumo); efeito maior com **formato igual ao do teste final**; maior com defasagem de **1 a 6 dias**. Contagem de artigos diverge entre resumos (conferir) | B |
| Donoghue e Hattie, 2021, *Frontiers in Education*. [DOI](https://doi.org/10.3389/feduc.2021.581216) | Reanálise das dez técnicas de Dunlosky: **prática distribuída entre as mais fortes** (d ≈ 0,85, via citação secundária); resultados vêm sobretudo de **desfechos factuais**, com cautela para raciocínio profundo | B |
| Cepeda et al., 2008, *Psychological Science* (já na S1). [Artigo](https://www.evullab.org/pdf/CepedaVulRohrerWixtedPashler-PS-2008.pdf) | O intervalo ótimo entre estudos cresce com o prazo até o teste, mas cai em proporção a ele. Para **62 dias** até a prova (a partir de 16/11), intervalos de uma a duas semanas são **coerentes** com o padrão D-11, **sem provar** que 7, 15 e 30 sejam ótimos | B |
| Rawson e Dunlosky, **reaprendizagem sucessiva**. [Revisão de 2022](https://journals.sagepub.com/doi/full/10.1177/09637214221100484) · [Revisão de 2023](https://link.springer.com/article/10.1007/s10648-023-09809-2) | Praticar **até um critério** de acerto e **repetir em sessões espaçadas** sustenta retenção (em estudo de curso, ainda alta 24 dias depois). Retorno **decrescente** do critério da primeira sessão; poucos estudos (cerca de oito na revisão); controle de exposição total nem sempre existe | B |
| Rohrer e Taylor, 2006, *Applied Cognitive Psychology*. [DOI](https://doi.org/10.1002/acp.1266) | Em matemática, **exercícios extras na mesma sessão (supraaprendizagem) não ajudaram** em 1 e 4 semanas; **distribuir** ajudou muito aos 4 semanas. Amostra universitária pequena e prazos curtos | B |
| Murre e Dros, 2015, *PLoS ONE*. [DOI](https://doi.org/10.1371/journal.pone.0120644) | Replicação de Ebbinghaus com **um sujeito** (70 h): curva semelhante à original, com um **salto a partir de 24 h**. Serve de lembrete de que o esquecimento é rápido no início, **não** de parâmetro para o plano | B |
| Pan e Sana, 2021, *J. Exp. Psychol.: Applied*. [PDF](https://sc-pan.github.io/pdf/PS_2021.pdf) | **Pré-teste** (tentar antes de estudar) pode superar o pós-teste em texto até 48 h depois; sem feedback o efeito falha em alguns estudos. Evidência de laboratório, com textos enciclopédicos | B |
| Kang, McDermott e Roediger, 2007. [PDF](https://www.gwern.net/docs/spaced-repetition/2007-kang.pdf) | Com feedback, prática por **resposta curta** deu o melhor desempenho no teste final; o resumo que li não permite afirmar o efeito sobre múltipla escolha | B |
| Murayama et al., 2014, *Psychological Bulletin*. [DOI](https://doi.org/10.1037/a0037505) | **Esquecimento induzido pela recuperação:** praticar alguns itens pode **prejudicar** a lembrança de itens relacionados **não praticados**; há ressalva para material bem integrado e teste após 24 h. Risco para revisão **seletiva** de tópicos parecidos (legislação) | B |

### Eixo 2 — condições da prova: contexto, estresse, calibração, sono

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Smith e Vela, 2001, *Psychonomic Bulletin & Review*. [DOI](https://doi.org/10.3758/BF03196157) | Dependência de **contexto ambiental**: efeito real e **modesto** (d ≈ 0,28; 93 efeitos). **Reinstalar mentalmente** o contexto no teste reduz a diferença | B |
| Smith, Floerke e Thomas, 2016, *Science*. [DOI](https://doi.org/10.1126/science.aah5067) · [resumo](https://www.sciencedaily.com/releases/2016/11/161124160426.htm) | Em laboratório (cerca de 120 estudantes), **estresse agudo prejudicou** quem só reestudou e **não** quem praticou recuperação. Não testou prova real nem ansiedade de prova; Hinze e Rapp, 2014, achou que **pressão** durante a prática pode reduzir o benefício | B |
| Butterfield e Metcalfe, 2001, e Metcalfe e Finn. [Revisão](https://pmc.ncbi.nlm.nih.gov/articles/PMC3079415) | **Hipercorreção:** erros cometidos com **alta confiança** são mais corrigidos depois do feedback que os de baixa confiança; vale para perguntas de conhecimento geral. Há condição de contorno (perguntas capciosas) | B |
| Koriat e Bjork, 2005. [PDF](https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/2005-Koriat-Bjork-JEPLMC-KBA.pdf) | **Ilusão de competência** durante o estudo, porque a resposta está à vista ao julgar; julgamento **tardio e a partir da pista** prevê melhor a memória futura | B |
| Diekelmann, Wilhelm e Born, 2009, revisão. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2739268) | O **sono após aprender** consolida memória declarativa; mais para traços fracos. Não achei evidência direta sobre sono **na véspera** de prova de concurso | B |

### Eixo 3 — tutor de IA e harness

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Bastani et al., 2025, *PNAS*. [Registro](https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html) | Experimento com quase mil alunos de ensino médio: **GPT sem salvaguardas melhorou a prática assistida e piorou a prova sem IA em cerca de 17%**; o **GPT Tutor com salvaguardas** neutralizou o dano. Base do requisito contra a **muleta** | B |
| Kestin et al., 2024-2025 (RCT, *Scientific Reports*). [Matéria da Harvard](https://news.harvard.edu/gazette/story/2024/09/professor-tailored-ai-tutor-to-physics-course-engagement-doubled/) | 194 alunos de física em Harvard: tutor de IA bem desenhado superou aula de aprendizagem ativa em ganho e tempo. **Um curso, intervenção curta, só Harvard**; o próprio grupo diz que não substitui aulas | B |
| MathTutorBench, 2025. [arXiv](https://arxiv.org/pdf/2502.18940) · TutorBench, 2026. [ICLR](https://iclr.cc/virtual/2026/10019695) | Avaliam tutores de IA em **conhecimento, correção de erro do aluno e qualidade pedagógica**; há **tensão entre resolver bem e ensinar bem** (tender a entregar a resposta). Métricas por **modelo-juiz** ou aprendidas podem ser "otimizadas"; não li os conjuntos | B |
| Engram. [Repositório](https://github.com/nagisanzenin/engram) · OpenTutor. [Repositório](https://github.com/zijinz456/OpenTutor) | Padrão público parecido com o nosso: **agendador em código** (FSRS) separado do LLM, tutor que obriga a pensar e um "examinador cego". **Código não lido**; estrelas e maturidade não verificadas | C |
| Benchmark de agendadores. [Expertium](https://expertium.github.io/Benchmark.html) | O FSRS prevê o recall melhor que o SM-2 em milhares de coleções do Anki (as cifras divergem entre fontes). Exige **muitos registros por item**; **não se aplica** com zero eventos | C |

### Eixo 4 — prática de concursos (opinião de cursinho, não estudo controlado)

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Caderno de erros: [Estratégia](https://www.estrategiaconcursos.com.br/blog/caderno-de-erros-para-concurso/amp/), [Direção](https://www.direcaoconcursos.com.br/artigos/concursos-publicos-aprenda-a-fazer-caderno-de-erros) | Registrar **errados e em branco**, em linhas curtas (tópico, causa, regra, artigo), **sem copiar a questão**, com **revisão ativa**; sem revisão vira diário. Cifras de eficiência citadas não têm fonte | C |
| Penalidade e chute: [Correio Braziliense](https://blogs.correiobraziliense.com.br/papodeconcurseiro/7549-2/) | A regra de pontuação **depende do edital** (nem toda prova aplica "uma errada anula uma certa"); sem penalidade, marcar costuma compensar. **Não achei a regra da FAPEC para este edital** | C |
| Spec Lean. [Página oficial](https://agent-skills.techleads.club/skills/tlc-spec-lean/) | Processo: plano com portas sem volta e critérios, **checks** (afirmação + prova que decide), construção e **verificador independente**. A skill **não está instalada** neste ambiente; usei o que a página descreve, adaptado (D-13) | A |

- **Lacunas:** não há estudo controlado do ciclo **completo** (aprender, reter, revisar, recuperar) em candidatos a concurso; nenhum estudo compara o Método 4.2 ou a revisão em 7, 15 e 30 dias; o efeito de **simulado cronometrado** e de **dormir bem na véspera** veio de blogs de fornecedores ou de nada, **não de evidência primária**; a cadência de simulados e a **duração da fase final** são **hipóteses**, não achados; não li o artigo original de nenhuma fonte B (números de Rowland, Donoghue e Hattie, Smith e Vela, Bastani podem diferir do texto); não li o código de Engram e OpenTutor; a regra de penalidade, o formato das alternativas e o gabarito da FAPEC para este edital **não foram conferidos**; a pesquisa foi em inglês e português por buscas em resumo, sem acesso a bases pagas; não há evidência de que o conjunto funcione **para este estudante** (E0, zero eventos).

## Ciclo completo

Cada fase diz **quem pensa** (Tutor ou Coach, probabilístico) e **quem prova** (gate, determinístico). "Decide" nunca significa afirmar domínio sem evidência (S1-R7).

| Fase | Pergunta | Prática com evidência (ou hipótese marcada) | O agente decide | O gate prova |
|---|---|---|---|---|
| F0 Alvo | O que a prova cobra? | Formato, pesos, corte e regra de pontuação vêm do edital | Como explicar ao proprietário | Valores de `config/concursos.json`; regra não conferida fica "a confirmar" |
| F1 Aprender | Como entra o conteúdo? | Aprendizagem guiada; tentar antes (pré-teste) quando houver o que tentar; sem releitura como técnica principal | Ordem, explicação, exemplo | Cita tópico do edital (S2-R2); não entrega a resposta antes da tentativa (S2-R1) |
| F2 Fixar | Como fixa no mesmo ciclo? | Questões com **feedback** ao fim do bloco; parar ao atingir o critério (sem supraaprendizagem) | Dificuldade e quantidade **sugerida** | Quantidade e filtros só como sugestão; sem disponibilidade inventada |
| F3 Revisar | Como retém por semanas? | Recuperação espaçada com **reaprendizagem** do que falhou | Quando antecipar, alongar ou encurtar | Datas D+7, D+15 e D+30 e vencidas vêm de `scripts/study_plan.py`; desvio só com registro (R5) |
| F4 Corrigir | O que fazer com o erro? | Erro com **alta confiança** primeiro; caderno de erros curto | Causa provável, regra correta | Registro mínimo e dados pessoais só no privado (R6, R7) |
| F5 Calibrar | Sei o que sei? | Confiança antes do gabarito; julgamento **tardio** | Leitura da calibração | Estatística com n e período (S3-R4, S3-R5) |
| F6 Treinar a prova | Aguento 60 questões em 240 min? | Simulado **nas condições** da prova, no turno do cargo | Quando e qual simulado | Pontuação e corte por `scripts/simulado_score.py`; independência e condições registradas (R8, R9) |
| F7 Fase final | O que fazer nos últimos dias? | Revisão cumulativa guiada pelo caderno de erros (**hipótese**) | Quanto e o quê | Só proposta com o humano; padrão do plano não muda sozinho (S1-R9) |
| F8 Dia da prova | Como recupero lá? | Estratégia de tempo e marcação; reinstalar o contexto de estudo (efeito **pequeno**) | Texto e checklist | Logística só do edital, com página (R11) |

## Requisitos

Escritos como "quando X, o Y deve Z". A **prova** de cada um é o critério de aceite; os testes de código são **tarefas próprias** (lista no Aceite), com fixtures sintéticas.

| ID | Requisito | Critério de aceite |
|---|---|---|
| S12-R1 | **Alvo vindo do edital:** quando o Tutor ou o Coach falar de formato, pesos, corte, tempo ou **regra de pontuação**, o valor deve vir de `config/concursos.json` ou do edital com página (S2-R2). Se a regra de penalidade ou o formato das alternativas não estiver conferido, a resposta deve dizer "a confirmar no edital" e **não** recomendar marcar ou deixar em branco. | Teste de contrato com fixtures: pergunta sobre chute sem regra no estado → resposta contém "a confirmar"; com regra e página citada → recomendação permitida. Hoje a regra da FAPEC consta como lacuna. |
| S12-R2 | **Nenhuma área fica sem preparo:** como a prova elimina quem zera uma área (Português, Inglês, Legislação, Raciocínio Lógico, Específicos), o harness deve relatar, a cada plano e a cada simulado, as áreas **sem estudo** ou **sem evidência**. O Tutor decide o que fazer, mas **não pode omitir** a área do relato. | Teste do relato sobre fixture de plano com área ausente → aparece como "sem preparo"; plano com as cinco áreas → sem alerta. |
| S12-R3 | **Pontos em jogo, não só tópicos:** a prioridade deve considerar os pontos por questão da área (Legislação, Raciocínio e Específicos valem 2 pontos por questão; Português e Inglês, 1) **e** a lacuna de evidência. Com E0 não há ranking por domínio: o Tutor diz que a ordem é hipótese. | Teste do cálculo de pontos a partir de `config/concursos.json`; fixture E0 → texto "ordem é hipótese" e nenhum percentual de domínio (E0-E4 não é domínio). |
| S12-R4 | **Recuperação antes da reexposição, com feedback depois:** toda revisão prescrita deve começar por uma **tentativa de lembrar ou resolver** antes de ver a anotação ou o gabarito; o feedback correto vem **ao fim** da tentativa; **reler ou grifar não é a técnica principal**. A **escada de dicas** (dica mínima, dica maior, só então a explicação) vale contra a muleta (Bastani). | Validador do prompt de revisão (**PR-002**, tarefa própria) sobre fixtures: "reler o resumo" como atividade principal → recusa; "recorde e escreva antes de abrir" → aceita; resposta completa antes da tentativa → recusa (S2-R1). |
| S12-R5 | **Espaçamento e reaprendizagem com registro:** as datas D+7, D+15 e D+30 vêm **só** de `scripts/study_plan.py` (S1-R2), nunca do LLM. O item que **falha** numa revisão volta como "reaprender" e o Tutor **pode** propor revisão adicional mais curta; qualquer desvio do padrão D-11 exige registro {tópico, de, para, motivo, evidência com n e período}. Atingido o critério da sessão, **não** se acrescenta repetição na mesma sessão (supraaprendizagem); o tempo vai para a próxima sessão espaçada. | Teste de recusa: desvio sem motivo ou sem evidência → erro; teste de datas conferindo o plano; texto do Tutor proíbe "mais uma rodada hoje" após o critério. Padrão D-11 inalterado (C5 do `doc_cohesion`). |
| S12-R6 | **Confiança antes do gabarito:** quando o proprietário reportar resultados, o Tutor **pede** a confiança declarada (alta, média, baixa) por questão ou por bloco, **sem exigir**. Erro com **alta confiança** é marcado "erro confiante" e entra primeiro na revisão. A calibração mostra **n e período** e trata a confiança como autorrelato. | Teste sobre fixture com erros de confianças diferentes → ordem da revisão põe os confiantes antes; relatório sem n ou período → recusa (S3-R4). Sem confiança informada, o campo fica "desconhecido", não zero. |
| S12-R7 | **Caderno de erros mínimo e ativo:** cada entrada tem {tópico do edital, causa provável, regra correta, referência (artigo ou página), data} e **não copia a questão inteira**; erros **e** questões em branco entram. A revisão é **ativa** (cobrir e recordar). O **conteúdo** do caderno é dado pessoal: mora só no repositório **privado** (D-24); o público guarda apenas o esquema. | Teste do esquema com fixture sem dado pessoal; `scripts/write_policy.py --check` e `settings.json` mantêm `personal_results_writes_enabled` falso (S1-R8); entrada com texto de questão acima do limite do esquema → recusa. Prática de cursinho, **não evidência** (marcar). |
| S12-R8 | **Simulado nas condições da prova:** o simulado deve usar o formato (60 questões, 240 minutos, as cinco áreas e seus pesos), o **turno do cargo** (523 de manhã, 324 à tarde, segundo `config/concursos.json`), cronômetro, sem consulta e questões **inéditas** (independência). As condições entram no registro. O efeito de contexto é **pequeno** (d ≈ 0,28): o simulado treina **processo e resistência**, não substitui a revisão espaçada. A **cadência** é proposta do Tutor com evidência; sem proposta, o padrão do protocolo de simulados vale. | Fixture de registro de simulado sem condições ou sem independência → o diagnóstico recusa afirmar tendência (`docs/pedagogia/PROTOCOLO_SIMULADOS_v1.4.md`, seções 3, 5 e 7); `tests/` do simulado existente continuam passando. |
| S12-R9 | **Corte e áreas calculados em código:** a nota do simulado e as regras eliminatórias (mínimo de 50 pontos e nenhuma área zerada) vêm de `scripts/simulado_score.py`, nunca do LLM. O Tutor interpreta o resultado, declara limites e **não converte** E0-E4 em domínio. | Teste do script com fixtures de corte (49, 50 pontos; área zerada); texto sem número calculado por LLM (revisão humana). Retificações do edital não verificadas (`retificacoes_verificadas`: falso) aparecem como aviso. |
| S12-R10 | **Fase final como proposta, não padrão:** o Tutor **pode** propor, com o proprietário e com evidência, uma fase final com revisão cumulativa guiada pelo caderno de erros e pela lacuna por ponto em jogo, e **sem tópicos novos** nos últimos dias. Isso é **hipótese de prática**, sem estudo que fixe o número de dias. O padrão do plano (`final_phase_days`) fica **0** até a decisão (S1-R9). Sono e descanso entram como **orientação geral**, sem conselho clínico (S3-R8). | Teste de que `settings.json` não define a fase final; proposta sem justificativa → recusa; texto sobre sono sem diagnóstico ou prescrição médica (revisão humana). |
| S12-R11 | **Dia da prova com fonte:** o Tutor entrega, com antecedência, um roteiro com (a) logística tirada do edital **com página** (documento, local, horário, regras), nunca presumida; (b) **estratégia de tempo**: orçamento por área calculado a partir dos pontos e da duração, ordem por pontos por minuto com **marcar e voltar** (prática de cursinho, **C**) respeitando a regra da área; (c) reinstalação mental do contexto de estudo, **sem prometer efeito**. O Coach só lembra em rotina autorizada (S8, S3-R9). | Teste do roteiro: item de logística sem página → recusa (`scripts/fact_gate.py`); orçamento de tempo soma 240 minutos nas fixtures; sem regra de penalidade conferida, o roteiro **não** manda chutar (R1). |
| S12-R12 | **Pensar e provar, separados:** o agente decide **com julgamento** abordagem, explicação, ordem, causa provável, material de revisão e propostas; o harness **prova com código** datas e intervalos, pontos e corte, citação do edital, ausência de vazamento de resposta, registro de desvio, ausência de afirmação de domínio sem evidência e **ausência de persistência declarada sem readback**. Nenhum desses pontos pode depender de o LLM "lembrar". | Cada ponto tem o teste ou gate nomeado nas linhas anteriores; `scripts/doc_cohesion.py --check` garante a presença desta especificação e do vínculo no `work_queue`; testes novos entram como tarefas do Aceite. |
| S12-R13 | **Honestidade sobre eficácia:** toda recomendação do ciclo informa o **tipo de evidência** (A, B ou C, ou hipótese) e **não promete** que o conjunto funcione para o proprietário. Os números desta especificação são de resumos (B) e precisam ser conferidos antes de qualquer afirmação fora do repositório. | Revisão humana; o tutor cita "hipótese" quando a fonte é C ou ausente (S2-R8). |

## Portas sem volta (Spec Lean)

Decisões difíceis de desfazer, ditas literalmente para que **só o proprietário** as passe:

1. **Mudar o padrão D-11** (Método 4.2 e revisão em 7, 15 e 30): só por proposta registrada e aprovação humana.
2. **Gravar resultados ou o caderno de erros em qualquer lugar:** continua **proibido** (`personal_results_writes_enabled=false`); depende de P4, S7 e PR próprio com aprovação (D-24).
3. **Alterar `AGENTS.md`** ou o escopo oficial: aprovação humana.
4. **Recomendar chute ou deixar em branco** sem a regra do edital conferida: proibido.

## Aceite

Para **este** PR (só especificação):

1. `python scripts/doc_cohesion.py --check` passa (C7: pesquisa com links e lacunas; C8: item `S12` no `work_queue`).
2. `python scripts/product_gate.py --check`, `roadmap_gate`, `governance_sync_gate` e `single_flow_gate --check` passam; a suíte de testes passa; a CI fica verde no HEAD.
3. A S12 **não cria** código, job, mensagem, notebook nem grava dado pessoal; não toca em `scripts/tool_gateway.py`.
4. **Verificação:** feita pelo autor (**self-verified**, como a Spec Lean prevê sem sub-agente); a conferência independente fica para a revisão do proprietário.

**Tarefas derivadas (cada uma é um PR próprio, em série, com testes sintéticos e contraprovas):**

| Item | O que implementa | Requisitos |
|---|---|---|
| D1 | Validador do prompt de revisão e escada de dicas (**PR-002**) | R4 |
| D2 | Registro de desvio do padrão e relato de áreas sem preparo no `study_plan.py` | R2, R5 |
| D3 | Confiança por questão no esquema de resultado e ordem da revisão (**PR-015** e **PR-008**) | R3, R6 |
| D4 | Esquema do caderno de erros (sem dado pessoal) | R7 |
| D5 | Roteiro do dia da prova com orçamento de tempo e gate de logística com página | R1, R11 |
| D6 | Condições e independência no registro de simulado | R8, R9 |

## Limites

- **Não prova** que o ciclo faz o proprietário recuperar mais na prova: as evidências são de laboratório, de estudantes de outros contextos e de blogs; efeitos de sono, simulado e fase final são **hipóteses**.
- **Pontos a confirmar pelo proprietário:** a **cadência de simulados**; a **duração da fase final** (0 por padrão); se aceita informar **confiança** por questão; se o caderno de erros entra no repositório privado; a regra de pontuação e o formato das alternativas conferidos no edital da FAPEC.
- A regra de penalidade e o formato das alternativas **não foram conferidos** neste edital; enquanto isso a recomendação de marcar ou deixar em branco fica **suspensa** (R1).
- Não contém horário, ritmo, plano nem resultado do proprietário; não habilita a escrita de resultados nem altera o `AGENTS.md`.
- A Spec Lean foi aplicada **no que couber** (D-13): sem sub-agente verificador nem scripts da skill neste ambiente.
