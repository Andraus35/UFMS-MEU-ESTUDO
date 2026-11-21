# Fila de gaps, falhas e divergências (observados em 21/11/2026)

**Natureza:** registro dos achados dos testes de capacidade do **Tutor** e do **Coach** (subagentes, somente leitura, cenários **sintéticos**, 21/11/2026) e das sessões de S18 e S19. Cada item entra na fila `work_queue` de `state/WORKFLOW.json` como **lote** (GAP-A a GAP-E) ou como pendência do proprietário (G). **Os achados dos subagentes não foram reproduzidos por quem escreveu este documento**, exceto onde indicado; antes de corrigir, o lote **reproduz** o achado com um teste que falha. Não contém estado nem dado pessoal. Para o prompt do que a Zapia ainda não respondeu, ver `docs/especificacoes/S19_ZAPIA_INTERFACE_AGENDAMENTOS_GATILHOS.md`.

## Ordem (série, um lote por vez, com merge entre lotes)

`S20` (esta frente) → **HOOKR** (correção do hook, abaixo) → **GAP-A** (GA-1 e GA-2, feitos) → **GAP-A2** (GA-3 a GA-5 e esquemas restantes, entrega `scripts/command_idempotency.py`) → **GAP-B** → **GAP-C** → **GAP-D** → **GAP-E**. O lote **G** (Zapia e proprietário) corre em paralelo **fora do repositório**, porque são atos dele.

## GAP-A (GA) — Comandos e entrega (entrega: `scripts/command_params_schema.py`)

| ID | Gap | Gravidade | Onde | Correção proposta | Origem |
|---|---|---|---|---|---|
| GA-1 | **[feito: GAP-A fechou `enviar_mensagem` e `enviar_prompt_notebook` e recusou `registrar_*` pessoais com a flag falsa; GAP-A2 fechou `ler_arquivo_repositorio`, `criar_lembrete`, `consultar_agenda_minima` e `registrar_plano` (forma PROPOSTA, a confirmar pelo proprietário; `registrar_plano` também recusado com a flag falsa)]** O esquema de comandos **não define `params` por operação**; o validador aceitou `registrar_resultado` com parâmetros arbitrários e só barra chaves proibidas | **Alta** | `config/agent_command_schema.json`, `scripts/agent_commands.py` | Esquema fechado de `params` por operação e recusa explícita de `registrar_*` com `personal_results_writes_enabled` falso | Tutor e Coach |
| GA-2 | **[feito no lote GAP-A: o texto de `params.texto` passa pelos filtros do corpo]** `delivery_gate` **aceitou** um COMANDO `enviar_mensagem` com texto "acertou 80% e há 300 questões disponíveis": os filtros de percentual e disponibilidade só rodam no corpo, e o COMANDO exige corpo vazio | **Alta** | `scripts/delivery_gate.py` (`_comando`, `_verificar`) | Aplicar `_corpo` ao texto de `params` e exigir que o COMANDO referencie o hash do LEMBRETE | Coach |
| GA-3 | **[feito no GAP-A2: `validate_command` confere hash e forma canônica do prompt (`PROMPT_HASH_DIVERGENTE`, `PROMPT_FORMA_NAO_CANONICA`)]** `validate_command` aceita prompt **editado e reassinado**; só `conferir_parametros`/`command_box` recusa (`HASH_DIVERGENTE`) | Média | `scripts/agent_commands.py`, `scripts/command_box.py` | Hash do prompt obrigatório no validador | Tutor |
| GA-4 | **[feito no GAP-A2: LEMBRETE com `atividade_ids` (1 a 5, todas pendentes) e `lembrete_sha256` no resultado; COMANDO `criar_lembrete` carrega o hash e exige LEMBRETE verificado]** O LEMBRETE aceita **um** `atividade_id`, mas o briefing traz bloco e revisão; sem vínculo entre o envelope LEMBRETE e o COMANDO | Média | `scripts/delivery_gate.py` | Lista de atividades e vínculo por hash | Coach |
| GA-5 | **[feito no GAP-A2 em `scripts/command_idempotency.py`: formato único `rotina-AAAA-MM-DD-<tipo>-<id>` (S15-R6), `tipo` em briefing ou lembrete2, data local de Campo Grande; formato antigo recusado; janela de assinatura de 120 s e janela de dia são regras distintas; PROPOSTA a confirmar pelo proprietário]** **Dois formatos** de chave de idempotência (S8-R1 `rotina-AAAA-MM-DD-briefing` × S15-R6 `rotina-AAAA-MM-DD-<tipo>-<id>`); janela do comando 120 s × janela de rotina da S15-R6 | Baixa (divergência) | S8, S15, schema | Escolher um formato e reconciliar as janelas | Coach |

## GAP-B (GB) — Tempo e rotina (entrega: `scripts/day_classifier.py`)

| ID | Gap | Gravidade | Onde | Correção proposta | Origem |
|---|---|---|---|---|---|
| GB-1 | **[feito no GAP-B: `scripts/day_classifier.py`, função pura com relógio injetado e entrada desconhecida que não classifica]** A classificação do dia (S15-R16: `DESCANSO`, `SEM_PLANO`, `REVISAO_VENCIDA`, `DEVIDO_HOJE`…) **não existe em código**; o Coach classifica à mão | Média | S15-R16, `scripts/` | Função pura com relógio injetado e testes | Coach |
| GB-2 | **[feito no GAP-B: `check_projection` aceita instante UTC (e a data legada), `conferir_idade` aplica 24 h para prazo e 72 h para orientação, o gerador emite instante UTC]** `session_read_guard.py` aceitava `gerado_em` só como **data**, mas a S15-R5 exige idade máxima de 24 h (instante UTC): projeção com timestamp é recusada | Média | `scripts/session_read_guard.py` | Aceitar instante UTC ou rever a S15 | Coach |

## GAP-C (GC) — START e documentos (entrega: `scripts/study_summary.py`)

| ID | Gap | Gravidade | Onde | Correção proposta | Origem |
|---|---|---|---|---|---|
| GC-1 | **[feito no GAP-C: `scripts/study_summary.py`, resumo de até 4 KB gerado de `AGENTS.md` e `state/CURRENT.json`, com hash e verificação de defasagem; é auxílio e NÃO substitui o START de quatro arquivos até o proprietário aprovar a troca em `AGENTS.md`]** O START de estudo exige ler cerca de **115 KB** (ROADMAP e HANDOFF com histórico de engenharia) | Média | `AGENTS.md`, `memory/HANDOFF.md`, `ROADMAP.md` | Resumo de estudo de **uma página**, gerado e com hash | Tutor e Coach |
| GC-2 | **[feito no GAP-C: o broker declara `sha_origin` (orquestrador, ci, local ou não declarada) e `--producao` exige origem externa; a origem é DECLARADA pelo ambiente, não provada aqui]** O SHA confiável do START vem do **git local** (circular) quando não há SHA externo | Média | `scripts/agent_entrypoint.py`, `scripts/bootstrap.py` | Exigir SHA externo para o START de produção; declarar o limite | Coach |
| GC-3 | **[feito no que não é contrato: HANDOFF rotulado como histórico, IMC reconciliado, ROADMAP explica próxima RM-08 × frente RM-09; dois itens de contrato ficam como decisão do proprietário, abaixo]** Divergências documentais: parágrafo "Estado" do HANDOFF defasado; "IMC-COACH-001 será reanexado" (já está no repositório); ROADMAP "próxima RM-08" × frente ativa RM-09; AGENTS.md pede "quantidade sugerida" mas o script só a produz com disponibilidade confirmada; `registrar_acompanhamento` no perfil do Coach com destino inoperante (flags `false`) | Baixa | HANDOFF, ROADMAP, `AGENTS.md`, `agents/COACH.md` | Reconciliar em um lote documental | Tutor e Coach |

## GAP-D (GD) — Tutor e cadernos (entrega: `scripts/tutor_coach_handoff.py`)

| ID | Gap | Gravidade | Onde | Correção proposta | Origem |
|---|---|---|---|---|---|
| GD-1 | **[feito no GAP-D: `scripts/tutor_coach_handoff.py`, esquema fechado do registro de passagem com validador e encaminhamento (S13-R3); mapa código→destino é leitura proposta]** Não existe **formato estruturado Tutor→Coach** (IMC 11.2 é lista de cinco sinais; S13-R3/T3 não implementado) | Média | S13, `docs/canonicos` | Esquema do registro de passagem com validador | Tutor |
| GD-2 | **[feito no GAP-D: campo `meta` {pretendida, disponivel, status} separado em `notebook_prescriber`]** `questions_suggested` é nulo sem disponibilidade; falta campo **"meta pretendida"** separado | Média | `scripts/notebook_prescriber.py` | Campo `meta` distinto de `disponibilidade` | Tutor |
| GD-3 | **[feito no GAP-D: `agent_commands.texto_de_questao` pega comando de prova, alternativas entre parênteses e `Gabarito:` nos params (`PARAMS_TEXTO_DE_QUESTAO`); continua heurístico; o filtro do prompt do Notebook já existe na N2 (`QUESTAO_INTEGRAL`)]** Filtro de dado pessoal **heurístico** (não pega texto de questão em prosa curta); filtro do prompt do Notebook pendente (S2-R7) | Média | `scripts/agent_commands.py` (`scan_text`), `notebook_prompt_validator.py` | Reforçar e testar contraprovas | Tutor |
| GD-4 | **[PARCIAL no GAP-D: estrutura e conferência prontas (`config/norma_ancoras.json`, `conferir_citacao_norma`), lista de âncoras VAZIA porque planalto.gov.br estava bloqueado e texto de memória não é fonte; PENDENTE DO PROPRIETÁRIO: fornecer o trecho oficial por artigo ou liberar o acesso]** **Sem cópia ou âncora local da Lei 8.112**: a conferência da S10-R7 é externa | Média | `docs/`, S10-R7 | Âncora por artigo e página no repositório (texto oficial, só o necessário) | Tutor |
| GD-5 | **[PARCIAL no GAP-D: `decision_queue.rank_simple` (poucos fatores, sem SHA, snapshot marcado `simples` e `auditavel: False`); tópicos mais finos NÃO feitos: dividir `GER-LEG` exige citar páginas do edital por subtópico e se cruza com o top 10 da S16, decisão do proprietário]** `decision_queue` exige 10 fatores e SHA para consulta simples; mapeamento tópico→edital **grosso** (`GER-LEG` engloba toda a legislação) | Baixa | `scripts/decision_queue.py`, `config/topics.csv` | Consulta simples e tópicos mais finos | Tutor |

## GAP-E (GE) — Manual e IMC (entrega: `scripts/manual_pages.py`)

| ID | Gap | Gravidade | Onde | Correção proposta | Origem |
|---|---|---|---|---|---|
| GE-1 | O Coach **não leu** as p. 148 a 153 (conector do Drive truncou; só ficha e sumário): S18-R14 **não é cumprível** com o PDF único | **Alta** (para a S18-R14) | S18-R14, índice do Manual | Derivado **paginado** na pasta privada (decisão do proprietário) e teste de leitura | Coach |
| GE-2 | Os gates `G-MOT-01` a `22` são **todos não implementados** (14 aplicados só por conduta) | Média | S18-R11 | Implementar os verificáveis, em tarefa própria e com aprovação | Coach |

## HOOKR — Hook de passagem desarma abaixo do limite (entrega: `scripts/context_guard_state.py`)

| ID | Gap | Gravidade | Onde | Correção proposta | Origem |
|---|---|---|---|---|---|
| HK-1 | `armed_at` e `sealed` ficam **permanentes** na sessão: depois do falso alarme (janela de 200k), o hook de perguntas **cede para sempre**, mesmo com a medição corrigida (43% de 1M) | Média | `scripts/claude_context_guard.py` (`on_measure`), `.claude/hooks/perguntas_boas_praticas.py` (só lê) | Desarmar quando a medição cair abaixo do limite, com teste que falha antes e contraprova de que acima do limite continua armado | Proprietário (21/11/2026) |

## G — Zapia e proprietário (fora do repositório)

| ID | Pendência | Quem |
|---|---|---|
| G-1 | Cota e uso reais do plano Pro (tela **Uso do plano**), histórico por execução (tela **Rotinas**) | proprietário |
| G-2 | Menor intervalo, execuções por dia, janela máxima, aviso de falha, nova tentativa, recuperação de execução perdida, pontualidade | prova sem efeito (S15-R4) com `AUTORIZO` |
| G-3 | Hook em conta real (nenhum configurado; WhatsApp e Gmail não conectados) | proprietário |
| G-4 | Envio pelo **Outlook** sem confirmação e como restringir a leitura (risco aceito em 21/11/2026, sem prova) | proprietário |
| G-5 | Proteção contra instrução embutida no evento do hook | prova sem efeito |
| G-6 | Decisões D1 a D3 da S20 (como o comando chega à Zapia, quem acorda os agentes, onde fica a chave) | proprietário |

## Limites

Este registro **não prova** que os achados dos subagentes são corretos; **não corrige** nenhum deles; a Zapia é **autorrelato (C)**. Os lotes GAP-A a GAP-E seguem o fluxo único: uma branch, um PR draft, testes e contraprovas, e merge só por pedido expresso do proprietário.

## Decisões de contrato pendentes do GC-3 (21/11/2026)

- **DECISÃO DO PROPRIETÁRIO PENDENTE (AGENTS.md, quantidade sugerida):** a ordem operacional item 5 pede "quantidade sugerida", mas o script de caderno só a produz com disponibilidade confirmada, e o contrato proíbe inventar disponibilidade. Opções: manter (a quantidade é sugestão do Tutor, sem afirmar disponibilidade) ou reescrever o item. Não alterado: `AGENTS.md` é arquivo de contrato.
- **DECISÃO DO PROPRIETÁRIO PENDENTE (agents/COACH.md, registrar_acompanhamento):** a operação consta no perfil do Coach, mas seu destino (`repo_privado_dados`) fica inoperante enquanto as flags de gravação estão `false`. Opções: manter (o validador já a recusa com a flag falsa, GAP-A) ou retirá-la do perfil até a janela do piloto. Não alterado: `agents/` é contrato.
