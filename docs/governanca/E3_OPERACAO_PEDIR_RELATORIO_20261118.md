# E3 — Proposta: pedir o relatório de desempenho e registrar início e encerramento do estudo (texto para aprovação)

**Natureza:** **proposta de texto** para o proprietário aprovar; **nada aqui está aplicado**. Este documento **não altera** `agents/`, `config/agent_command_schema.json`, `scripts/agents_gate.py`, `AGENTS.md` nem `PRODUCT.md`. A aplicação nesses arquivos de contrato é um **lote seguinte**, só depois de **duas aprovações expressas** do proprietário: do texto abaixo e do merge, citando PR e head. Origem: item E3 da fila (decisão de 18/11/2026) e a pendência C3 da S16 (decisão de 21/11/2026).

## O que a E3 resolve

1. A S16-R10 e a S16-R11 pedem que a Zapia informe Tutor e Coach no **início** e no **encerramento** do estudo (a frase de encerramento, hoje "finalizar estudos", B1b) e que reúna as evidências da rodada. **Não existe** operação nem evento para isso.
2. O item E3 da fila pede uma operação **compartilhada por Tutor e Coach** (como `enviar_mensagem`) para **pedir à Zapia o relatório de desempenho**, no lugar da exportação manual (decisão de 18/11/2026).

## Duas coisas diferentes, dois caminhos

O esquema de comandos modela **agente → Zapia** (origens `tutor` e `coach`). O início e o fim do estudo são **proprietário → Zapia → agentes**, o sentido contrário. Por isso:

| Item | Direção | Mecanismo proposto | Muda o esquema de comandos? |
|---|---|---|---|
| **Pedir relatório de desempenho** | Tutor ou Coach → Zapia | **Operação nova** `pedir_relatorio_desempenho`, compartilhada (como `enviar_mensagem`) | **Sim** (operação e destino novos) |
| **Início do estudo** | proprietário → Zapia → fila `entrada` | **Evento** `estudo_iniciado`, entregue pela Zapia na fila (S6, S7); a Zapia **informa** Tutor e Coach lendo o recibo | **Não**; muda o esquema de eventos (S7) |
| **Encerramento do estudo** | proprietário → Zapia → fila `entrada` | **Evento** `estudo_finalizado`, disparado pela frase **"finalizar estudos"**, com as evidências da rodada | **Não**; muda o esquema de eventos (S7) |

**Por que evento e não comando:** a Zapia **só executa** comandos de Tutor e Coach (S5) e **não** os emite; um comando "de encerramento" com origem `zapia` quebraria a regra de origens e o equilíbrio das operações por perfil (`scripts/agents_gate.py`). A fila `entrada` e o fluxo de promoção (S6-R3, R4) já existem para o que a Zapia entrega.

## Proposta A — operação `pedir_relatorio_desempenho`

| Campo | Proposta |
|---|---|
| Nome | `pedir_relatorio_desempenho` |
| Perfil | **Compartilhada** por Tutor e Coach (entra em `SHARED`, ao lado de `ler_arquivo_repositorio` e `enviar_mensagem`) |
| Destino | `zapia_relatorio` (novo, fechado) |
| Parâmetros (fechados) | `plataforma` (`tec` ou `gemini_notebook`), `modalidade` (só para `tec`: `1` caderno exclusivo FAPEC; `2` guias do TEC), `cargo` (`324` ou `523`), `recorte` (período e filtros, texto curto) |
| Proibido | **comentário de professor e recursos exclusivos do TEC** (material, análise, explicações), HTML, captura, credencial e dado pessoal (`forbidden_param_keys`). **Revisto em 25/11/2026 (decisão C1):** enunciado e gabarito **deixam de ser proibidos** (ver abaixo); estavam nesta lista na proposta de 18/11/2026 |
| Limite | **até 2 pedidos por dia, no máximo 1 por plataforma e só com atividade concluída**: um para o **estudo no TEC** e outro para a **revisão no Gemini Notebook** (decisão do proprietário de 21/11/2026, que substitui o "1 por dia" de 18/11/2026) |
| Compartilhamento | **O Tutor compartilha com o Coach o resultado do aluno em cada sessão** (decisão de 21/11/2026), cada um na sua função (S2, S3); o **mecanismo** desse compartilhamento (por exemplo, a leitura das projeções do S6-R9 ou uma mensagem) **ainda não está definido** e fica como pendência E3-C |
| Efeito | **só orientação**: a Zapia devolve o relatório pelo contrato de entrega (S9, L2, S16-R12); **nunca grava** no repositório público; resultado pessoal só pela fila e pelo portão (flag `false`) |

**Decisão A1 (21/11/2026):** o limite passa a **até 2 pedidos por dia, um por plataforma** (estudo no TEC e revisão no Gemini Notebook); a cadência é do **canal de comandos**, não do acesso aos sites (D-27).

## Proposta B — eventos de início e de encerramento

| Campo | `estudo_iniciado` | `estudo_finalizado` |
|---|---|---|
| Disparo | O proprietário avisa a Zapia com a frase **"Iniciar estudos"** (decisão B1, 21/11/2026) | A frase **"finalizar estudos"** (decisão B1b, 21/11/2026, que **substitui** a "Estudo de hoje finalizado." do requisito anterior) |
| Quem escreve | A Zapia, **só** na fila `entrada` (S6-R2) | A Zapia, **só** na fila `entrada` |
| Conteúdo mínimo | data e hora (relógio injetado, S15), cargo, matéria e caminho do nó do dia **quando informados** | data e hora, e as **evidências da rodada** (acertos, erros e referências a cadernos ou questões **quando disponíveis**) pelo contrato de entrega; campo ausente = "desconhecido" |
| Proibido | dado pessoal, credencial, comentário de professor e recursos exclusivos do TEC (a proibição de texto de questão foi **revista em 25/11/2026**, decisão C1) | idem |
| Quem lê | Tutor e Coach, pelas projeções (S6-R9), **cada um na sua função** | idem |
| Honestidade | O evento **não prova** leitura, envio ou registro por si; só o **recibo do fluxo** prova (S6-R4) | idem |

**Decisões registradas e pendências:**
- **B1 (decidida, 21/11/2026):** a frase de **início** é **"Iniciar estudos"**.
- **B1b (decidida, 21/11/2026):** a frase de **encerramento** é **"finalizar estudos"**, simétrica a "Iniciar estudos"; ela **substitui** "Estudo de hoje finalizado." (S16-R11 atualizada no mesmo PR).
- **B2 (decidida, 21/11/2026):** os eventos entram como **tipos novos no esquema da S7**, **como proposta** (emenda à S7). Enquanto a **flag de escrita** estiver `false`, o evento fica **só como texto proposto**.
- **E3-C (decidida, 21/11/2026):** o **Coach lê as projeções** do S6-R9, as mesmas do Tutor, **cada um na sua função**; o Tutor **não** precisa enviar mensagem ao Coach a cada sessão. Isso **depende do consentimento v4** (S6-R9).

## Decisão do proprietário (21/11/2026): a Zapia como interface única do estudo

**O comando vai à Zapia, não à sessão do Claude.** "Iniciar estudos" e a frase de encerramento são ditas **à Zapia**, que é o elo entre o harness, o Tutor, o Coach, o TEC, o Gemini Notebook e o estudante. A Zapia grava o evento na fila `entrada` (proposta B); nenhuma sessão de Tutor ou Coach recebe a frase do proprietário diretamente.

**Fluxo desejado ao fim de cada sessão de estudo (requisito, não capacidade provada):**
1. O proprietário diz a frase de encerramento à Zapia.
2. A Zapia **faz perguntas ao proprietário sobre o que foi estudado**.
3. A Zapia **entra no TEC** e **puxa o resultado dos cadernos de acertos e erros** (S16-R12, S9).
4. A Zapia **leva o resultado só ao Tutor e ao Coach**, que o tratam **segundo suas expertises individuais** (S2, S3): o Tutor no diagnóstico e na próxima intervenção pedagógica; o Coach no acompanhamento e na rotina.
5. **O mesmo vale para as revisões no Gemini Notebook:** a Zapia informa o que foi criado e o estado (material criado, processamento pendente, erro, validação pedagógica; S16-R13) a Tutor e Coach.

**O que este fluxo exige e ainda não existe (nada disso está implantado ou testado):**

| Peça | Situação | Pendência |
|---|---|---|
| Perguntas da Zapia ao proprietário ao fim da sessão | Não especificadas | **F1 (decidida, 21/11/2026):** o **Tutor define um roteiro fixo e mínimo** (o que estudou, caminho do nó, dificuldades, tempo) e a Zapia **só o aplica** e registra as respostas, sem criar pergunta nova (a Zapia não gera conteúdo pedagógico, S5) |
| Coleta no TEC pela Zapia | Liberada pelo D-27; sem leitura real provada; contrato de entrega e filtro de dados existem (L1, L2) | **F2 (decidida, 21/11/2026):** os **cadernos da sessão**, indicados pelo Tutor para o dia; a Zapia informa o **modo de pontuação** (líquida ou bruta) e a regra de contagem lidos na tela, **sem inferir**; campo ausente fica "desconhecido" |
| Entrega "só a Tutor e Coach" | Canal: fila `entrada` e fluxo (S6); a Zapia entrega, o fluxo grava, os agentes leem as projeções (S6-R9) | **Bloqueado pela flag de escrita (`false`)** e pelo consentimento v4: sem ele o resultado **não é gravado**; o repositório público **nunca** recebe o resultado **F3 (decidida, 21/11/2026):** a prioridade do proprietário é **destravar a persistência privada primeiro** (consentimento v4, repositório privado de dados e prova do fluxo de escrita), **antes** de aplicar a E3 nos arquivos de contrato |
| Compartilhamento Tutor → Coach por sessão | Definido (A1) | Coach lê as projeções (E3-C, decidida); depende do consentimento v4 |
| Revisão no Gemini Notebook | Prompt do Tutor (S10); a Zapia executa | Teste real não feito (N1) |

**"Persistido no harness" significa, aqui, texto de especificação e testes de contrato; não significa funcionamento.** Esta proposta, a S16 e o ROADMAP registram o requisito de forma versionada; **nenhum resultado de estudo é gravado**, porque a escrita de resultados pessoais continua bloqueada (flag `false`), e **nenhuma orquestração Zapia–Tutor–Coach é afirmada** sem prova.

## Texto exato proposto para os arquivos de contrato (não aplicado)

**`config/agent_command_schema.json`:** em `destinations`, acrescentar `"pedir_relatorio_desempenho": "zapia_relatorio"`.

**`scripts/agents_gate.py`:** acrescentar `pedir_relatorio_desempenho` a `SHARED` (o gate exige que Tutor e Coach compartilhem **exatamente** o conjunto `SHARED`).

**`agents/TUTOR.md`, `agents/COACH.md` e `agents/ZAPIA.md`:** acrescentar, em cada lista de operações, `pedir_relatorio_desempenho` (orientação; pede o relatório de desempenho do TEC; até 2 por dia, no máximo 1 por plataforma, e só com atividade concluída). No `ZAPIA.md`, incluir em "Faz": "Registra, quando o proprietário diz *Iniciar estudos* e *finalizar estudos*, o evento correspondente na fila e informa Tutor e Coach pelo recibo."

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

Esta proposta está **aceita pelo contrato** quando `python scripts/doc_cohesion.py --check` passa e `tests/test_e3_proposta.py` confere: a distinção comando × evento, a operação compartilhada, os parâmetros e limites, a frase literal de encerramento, as decisões A1, B1, B1b, B2, E3-C e F1 a F3, e a Zapia como interface única, o texto proposto para os arquivos de contrato e a **ausência de mudança** neles. **A aplicação depende da aprovação expressa do proprietário.**

## Ordem de aplicação (decisão F3)

O proprietário priorizou a **persistência privada** (consentimento v4, repositório privado de dados e prova do fluxo de escrita). Portanto a **aplicação** da E3 em `agents/`, no esquema e no gate vem **depois** desse destrave; **até lá** esta proposta permanece como texto aprovado em princípio, sem efeito. No estado registrado em `state/WORKFLOW.json`, a infraestrutura já existe (repositórios privados, consentimento v4 e fluxo que promoveu uma prova sintética); o que falta é a **janela do piloto (PJ)**, que depende da **aprovação expressa do proprietário**, e a **renovação dos tokens (P9)**, que são atos dele.

## Decisão C1 (25/11/2026): enunciado e gabarito permitidos na entrega da Zapia

**Decisão do proprietário, nas palavras dele:** o conteúdo das questões é **público**, obtido em sites de bancas de concursos; é razoável **retirar a proibição de enunciados e gabaritos**, porque o Tutor precisa saber **o que o aluno acertou ou errou** ao confrontar com o relatório de desempenho. **Não pode** a Zapia trazer o **comentário do professor** nem os **recursos do TEC**, que são a expertise da empresa. Registro em `docs/governanca/E37_DECISAO_CONTEUDO_DE_QUESTAO_20261125.md`.

Isto **continua sendo proposta de texto**: nada foi aplicado em `agents/`, no esquema de comandos nem nos filtros (a lista `forbidden_param_keys` ainda traz `enunciado`). A aplicação segue a regra de duas aprovações expressas e depois da janela do piloto.

## Aprovação do texto (25/11/2026)

O proprietário **aprovou o texto desta proposta como está**, já com a decisão C1, e **confirmou a frase "finalizar estudos"** (resposta registrada em `docs/governanca/E38_REGISTRO_DE_APROVACOES_E3_E_FRASE_20261125.md`). **Isto não aplica nada:** `agents/`, `config/agent_command_schema.json`, `scripts/agents_gate.py` e os filtros seguem como estão; a aplicação exige **a segunda aprovação expressa (o merge, citando PR e head)** e vem **depois da janela do piloto**.
