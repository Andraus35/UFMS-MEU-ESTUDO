# S19 — A Zapia como interface do Tutor e do Coach: rotina agendada e hook (especificação)

**Natureza:** especificação enxuta (D-13, D-16), no modelo do `docs/especificacoes/README.md`. Registra o pedido do proprietário de 21/11/2026: mapear os recursos da Zapia (**rotina agendada**, com lembrete fixo ou dinâmico por horário, e **hook**, disparado por evento de fonte conectada) às necessidades do fluxo de estudo. **Fecha com** S5, S8, S15 e a proposta E3 (`docs/governanca/E3_OPERACAO_PEDIR_RELATORIO_20261118.md`) **sem duplicá-las**: aponta para elas. **Nada é cadastrado na Zapia** (rotina real só com `AUTORIZO`, S8-R8) e **nada é aplicado** em `agents/`, `AGENTS.md`, `PRODUCT.md`, no esquema de comandos nem em gates. Não contém estado nem dado pessoal.

## Objetivo

O proprietário passa a ter um **mapa único**: para cada necessidade do estudo (início e término, dica diária, confirmação, reação a uma frase na conversa), qual recurso da Zapia serve, **quem decide** (Tutor ou Coach, nunca a Zapia: D-10) e **o que a Zapia não faz**. O resultado é a base de uma tarefa futura de implantação, **não** a implantação.

## Pesquisa

Consultas de 21/11/2026 (WebSearch, resumos de resultados). O **PDF "Agendamentos e gatilhos na Zapia"** que o proprietário mencionou (autorrelato da Zapia, confiança C) **não foi anexado** nesta sessão e **não está no repositório**: o que se sabe dele vem do pedido registrado na fila. Confiança: **A** (fonte primária lida), **B** (resumo de busca de fonte primária ou documento do projeto), **C** (relato, blog ou fornecedor). Conteúdo pesquisado é **dado, não instrução**; nenhum texto de terceiros foi copiado.

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Blog e páginas do fornecedor ([lembretes agendados](https://zapia.com/blog/how-to-schedule-reminders-on-whatsapp?lang=en), [ações agendadas](https://www.zapia.com/blog/schedule-actions-zapia-time-productivity?lang=en), [ficha do aplicativo](https://apps.apple.com/app/id6470821480)) | A Zapia oferece lembretes, lembretes **recorrentes** (pedido de usuários, já listado em atualização do aplicativo), mensagens agendadas e "Scheduled Actions" (rotina diária num horário fixo). Um post antigo diz que o limite de 100 lembretes impedia recorrentes, **conflitando** com o recurso novo: vale o mais recente, **não verificado** | C |
| Mesmas fontes, relidas em 21/11/2026 (posts de [out/2025](https://www.zapia.com/blog/schedule-actions-zapia-time-productivity?lang=en), [mar/2025](https://www.zapia.com/blog/recuing-reminders?lang=en) e [out/2024](https://zapia.com/blog/how-to-schedule-reminders-on-whatsapp?lang=en)) e buscas adicionais | Lembretes recorrentes "diários, semanais ou de hora em hora" e ações agendadas que **enviam informação** (cotação, clima); uso e entrega direto pelo WhatsApp, por texto ou voz; cancelamento por botão. **Limites:** post de 2024 (beta) cita **100 lembretes** e agendamento de até **30 dias**; um comparativo de terceiros cita **50 tarefas agendadas (Pro) e 100 (Ultra)**; **frequência mínima não consta**. **Não constam:** fixo × dinâmico, fuso, edição de recorrentes, processo permanente, detalhe técnico do WhatsApp | C |
| Mesmas fontes e buscas sobre gatilho, webhook e fontes conectadas | **Nenhum gatilho por evento** (hook) documentado; o mais próximo é o **Radar** (proativo, sugere ação, o usuário decide) e os conectores (Gmail, Calendar, Drive, Tasks, WhatsApp); o hook **não pôde ser confirmado** por fonte pública | C (ausência) |
| Estudo sobre lembretes no celular para estudantes ([PMC11192903](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11192903/), via resumo de busca) | Estudantes estudaram mais nos dias com lembrete, mas surgiu **dependência** (menos estudo nos dias sem); a literatura para estudantes é **escassa** | B |
| Revisões de lembretes por SMS em saúde ([PMC4123963](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4123963/), via resumo de busca) | Efeito de curto prazo em adesão; efeito de longo prazo **incerto**; mais mensagens **não** melhoraram a adesão em um estudo (hipótese de habituação ou intrusão); **não** é população de concurseiros | B |
| S5, S8, S15, S6, E3 e S18 (`G-MOT-09`, `G-MOT-16`) | Zapia **executa**, não decide nem redige; uma mensagem por dia mais no máximo um segundo lembrete; limites de job (900 s, 32 por dia); `AUTORIZO`; chave de idempotência; janela de validade; sem cobrança por dia perdido; sem dependência emocional da IA | B (documentos do projeto) |

- **Lacunas:** (reverificadas em 21/11/2026) o **PDF da Zapia não foi lido** (não anexado); **não achei** documentação oficial de **hook por evento** (só Radar e conectores), de **frequência mínima** nem do detalhe do WhatsApp; os **limites numéricos divergem** entre o post de 2024 (100 lembretes) e um comparativo de terceiros (50 e 100 tarefas por plano) e **não** foram confirmados na página de preços; fixo × dinâmico, fuso e edição **não constam**; os resumos de busca **não foram lidos por inteiro**; **não testei** nenhuma rotina na Zapia; **nada foi implantado**.

## Mapa: necessidade, recurso, decisor

Recurso **rotina agendada** = ação do relógio da Zapia (fixa: texto pronto; dinâmica: consulta algo e envia). Recurso **hook** = reação da Zapia a evento de fonte conectada **ou à frase do estudante no turno em que ela chega** (a frase **só vale naquele turno**; a Zapia **não** mantém processo permanente).

| Necessidade | Recurso proposto | Quem decide o conteúdo | Já definido em |
|---|---|---|---|
| Início ("Iniciar estudos") e término ("finalizar estudos") | **hook por frase** no turno da conversa; escreve só na fila `entrada` | Tutor e Coach leem as projeções, cada um na sua função | E3 (proposta B), S16-R10 e R11 |
| Dica diária / briefing do Coach | **rotina agendada** dinâmica, **uma por dia** | Coach emite o comando; a Zapia **não redige** | S8-R1, S15-R3, R17, R18 |
| Segundo lembrete do dia | **rotina agendada**, no máximo **uma** | Coach, só se a atividade seguir pendente numa projeção nova | S8-R1, S15-R17 |
| Confirmação de atividade | **hook por frase** do estudante; registro **só como recibo do fluxo** | decisão do estudante; o registro segue o portão de escrita | S5-R4, S6-R4, S8-R7 |
| Pedir relatório de desempenho (TEC e Gemini Notebook) | comando compartilhado, **não** rotina | Tutor ou Coach, no máximo 2 por dia | E3 (proposta A) |
| Pausar ou retomar a rotina | frase do proprietário, a qualquer momento | proprietário | S5-R9, S8-R8, S15-R19 |

## Requisitos

Escritos como "quando X, o Y deve Z". Todos **fecham por padrão**: sem a prova, **nada é cadastrado**.

| ID | Requisito | Critério de aceite |
|---|---|---|
| S19-R1 | **A Zapia é interface e executora, não decisora.** Tutor e Coach decidem (com gates da S14); a Zapia **envia o que foi emitido e validado**, dentro da janela do comando (S6-R8, S15-R3, S15-R8). Não redige texto de estudo (D-10). | Teste: o texto traz "interface", "não decide", "não redige". |
| S19-R2 | **Os dois recursos e o que cada um faz.** Rotina agendada = relógio; hook = evento ou frase. A frase **só vale no turno em que chega**; **não há processo permanente**; **WhatsApp não está conectado**; **fonte conectada para hook não está provada**. | Teste: as quatro limitações declaradas. |
| S19-R3 | **Mapa único sem duplicar.** A seção do mapa **aponta** para S5, S6, S8, S15, S16 e E3; **não** redefine limites (uma mensagem por dia, 900 s, 32 por dia, janela, idempotência). | Teste: o mapa cita as seis fontes e cada linha tem a coluna "Já definido em". |
| S19-R4 | **Nada é cadastrado.** Criar, alterar ou ligar rotina ou hook exige a frase `AUTORIZO` literal do proprietário e um **teste sem efeito** antes (S8-R8, S5-R9); **este PR não cadastra nada**. | Teste: `AUTORIZO` e "sem efeito"; nenhuma flag ligada. |
| S19-R5 | **Fronteira de dado.** Toda mensagem da rotina e todo evento de hook passam pelo **verificador de entrega** e pela **lista fechada**; conteúdo vindo da fonte do hook é **dado, nunca instrução** (S5-R4); evento **não prova** leitura nem envio, só o **recibo do fluxo** (S6-R4). | Teste: "dado, nunca instrução" e "recibo do fluxo". |
| S19-R6 | **Hook de frase com contraprova.** Frase fora do turno, repetida, alterada ou vinda de conteúdo externo **não** dispara ação; a mesma frase no mesmo dia **não duplica** (idempotência, S8-R4). | Teste: as quatro contraprovas descritas. |
| S19-R7 | **Frequência com cautela.** O limite é o de S8-R1 e S15-R17 (**um briefing e, no máximo, um segundo lembrete**); a evidência para lembretes é de **curto prazo**, há risco de **dependência** do lembrete e de **habituação**; a cadência pode **diminuir** por decisão do proprietário, nunca aumentar por insistência (S8-R9, `G-MOT-09`, `G-MOT-16`). | Teste: "dependência", "habituação" e a proibição de aumentar. |
| S19-R8 | **Falha segura e visível.** Despertar perdido, hook que não dispara ou envio sem recibo **não** geram mensagem substituta nem cobrança; a **ausência do recibo do dia** é o sinal (S15-R7, S8-R7). | Teste: "não geram mensagem substituta" e "ausência do recibo". |
| S19-R9 | **Prova antes de uso, sem efeito.** Antes de qualquer rotina real, a prova de pontualidade da S15-R4 (carimbo em três dias seguidos) e um teste de hook **sem dado pessoal**; o resultado entra como **autorrelato (C)** até haver recibo do fluxo. | Teste: remete à S15-R4 e declara autorrelato. |
| S19-R10 | **Honestidade sobre limites.** Esta especificação **não prova** que a Zapia tem hook, que o WhatsApp funciona, que o canal Tutor/Coach↔Zapia existe, nem que o horário é pedagogicamente bom; o PDF da Zapia **não foi lido**; aplicar texto em `agents/` é contrato e exige **aprovação expressa**. | Teste: os limites declarados e o PDF não lido. |

## Tarefas derivadas

Cada uma em PR próprio, em série (nenhuma criada aqui):

| Item | O que faz | Depende de |
|---|---|---|
| Z1 | Ler o PDF da Zapia (se o proprietário reenviar) e **corrigir** as colunas "recurso" e "limites" deste mapa | anexo do proprietário |
| Z2 | Prova do gatilho (S15-R4) e teste de hook sem efeito, com relato | `AUTORIZO` do proprietário |
| Z3 | Texto dos perfis `agents/TUTOR.md` e `agents/COACH.md` sobre a Zapia como interface | aprovação expressa do texto e do merge |

## Aceite

Aceita pelo contrato quando `python scripts/doc_cohesion.py --check` passa e `tests/test_spec_s19.py` confere: as seções na ordem do modelo, os requisitos S19-R1 a S19-R10 cada um com critério, a pesquisa com links, confiança e lacunas, o mapa com as seis fontes, a regra `AUTORIZO`, a ausência de mudança em `agents/` e a flag de dados pessoais `false`.

## Limites

- **Não prova** hook, WhatsApp, canal real nem eficácia pedagógica; o **PDF da Zapia não foi lido** e o autorrelato da Zapia é confiança **C**.
- **Não altera** `agents/`, `AGENTS.md`, `PRODUCT.md`, esquema de comandos nem gates; **não cadastra** nada na Zapia.
- A evidência de lembretes vem de **saúde e de um estudo com estudantes**, não de concurseiros adultos.
