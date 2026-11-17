# S13 — Integração dos conceitos cognitivos (especificação)

**Natureza:** especificação enxuta (D-13, D-16), segundo a Spec Lean da Tech Leads Club **no que couber**: plano com portas sem volta, requisitos pareados a uma prova e verificação por quem não escreveu. **Reconcilia** os documentos canônicos de `docs/canonicos/` (pesquisa adversarial, ciclo de aprendizagem e bases cognitivas) com S2, S3, S12 e o D-23, nos sete pontos que o `docs/canonicos/README.md` deixou abertos. **Aponta** para o que existe; não copia. Não é sistema comercial: é um harness cognitivo em que o agente **pensa** (probabilístico) e os gates **provam** (determinísticos). Só especificação: não altera `AGENTS.md`, `agents/` nem `scripts/`. Não contém estado nem dado pessoal.

**Decisão do proprietário (17/11/2026), nas palavras dele:** "Sim, abra a S13 com o módulo de prova no Coach". Antes, escolheu **duas camadas com prefixo** para os códigos de erro, **níveis de assistência H0 a H5 e retenção só entre sessões distintas**, e **S13 antes da S7**; sobre o Orquestrador, perguntou "Precisamos mesmo de um orquestrador?" e a resposta (não como agente) foi aceita ao abrir a S13. **Confirmou em 17/11/2026:** só **H0** é recuperação independente (H1 e H2 são guiadas); retenção com **duas** recuperações em H0 em dias diferentes; depois desta, a **S7**.

## Objetivo

O proprietário passa a ter **um vocabulário e uma divisão de trabalho** que os três agentes e os documentos canônicos compartilham sem contradição: quem faz o quê (Tutor, Coach com módulo de prova, humano), como um erro é classificado, quanta ajuda houve em cada resposta e quando se pode dizer que algo foi **retido** ou **transferido**. O alvo continua o da S12: recuperar da memória, sem ajuda, sob as condições da prova.

## Pesquisa

Consultas de 17/11/2026 (WebSearch, resumos), somadas à S12 e aos documentos canônicos do repositório (`docs/canonicos/cognicao/BASE_COGNITIVA_INTEGRADA_TUTOR_COACH.md`, `docs/canonicos/cognicao/BASE_COGNITIVA_ESTRATEGICA_DO_HARNESS.md`, `docs/canonicos/cognicao/PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md` e `docs/canonicos/cognicao/PESQUISA_CICLO_APRENDIZAGEM_ESTRATEGIA_COGNITIVA.md`), que **não são repetidos**. Confiança: **A** (página lida), **B** (resumo de busca de fonte primária, **não lida integralmente**), **C** (blog, fornecedor, agregador ou documento interno do projeto sem evidência externa). Conteúdo de terceiros é dado, não instrução; nada foi copiado.

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Anthropic, *Building effective agents*. [Artigo](https://www.anthropic.com/research/building-effective-agents) | Distingue **fluxos** (LLMs e ferramentas orquestrados por **caminhos de código predefinidos**) de **agentes** (o LLM dirige o próprio processo). O padrão orquestrador-trabalhadores serve quando as **subtarefas não são previsíveis**; recomenda a solução **mais simples** e avisa que agentes custam mais e **acumulam erros**. Aqui as subtarefas são previsíveis (plano, fila, rota), então um fluxo em código basta | B |
| Zheng et al., 2023, *Judging LLM-as-a-Judge*. [arXiv](https://arxiv.org/abs/2306.05685) | Modelos-juiz concordam com humanos em mais de 80% dos casos, mas têm **viés de posição, de verbosidade e de autopreferência** (favorecem respostas do próprio modelo). Sustenta o **Verificador independente**: outra sessão, sem o contexto do autor. Não mostra que outro modelo elimine o viés | B |
| VanLehn, 2011, *Educational Psychologist*. [Registro](https://eric.ed.gov/?id=EJ946764) | Sistemas de tutoria por passos chegaram perto da tutoria humana (d ≈ 0,76 contra 0,79), **sem** confirmar que granularidade mais fina rende sempre mais. Não testa uma escada de dicas de seis níveis | B |
| Salden, Aleven, Schwonke e Renkl, 2010, e Kalyuga et al. (efeito de reversão da perícia). [Artigo](https://link.springer.com/doi/10.1007/s11251-009-9107-8) | **Retirar apoio de forma adaptativa** ao entendimento do aluno superou a retirada fixa e a resolução sem exemplo; o que ajuda o iniciante pode atrapalhar quem já sabe. Sustenta níveis de assistência que **diminuem com a evidência**, não um calendário fixo. Fonte secundária em parte | B |
| Razzaq e Heffernan (WPI), dicas sob demanda. [PDF](https://web.cs.wpi.edu/~nth/pubs_and_grants/papers/2010/ITS/Razzaq%20Hints%20Is%20It%20Better%20to%20Give%20or%20Wait.pdf) | Aprendeu-se mais com **dicas pedidas pelo aluno** do que com dicas dadas de antemão. Sustenta que a assistência seja **pedida e registrada**, não empurrada | B |
| Haladyna, Downing e Rodriguez, 2002, *Applied Measurement in Education*. [Resumo](https://cpl.health.unm.edu/AssetListing/Writing-Questions-for-Learning-and-Assessment-2573/Rules-for-Multiple-Choice-Items-Haladyna-et-al-2002-5943) | Diretrizes de elaboração: distratores **plausíveis, baseados em erros típicos**; evitar pistas (termos absolutos, alternativa óbvia). Sustenta a camada de **item** da taxonomia e o alerta contra "heurísticas de gabarito". É referência de avaliação educacional, não manual de bancas de concurso | B |
| Documentos canônicos do repositório (`docs/canonicos/README.md`) | Propõem Tutor, Coach de Prova, Orquestrador e Verificador, três listas de códigos de erro, assistência H0 a H5 e gates próprios. **Autorrelato e proposta** de quem os escreveu; as referências deles não foram conferidas | C |

- **Lacunas:** não há estudo da **escada H0 a H5** como desenhada (a fonte é o documento canônico), nem de um limite para "ajuda decisiva", então a **fronteira de independência** (só H0 conta) foi **proposta minha** e o proprietário a confirmou em 17/11/2026, sem evidência externa; não achei evidência sobre **orquestradores de LLM** em tutoria de concurso, só orientação geral de engenharia de agentes; a exigência de **duas recuperações em dias diferentes** para declarar retenção é **hipótese de prática**, sem estudo que fixe o número; não li o artigo original de nenhuma fonte B; o efeito de um **módulo de prova** dentro do Coach não foi testado em ninguém; não consultei provas reais da FAPEC, então a camada de **item** vale como vocabulário de análise, não como retrato da banca; as taxonomias dos documentos canônicos vêm de **três autorias com códigos que colidem** e não foram validadas contra um conjunto de questões.

## Plano

### O que muda e o que não muda

| Ponto reconciliado | Decisão desta especificação |
|---|---|
| Papel do Coach | **O mesmo Coach da S3, com dois módulos**: rotina (S3, S8) e **prova** (análise de item, estratégia, condições de simulado). Sem agente novo |
| Orquestrador | **Função, não agente**: código determinístico mais o humano como árbitro (R2) |
| Verificador | **Sessão independente**, sem o contexto do autor (D-23), não um perfil novo |
| Códigos de erro | **Três prefixos** (aprendizagem, item e meta) com tabela de conversão das três fontes (R4) |
| Assistência e retenção | **H0 a H5**; retenção só com recuperações em dias diferentes; transferência só com item novo (R5, R6) |
| Intervalos | **D-11 prevalece** (D+7, D+15, D+30); D1, D3 e D14 das fontes ficam como hipótese que o Tutor pode propor com evidência |
| Confiança | **S12-R6 prevalece** (alta, média, baixa por bloco); a escala 0 a 4 das fontes não é adotada |

### Portas sem volta

1. **Alterar `agents/COACH.md` ou `agents/TUTOR.md`:** exige PR com aprovação humana (T4). Esta especificação **não** os altera.
2. **Alterar o `AGENTS.md` ou o START** para ler os documentos canônicos: exige aprovação humana (T5).
3. **Criar um agente ou perfil novo** em `agents/`: fora desta especificação; se surgir a necessidade, é decisão do proprietário.
4. **Gravar resultados, assistência ou o caderno de erros:** continua proibido (`personal_results_writes_enabled=false`); depende de P4, S7 e PR próprio (D-24).
5. **Mudar o padrão D-11:** só por proposta registrada e aprovação humana.

## Requisitos

Escritos como "quando X, o Y deve Z". A **prova** de cada um é o critério de aceite; testes de código são **tarefas próprias** (lista no Aceite), com fixtures sintéticas e contraprovas.

| ID | Requisito | Critério de aceite |
|---|---|---|
| S13-R1 | **Coach com dois módulos.** O Coach da S3 passa a ter o módulo **rotina** (S3, S8) e o módulo **prova**. O módulo prova **pode**: classificar item e erro na camada de item (R4); desmontar a questão pelo protocolo de 12 passos do documento adversarial (comando, polaridade, sujeito, ação, objeto, condições, abrangência, temporalidade, fundamento, consequência, relações, julgamento); recomendar a **estratégia de tempo e risco** com a regra do edital (S12-R1, S12-R11); especificar as **condições do simulado** (S12-R8, S12-R9); emitir o registro de passagem ao Tutor (R3). Ele **não pode**: produzir conteúdo, questão ou material (o Tutor é o único produtor, D-23); registrar resultado (`registrar_resultado` é só do Tutor); ensinar conteúdo; usar operações fora das do Coach. | `scripts/agents_gate.py --check` continua passando com as operações atuais (nenhuma operação do Tutor no Coach); teste de contrato desta especificação garante que a lista "pode" e "não pode" está presente e que nenhum arquivo novo existe em `agents/`. A mudança do perfil é a tarefa T4, com aprovação. |
| S13-R2 | **Orquestração é função, não agente.** Priorizar, rotear e encaminhar é feito por código determinístico: `scripts/decision_queue.py` (fila e prioridade explicável), `scripts/session_route.py` (rota da sessão), `scripts/next_task.py` (próximo item), `scripts/study_plan.py` (datas) e `scripts/evidence_projection.py` (níveis de evidência). Em **conflito** entre Tutor e Coach, ou diante de **causa mista**, a decisão é do **humano**; o agente recomenda e **não** arbitra. **Não existe orquestrador-LLM.** O **Verificador** é uma sessão que **não escreveu** o conteúdo e **não recebe a conclusão** do autor, só critérios, fontes e registros (D-23, `scripts/review_provenance.py`); não é perfil permanente. | Teste de contrato: os cinco scripts existem; nenhum perfil novo em `agents/`; texto de conflito remete ao humano (S3-R6). Prova de que o Verificador não é o autor: registro de proveniência do `scripts/review_provenance.py`, já testado. |
| S13-R3 | **Encaminhamento e registro de passagem.** Falta de conhecimento ou compreensão, recuperação sem pista, esquecimento e dependência de pista vão ao **Tutor**; erro de comando, negação, quantificador, extrapolação, estratégia, risco ou tempo vão ao **Coach (prova)**; confusão de conceitos, falha de aplicação e de transferência vão a **ambos**; **causa mista ou incerta**, a diagnóstico complementar e, se persistir, ao humano. O registro de passagem tem, no mínimo: tópico do edital, **origem e proveniência do item** (oficial, banco, adaptado ou sintético), **referência** ao item (nunca o texto da questão), resposta, referência ao fundamento verificado, confiança por bloco (S12-R6), **nível de assistência** (R5), tempo, **códigos de erro com evidência e incerteza** (R4), objetivo e **critério de reteste com item novo**. O dado real mora **só no repositório privado** (D-24); o público guarda apenas o esquema. | Esquema do registro validado em tarefa própria (T3) com fixtures sem dado pessoal; recusa de registro sem origem do item, sem assistência ou com texto de questão. Hoje a tabela de encaminhamento está nesta especificação e nos canônicos. |
| S13-R4 | **Taxonomia de erros em três prefixos, com conversão.** Prefixo **L-** (aprendizagem, camada do Tutor): L-KNO conhecimento, L-COM compreensão, L-REC recuperação, L-RET retenção, L-DIS discriminação, L-APP aplicação, L-TRF transferência, L-HNT dependência de pista, L-CAL calibração. Prefixo **P-** (item e prova, camada do Coach): P-SEM semântica, P-QNT quantificador, P-NEG negação, P-EXT extrapolação, P-INS institutos, P-INV invenção, P-VIG vigência, P-CPT competência, P-CON condição, P-CNS consequência, P-TAN tangenciamento, P-REL relação lógica, P-CAR carga, P-DEC decisão e risco, P-TEM tempo, P-CMD comando, P-EST estabilidade. Prefixo **M-** (meta): M-SRC fonte, gabarito ou norma sem validação; M-ITM item ambíguo, anulado ou defeituoso. **Regras:** um erro admite **vários códigos**, cada um com evidência; o código **nunca** vem só do gabarito (usar justificativa, confiança, tempo, assistência e histórico); causa incerta fica **marcada como hipótese**; **erro com alta confiança** é prioridade (S12-R6); queda de desempenho **não** vira "fadiga" sem confirmação (P-EST é "a investigar"); erro M- **suspende a pontuação** do item até validação; não se atribui intenção à banca nem se ensina suspeita generalizada. A tabela de conversão abaixo cobre **todo** código das três fontes; os que **colidiam** (CMP) ficam separados. | Teste desta especificação: todo código listado nas tabelas de erro dos três documentos canônicos aparece na conversão; códigos S13 únicos; nenhum código sem prefixo. Catálogo em JSON e validador na tarefa T2. |
| S13-R5 | **Assistência H0 a H5 e independência.** Cada tentativa registra o nível: **H0** nenhuma, **H1** pista geral sobre a categoria, **H2** pista conceitual, **H3** pergunta orientadora, **H4** explicação parcial, **H5** demonstração completa. **Só H0 conta como recuperação independente**; H1 e H2 contam como **guiada**; H3 a H5, como **assistida**. Assistência **não registrada é "desconhecido"**, nunca H0. Em avaliação independente (simulado, reteste) a tentativa **começa em H0** e não se mostra resposta nem pista decisiva antes da tentativa. Pedir a resposta é permitido e vira registro de assistência. Resposta correta depois de H3 ou mais exige **nova tentativa sem ajuda** em outra ocasião. O Tutor **reduz** a assistência conforme a evidência (retirada adaptativa) e a oferece **sob demanda**. A fronteira "só H0" foi **confirmada pelo proprietário** em 17/11/2026 e continua **hipótese de prática**. | Funções de classificação em tarefa própria (T1), com fixtures: tentativa sem campo → "desconhecido"; H0 → independente; H1 e H2 → guiada; H3 a H5 → assistida; resposta mostrada antes da tentativa → recusa (S12-R4, S2-R1). A relação com a dimensão "independência" do `docs/pedagogia/MODELO_EVIDENCIAS_v1.2.md` é: H0 → "sem consulta"; H1 a H5 → "com consulta"; mistura → "misto"; ausência → "desconhecido". |
| S13-R6 | **Retenção e transferência com critério.** Só se declara **retenção tardia** de uma unidade com **duas ou mais recuperações corretas em H0 em dias diferentes** (fuso America/Campo_Grande) e com o **intervalo registrado**; repetições na **mesma sessão não contam** (reaprendizagem sucessiva). Só se declara **transferência** com resposta correta em H0 a um **item novo** (nunca exposto) e de formulação diferente; repetir a mesma questão ou mudar só a aparência **não conta**. Os dois resultados são **rótulos de evidência**, não percentual de domínio nem nota (E0 a E4 não é domínio). Faltando campo, o resultado é **"não declarável"**, nunca aprovação por omissão. O que não foi feito permanece **pendente**: revisão vencida não some. | Funções em tarefa própria (T1), com fixtures: duas H0 no mesmo dia → não retido; H0 em dois dias → retido com intervalo; mesma questão → sem transferência; item novo em H0 → transferência; campo ausente → "não declarável". Intervalos do plano seguem a S1 e o D-11. |
| S13-R7 | **Gates, em ordem de implementação.** G1 **tentativa antes da resposta** (canônico G-LEARN-02, G-HARNESS-03, G-COG-02); G2 **assistência registrada** (G-LEARN-03, G-HARNESS-04); G3 **retenção entre sessões distintas** (G-LEARN-05, G-HARNESS-07, G-COG-05); G4 **transferência com item novo** (G-LEARN-06, G-HARNESS-08, G-COG-06); G5 **cobertura do edital** (G-LEARN-08, G-HARNESS-13; é a S12-R2); G6 **histórico íntegro** (G-HARNESS-09: nova tentativa soma, não apaga; revisão não feita fica pendente). Todos **fecham por padrão**: dado ausente = não passa. São **requisitos**, não implementação: nenhum gate existe hoje. | Cada gate vira função com teste e contraprova na tarefa T1 (G1 a G4 e G6) e no relato de áreas da S12 (G5). Esta especificação só fixa nome, ordem e regra. |
| S13-R8 | **Itens sintéticos sob o D-23.** O módulo prova do Coach **pede** variações de uma questão (alterar quantificador, negação, competência, condição, prazo, consequência, contexto); **quem escreve é o Tutor**, e a verificação é de **sessão independente** (R2). Todo item sintético é **rotulado como sintético**, tem gabarito, fundamento e fonte verificáveis, **nunca** é atribuído à banca nem apresentado como previsão de prova, e a IA **não inventa** norma ou exceção para fabricar uma pegadinha: se não validar, **se abstém** e marca como não validado. Estatísticas **separam** itens oficiais, de banco, adaptados e sintéticos (S3-R4, com n e período). | Teste de esquema do item (T6) com fixtures: item sem rótulo de origem → recusa; sintético sem fundamento ou sem verificação → recusa; estatística que mistura origens → recusa. Proveniência pelo `scripts/review_provenance.py`. |
| S13-R9 | **Precedência e ligação ao START.** Os documentos canônicos continuam **referência**, abaixo de `AGENTS.md`, `PRODUCT.md` e `ROADMAP.md`, e **abaixo desta especificação** nos pontos que ela reconcilia. Ligar os canônicos ao START, aos perfis ou a gates é feito **só** pelas tarefas T4 e T5, cada uma com aprovação humana. Até lá, o Tutor e o Coach **não** afirmam ter lido esses documentos. | Teste desta especificação: `agents/TUTOR.md`, `agents/COACH.md` e o `AGENTS.md` não citam `docs/canonicos`; o `README.md` dos canônicos continua apontando os sete pontos. |
| S13-R10 | **Honestidade.** Toda recomendação indica o tipo de evidência (A, B, C ou hipótese) e não promete eficácia; as fontes desta especificação são resumos (B ou C). A fronteira de independência, o número de recuperações e a cadência são **hipóteses de prática**. O Coach **não** diagnostica fadiga nem dá conselho clínico (S3-R8) e **não** atribui intenção psicológica à banca. | Revisão humana; o texto do Tutor diz "hipótese" quando a fonte é C ou ausente (S2-R8). |

### Conversão dos códigos das fontes

Fontes: **A** = `PESQUISA-COACH-PROVA-001` (adversarial), **C** = `PESQUISA-CICLO-APRENDIZAGEM-001` (ciclo), **I** = `BASE-COGNITIVA-TUTOR-COACH-001` (integrada). Onde o mesmo código tem sentidos diferentes, a coluna "Observação" diz qual.

| Fonte | Código na fonte | Código S13 | Observação |
|---|---|---|---|
| A | KNW | L-KNO | conhecimento |
| A | SEM | P-SEM | |
| A | QNT | P-QNT | |
| A | NEG | P-NEG | |
| A | EXT | P-EXT | |
| A | INS | P-INS | confusão de institutos; vista pelo Tutor como L-DIS |
| A | INV | P-INV | |
| A | TMP | P-VIG | temporalidade normativa (vigência), não tempo de prova |
| A | CMP | P-CPT | **competência** do órgão ou agente; colidia com CMP de compreensão |
| A | CON | P-CON | |
| A | CONC | P-CNS | consequência |
| A | TAN | P-TAN | |
| A | REL | P-REL | |
| A | CAR | P-CAR | |
| A | DEC | P-DEC | |
| A | TEM | P-TEM | tempo de prova |
| A | FAD | P-EST | estabilidade; "a investigar", nunca fadiga automática |
| C | KNO | L-KNO | |
| C | COM | L-COM | |
| C | REC | L-REC | |
| C | MEM | L-RET | retenção instável |
| C | DIS | L-DIS | |
| C | APP | L-APP | |
| C | TRF | L-TRF | |
| C | CAL | L-CAL | |
| C | MIX | vários | causa mista: **vários códigos** com incerteza, não um código próprio |
| I | KNW | L-KNO | |
| I | CMP | L-COM | **compreensão**; colidia com CMP de competência |
| I | REC | L-REC | |
| I | RET | L-RET | |
| I | DIS | L-DIS | |
| I | APP | L-APP | |
| I | TRF | L-TRF | |
| I | HNT | L-HNT | dependência de pista |
| I | SEM | P-SEM | |
| I | CMD | P-CMD | erro de comando |
| I | STR | P-DEC | estratégia e risco; **ou** P-TEM se o problema foi o tempo |
| I | CAL | L-CAL | |
| I | FAT? | P-EST | fadiga **possível**, a investigar |
| I | SRC | M-SRC | suspende a pontuação até validar |

## Aceite

Para **este** PR (só especificação):

1. `python scripts/doc_cohesion.py --check` passa (C1: caminhos citados existem; C7: pesquisa com links e lacunas; C8: item `S13` na fila).
2. `python scripts/product_gate.py --check`, `roadmap_gate`, `governance_sync_gate` e `single_flow_gate --check` passam; a suíte passa; a CI fica verde no HEAD.
3. A S13 **não cria** código, perfil, job, mensagem ou notebook, **não altera** `AGENTS.md`, `agents/` nem `scripts/tool_gateway.py` e **não grava** dado pessoal.
4. **Verificação:** feita pelo autor (**self-verified**, como a Spec Lean prevê sem sub-agente). A conferência independente fica para a revisão do proprietário.

**Tarefas derivadas** (cada uma em PR próprio, em série, com testes sintéticos e contraprovas; as marcadas com **aprovação** não começam sem ela):

| Item | O que implementa | Requisitos |
|---|---|---|
| T1 | Módulo de gates de aprendizagem: classificar independência por H0 a H5, retenção tardia, transferência e histórico íntegro, fechando por padrão | R5, R6, R7 |
| T2 | Catálogo JSON dos códigos L-, P- e M- e validador da conversão | R4 |
| T3 | Esquema do registro de passagem Tutor e Coach, sem dado pessoal | R3 |
| T4 | **Aprovação.** Módulo prova no `agents/COACH.md` e ajuste do `scripts/agents_gate.py`, sem operação nova | R1 |
| T5 | **Aprovação.** Ligar os canônicos ao START (`AGENTS.md` e entrega por hash) | R9 |
| T6 | Esquema e validador do item sintético, com origem e verificação | R8 |

## Limites

- **Não prova** que o módulo de prova, a escada de assistência ou a regra de retenção melhorem o resultado do proprietário: as fontes são de outros contextos e as regras desta especificação são **hipóteses de prática**.
- **Decisões do proprietário (17/11/2026):** só H0 é independente e H1 e H2 contam como guiadas (R5); o mínimo de **duas** recuperações em H0 em dias diferentes (R6). Ambas são **hipóteses de prática**, a rever com dados do primeiro piloto.
- Não contém horário, ritmo, plano nem resultado do proprietário; não habilita a escrita de resultados nem toca em `scripts/tool_gateway.py`.
- A Spec Lean foi aplicada **no que couber** (D-13): sem sub-agente verificador e sem os artefatos `.specs/` da skill, porque a especificação segue o formato do projeto em `docs/especificacoes/README.md`.
