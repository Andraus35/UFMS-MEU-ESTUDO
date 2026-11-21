# E3 — Proposta: pedir o relatório de desempenho e registrar início e encerramento do estudo (texto para aprovação)

**Natureza:** **proposta de texto** para o proprietário aprovar; **nada aqui está aplicado**. Este documento **não altera** `agents/`, `config/agent_command_schema.json`, `scripts/agents_gate.py`, `AGENTS.md` nem `PRODUCT.md`. A aplicação nesses arquivos de contrato é um **lote seguinte**, só depois de **duas aprovações expressas** do proprietário: do texto abaixo e do merge, citando PR e head. Origem: item E3 da fila (decisão de 18/11/2026) e a pendência C3 da S16 (decisão de 21/11/2026).

## O que a E3 resolve

1. A S16-R10 e a S16-R11 pedem que a Zapia informe Tutor e Coach no **início** e no **encerramento** do estudo (a frase "Estudo de hoje finalizado.") e que reúna as evidências da rodada. **Não existe** operação nem evento para isso.
2. O item E3 da fila pede uma operação **compartilhada por Tutor e Coach** (como `enviar_mensagem`) para **pedir à Zapia o relatório de desempenho**, no lugar da exportação manual (decisão de 18/11/2026).

## Duas coisas diferentes, dois caminhos

O esquema de comandos modela **agente → Zapia** (origens `tutor` e `coach`). O início e o fim do estudo são **proprietário → Zapia → agentes**, o sentido contrário. Por isso:

| Item | Direção | Mecanismo proposto | Muda o esquema de comandos? |
|---|---|---|---|
| **Pedir relatório de desempenho** | Tutor ou Coach → Zapia | **Operação nova** `pedir_relatorio_desempenho`, compartilhada (como `enviar_mensagem`) | **Sim** (operação e destino novos) |
| **Início do estudo** | proprietário → Zapia → fila `entrada` | **Evento** `estudo_iniciado`, entregue pela Zapia na fila (S6, S7); a Zapia **informa** Tutor e Coach lendo o recibo | **Não**; muda o esquema de eventos (S7) |
| **Encerramento do estudo** | proprietário → Zapia → fila `entrada` | **Evento** `estudo_finalizado`, disparado pela frase literal **"Estudo de hoje finalizado."**, com as evidências da rodada | **Não**; muda o esquema de eventos (S7) |

**Por que evento e não comando:** a Zapia **só executa** comandos de Tutor e Coach (S5) e **não** os emite; um comando "de encerramento" com origem `zapia` quebraria a regra de origens e o equilíbrio das operações por perfil (`scripts/agents_gate.py`). A fila `entrada` e o fluxo de promoção (S6-R3, R4) já existem para o que a Zapia entrega.

## Proposta A — operação `pedir_relatorio_desempenho`

| Campo | Proposta |
|---|---|
| Nome | `pedir_relatorio_desempenho` |
| Perfil | **Compartilhada** por Tutor e Coach (entra em `SHARED`, ao lado de `ler_arquivo_repositorio` e `enviar_mensagem`) |
| Destino | `zapia_relatorio` (novo, fechado) |
| Parâmetros (fechados) | `plataforma` (`tec`), `modalidade` (`1` caderno exclusivo FAPEC; `2` guias do TEC), `cargo` (`324` ou `523`), `recorte` (período e filtros, texto curto) |
| Proibido | enunciado, gabarito, texto de questão, HTML, captura, credencial e dado pessoal (`forbidden_param_keys`) |
| Limite | **no máximo 1 pedido por dia e só com atividade concluída** (decisão de 18/11/2026) |
| Efeito | **só orientação**: a Zapia devolve o relatório pelo contrato de entrega (S9, L2, S16-R12); **nunca grava** no repositório público; resultado pessoal só pela fila e pelo portão (flag `false`) |

**Decisão pedida (A1):** manter o limite de **1 pedido por dia** mesmo com a Zapia liberada nas plataformas (D-27)? Esse limite é da cadência do **canal de comandos**, não do acesso aos sites.

## Proposta B — eventos de início e de encerramento

| Campo | `estudo_iniciado` | `estudo_finalizado` |
|---|---|---|
| Disparo | O proprietário avisa a Zapia que começou (**frase de início a definir**; ver B1) | A frase literal **"Estudo de hoje finalizado."** |
| Quem escreve | A Zapia, **só** na fila `entrada` (S6-R2) | A Zapia, **só** na fila `entrada` |
| Conteúdo mínimo | data e hora (relógio injetado, S15), cargo, matéria e caminho do nó do dia **quando informados** | data e hora, e as **evidências da rodada** (acertos, erros e referências a cadernos ou questões **quando disponíveis**) pelo contrato de entrega; campo ausente = "desconhecido" |
| Proibido | dado pessoal, credencial, texto de questão | idem |
| Quem lê | Tutor e Coach, pelas projeções (S6-R9), **cada um na sua função** | idem |
| Honestidade | O evento **não prova** leitura, envio ou registro por si; só o **recibo do fluxo** prova (S6-R4) | idem |

**Decisões pedidas:**
- **B1:** qual é a **frase de início** (o requisito só fixou a de encerramento)?
- **B2:** o evento de início/encerramento entra no **esquema de eventos da S7** como tipos novos? Isso **emenda a S7** e o esquema de ingestão, e cai sob a **flag de escrita** (`false`): enquanto ela estiver falsa, o evento fica **só como texto proposto**.

## Texto exato proposto para os arquivos de contrato (não aplicado)

**`config/agent_command_schema.json`:** em `destinations`, acrescentar `"pedir_relatorio_desempenho": "zapia_relatorio"`.

**`scripts/agents_gate.py`:** acrescentar `pedir_relatorio_desempenho` a `SHARED` (o gate exige que Tutor e Coach compartilhem **exatamente** o conjunto `SHARED`).

**`agents/TUTOR.md`, `agents/COACH.md` e `agents/ZAPIA.md`:** acrescentar, em cada lista de operações, `pedir_relatorio_desempenho` (orientação; pede o relatório de desempenho do TEC; no máximo 1 por dia e só com atividade concluída). No `ZAPIA.md`, incluir em "Faz": "Registra, quando o proprietário avisa o início e diz *Estudo de hoje finalizado.*, o evento correspondente na fila e informa Tutor e Coach pelo recibo."

**`docs/especificacoes/S5_ZAPIA.md` e `S7_PERSISTENCIA_ESCRITOR.md`:** emendas curtas apontando para esta proposta (só se B2 for aprovada).

## Impacto e testes (quando aprovado)

| Arquivo | Mudança | Teste |
|---|---|---|
| `config/agent_command_schema.json` | destino novo | `tests/test_agent_commands.py` (destino fechado, parâmetros proibidos) |
| `scripts/agents_gate.py`, `agents/*.md` | operação compartilhada e paridade entre perfis e esquema | `tests/test_agents_gate.py` |
| `docs/especificacoes/S16_*.md` | S16-R10 e R11 deixam de ser "ausência declarada" | `tests/test_spec_s16.py` |

## O que a E3 **não** faz

- **Não** aplica nenhuma mudança em `agents/`, no esquema ou no gate.
- **Não** cria job, lembrete, fluxo, integração ou comando ativo, e **não** muda flag.
- **Não** prova que Zapia, Tutor e Coach se comunicam: nenhum canal foi implantado nem testado (S6-R13).
- **Não** altera a liberação da Zapia nas plataformas (D-27, 21/11/2026).

## Aceite

Esta proposta está **aceita pelo contrato** quando `python scripts/doc_cohesion.py --check` passa e `tests/test_e3_proposta.py` confere: a distinção comando × evento, a operação compartilhada, os parâmetros e limites, a frase literal de encerramento, as decisões A1, B1 e B2, o texto proposto para os arquivos de contrato e a **ausência de mudança** neles. **A aplicação depende da aprovação expressa do proprietário.**
