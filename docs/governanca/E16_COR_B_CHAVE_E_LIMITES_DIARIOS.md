# E16: COR-B, chave e limites diários da rotina (21/11/2026)

**Natureza:** registro do lote COR-B da fila de auditoria Tutor e Coach (`docs/governanca/FILA_AUDITORIA_TUTOR_COACH_20261121.md`). Nada altera `agents/`, `AGENTS.md`, `PRODUCT.md` nem o esquema de comandos. Os limites abaixo são **PROPOSTA** (S8-R1 e S15-R17), a confirmar pelo proprietário.

| Achado | Correção | Prova |
|---|---|---|
| AC-3 (média) | A chave `briefing` só aceita o id fixo `dia` (`CHAVE_BRIEFING_ID_INVALIDO`); decisor do teto diário em `command_idempotency.decidir_rotina`: no máximo 1 `briefing` e 1 `lembrete2` por dia local (`TETO_DIARIO_TIPO`, `TETO_DIARIO`); chave do mesmo dia repetida passa (a idempotência é do registro); chaves de outro dia não contam; teto desconhecido (`None`) recusa (`TETO_DESCONHECIDO`) | `tests/test_cor_b_chave_limites_diarios.py`, `tests/test_command_box_runner.py` (teto em série na mesma execução) |
| AC-4 (média) | Descanso e atividade pendente valem para `criar_lembrete` **e** para qualquer chave `lembrete2` (inclusive em `enviar_mensagem`): `DIA_DE_DESCANSO`, `DESCANSO_DESCONHECIDO`, `SEM_ATIVIDADE_PENDENTE` (a da chave e as da lista), `PENDENCIA_DESCONHECIDA`; briefing e acompanhamento em descanso seguem permitidos (S8-R1: mensagem curta) | idem |
| AC-8 (baixa) | `janela_segundos` injetada tem teto (`MAX_JANELA_SEGUNDOS` = 86400, o da retomada do runner); `ROTINA-...` em qualquer caixa entra na regra e é recusada por formato (`CHAVE_ROTINA_INVALIDA`); `consultar_agenda_minima` só para hoje ou amanhã (data local, `AGENDA_DATA_FORA_DA_JANELA`) e nunca em descanso | idem |

**Contexto injetado (`command_box.validar` e `command_box_runner.executar`):** `dia_de_descanso`, `atividades_pendentes` e `chaves_do_dia`. O runner acrescenta a chave promovida ao teto das entradas seguintes (execução em série).

**Efeito em testes:** as chaves de teste `briefing-b`, `-outra` e `-velho` (id livre) viram chaves comuns; os contextos-padrão dos testes passam `atividades_pendentes` e `chaves_do_dia`.

**Limites (declarados):**
- O CLI do runner (`main`) **não tem leitor** de plano nem de histórico do dia: sem `chaves_do_dia` e `atividades_pendentes`, a chave de rotina e o `lembrete2` são recusados (fail-closed, como o descanso desconhecido já era). Antes de a rotina real existir é preciso um leitor injetado, ainda não implementado.
- O decisor vale na caixa; o validador `agent_commands.validate_command` (assinatura) não recebe esse contexto.
- S8-R5 a R9 (validador de job, modelo de tarefa com START, decisor de falha segura) e o contador de três dias sem interação seguem **sem código**.
- Os limites são propostas; nada foi cadastrado na Zapia nem testado com serviço real.
