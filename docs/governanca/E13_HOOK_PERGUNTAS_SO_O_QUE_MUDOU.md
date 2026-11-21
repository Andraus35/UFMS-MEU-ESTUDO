# E13 — Hook de perguntas de fim de rodada: perguntar só o que mudou

**Natureza:** registro do item `HOOKP` (pedido do proprietário de 21/11/2026, "Sim, propor em PR próprio", sobre repetir as mesmas perguntas a cada entrega). Altera `.claude/hooks/perguntas_boas_praticas.py` (**arquivo de contrato**, `CODEOWNERS`): **exige a aprovação expressa do texto e do merge, citando PR e head.** Aprovação a registrar: `Aprovo o texto e o merge do PR #159, head <sha completo>.`

## O que muda

| Antes | Depois |
|---|---|
| Toda rodada com entrega bloqueia o fim e manda abrir `AskUserQuestion` com as três perguntas, mesmo com o estado igual ao da pergunta anterior | Se o **último estado** que o próprio hook emitiu (`Estado lido agora: ...`, lido do **transcript**) é **igual ao atual** e **já houve `AskUserQuestion` depois dele**, o hook **não bloqueia de novo** |
| O motivo só traz o estado atual | Se o estado mudou, o motivo diz **"O que mudou desde a última pergunta: antes — X; agora — Y"** e pede para perguntar só sobre isso |

**O que NÃO muda:** a detecção de entrega (commit, push, operação de PR), a sequência (1) pendências, (2) roadmap, (3) fila, a regra de lote do `AGENTS.md`, a trava `stop_hook_active`, a falha aberta e o prazo. **O hook continua só lendo:** não grava arquivo nem estado (testes proíbem escrita); por isso a memória do "já perguntei" vem do transcript, não de arquivo.

## Prioridade do hook de passagem sobre as perguntas (correção de 21/11/2026)

**Defeito observado pelo proprietário:** depois do limite de 50% e do prompt selado, a sessão antiga continuava propondo continuidade, porque o hook de perguntas seguia bloqueando o fim de rodada e o hook de passagem ficava em silêncio depois do selo. **Verificado:** o hook de passagem funcionava (estado da sessão com `armed_at`, `sealed`, 63% e sem erro); faltava mandar **encerrar** e fazer as perguntas **cederem**.

| Situação | Hook de passagem (`claude_context_guard`) | Hook de perguntas |
|---|---|---|
| Abaixo do limite | nada | como antes (e só o que mudou) |
| Acima do limite, sem selo | ordena preparar e selar; bloqueia o fim (até 3 vezes) | **cede** (não compete) |
| Acima do limite, selado, **lote finalizado** (árvore limpa e tudo enviado) | a cada prompt e ferramenta avisa: **não proponha novo lote nem pergunte sobre a próxima rodada; diga ao usuário que a próxima sessão começa pelo prompt selado e encerre** | **cede**: não bloqueia |
| Acima do limite, selado, **lote pendente** (alteração não commitada ou commit não enviado) | avisa: **finalize o lote, não abra outro e depois peça nova sessão** | **continua valendo** (o lote ainda precisa ser finalizado) |

**Como o hook de perguntas sabe:** só **lê** `~/.claude/context-guard/state/<sessão>.json`, que o hook de passagem atualiza a cada medição acima do limite (`armed_at` e `lote_pendente`). **Na dúvida, não cede** (estado ausente, ilegível, de outra sessão, sem `lote_pendente` ou sem `armed_at`). A pendência do lote é medida pelo git (`status --porcelain` e `@{u}..HEAD`) a cada prompt e a cada ferramenta, então reflete o último commit e push da sessão.

**Limites:** o aviso é instrução ao modelo (não impede o usuário de seguir conversando); a medição do contexto tem atraso de um turno; **não observado ainda em Claude Code real além do disparo do aviso nesta sessão**. Sessões novas não herdam o estado (é por sessão).

## Garantias e limites

- **Na dúvida, pergunta:** sem estado legível (`next_task.py` indisponível), sem aviso anterior no transcript ou sem pergunta depois do último aviso, o hook bloqueia como antes. Pergunta feita **antes** do aviso não conta.
- **Depende do formato do transcript:** o aviso do hook precisa aparecer como texto de mensagem no `transcript_path` (nos testes, mensagem de usuário em texto ou em bloco `text`). **Não foi observado num Claude Code real** neste PR; se o formato real for outro, o efeito é **voltar ao comportamento antigo** (pergunta sempre), nunca perguntar menos.
- **O estado inclui o número do PR e o próximo item da fila:** cada lote novo muda o estado e, portanto, **gera pergunta**; o que some é a repetição dentro do mesmo estado (vários commits no mesmo PR, rodadas sem mudança de fila).
- **Não substitui** a regra de aprovação humana de merge, contrato e flags.

## Testes

`tests/test_hook_perguntas.py` (35) e `tests/test_claude_context_guard.py` (36): mesmo estado com pergunta depois não bloqueia; sem pergunta depois bloqueia; pergunta antes do aviso não conta (duas posições); estado mudado bloqueia e mostra o antes e o agora; aviso em bloco `text` é lido; sem histórico ou sem estado legível pergunta como antes; o hook continua sem escrever. **7 de 7 mutações mortas.**

## Como desfazer

Reverter este PR restaura o comportamento anterior.
