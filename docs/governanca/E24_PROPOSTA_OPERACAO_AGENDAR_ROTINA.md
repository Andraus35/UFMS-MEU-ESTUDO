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
| `BRIEFING_DIARIO` | `coach` | rotina diária do Coach (S8, F3) | **fora desta aprovação** |
| `RELATORIO_TEC_AGENDADO` | `tutor` | pedir o relatório de desempenho do TEC no horário (E3, depende dela) | **fora desta aprovação** |
| `REVISAO_NOTEBOOK_AGENDADA` | `tutor` | entregar um `enviar_prompt_notebook` já validado no horário (S10) | **fora desta aprovação** |

A caixa recusa modelo que não pertença à origem do comando (`ORIGEM_FORA_DO_MODELO`). `F1_ENTREGA_UNICA` e `ROTINA_ESTUDO_DIARIA` são propostos para aprovação agora; os demais são só o mapa.

**A instrução que a Zapia segue NÃO vem do comando.** Ela está num **modelo versionado no repositório público**, com hash (primeiro modelo: o passo 3 de `ROTEIRO_ZAPIA_ROTINA_TESTE_20261122.md`). O comando só preenche **horário** e **hash**. Assim, a Zapia nunca obedece texto escrito por um agente: ela lê um **pedido estruturado** e um **modelo fixo**, e ambos são **dado**, não ordem (`ZAPIA.md`, regra de conteúdo do repositório como dado).

### Modelo `ROTINA_ESTUDO_DIARIA` (Tutor, 2 dias)

- **Params fechados:** `modelo`, `agendado_utc_d1`, `agendado_utc_d2`, `comando_sha256_d1`, `comando_sha256_d2`. Cada dia aponta para **um `enviar_mensagem` já promovido**, gerado por `scripts/entrega_diaria.py` a partir de matéria, assunto e quantidade escolhidos **pelo Tutor**. **Nenhum conteúdo pedagógico vai nos params do agendamento**, e a Zapia **não redige** o texto (`ZAPIA.md`: ela executa, não decide).
- **Mesma regra de instrução:** o passo a passo da Zapia (usar o recurso nativo de rotina agendada, `AUTORIZO` por turno, uma mensagem por dia, parar sem laço) vem do **modelo versionado**.
- **Prova em 2 dias (indício, não a prova de 3 dias da S15-R4):** a Zapia grava o recibo de volta com `entregue_em` do relógio e `rotina_id_relatado` (id da rotina como o app a mostra; **autorrelato**). `scripts/zapia_disparo.py` (modo `--dia2-nome` e `--dia2-agendado`) confere cada dia (hash, carimbo não anterior ao agendado e até 900 s depois, entrega única, teto diário), o id relatado nos dois dias, a distância de 20 h a 28 h entre os agendamentos e dias de entrega diferentes.
- **O que o verificador NÃO distingue:** entrega manual feita logo depois do horário. Só a **captura da lista de rotinas do app** e a notificação recebida **sem você estar na conversa** separam rotina nativa de entrega manual. "Necessariamente usar o agendamento nativo" **não é garantível por código**: é verificável só pelo recibo e pela sua captura.
- **Rascunho sintético do conteúdo do dia 1** (marcadores, sem questões nem disponibilidade afirmada): "Estudo de DIA_1 (cargo CARGO_523) / Matéria: MATERIA_X / Caminho: MATERIA_X > ASSUNTO_A / Posição e percentual: não verificado / Atividade: resolver caderno · N1 questões (definidas pelo Tutor; existência no acervo não verificada) / Objetivo: OBJETIVO_1". O dia 2 repete com `ASSUNTO_B` e `N2`. Limite do texto: 600 caracteres e comando válido por 24 h, então **o comando de cada dia é emitido dentro de 24 h do disparo**.

## Onde entra o `AUTORIZO` (S8-R8, S20-R6)

O comando é um **pedido**, não uma criação. Fluxo proposto: (1) o Coach emite `agendar_rotina`; (2) a caixa valida e o fluxo promove; (3) a Zapia, ao ler o recibo, **mostra ao proprietário** o pedido ("o Coach pede uma rotina única às HH:MM; hash X") e **espera a frase `AUTORIZO` dele naquele turno**; (4) só então cria a rotina no app dela, de execução única, a partir do modelo; (5) grava um **recibo de volta** (hash do pedido, id da rotina como a Zapia a relata, horário criado, sem token). **Sem `AUTORIZO` não há criação**, e a Zapia para sem insistir nem reenviar (S20-R9). O campo do comando **não** substitui a frase.

## O que a aplicação mudaria (lote seguinte, com aprovação)

1. `config/agent_command_schema.json`: destino `zapia_rotina` e a operação (compartilhada).
2. `scripts/command_params_schema.py`: esquema fechado (`modelo` enum, `agendado_utc`, `comando_sha256`), sem campo extra.
3. `scripts/command_box.py`: limites (15 min a 24 h, 1 por dia por origem, recibo de mesmo hash do alvo) e a tabela modelo-origem.
4. `agents/TUTOR.md`, `agents/COACH.md` e `agents/ZAPIA.md`: lista de operações e a regra do `AUTORIZO` por turno.
5. `scripts/agents_gate.py`: `SHARED` ganha a operação (mesma lista nos dois perfis).
6. Testes com contraprovas (ALTA e MEDIA): modelo fora da origem (Tutor pedindo modelo do Coach e o inverso), campo extra, modelo fora da lista, horário fora da janela, hash sem recibo, segundo pedido no dia da mesma origem, texto livre.
7. Modelo da instrução em `docs/governanca/` com hash no manifesto.

## Riscos declarados

- **Autoescalonamento:** o agente pediria a própria rotina. Mitigação: só pedido estruturado e **`AUTORIZO` humano obrigatório**.
- **A Zapia é um modelo** e pode não obedecer ou não conseguir criar rotina por esse caminho (autorrelato dela até a prova). O recibo de volta e o verificador (`zapia_disparo.py`) medem o resultado, não a intenção.
- **A origem do comando não é provada** na nuvem (S4-R2 segue não atendida): quem escreve em `entrada` é a conta do proprietário.
- **`AUTORIZO` vale por turno:** se o pedido chegar quando o proprietário não está na conversa, a Zapia só o **apresenta**; não cria.
- A rotina de teste F2a **pode ser provada antes**, pelo roteiro atual (o proprietário cria a rotina à mão), **sem** esta operação.

## O que esta proposta NÃO é

Não é a aplicação, não altera contrato, não cria rotina nem lembrete na Zapia, não prova que a Zapia crie rotina por comando e não dispensa o `AUTORIZO`. A decisão de **criar rotina diária recorrente** (F3) é outro modelo e outra aprovação.

## Para o proprietário aprovar

1. O **nome** `agendar_rotina` e o destino `zapia_rotina`.
2. **Compartilhada** (Tutor e Coach), cada modelo preso à sua origem.
3. A **tolerância** de 15 min a 24 h e **1 por dia**.
4. Os **dois primeiros modelos** `F1_ENTREGA_UNICA` e `ROTINA_ESTUDO_DIARIA` e a instrução vir de **modelo versionado**, nunca do comando.
5. O **`AUTORIZO` por turno** como condição de criação.
6. Depois: aprovar o **merge** da aplicação, citando PR e head.
