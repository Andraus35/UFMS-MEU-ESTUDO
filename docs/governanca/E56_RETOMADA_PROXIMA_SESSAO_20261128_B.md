# E56: ponto de retomada depois do lote de 28/11/2026 (canal pronto, rotina de despertar, rodada Tutor–Coach)

**Natureza:** registro de **continuidade**, não contrato nem prova. Estado vivo: `state/WORKFLOW.json` e `python scripts/next_task.py`. **Substitui** o estado do E52 (§1 a §4 e §6); o resto do E52 (armadilhas, decisões) continua válido. Leia depois do START.

## 1. Onde estamos (28/11/2026)
- `main` tem os PRs **#213 a #219** mesclados (squash do #219: `4368e00d31f8917f6ed9b3c8dd2867d4759b4b6e`). Ciclo ativo: **#220** (lote de reconciliação; draft). Merge **só por pedido do proprietário**, CI verde no head exato ("Mesclar" vale com um só PR aberto).
- Entregas: hook de perguntas que **persiste** o estado e as respostas (`memory/PERGUNTAS.json`, `scripts/registrar_perguntas.py`, E53 do hook); **canal de engenharia provado** para `notebook_listar`, `tec_listar_cadernos`, `tec_estrutura_caderno` e o **passo 5**; hook ENG **v14** (3927 caracteres) na Zapia; sinônimo `items` aceito no validador; **rotina de despertar** criada e provada em 4 execuções; **emenda E54** da S6-R6 (Issues no `zapia token`) com o perfil `privado_issues`; **resumo do canal no START do broker** (`--entrada`, E55); rodada Tutor–Coach sintética com subagentes reais; `state/WORKFLOW.json` arquivado (59 KB).

## 2. Como o canal funciona hoje
1. Orquestrador grava `pedidos/eng-NNNN.json` (`canal_engenharia.montar_pedido`) no `entrada` e abre a issue `ENG eng-NNNN`; **a 1ª issue às vezes não acorda o hook** (2 de 6): reabra outra issue com o mesmo título após ~5 minutos.
2. Hook de Gmail (`9f622bbf`) → Zapia opera TEC ou Notebook, grava `respostas/` e abre `RESP eng-NNNN` (resposta em 2 a 5 minutos; a chave pode vir como `items`, aceita).
3. Rotina de despertar (gatilho GitHub, ambiente Default) grava `registro/` em **branch `claude/adoring-turing-*`**; o orquestrador **confere por código** (`--conferir`) e grava o `registro/` na `main`.
- `add_repo` do `entrada` (`access: push`) e clone em `/home/user/ufms-meu-estudo-entrada` se repetem em sessão nova; **revogar é ato do proprietário**. Issues `ENG`/`RESP` (#12 em diante): **não fechar nem comentar**.

## 3. Pendências do proprietário
1. Sonda do token: `PERFIL=privado_issues bash scripts/termux/verifica_token.sh` (sem mostrar o token).
2. Excluir pelo navegador os branches `claude/adoring-turing-*` do `entrada` (a exclusão por este ambiente foi **recusada**).
3. Conferir nos detalhes da rotina se o **filtro Autor = Andraus35** está ativo; revisar o **pedido de permissões pendente** do App Claude antes de aceitar.
4. Revogar o anexo do `entrada` ao fim; PJ, RM-08, `S22-PROVA-MIN` (frase "Criar a tarefa S22" e horário) e `N1-RODADA-4` seguem dele.

## 4. Ordem das tarefas (uma por vez, merge antes de mudar de frente)
1. Conferir CI e mesclar o #220 (reconciliação). Depois, `git fetch` e `git reset --hard origin/main` + `git merge -s ours origin/<branch>` (squash recusa o push normal).
2. **`FILTRO-HASH-CPF`** (decidido: isentar campos de hash no `scan_text`, com contraprova de que CPF de verdade segue recusado; muda código de segurança, texto a aprovar).
3. `N1-RODADA-4` (próximo item liberado; uma issue `SINAL` já confirmada pelo proprietário).
4. Eventual `RODADA-NO-START` evoluir: chamar os subagentes numa sessão com o clone do `entrada` e gravar a rodada (hoje só sintética, sem gravação).

## 5. Armadilhas
- O texto do hook tem de ter **≤ 3950** caracteres, só ASCII; mudar o hook exige a Zapia reaplicar (prompt: `python scripts/canal_engenharia.py --entrada . --prompt-hook`). A Zapia **diz "sem diferenças" sem conferir**: compare o tamanho e trechos.
- `state/WORKFLOW.json` ~59 KB (limite 64 KiB); o HANDOFF tem orçamento de 60 KiB. Arquive antes de crescer.
- `.claude/hooks/` e `scripts/agent_entrypoint.py` pedem aprovação expressa do texto; tarefa em lote não mistura frentes.
- Um subagente real tende a devolver campos extras; a recusa em código é o que protege.
