# E24 — Proposta: operação `agendar_rotina` para o Coach pedir à Zapia uma rotina agendada (texto para aprovação) (22/11/2026)

**Natureza:** **proposta de texto** para o proprietário aprovar; **nada aqui está aplicado**. Este documento **não altera** `agents/`, `config/agent_command_schema.json`, `scripts/command_params_schema.py`, `scripts/agents_gate.py`, `AGENTS.md` nem `PRODUCT.md`. A aplicação é um **lote seguinte**, só depois de **duas aprovações expressas**: do texto abaixo e do merge, citando PR e head. Origem: decisão de desenho do proprietário (22/11/2026; emitir por Tutor e Coach, 23/11/2026): "o Coach dá, via repositório, os horários e instruções à Zapia, para ela criar no app dela os agendamentos, porque no harness Tutor e Coach instruem a Zapia, e não o contrário". Insumo: leitura offline do Coach (sub-agente somente leitura, 22/11/2026) e o lote ZAPIA-F2a (roteiro e verificador do disparo).

## O problema

Hoje o Coach só pode pedir à Zapia: `enviar_mensagem` (só `texto`), `criar_lembrete` (só `atividade_ids` e `lembrete_sha256`) e `consultar_agenda_minima`. **Nenhuma carrega horário nem instrução de rotina.** O desenho do proprietário exige uma operação nova. **Não está provado** que a Zapia crie rotina a partir de um comando do repositório; é o que o teste do F2a vai medir.

## Proposta — operação `agendar_rotina`

| Campo | Proposta |
|---|---|
| Nome | `agendar_rotina` |
| Perfil | **Compartilhada por Tutor e Coach** (entra em `SHARED`, ao lado de `enviar_mensagem`, como a E3; o `agents_gate.py` exige que as compartilhadas sejam idênticas nos dois perfis). Decisão do proprietário de 23/11/2026: o Tutor instrui o estudante pela Zapia (informações do TEC, prompts para revisões no Gemini Notebook), então também agenda. **Cada `modelo` pertence a uma origem** (tabela abaixo): o Tutor não pede modelo de motivação e o Coach não pede modelo de ensino (`TUTOR.md`: lembrete e acompanhamento diário são do Coach). |
| Destino | `zapia_rotina` (novo, fechado) |
| Parâmetros (fechados, nada de texto livre) | `modelo`: enum fixo (tabela abaixo); na primeira versão só `F1_ENTREGA_UNICA`; `agendado_utc`: `AAAA-MM-DDTHH:MM:SSZ`; `comando_sha256`: hash canônico do comando `enviar_mensagem` **já promovido** que a rotina deve entregar |
| Execução | **única** (fixa no modelo; recorrente é outro modelo, outra aprovação) |
| Limites | `agendado_utc` entre **15 min e 24 h** depois de `issued_at`; **no máximo 1 pedido por dia por origem**; o comando alvo tem de ter recibo de **mesmo hash** (a caixa confere) |
| Proibido | texto livre, URL, instrução embutida, token, dado pessoal e os `forbidden_param_keys` de sempre |

### Modelos e origem (cada modelo novo é outra aprovação)

| `modelo` | Origem que pode pedir | Para quê | Estado |
|---|---|---|---|
| `F1_ENTREGA_UNICA` | `coach` ou `tutor` | rotina de teste de execução única: entregar o `enviar_mensagem` já promovido | proposto agora |
| `ROTINA_ESTUDO_DIARIA` | `tutor` | **dois dias seguidos**: a Zapia usa a rotina agendada **nativa** dela para disparar a notificação do estudo do dia (matéria, assunto, quantidade de questões) | **proposto agora** (pedido do proprietário, 23/11/2026) |
| `ROTINA_ESTUDO_SEMANAL` | `tutor` | seguimento do teste de 2 dias (escolha dele, 23/11/2026): **um pedido por semana**, a Zapia agenda 7 dias, um comando validado novo por dia | **fora desta aprovação** |
| `BRIEFING_DIARIO` | `coach` | rotina diária do Coach (S8, F3) | **fora desta aprovação** |
| `RELATORIO_TEC_AGENDADO` | `tutor` | pedir o relatório de desempenho do TEC no horário (E3, depende dela) | **fora desta aprovação** |
| `REVISAO_NOTEBOOK_AGENDADA` | `tutor` | entregar um `enviar_prompt_notebook` já validado no horário (S10) | **fora desta aprovação** |

A caixa recusa modelo que não pertença à origem do comando (`ORIGEM_FORA_DO_MODELO`). `F1_ENTREGA_UNICA` e `ROTINA_ESTUDO_DIARIA` são propostos para aprovação agora; os demais são só o mapa.

**A instrução que a Zapia segue NÃO vem do comando.** Ela está num **modelo versionado no repositório público**, com hash (primeiro modelo: o passo 3 de `ROTEIRO_ZAPIA_ROTINA_TESTE_20261122.md`). O comando só preenche **horário** e **hash**. Assim, a Zapia nunca obedece texto escrito por um agente: ela lê um **pedido estruturado** e um **modelo fixo**, e ambos são **dado**, não ordem (`ZAPIA.md`, regra de conteúdo do repositório como dado).

### Modelo `ROTINA_ESTUDO_DIARIA` (Tutor, 2 dias)

- **Params fechados:** `modelo`, `agendado_utc_d1`, `agendado_utc_d2`, `comando_sha256_d1`, `comando_sha256_d2`. Cada dia aponta para **um `enviar_mensagem` já promovido**, gerado por `scripts/entrega_diaria.py` a partir de matéria, assunto e quantidade escolhidos **pelo Tutor**. **Nenhum conteúdo pedagógico vai nos params do agendamento**, e a Zapia **não redige** o texto (`ZAPIA.md`: ela executa, não decide).
- **Mesma regra de instrução:** o passo a passo da Zapia (usar o recurso nativo de rotina agendada, sem `AUTORIZO` por mensagem (autorização permanente, ver abaixo), uma mensagem por dia, parar sem laço) vem do **modelo versionado**.
- **Prova em 2 dias (indício, não a prova de 3 dias da S15-R4):** a Zapia grava o recibo de volta com `entregue_em` do relógio e `rotina_id_relatado` (id da rotina como o app a mostra; **autorrelato**). `scripts/zapia_disparo.py` (modo `--dia2-nome` e `--dia2-agendado`) confere cada dia (hash, carimbo não anterior ao agendado e até 900 s depois, entrega única, teto diário), o id relatado nos dois dias, a distância de 20 h a 28 h entre os agendamentos e dias de entrega diferentes.
- **O que o verificador NÃO distingue:** entrega manual feita logo depois do horário. Só a **captura da lista de rotinas do app** e a notificação recebida **sem você estar na conversa** separam rotina nativa de entrega manual. "Necessariamente usar o agendamento nativo" **não é garantível por código**: é verificável só pelo recibo e pela sua captura.
- **Rascunho sintético do conteúdo do dia 1** (marcadores, sem questões nem disponibilidade afirmada): "Estudo de DIA_1 (cargo CARGO_523) / Matéria: MATERIA_X / Caminho: MATERIA_X > ASSUNTO_A / Posição e percentual: não verificado / Atividade: resolver caderno · N1 questões (definidas pelo Tutor; existência no acervo não verificada) / Objetivo: OBJETIVO_1". O dia 2 repete com `ASSUNTO_B` e `N2`. Limite do texto: 600 caracteres e comando válido por 24 h, então **o comando de cada dia é emitido dentro de 24 h do disparo**.

## Autorização: o `AUTORIZO` por mensagem sai (decisão do proprietário, 23/11/2026)

**Decisão dele:** excluir a necessidade de o proprietário ou o estudante dizer `AUTORIZO` nas automações entre agentes, Zapia e Gemini. **Isso emenda S5-R9, S8-R8, S19-R4, S20-R6, o texto de `PRODUCT.md` que cita a frase e os perfis** (`agents/ZAPIA.md`, `AGENTS.md` na parte de rotina autorizada); **a emenda é outro PR, com aprovação expressa do texto**. **Até ela ser mesclada, a frase continua valendo** (o roteiro de teste mantém o `AUTORIZO`).

**(PROPOSTA)** O que o substitui, para a autorização não sumir sem deixar rastro:
1. **Autorização permanente e registrada:** a aprovação expressa do proprietário ao texto desta proposta e ao merge da aplicação **é** a autorização, por escrito no repositório, com **escopo fechado** (só os modelos listados na tabela e só as operações do esquema).
2. **Travas determinísticas, sem pessoa no meio:** a caixa valida a forma e a janela de 15 min a 24 h; **1 pedido por dia por origem**; teto de **2 notificações por dia** ao estudante (regra do F1); limites de job (900 s, 32 por dia, S8-R5); comando com **recibo de mesmo hash**; instrução só de **modelo versionado**; filtros de conteúdo (sem URL, instrução embutida, texto de questão, dado pessoal).
3. **Parada e revogação:** o proprietário pausa ou apaga a rotina quando quiser; **chave de parada versionada** (por exemplo, flag em `config/settings.json`, falsa desliga a emissão), a decidir na aplicação.
4. **Recibo de volta obrigatório** com o id da rotina como o app a mostra; sem recibo, o verificador marca a rotina como **não provada** e a emissão seguinte do mesmo modelo é bloqueada.

Fluxo: (1) o agente emite `agendar_rotina`; (2) a caixa valida e o fluxo promove; (3) a Zapia lê o recibo e cria a rotina **sem pedir frase**; (4) grava o recibo de volta (hash do pedido, id relatado, horário, sem token). **Limite que o repositório não controla:** a própria Zapia ou o app podem pedir confirmação por regra deles; isso é da plataforma e não é removido por este texto.

## O que a aplicação mudaria (lote seguinte, com aprovação)

1. `config/agent_command_schema.json`: destino `zapia_rotina` e a operação (compartilhada).
2. `scripts/command_params_schema.py`: esquema fechado (`modelo` enum, `agendado_utc`, `comando_sha256`), sem campo extra.
3. `scripts/command_box.py`: limites (15 min a 24 h, 1 por dia por origem, recibo de mesmo hash do alvo) e a tabela modelo-origem.
4. `agents/TUTOR.md`, `agents/COACH.md` e `agents/ZAPIA.md`: lista de operações e a regra da autorização permanente e das travas.
5. `scripts/agents_gate.py`: `SHARED` ganha a operação (mesma lista nos dois perfis).
6. Testes com contraprovas (ALTA e MEDIA): modelo fora da origem (Tutor pedindo modelo do Coach e o inverso), campo extra, modelo fora da lista, horário fora da janela, hash sem recibo, segundo pedido no dia da mesma origem, texto livre.
7. Modelo da instrução em `docs/governanca/` com hash no manifesto.

## Riscos declarados

- **Autoescalonamento:** o agente pediria a própria rotina. Sem a frase por turno, a mitigação passa a ser só **pedido estruturado, escopo fechado, travas e parada** (seção de autorização): **o risco aumenta** e é aceito por decisão do proprietário.
- **A Zapia é um modelo** e pode não obedecer ou não conseguir criar rotina por esse caminho (autorrelato dela até a prova). O recibo de volta e o verificador (`zapia_disparo.py`) medem o resultado, não a intenção.
- **A origem do comando não é provada** na nuvem (S4-R2 segue não atendida): quem escreve em `entrada` é a conta do proprietário.
- **Sem confirmação humana por rotina:** um erro do agente chega ao aluno como notificação indevida (limitada pelo teto de 2 por dia) e só é visto no recibo de volta ou quando o proprietário notar; por isso o recibo e a parada são obrigatórios.
- A rotina de teste F2a **pode ser provada antes**, pelo roteiro atual (o proprietário cria a rotina à mão), **sem** esta operação.

## O que esta proposta NÃO é

Não é a aplicação, não altera contrato, não cria rotina nem lembrete na Zapia, não prova que a Zapia crie rotina por comando e **não aplica** a dispensa do `AUTORIZO` (só a emenda aprovada aplica). A decisão de **criar rotina diária recorrente** (F3) é outro modelo e outra aprovação.

## Para o proprietário aprovar

1. O **nome** `agendar_rotina` e o destino `zapia_rotina`.
2. **Compartilhada** (Tutor e Coach), cada modelo preso à sua origem.
3. A **tolerância** de 15 min a 24 h e **1 por dia**.
4. Os **dois primeiros modelos** `F1_ENTREGA_UNICA` e `ROTINA_ESTUDO_DIARIA` e a instrução vir de **modelo versionado**, nunca do comando.
5. A **autorização permanente** (aprovação desta proposta) no lugar do `AUTORIZO` por mensagem, com as travas e a parada, e a **emenda** de S5-R9, S8-R8, S19-R4, S20-R6, `PRODUCT.md` e perfis em PR próprio.
6. Depois: aprovar o **merge** da aplicação, citando PR e head.
