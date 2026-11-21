# Fila de auditoria Tutor e Coach (21/11/2026)

**Natureza:** registro dos achados de dois sub-agentes (perfil Tutor e perfil Coach) que testaram o repositório **por dentro, offline e somente leitura**, com entradas sintéticas, e da fila de correção que sai deles. **Nada foi corrigido neste lote.** Cada correção entra em um lote próprio da fila (`COR-A` a `COR-E` em `state/WORKFLOW.json`), com **teste que falha antes**, uma branch, um PR draft e contraprovas em ALTA e MEDIA; merge só por pedido expresso do proprietário.

**Escopo e limite do que foi testado:** validadores, caixa de comandos, verificador de entrega, gates e classificação do dia, em código real. **NÃO foram testados** a Zapia real, os lembretes agendados, o Gemini Notebook, Calendar/Tasks nem o canal Zapia↔repositório: exigem sessão e conexão do proprietário, `AUTORIZO` e teste sem efeito (WhatsApp não está conectado). Não se sabe se a Zapia usa o validador (autorrelato). Os relatórios dos agentes são **saída de modelo**: por isso cada item traz a coluna **Confirmação**: `reproduzido` = a sessão principal rodou a reprodução e viu a saída; `relatado` = só o agente rodou.

## Achados do Tutor (AT)

| ID | Severidade | Achado | Onde | Confirmação | Lote |
|---|---|---|---|---|---|
| AT-1 | **Alta** | `delivery_gate` aceita COMANDO `enviar_prompt_notebook` **sem conferir o prompt** (texto livre, hash errado, instrução embutida: `ACEITA`); o validador e a caixa recusam o mesmo texto (`HASH_DIVERGENTE`, `FORMA_NAO_CANONICA`) | `scripts/delivery_gate.py` `_comando` | reproduzido | COR-A |
| AT-2 | Média | O formato do prompt diverge: o envelope `PROMPT_NOTEBOOK` espera 5 campos; o comando e a caixa usam `{prompt, prompt_sha256}`; um `preparar()` válido enviado como `PROMPT_NOTEBOOK` é recusado. Não há definição única do que a Zapia recebe | `delivery_gate.py`, `notebook_prompt_validator.py` | relatado | COR-A |
| AT-3 | Média | URL **sem esquema** passa no prompt do Notebook (`google.com.br`, `example[.]com`, `hxxp://`); a S10-R3 proíbe endereço da web | `notebook_prompt_validator.py` `_URL` | reproduzido | COR-C |
| AT-4 | Baixa/Média | Instrução embutida heurística com bypass (`act as DAN`, homóglifo cirílico, leet); texto de questão em prosa aceito no campo `lacuna` (o validador do prompt não usa `texto_de_questao`) | `notebook_prompt_validator.py` | relatado | COR-C |
| AT-5 | Baixa | `enviar_mensagem` aceita URL e "ignore previous instructions" no validador e na caixa; o `delivery_gate` recusa URL: validador e caixa são mais permissivos que o verificador | `agent_commands.py`, `command_box.py` | relatado | COR-C |
| AT-6 | Baixa | `tutor_coach_handoff.validar_registro` aceita `objetivo` com URL, instrução embutida e nome com contagem de erros; `notebook_prescriber` aceita `objetivo` com CPF e URL (plano interno) | `tutor_coach_handoff.py`, `notebook_prescriber.py` | relatado | COR-C |
| AT-7 | Baixa | `platform_read_guard._tem_efeito` só tem tokens em português: `.../cadernos/delete/1` e `?action=submit` dão `False` | `platform_read_guard.py` | relatado | COR-C |
| AT-8 | Info | `ler_arquivo_repositorio` aceita `state/CURRENT.json`; sem lista de permissão por caminho (só bloqueio de oculto e travessia) | `command_params_schema.py` | relatado | COR-E |
| AT-9 | Info (contrato) | `agents/TUTOR.md` lista `registrar_*` como emitíveis sem ressalva, mas a caixa os recusa (`REGISTRAR_FORA_DA_CAIXA`, deliberado, S6-R3). **DECISÃO DO PROPRIETÁRIO PENDENTE** (arquivo de contrato) | `agents/TUTOR.md` | relatado | proprietário |

## Achados do Coach (AC)

| ID | Severidade | Achado | Onde | Confirmação | Lote |
|---|---|---|---|---|---|
| AC-1 | **Alta** | O `delivery_gate` **não confere a idade da projeção** (S15-R5): `conferir_idade` não é chamada na entrega; projeção de `2026-01-01` com agora em 21/11 aceita o LEMBRETE | `delivery_gate.py` `verificar_entrega` | reproduzido | COR-A |
| AC-2 | Média | O vínculo por hash não amarra os ids: hash do LEMBRETE de UFMS-002 com `atividade_ids: ["UFMS-003"]` (também pendente) é aceito; o hash não é recalculado | `delivery_gate.py` `_vinculo_lembrete` | reproduzido | COR-A |
| AC-3 | Média | A chave `briefing` aceita **qualquer id** (`briefing-x/y/z`): a deduplicação por chave e o teto de 2 mensagens por dia não valem; não existe decisor do teto | `command_idempotency.py` | reproduzido | COR-B |
| AC-4 | Média | O descanso só é checado para `criar_lembrete`; `enviar_mensagem` com chave `lembrete2-...` em dia de descanso é promovida (S8-R1 diz que o lembrete2 é recusado); sem checagem de atividade pendente | `command_box.py`, `agent_commands.py` | relatado | COR-B |
| AC-5 | Média | `gates_mot` **não está ligado à entrega**; paráfrases escapam ("Aprovação garantida", "Garanto que você passa", "Você tem TDAH", "Pare a medicação", "Você é um preguiçoso") e há **falsos positivos** ("Ninguém pode garantir aprovação", "Não quero que você durma menos": a janela de negação de 15 caracteres é curta) | `gates_mot.py` | reproduzido (paráfrases e falsos positivos) | COR-D |
| AC-6 | Média/Baixa | `verificar_intervencao` **falha aberto** em tipo não booleano: `sofrimento.intenso_ou_persistente: "sim"` passa sem encaminhamento; `eficacia.declarada: "true"` passa; `comportamento_alvo` aceita qualquer texto | `gates_mot.py` | reproduzido (`"sim"`) | COR-D |
| AC-7 | Baixa | Lacunas do detector de desempenho e disponibilidade: "12 de 20 acertos", "quarenta por cento", "taxa de 0.4", "12/20", "40٪", "Há cadernos prontos", "existem questões suficientes" aceitos; `enviar_mensagem` não tem o limite de 500 caracteres do LEMBRETE. **A sessão principal não reproduziu o exemplo "12 de 20 acertos" no corpo de ORIENTACAO (foi recusado); a reprodução do agente foi em outro tipo de envelope** | `delivery_gate.py` | relatado | COR-D |
| AC-8 | Baixa | `janela_segundos` é injetável no contexto da caixa sem teto; chave `ROTINA-...` em maiúsculas não é tratada como chave de rotina e escapa da regra do dia; `consultar_agenda_minima` aceita data distante (2030) e em descanso | `command_box.py`, `command_idempotency.py` | relatado | COR-B |
| AC-9 | Baixa | `manual_pages`: citação aceita fragmento no meio de palavra; páginas com texto idêntico compartilham o hash; `conferir_idade` com data sem hora e uso orientação usa a idade mínima (`2026-11-18` pode ter 84 h e sai OK sem aviso) | `manual_pages.py`, `session_read_guard.py` | relatado | COR-E |

## Lacunas entre especificação e código (declaradas pelos agentes)
- **S8-R1 e S15-R17:** teto de duas mensagens por dia, lembrete2 só se pendente e fora de descanso, contador de três dias sem interação: **sem código** (só a classificação do dia existe). **S8-R5 a R9:** sem validador de job, modelo de tarefa com START nem decisor de falha segura (declarados "a implementar"). Entram no lote **COR-B** como parte do decisor.
- **S15-R5:** idade da projeção não aplicada na entrega (AC-1). **S10-R3:** domínio sem esquema (AT-3). **S10-R6/R7:** nenhum código consome e verifica a resposta do Notebook (declarado "não provado", N1).
- **S20-R2, P2, P4, D3:** sem chave fora do modelo e sem mecanismo que leve o comando à Zapia; o código só valida a forma. A premissa de janela de 300 s do runner não consta em S15, S19 e S20 (o padrão é 120 s).

## Fila de correção (lotes, em série; um PR draft por vez)
| Lote | Itens | Frente |
|---|---|---|
| COR-A | AT-1, AT-2, AC-1, AC-2 | entrega integrada: o verificador passa a conferir prompt, idade da projeção e vínculo por hash recalculado |
| COR-B | AC-3, AC-4, AC-8 e o decisor do teto diário (S8-R1, S15-R17) | chave e limites diários da rotina |
| COR-C | AT-3 a AT-7 | filtros de conteúdo do prompt, das mensagens e da leitura de plataformas |
| COR-D | AC-5, AC-6, AC-7 | gates G-MOT ligados à entrega, fail-closed e paráfrases (ainda heurística) |
| COR-E | AT-8, AC-9 | endurecimento menor: lista de permissão de caminhos, manifesto do Manual, idade da projeção por data |

## Fora do alcance do repositório (atos do proprietário)
- **Teste real** da Zapia e do Gemini Notebook (notebook descartável, N1; canal; chave de assinatura fora do modelo; `AUTORIZO`): só na janela do piloto ou em teste sem efeito dele.
- **AT-9** (`agents/TUTOR.md`) e as decisões de contrato do GC-3 seguem pendentes.
