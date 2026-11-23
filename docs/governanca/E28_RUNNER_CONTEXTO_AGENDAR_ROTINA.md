# E28: contexto do runner real para `agendar_rotina` (lote ZAPIA-CTX, 23/11/2026)

**Natureza:** registro do lote `ZAPIA-CTX` (RM-09, S20). Fecha a lacuna declarada na **E27**: o runner real da caixa não alimentava `hashes_promovidos` nem `agendamentos_do_dia`, e por isso todo `agendar_rotina` era recusado no fluxo real (`ALVOS_DESCONHECIDOS`, `TETO_DESCONHECIDO`). **Não altera `agents/`, `AGENTS.md`, o esquema de comandos nem `settings.json`**; muda só `scripts/command_box_runner.py` e testes. O merge segue o pedido expresso do proprietário, citando PR e head.

## O que foi feito

- **`Caixa.listar`** (`scripts/command_box_runner.py`): lista os arquivos comuns de uma pasta do `entrada` (pasta ausente = vazia; resposta fora do formato, falha de API: propaga como `ApiError`, sem inventar lista).
- **`ler_contexto_agendar(caixa, agora)`**: lê a caixa e devolve só duas listas, sem dado do comando:
  - **`hashes_promovidos`**: hash do comando inteiro de cada `comandos/validados/<nome>` que tem recibo `PROMOVER` do **mesmo nome** com o **mesmo hash recalculado** sobre os bytes de `validados/` (reaproveita `command_box.selecionar_executaveis`, a mesma regra de S6-R8 e S5-R7). Recibo ausente, ilegível, de status que não é promoção, hash divergente ou comando alterado depois do recibo: **não conta**.
  - **`agendamentos_do_dia`**: origem de cada `agendar_rotina` em `validados/` cujo `issued_at` cai no **dia local de Campo Grande** (`command_idempotency.data_local`, UTC−4) do relógio injetado. Conta **mesmo sem recibo** e com emissão ilegível (na dúvida, recusa a mais). Dia virado libera o teto; o dia anterior não conta.
  - Relógio sem fuso ou que não é data: devolve `{}` e o pedido segue recusado (`ALVOS_DESCONHECIDOS`).
- **`main`** passa a chamar `ler_contexto_agendar` e funde o resultado no contexto antes de `executar`. Falha de API nessa leitura cai no mesmo tratamento do runner (`ERRO` com a classe, nada promovido nem recusado).
- **Retomada** (`validados/<nome>` já existe): o pedido já promovido consta em `agendamentos_do_dia`; `_sem_o_proprio` tira **uma** ocorrência dele só na revalidação, para não ser recusado pelo próprio teto, sem apagar o teto de outro pedido da mesma origem.
- **Testes** (`tests/test_e28_runner_contexto.py`, 22): caixa vazia, alvo promovido aceito, recibo ausente, hash divergente, validado alterado, recibo de status errado, validado ilegível, teto por origem, dia virado e virada em Campo Grande (não em UTC), relógio sem fuso, contexto sem dado do comando, retomada com e sem outro pedido da origem, falha de API, listagem fora do formato, pasta ausente, subpasta e CLI ponta a ponta. Mutações verificadas: filtro do dia, parada da retomada, filtro de status do recibo e conferência de hash; todas mortas.

## O que NÃO está feito (declarado)

- **`dia_de_descanso`, `atividades_pendentes` e `chaves_do_dia` do lembrete continuam sem leitor** (o item citava que a mesma leitura pode alimentá-los; fica como lote próprio, porque exige o plano e o formato das chaves). `criar_lembrete` e a chave de rotina seguem recusados no fluxo real por falha fechada.
- **Provado só com o GitHub falso em memória.** Não houve execução no fluxo real do `entrada`; a prova real é ato do proprietário.
- **A leitura não é atômica** com a promoção: duas execuções concorrentes poderiam ler o mesmo estado. O fluxo é serial (S6) e o ledger e o teto continuam sendo a defesa; não há prova adicional.
- **A Zapia não executa este Python** e a **origem do comando não é provada na nuvem** (S4-R2); o ZAPIA-F3 (rotina cria rotina) segue **não provado**.
- Listagem do GitHub limitada a uma página da API (até 1000 itens por pasta); acima disso o contexto fica incompleto. A caixa tem teto de 500 entradas, mas `validados/` cresce com o tempo: **a paginação é lacuna conhecida**.

## Para o proprietário

Aprovar o merge, citando PR e head. Próximo item: **ZAPIA-F3**.
