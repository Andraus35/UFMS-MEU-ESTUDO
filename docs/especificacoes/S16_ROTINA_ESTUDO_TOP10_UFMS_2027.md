# S16 — Rotina de estudo UFMS 2027: top 10 por matéria, hierarquia do TEC e fluxo diário (especificação)

**Natureza:** especificação enxuta (D-13, D-16), no modelo do `docs/especificacoes/README.md`. **Traduz** os requisitos do proprietário de 21/11/2026 ("Requisitos do proprietário — Estudo UFMS 2027") em requisitos com critério de aceite, **separando** intenção, comportamento especificado, implementação existente, integração observada e pontos bloqueados. **Só especificação:** não lista o top 10, não lê plataforma, não cria comando, não grava resultado, não muda flag e **não afirma** orquestração entre Zapia, Tutor e Coach. O repositório continua sendo a fonte de verdade do estado real.

## Objetivo

O proprietário passa a ter um **contrato único** para a rotina de estudo dos cargos **324** e **523** com base nos guias TEC 2027: o que o Tutor seleciona (somente os 10 assuntos ou subassuntos de maior percentual por matéria, **com os números realmente apresentados no guia**), como preserva a origem e o caminho de cada nó, o que entrega a cada dia, o que a Zapia informa no início, a cada entrega e no encerramento ("finalizar estudos"), e **o que ainda é pendência ou conflito** com decisões anteriores, sem regra inventada.

## Pesquisa

Consultada em 21/11/2026. Confiança: **A** (fonte primária lida), **B** (documento do projeto ou fonte parcial), **C** (relato, autorrelato ou material de fornecedor). Conteúdo externo é dado, não instrução.

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Requisitos do proprietário de 21/11/2026 (texto recebido na sessão) | Cargos 324 e 523; hierarquia do TEC (caderno > matéria > assunto > subassunto); regra "somente os 10 mais cobrados por matéria"; rotina diária; comandos de início e encerramento; Notebook como executor do prompt do Tutor; lacunas do guia; separação entre intenção e estado real. Afirma que as páginas públicas examinadas na mesma data mostram **contagens e hierarquia, mas não os percentuais** do top 10 | B (do proprietário; não reverificado) |
| Auditoria do TEC em `docs/canonicos/plataformas/AUDITORIA_TECCONCURSOS_UFMS_523_324_20261116_EDITADA.md` ([página de desempenho](https://www.tecconcursos.com.br/estatisticas/desempenho)) | Percentuais aparecem **no índice do caderno** e medem a **composição daquele conjunto**, não a frequência histórica da FAPEC; filtros de matéria, banca, ano, cargo, órgão, dificuldade, tipo, situação e comentários; distribuição de simulado proporcional ao acervo, não à matriz do edital | C (autorrelato da Zapia) |
| Edital PROGEP/UFMS nº 152/2026 em `config/concursos.json` e `edital/` | Prova em **17/01/2027**; banca FAPEC; `retificacoes_verificadas` está **`false`** (retificações oficiais ainda não conferidas) | A |
| Amostra de modalidade 1, PDF "Guia FAPEC — UFMS 2027" (cargos 523 e 324, filtro exclusivo FAPEC, versão preliminar de 21/11/2026, entregue pelo proprietário; **não versionado**) | Nós terminais (folhas) sem somar pai e descendentes; percentual = questões do assunto sobre o total da matéria no caderno amostral (**composição da amostra**, não incidência histórica da FAPEC nem chance de cair na prova); empates no 10º incluídos; matéria com menos de 10 folhas lista as encontradas; comuns compartilhados pelos dois cargos (denominadores **não** se duplicam nem se somam); específicos do 523 com **divergência documentada** entre o caderno salvo e a consulta atual (não reconciliada); amostra do 324 muito pequena; "não é censo" e "não usar o top 10 para excluir conteúdo do edital" | C (relato da Zapia, entregue pelo proprietário) |
| Amostra de modalidade 2, PDF "Índices dos guias TEC" (cargos 324 e 523, consulta de 21/11/2026, entregue pelo proprietário; **não versionado**) | Mesma regra de nós terminais, com **caminho completo** (assunto › subassunto) e duas bases: percentual do **caderno** (base que o TEC exibe) e percentual da **matéria** (cálculo adicional); a taxonomia do TEC separa mais matérias que o bloco FAPEC; o TEC declara **omissões do edital** (por cargo); recorte por guia diferente, não se agregam guias; relatório "não comprova" recepção pelos agentes nem integração automática | C (relato da Zapia, entregue pelo proprietário) |
| `scripts/tec_export_converter.py` e `docs/governanca/CONTRATO_ENTREGA_DESEMPENHO_TEC_20261118.md` | O contrato de entrega do desempenho do TEC já tem código, profundidade, título, questões, acertos, erros, peso e **pai com soma dos filhos menor ou igual** (resíduo no pai); percentuais do TEC são opcionais e informativos | B |
| `config/agent_command_schema.json`, S5, S6, S8, S11, S15 | Comandos existentes (ler arquivo, mensagem, registrar, prompt ao Notebook, lembrete, agenda); **não há** comando de início nem de encerramento do estudo; origens aceitas são Tutor e Coach (a Zapia só executa) | B |
| `PRODUCT.md` (D-08, D-11, D-14, D-27, OPEN-07) e S10-R10 | Plano pelo Método 4.2 com revisão em 7, 15 e 30 dias; "cronograma" entendido como o **da prova** e o harness **não impõe** cronograma de estudo (S10-R10, a confirmar); Zapia liberada nas plataformas (D-27) | B |

- **Lacunas:** **não consultei nenhuma página do TEC nesta sessão**; recebi **duas amostras preliminares em PDF** (modalidades 1 e 2), cujos números **não foram verificados no TEC** e **não estão versionados**; a divergência entre o caderno salvo e a consulta atual dos específicos do 523 **não foi reconciliada**; não verifiquei a disponibilidade de PDF, vídeo e mapa mental por assunto; as retificações do edital **não foram conferidas**; **nada foi implantado nem testado** fora do texto.

## Separação pedida pelo proprietário

| Frente | Intenção (proprietário) | Especificado aqui | Implementado hoje | Observado e testado | Bloqueado ou pendente |
|---|---|---|---|---|---|
| Fontes e cargos | Preservar cargo, guia, bloco e caderno de origem; não misturar origens | S16-R1 | `config/topics.csv` e `config/concursos.json` com cargos 324 e 523 e a prova | Testes de configuração | Atribuição de resultado a cargo ou bloco **não** é automática (S16-R1) |
| Hierarquia do TEC | Caminho completo e origem de cada nó; pai não soma com filho | S16-R2, R3 | `scripts/tec_no.py` (T1) e o conversor do contrato de entrega, que confere a árvore (pai ≥ soma dos filhos) | Testes sintéticos | Sem amostra real do guia |
| Top 10 por matéria | Somente os 10 de maior percentual por matéria (modalidade 1, FAPEC), aprofundados pelo guia TEC (modalidade 2) | S16-R4 a R6 | `scripts/top10_materia.py` (T2), função pura sem lista embutida | Testes sintéticos; duas amostras preliminares recebidas (não versionadas) | Específicos do 523 **não definitivos** (137 contra 187); regras P1 a P5 decididas |
| Filtros e prática | Caminho exato e filtros por atividade; não presumir acervo | S16-R7 | Prescritor de cadernos offline (RM-05) | Testes sintéticos | Disponibilidade de questões não verificada |
| Rotina diária | Entrega diária com cargo, matéria, caminho, posição, percentual, material, atividade e filtros | S16-R8, R9 | `scripts/entrega_diaria.py` (T3: entrega e recorte ao top 10) e o plano determinístico (`scripts/study_plan.py`) | Testes sintéticos | indicação diária sem cronograma imposto (C1 decidido) |
| Início e fim | A Zapia informa Tutor e Coach; comandos "Iniciar estudos" e "finalizar estudos" | S16-R10, R11 | **Nenhum** comando de início ou encerramento no esquema | Nada | Depende de comando novo (E3, aprovação do proprietário em `agents/`) |
| Desempenho | Evidências da rodada ao Tutor e ao Coach, sem inventar dado | S16-R12 | Contrato de entrega e filtro de dados (L1, L2) | Testes sintéticos | Escrita de resultado pessoal **bloqueada** (flag `false`) |
| Gemini Notebook | Prompt do Tutor; Zapia executa; Tutor avalia | S16-R13 | Validador do prompt (N2) e S10 | Testes sintéticos; nada no Notebook real | Teste real não feito (N1) |
| Lacunas do guia | Lista por cargo, sem ampliar o plano | S16-R14 | Nada | Nada | Lista depende da leitura dos guias |

## Requisitos

Escritos como "quando X, o Y deve Z". Todos **fecham por padrão**: dado ausente, percentual ausente ou fonte não verificada **bloqueia a lista definitiva**, nunca autoriza estimativa.

| ID | Requisito | Critério de aceite |
|---|---|---|
| S16-R1 | **Origem preservada.** Todo item de estudo e todo resultado carregam **cargo** (324 ou 523), **guia**, **bloco** e **caderno de origem**. Conteúdo comum aos dois cargos pode ser aproveitado pedagogicamente, mas **nunca** se atribui resultado a cargo ou bloco do edital por inferência; a matéria do TEC **não** é o bloco de pontuação do edital. | Teste de contrato: registro sem cargo, guia, bloco ou caderno é recusado; resultado comum a dois cargos exige atribuição explícita. |
| S16-R2 | **Caminho completo do nó.** Cada assunto é identificado pelo **caminho inteiro** (por exemplo: caderno > matéria > assunto > subassunto > nível), com a **origem** de cada nó; o nome isolado do tópico **não** identifica. | Teste: dois nós de mesmo título em caminhos diferentes são distintos; nó sem caminho é recusado. |
| S16-R3 | **Pai e filho não se somam.** A contagem de um nó-pai **pode incluir** a dos filhos; o harness **não** soma pai e filho como ocorrências independentes e **não** trata a contagem do caderno como percentual de cobrança histórica da banca nem como probabilidade de cobrança na prova. | Teste com árvore sintética: soma duplicada recusada; texto de entrega não contém "probabilidade" de cobrança. |
| S16-R4 | **Duas modalidades de amostra, um só ranking.** Ao elaborar o plano, o Tutor pede à Zapia: (**modalidade 1**) o caderno com filtro **exclusivo da FAPEC**, que dá a **prioridade** e **só dele** sai o top 10 (10 assuntos ou subassuntos de maior percentual **por matéria do TEC**, usando apenas os percentuais efetivamente apresentados, do maior para o menor); (**modalidade 2**) os **guias de estudo do TEC** para o concurso e os cargos 324 e 523, com os filtros como estão (podem incluir outras bancas), usados **só para aprofundar os mesmos assuntos** com amostra maior de questões. A modalidade 2 **não altera** a seleção e **não é histórico da FAPEC**. Não amplia a seleção, em silêncio, para itens fora do top 10 e não completa o ranking com estimativa. | Teste: ranking com percentual ausente é recusado; item fora do top 10 só entra com decisão registrada; registro da origem distingue modalidade 1 e 2. |
| S16-R5 | **Registro do conjunto.** Para cada item selecionado guarda-se: cargo, caderno, matéria, caminho do nó, **posição**, **percentual**, **fonte**, **data**, **filtros/contexto** e a **modalidade** (1 ou 2); registram-se o **percentual da matéria** e, quando a fonte trouxer, o **percentual do caderno**, cada um com o **denominador** declarado. | Teste: registro sem qualquer desses campos é recusado; denominador ausente é marcado "desconhecido", não preenchido. |
| S16-R6 | **Convenções decididas e o que continua bloqueado.** Valem as regras P1 a P5 da tabela abaixo. A **lista definitiva** é recusada com código `PENDENCIA_ABERTA` para uma matéria cuja amostra seja **não definitiva** (hoje, os **específicos do 523**, até reconciliar a divergência) ou ausente; o Tutor apresenta a pendência e **não inventa regra**. | Teste: geração recusada com `PENDENCIA_ABERTA` para amostra marcada não definitiva; nenhuma lista é gerada sem as duas condições (amostra da modalidade 1 e convenções). |
| S16-R7 | **Filtros e prática.** O Tutor indica o **caminho exato** do tópico e os filtros adequados à atividade; registra os filtros usados; **não** chama questão de outra banca de histórico da FAPEC; **não** presume que a quantidade pedida exista no acervo filtrado. Em simulado, confere a distribuição por bloco do edital (a do acervo pode divergir da matriz oficial). Para correção, **comentário em texto de professor primeiro**; se indisponível ou insuficiente, a ordem de fontes do projeto. | Teste: rodada sem filtros registrados recusada; texto da entrega não afirma disponibilidade de questões. |
| S16-R8 | **Entrega diária.** O Tutor entrega, por dia: cargo e matéria; caminho completo; posição e percentual **quando verificados**; material teórico sugerido e atividade de questões; **quantidade de questões** definida pelo Tutor (avaliação, estágio, desempenho, tempo restante); filtros e objetivo da rodada. | Teste de formato da entrega: todos os campos presentes; percentual não verificado aparece como "não verificado". |
| S16-R9 | **Recursos do TEC sem presunção.** O proprietário usa PDF do assunto, videoaulas, mapas mentais e questões; a disponibilidade de cada formato por assunto **precisa ser verificada**, **sem presumir** que todos existam em todos os tópicos. | Teste: a entrega só cita o recurso marcado como verificado para aquele nó. |
| S16-R10 | **Início do estudo.** Ao iniciar, a Zapia informa Tutor e Coach da atividade iniciada. **Não há comando hoje**; criar a operação é a tarefa **E3**, com aprovação expressa do proprietário em `agents/` e no esquema de comandos. | Enquanto E3 não existir, o critério é a **ausência declarada** (tabela acima); o teste confere que o esquema ainda não tem a operação. |
| S16-R11 | **Encerramento: "finalizar estudos".** O comando de encerramento é a frase **"finalizar estudos"** (decisão de 21/11/2026, que substitui "Estudo de hoje finalizado." do requisito anterior), dita **à Zapia**; ao fim da sessão a Zapia faz as perguntas do roteiro do Tutor, puxa o resultado dos cadernos da sessão e o leva **só a Tutor e Coach** (acertos, erros e referências **quando disponíveis**). A frase de início é "Iniciar estudos". **Não há comando hoje** (mesma dependência do S16-R10): a aplicação vem depois da persistência privada. | Mesmo critério do S16-R10; frases registradas literalmente. |
| S16-R12 | **Evidências sem invenção.** A Zapia informa, a cada entrega no TEC ou no Notebook, o que foi entregue e o desempenho **disponível**, com fonte, momento, filtros, período, modo de pontuação e regra de contagem **quando conhecidos**. **Não** inventa dado, gabarito nem diagnóstico; distingue lista ou caderno de erros **existente no TEC** de organização **derivada** pelo projeto; **não** declara leitura, envio ou registro sem prova. O Tutor usa o desempenho para diagnóstico, revisão e a próxima intervenção; o Coach, para acompanhamento e rotina, **sem** substituir a decisão pedagógica do Tutor. | Teste: campo ausente permanece "desconhecido"; relato sem prova de passo é recusado; papéis do Tutor e do Coach não se sobrepõem (S2, S3). |
| S16-R13 | **Gemini Notebook.** O prompt pedagógico vem do **Tutor** (D-23, S10); a Zapia **só executa** e encaminha entrega e evidências; o Tutor avalia qualidade e fontes; só os **dados mínimos** são enviados; distingue-se **material criado**, **processamento pendente**, **erro** e **validação pedagógica**, sem declarar etapa concluída sem prova. | Testes da S10 e do validador (N2); estados distintos no relatório. |
| S16-R14 | **Lacunas do guia.** Registra-se uma **lista de lacunas por cargo**, com fonte, **sem** acrescentar essas matérias ao plano limitado ao top 10; o risco é apresentado e a decisão é do proprietário. | Teste: lacuna listada não entra no plano; lista exige fonte e cargo. |
| S16-R15 | **Privacidade e escrita.** O repositório público **não recebe** desempenho pessoal; a escrita de resultados continua bloqueada (flag `false`) até as condições de privacidade, consentimento e controles do projeto. | Teste: a flag segue `false`; nenhum arquivo desta especificação contém dado pessoal. |
| S16-R16 | **Honestidade sobre o que não se prova.** Nenhuma orquestração automática entre Zapia, Tutor e Coach é afirmada por causa de documentos, testes offline ou prompts; o acesso da Zapia às plataformas segue a liberação de 21/11/2026 (D-27), mas **leitura, envio e registro** só se declaram com prova. CI verde não é eficácia pedagógica. | Texto desta especificação; teste de contrato. |

## Pendências e conflitos para o proprietário

**Regras decididas pelo proprietário (21/11/2026), a partir das duas amostras:**

| ID | Regra | Efeito |
|---|---|---|
| P1 | **Nós terminais (folhas)** da árvore do TEC; **não** se soma pai e descendentes; o caminho mostra os níveis superiores | Nenhuma contagem duplicada |
| P2 | O percentual é a **composição da amostra** (questões do nó sobre o total da matéria no caderno amostral, ou sobre o caderno, conforme a coluna); **não** é incidência histórica da FAPEC nem chance de cair na prova | Texto de entrega não chama de probabilidade |
| P3 | **Empate no 10º lugar:** incluir **todos** os empatados **até um teto de 15 itens**; acima do teto o Tutor apresenta o empate ao proprietário, **sem desempate inventado** | Lista pode ter mais de 10, nunca mais de 15 sem decisão |
| P4 | Matéria com **menos de 10 folhas:** lista as encontradas; percentual ausente deixa o item de fora, sem estimativa | Lista parcial declarada |
| P5 | **Fonte dos percentuais:** o caderno **exclusivo FAPEC** (modalidade 1); a **unidade** do top 10 é a **matéria do TEC** do guia (a amostra FAPEC é re-agrupada por essas matérias); a modalidade 2 só aprofunda | Matéria do TEC continua distinta do bloco de pontuação do edital (S16-R1) |
| P6 | **Dados não versionados:** a S16 guarda só formato e regras; a Zapia traz a amostra a cada plano e o Tutor registra o conjunto no repositório **privado** | Nenhum ranking no repositório público |
| P7 | **Específicos do 523 não definitivos** até reconciliar o caderno salvo com a consulta atual; **específicos do 324** com amostra pequena marcados como instáveis | Sem lista final para essas amostras |
| P8 | **Sem correspondência:** nó do top 10 da FAPEC sem correspondente claro no guia fica registrado "sem correspondência"; o casamento **não** é forçado por nome | Decisão do proprietário caso a caso |

**Conflitos com decisões anteriores (C1 e C2 decididos pelo proprietário; C3 aberto):**

| ID | Conflito | Decisão pedida |
|---|---|---|
| C1 | **Decidido (21/11/2026):** o harness **não impõe** cronograma de estudo; vale a S10-R10 e o D-08 ("cronograma" é o da prova). O Tutor **indica o assunto do dia** dentre os selecionados, sem definir um cronograma completo até a prova; o plano determinístico do Método 4.2 (D-11, `scripts/study_plan.py`) segue como insumo. | Nenhuma; a frase do requisito "define um cronograma de estudo" fica lida como indicação diária. |
| C2 | **Decidido (21/11/2026):** o **top 10 por matéria restringe o plano**; os demais itens ficam **só como lacuna registrada** (S16-R14), com o risco apresentado ao proprietário. | Nenhuma; o recorte do plano de `scripts/study_plan.py` ao top 10 é a tarefa T3. |
| C3 | Os comandos de início e de encerramento **não existem** no esquema e o canal só aceita origem Tutor ou Coach. | Aprovar a tarefa E3 (mudança em `agents/` e no esquema). |

## Tarefas derivadas

T1 a T3 foram implementadas no lote B (PR #155; offline, sintéticas, sem dado real, sem rede, sem gravação); E3 segue pendente de aprovação:

| Item | O que faz | Depende de |
|---|---|---|
| T1 | Estrutura de dados do nó TEC com caminho, origem, modalidade e percentuais da matéria e do caderno (offline, sintética) | P1 a P8 (decididas) |
| T2 | Seleção do top 10 por matéria a partir de percentuais fornecidos, com empate até o teto de 15 e recusa para amostra não definitiva (função pura) | T1 |
| T3 | Formato da entrega diária (S16-R8), recorte do plano ao top 10 e verificador | T2 |
| E3 | Comandos de início e de encerramento | aprovação do proprietário (C3) |

## Aceite

Esta especificação está **aceita pelo contrato** quando `python scripts/doc_cohesion.py --check` passa e `tests/test_spec_s16.py` confere: as seções na ordem do modelo, os requisitos S16-R1 a S16-R16 cada um com critério, a pesquisa com links e lacunas, a tabela de separação, as regras P1 a P8, os conflitos C1 a C3 (C1 e C2 decididos), a ausência de lista do top 10, de comando novo e de dado pessoal, e a flag `false`. A decisão de C3 é do proprietário, por PR; P1 a P8, C1 e C2 estão decididos.

## Limites

- **Não prova nada** na plataforma, no Notebook nem na Zapia; **não lista o top 10**.
- **A origem do comando não é provada** (S6-R7): quem controla a conta do proprietário controla o canal.
- **Não é auditoria dos guias:** os percentuais e a hierarquia vêm das amostras entregues pelo proprietário e do autorrelato da Zapia; **o top 10 não exclui conteúdo previsto no edital** (o TEC declara omissões, que entram na lista de lacunas).
- **Retificações do edital** não foram conferidas (`retificacoes_verificadas=false`); a data de 17/01/2027 permanece como referência oficial.
