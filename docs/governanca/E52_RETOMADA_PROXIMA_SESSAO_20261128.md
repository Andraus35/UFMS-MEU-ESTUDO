# E52: ponto de retomada da sessão de 27 e 28/11/2026 (canal de engenharia, despertar dos agentes, rodada Tutor–Coach)

**Natureza:** registro de **continuidade**, não contrato nem prova. Tudo vem da conversa e dos arquivos do repositório; autorrelato da Zapia está marcado (confiança B). **Leia depois do START e antes de agir.** Estado vivo: `state/WORKFLOW.json` e `python scripts/next_task.py`. **Substitui** o E46 §3 (estado do `entrada` e da Zapia) e §7 (ordem das tarefas); o resto do E46 (decisões do N1, prompts do apêndice A) continua válido.

## 1. Onde estamos
- `main` tem os PRs **#192 a #212** mesclados (último: **#212**, squash `206306492cb6dbc7002bf7e2c26a81ffa86eee11`, CI da main verde). Ciclo ativo: **#213** (draft; lote `RODADA-TUTOR-COACH` mais os ajustes do canal que ela usa). Merge **só por pedido do proprietário citando PR e head**, CI verde no head exato.
- Frentes: (a) **canal de engenharia** entre o orquestrador e a Zapia (E49), (b) **despertar dos agentes** (E50), (c) **conversa Tutor–Coach** (E51). Nada de dado do aluno entra (estado E0; resultados pessoais `false`).
- Contas Zapia: **antiga e nova autorizadas e intercambiáveis só na engenharia** (decisão de 27/11/2026, em `CAPACIDADES_ZAPIA_VERIFICADAS.md`). O hook de Gmail só funciona na conta que **recebe o Gmail** `souza.merchan@gmail.com`; a conta nova relatou que **não** recebe. Conta Google do Notebook: `andraus.dev@gmail.com`.

## 2. O canal de engenharia (E49): estado e lições
- **Hook** `9f622bbf` (recorrente, habilitado, conta `souza.merchan@gmail.com`; filtro `[Andraus35/ufms-meu-estudo-entrada] ENG`). **Texto salvo hoje na Zapia: v9 (3941 caracteres, com o passo 5, base64 na leitura).** **Texto do repositório: v10 (3947 caracteres, leitura crua do pedido)**: **a Zapia ainda não o aplicou.**
- **Prompt para ela atualizar:** `python scripts/canal_engenharia.py --entrada . --prompt-hook` (gerado por código, sempre igual ao `hook_engenharia`). **Dê o prompt completo ao proprietário em toda resposta** (pedido dele).
- **Rodadas no `entrada`** (`comandos/engenharia/pedidos|respostas|registro/`): `eng-0001` recusada (`HASH_NAO_CONFERE`, eco de 64 caracteres com 1 errado); `eng-0002` recusada (e-mail no item "Conta"); `eng-0003` `PARADO` sem motivo; `eng-0004` recusada (item de 646 caracteres); **`eng-0005` ACEITA (`notebook_listar`, a única com conteúdo aceito)**; `eng-0006` `PARADO` sem motivo (primeira tentativa do TEC); `eng-0007` `PARADO` **com motivo**: "operawao" (a Zapia errou a chave ao decodificar base64) e o passo 5 falhou por **HTTP 403**.
- **Lições gravadas em código e teste:** assunto "começa com" (`extrair_id`, o GitHub acrescenta ` (Issue #N)`); título da issue só `ENG eng-NNNN`; eco de 16 caracteres (`pedido_sha16`); sem e-mail nos itens; itens de até 300 caracteres (dividir); `PARADO` exige um item `motivo`; leitura **crua** do pedido (`Accept: application/vnd.github.raw+json`); o texto do hook tem margem de 3950 caracteres (limite real 4000), só ASCII.
- **Não provado:** o **TEC pelo canal** (as três tentativas pararam antes), o `notebook_renomear`, a estabilidade em muitas ativações, o passo 5, a autenticidade do emissor no `entrada`.
- **Estado no `entrada`:** issues **#12 a #19 abertas: NÃO fechar nem comentar** com o hook habilitado (qualquer e-mail com o filtro o aciona); `comandos/engenharia/PARAR` **não existe**; comandos `n1c` do N1 **vencidos** (27/11 21:55Z); `sondas/` vazia. O anexo do `entrada` à sessão é **exceção dele**; **a revogação é ato dele**; refaça o `add_repo` (`access: push`) e clone `--depth 1` em `/home/user/ufms-meu-estudo-entrada`; grave **só** em `comandos/engenharia/` (e `sondas/` nas sondas), sem tocar fluxo, flag nem fila.
- **Conferir sempre por código:** `python scripts/canal_engenharia.py --entrada <clone>` (resumo: `aguardando_resposta`, `a_conferir`, `aceitas`, `aceitas_mas_paradas`, `recusadas`), `--conferir eng-NNNN`, `--proximo <agente>`, `--consumir <agente> <id>`, `--auditar <papel>` (caminhos pela entrada padrão).

## 3. Despertar dos agentes (E50)
- Caminho escolhido pelo proprietário: **D** (a Zapia abre a issue `RESP eng-NNNN` ao terminar; uma **rotina com gatilho GitHub de issue aberta** acorda uma sessão nova). **Bloqueado:** o token da Zapia recebeu **HTTP 403** em issues. Saídas: dar `Issues: Read and write` ao token fino (aumenta o poder dele) **ou** o caminho `/fire` (C, a Zapia dispara a rotina por API com token no cofre dela) **ou** nenhum dos dois.
- **Rotina ainda não criada.** Prompt fixo: `config/rotina_despertar_prompt.txt` (SHA-256 `666d66c7a200be9ca2ac75c42d10a5509b398ab1b02c573f0397b3901a90dda7`, pinado em teste). Ela só grava `registro/` e `leitura/` do `entrada` (decisão dele); `--auditar rotina` detecta violação. Rotinas abrem **sessão nova**; a documentação está em prévia; gatilho de API só se cria na web.
- **S22** (tarefa agendada de execução única): ele marcou a opção mas **não deu o horário** nem escreveu "Criar a tarefa S22"; **nada foi criado**; **nunca** crie tarefa agendada sem a frase e o horário.

## 4. Conversa Tutor–Coach (E51)
- Modelo aprovado: **orquestrador único + Tutor e Coach como subagentes em fases fixas, mensagens de esquema fechado**; síncrono só **dentro da sessão**; assíncrono pelo repositório entre sessões e com TEC e Notebook; **sem dado real** até a janela do piloto; agent teams **não** recomendado.
- Código offline e sintético: `scripts/rodada_tutor_coach.py` (pacote, saídas por papel, rodada com hash). **Falta:** ligar o resumo do canal ao START do broker (PR de contrato), chamar subagentes reais numa sessão e provar o esquema com saídas reais. RM-08 segue **bloqueado** por atos dele.

## 5. Decisões do proprietário (não reabrir)
Canal e Notebook pela Zapia (D-26, D-27); prompts do N1 vêm do Tutor; Gmail da `souza.merchan` é a caixa do disparo; duas contas Zapia intercambiáveis na engenharia; hook de engenharia só leitura, renomear e respostas em `respostas/`; chave de parada `PARAR`; eco de 16 caracteres; **não** afrouxar o filtro de e-mail; só RM-09 (RM-08 segue bloqueado); rotina grava só em `registro/` e `leitura/`; sem dado real nesta fase.

## 6. Atos do proprietário pendentes (ordem)
1. **Aplicar o v10 na Zapia** (colar o prompt de `--prompt-hook`) e trazer o relato (ID, conta, filtros, recorrente, habilitado, texto salvo, diferenças).
2. **Decidir o despertar:** `Issues: Read and write` no token da Zapia (D), ou token `/fire` no cofre dela (C), ou nenhum.
3. **Criar a rotina na web** (gatilho GitHub, evento **issue aberta**, repositórios principal e `entrada`, prompt do arquivo acima) e **instalar o Claude GitHub App no `entrada`** (a documentação não diz se funciona em repositório privado).
4. **S22:** se quiser, "Criar a tarefa S22" com horário.
5. Revogar o anexo do `entrada` ao fim; apagar ou manter os cadernos de teste do Notebook (nunca "REVISAO UFMS DIREITO ADM" nem "AUDITORIA"; há dois "diagnostico-n1-descartavel": `cff90194` com 2 fontes e `3ed6adfe` com 0); P9 (tokens, aviso de 04/12), janela PJ, consentimento v4 e reinstalar o fluxo seguem pendentes (ver HANDOFF e `next_task.py`).

## 7. Trabalho da próxima sessão (uma tarefa por vez, merge antes de mudar de frente)
1. Conferir no GitHub: último PR mesclado, SHA da `main`, CI; PR **#213** (draft): CI no head, descrição; pedir o merge só com "Mesclar" citando PR e head. Registrar o recibo no **primeiro commit** da tarefa seguinte (`scripts/record_merge_receipt.py`); reiniciar a branch da sessão de `origin/main` e usar `git merge -s ours origin/<branch>` após cada squash.
2. **ENG-V10-HOOK:** com o relato do v10, abrir `ENG eng-0008` (`tec_listar_cadernos`, `motivo` neutro, descritivo, nunca imperativo), conferir por código, gravar o registro; se parar, ler o `motivo`. Meta: **provar o TEC pelo canal**.
3. **ENG-DESPERTAR:** conforme a decisão dele (item 2 acima), provar a cadeia `RESP` → rotina → `--proximo`.
4. **RODADA-NO-START:** PR de contrato (aprovação expressa do texto): resumo do canal no START do broker; só então chamar subagentes reais.
5. **N1-RODADA-4** (hook v4 do N1, kit `n1d`, prompts do Tutor) e **E45-CORRETOR** seguem as filas do E46; o E47 (diagnóstico do "Texto copiado") está feito.

## 8. Armadilhas
- **Bytecode velho:** mutação que não muda o tamanho do arquivo (`16`→`64`) engana o Python; **apague `__pycache__`** (`find scripts tests -name __pycache__ -prune -exec rm -rf {} +`) antes de rodar mutações.
- `state/WORKFLOW.json` está **perto de 64 KiB** (o START recusa acima); o HANDOFF tem orçamento de 60 KiB (`tests/test_handoff_orcamento.py`); arquive antes de crescer.
- O texto do hook tem de ter **≤ 3950** caracteres (limite real 4000), **só ASCII**; mudar o hook muda o texto do repositório **e** exige a Zapia atualizar o salvo; a comparação "sem diferenças" é dela (autorrelato).
- O `motivo` de um pedido **não** pode soar como instrução (hipótese não provada: a `eng-0003` pode ter parado por isso).
- `sleep` em bloco foi bloqueado; use `python3 -c "import time; time.sleep(N)"`. Resposta da Zapia leva ~2 minutos.
- Um PR por vez: **não misturar frentes**; o #213 declara os ajustes do canal como parte do lote porque a rodada emite pedidos do canal.

## 9. Como a próxima sessão verifica que tudo está aqui
`python scripts/bootstrap.py --mode engineering`, `python scripts/single_flow_gate.py --check`, `python scripts/next_task.py`, `python -m unittest discover -s tests` (~2790 testes, ~3 min), `python scripts/canal_engenharia.py --entrada <clone>`, `python scripts/canal_engenharia.py --entrada . --prompt-hook`.
