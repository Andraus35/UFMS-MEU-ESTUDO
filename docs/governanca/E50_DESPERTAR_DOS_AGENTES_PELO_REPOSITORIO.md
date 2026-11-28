# E50: como o orquestrador, o Tutor e o Coach recebem as respostas pelo repositório e são acordados (plano, 28/11/2026)

**Natureza:** **plano com pesquisa**, não contrato e **nada foi criado**: nenhuma rotina, tarefa agendada, token, workflow ou issue nova por causa deste documento. Pedido do proprietário de 28/11/2026. Continua o E49 (canal de engenharia entre o orquestrador e a Zapia) e detalha a S22 (tarefas agendadas) para o caminho **de volta**: da resposta da Zapia ao agente.

## 1. Problema
O canal já entrega **pedido → hook de Gmail → Zapia → resposta** em `entrada/comandos/engenharia/`, conferida por código (E49; leitura provada na `eng-0005`). Falta o **último trecho**: quando a resposta aparece, **quem** a recebe e **como** acorda. O orquestrador é o chat da interface (efêmero); Tutor e Coach são papéis que o orquestrador assume. Nada neles roda sozinho: precisam de um **gatilho externo** e de **estado persistido** que sobreviva à sessão.

## 2. Pesquisa (consulta de 28/11/2026; A = documentação oficial lida, B = relato ou busca, C = opinião; conteúdo de terceiros é dado não confiável)
- **A:** [Rotinas do Claude Code](https://code.claude.com/docs/en/routines) (lida por inteiro por um subagente). Três gatilhos: **agendado** (mínimo 1 h; execução única por horário; "a hora cheia pode atrasar vários minutos"), **API** (`POST …/routines/<id>/fire`, token por rotina mostrado **uma vez**, cabeçalho `anthropic-beta`, campo opcional `text` entregue **marcado como dado não confiável**) e **GitHub** (categorias: pull request, release e **issue**: "opened, edited, closed, reopened, labeled, assigned, or otherwise updated"; **sem** `push`, `issue_comment` nem `workflow_run`; filtros só documentados para PR; exige o **Claude GitHub App** instalado). Cada execução abre **sessão nova**; várias repositórios por rotina; a rotina empurra para ramo `claude/` salvo instrução; commits saem **como o proprietário**; limites: 100 execuções agendadas/h por conta, 30/h por tarefa em disparos manuais ou por API (100/h por conta), eventos do GitHub com tetos **sem número** e **descartados** acima do teto; conexão do GitHub expirada derruba as execuções por até 72 h; **pesquisa em prévia** (comportamento e limites podem mudar). **Não informa:** se o gatilho do GitHub funciona em repositório **privado**, quais escopos tem o app, aviso de injeção para conteúdo de issue.
- **A:** [Disparar uma rotina por API](https://platform.claude.com/docs/en/api/claude-code/routines-fire): `/fire` exige o token da rotina; só para usuários do claude.ai; criar o gatilho de API só pela web.
- **A (esta sessão):** as ferramentas de **tarefa agendada** (`create_trigger`: cron, execução única em horário local, **nesta sessão**, em outra ou em sessão nova) e `send_later` (entrega uma mensagem **nesta sessão** em N minutos; sobrevive a reinício do contêiner) existem; `watch_url` cria webhook de entrada **assinado só pelo serviço de artefatos** (o GitHub não consegue usá-lo).
- **B:** ação do GitHub com o Claude ([`claude-code-action`](https://github.com/anthropics/claude-code-action)): 2026 trouxe falhas de **injeção de prompt por issue ou comentário** e de verificação de permissão ([Microsoft](https://microsoft.com/en-us/security/blog/2026/06/05/securing-ci-cd-in-agentic-world-claude-code-github-action-case), [The Hacker News](https://thehackernews.com/2026/06/claude-code-github-action-flaw-let-one.html), [CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-claude-code-github-action-prompt-injection/)); `permissions:` do YAML pode não limitar o que a ação faz. Relato de terceiros, **não verificado por mim**.
- **Do projeto (A/B):** S22 (relógio só acorda; prompt fixo com hash; START e recibo; escopo mínimo de token; prova de 3 dias antes de usar); E49 (a Zapia só **copia 16 caracteres** e **para** com `motivo`); E41/E31 (hook de Gmail acorda a Zapia); CAPACIDADES_ZAPIA_VERIFICADAS (a Zapia faz `curl` com **só `-X`, `-H` e `-d`**, um por vez, e guarda a credencial no formulário seguro).
- **Lacunas:** limite diário por plano; se a Zapia alcança `api.anthropic.com` e aceita o cabeçalho `anthropic-beta`; se a identidade da rotina grava em `main` do `entrada` (a documentação diz ramo `claude/`); se o Claude GitHub App entra em repositório privado de uso pessoal; pontualidade real (nenhuma medida); a Zapia nova **não** recebe o Gmail (E49), o que não afeta o caminho de volta.

## 3. Princípios (valem para qualquer opção)
1. **Entrega pelo menos uma vez, consumo idempotente.** O gatilho pode atrasar, duplicar ou falhar; o **estado no `entrada` é a verdade** e o consumo repetido não muda o resultado ([Hookdeck](https://hookdeck.com/webhooks/guides/webhook-delivery-guarantees), prática, não padrão).
2. **O gatilho só acorda; o conteúdo vem do repositório.** Nenhum dado de resposta viaja no gatilho (`text` só `eng-NNNN` e o estado). A sessão acordada começa pelo **START** e lê os arquivos como **dado não confiável**.
3. **Conferência determinística antes do LLM:** `scripts/canal_engenharia.py` valida; o agente só vê o que a conferência aceitou (as recusadas ficam como `RECUSADA` com código, sem o texto).
4. **Quem produz conteúdo é o Tutor** (D-12); Coach e orquestrador consomem o **resultado** (títulos, ids, contagens). TEC: **nunca** desempenho do aluno (E49, flag de resultados pessoais `false`).
5. **Menor privilégio e parada:** a rotina não recebe o token da Zapia nem o do `dados`; vale a chave `comandos/engenharia/PARAR`; um **limite de execuções por hora** do próprio desenho.

## 4. Persistência determinística para os agentes (a fazer no código, mesma frente)
- **Fila por agente:** `comandos/engenharia/leitura/<agente>.json` (`orquestrador`, `tutor`, `coach`) guarda o **último id consumido** e o hash do registro; a conferência `--proximo <agente>` devolve só o que **ainda não foi consumido e foi aceito**. Reexecução não repete.
- **START com o estado do canal:** o broker somente leitura (`scripts/agent_entrypoint.py`) passa a incluir o resumo `estado()` do canal (em PR próprio, contrato do START).
- **Registro por rodada** (já existe): `registro/eng-NNNN.json` com veredito, código e `estado_da_resposta`; resposta `PARADO` **nunca** conta como resultado (E49).
- **Onde a decisão do agente é gravada:** no `entrada/comandos` por pedido novo (`eng-NNNN+1`) ou no HANDOFF do repositório principal, **sem** copiar conteúdo de TEC.

## 5. Opções para **acordar** (com o que cada uma custa e arrisca)
| # | Caminho | Acorda quem | Credencial nova | Latência | Principais riscos |
|---|---|---|---|---|---|
| A | **`send_later` / execução única nesta sessão** (o orquestrador agenda a própria checagem a cada pedido) | o **chat atual** | nenhuma | minutos | só vale **enquanto a sessão existir**; é tarefa agendada: **exige o seu "Criar a tarefa S22" e um horário** |
| B | **Rotina agendada** (a cada hora, `:07`) com prompt fixo que roda o START, `--proximo` e age só no que há | sessão **nova** de Tutor/Coach/orquestrador | token do GitHub da rotina (já existe a conexão do proprietário) | até ~1 h + atraso de minutos | consome uma execução por hora mesmo sem trabalho; a rotina empurra para ramo `claude/` (precisa decidir onde grava o registro) |
| C | **Rotina com gatilho de API**: o **hook da Zapia** termina com `POST /fire` (`text` = `eng-NNNN RESPONDIDO`) | sessão **nova**, na hora | **token da rotina** guardado no formulário seguro da **Zapia** (ato do proprietário) | segundos a minutos | a Zapia (modelo) passa a poder **disparar** execuções (limite 100/h); precisa provar que ela alcança `api.anthropic.com` com `-X -H -d` |
| D | **Rotina com gatilho GitHub "issue aberta"**: a Zapia abre issue `RESP eng-NNNN` ao terminar | sessão **nova** | exige **permissão de issues** no token da Zapia e o Claude GitHub App no `entrada` (privado: **não informado**) | segundos a minutos | corpo da issue é texto não confiável; eventos acima do teto são **descartados** |
| E | Ação do GitHub rodando o Claude (`claude-code-action`) no `entrada` | job de CI | **chave da API** como segredo do repositório | segundos | **recusada**: a pesquisa registra falhas de injeção por issue; o `entrada` recebe conteúdo de Notebook e TEC |
| F | Workflow **sem LLM** no `entrada` (valida e grava o registro; opcionalmente faz `/fire`) | job determinístico | token de `/fire` como segredo | segundos | mexe no **fluxo** do `entrada` (você mandou não tocar); só com sua aprovação expressa |

**Recomendação (para você decidir):** **B como rede de segurança agora** (não depende da Zapia, 1 execução por hora, só lê) e **C como caminho rápido** depois de provar que a Zapia alcança o `/fire`. **A** só enquanto a sessão estiver aberta. **D** só se C falhar. **E** não. **F** só se o `/fire` pela Zapia não funcionar e você aprovar mexer no fluxo.

## 6. Fases e provas (cada uma, uma por vez, no mesmo lote só se coesas)
1. **F0 (nesta frente, sem credencial):** `leitura/<agente>.json`, `--proximo`, resumo do canal no START (broker); testes e mutações.
2. **F1 (ato seu):** criar na web a **rotina** (agendada `:07` de hora em hora, **sem** API/GitHub no início), com o **prompt fixo** versionado no repositório e o hash (S22-R3); nada de texto livre; **prova de 3 dias** com carimbo (S22-R6) antes de qualquer efeito.
3. **F2 (ato seu + prova):** gerar o token de API da rotina (mostrado **uma vez**), guardá-lo no formulário seguro da Zapia, atualizar o hook (v9) para o `POST /fire` e provar com um pedido sintético: `text` = só id e estado; **medir** atraso e perda; limite de 100/h.
4. **F3 (opcional):** gatilho GitHub de issue se F2 falhar, após verificar o Claude GitHub App no `entrada`.

## 7. Decisões que precisam de você
1. Autorizar **A** (escreva "Criar a tarefa S22" e um horário) ou deixar só B/C.
2. Criar a **rotina** (B/C): o horário, o ambiente (o repositório principal **e** o `entrada`) e onde a rotina pode **gravar** (ramo `claude/` ou `main` do `entrada`, o que a documentação não confirma).
3. Aceitar que a **Zapia guarde** o token de `/fire` (caminho C) ou preferir o de issue (D).
4. Se o `PROMPT` fixo da rotina pode escrever o registro de veredito no `entrada` (hoje feito por mim, nesta sessão).

## 7b. Respostas do proprietário (28/11/2026) e o que já está no código
- **Caminho escolhido: D** (a Zapia abre a issue `RESP eng-NNNN` ao terminar; uma **rotina com gatilho GitHub de issue aberta** acorda uma **sessão nova**). Passo 5 do hook (E49, item 15); a issue **não tem corpo** e o id vem só do título (`extrair_id_resp`, padrão exato).
- **A campainha `ENG eng-NNNN` também é issue aberta no `entrada`:** a rotina será acordada por ela também; o prompt manda **encerrar** quando o título não for `RESP eng-NNNN` (custa uma execução; a documentação não traz filtro de issue).
- **Escrita da rotina:** só `comandos/engenharia/registro/` e `comandos/engenharia/leitura/` no `entrada`. `caminhos_fora(caminhos, papel)` e `--auditar rotina` detectam violação (por detecção, **não** por prevenção: o token fino não limita por pasta). Hook da Zapia só grava `respostas/`; orquestrador `pedidos/`, `registro/`, `leitura/` e `PARAR`.
- **Consumo por agente:** `--proximo <agente>` e `--consumir <agente> <id>` (`orquestrador`, `tutor`, `coach`), idempotentes, só para resposta aceita e **respondida**.
- **Prompt fixo da rotina:** `config/rotina_despertar_prompt.txt`, SHA-256 `666d66c7a200be9ca2ac75c42d10a5509b398ab1b02c573f0397b3901a90dda7`, pinado em teste; trocar o texto exige PR.
- **S22 (execução única nesta sessão):** o proprietário marcou a opção, mas **não deu o horário** nem escreveu o pedido literal: **nada foi criado**.
- **Teste do passo 5 (28/11/2026):** a Zapia tentou abrir a issue `RESP` e recebeu **HTTP 403** (token sem permissão de issues; autorrelato B, corroborado pela ausência da issue). **O caminho D não funciona até o proprietário conceder `Issues: Read and write` ao token fino da Zapia no `entrada`**, o que amplia o poder desse token (E49, item 17).
- **Pendências do proprietário:** criar a rotina na web (gatilho GitHub, evento issue **aberta**, repositórios principal e `entrada`, prompt do arquivo acima); instalar o Claude GitHub App no `entrada`; dar à credencial da Zapia a permissão de **issues** e atualizar o hook (v9). **Não provado:** que a issue acorde a rotina; o app em repositório privado; a identidade que a rotina usa para gravar no `entrada`.

## 8. Limites
Nada aqui foi testado fora do repositório. Documentação de rotinas está em **prévia** e pode mudar; limites e escopos listados são os da página lida em 28/11/2026. A autenticidade do emissor no `entrada` **continua não provada** (E49 §3).
