# E13 — Hook de perguntas de fim de rodada: perguntar só o que mudou

**Natureza:** registro do item `HOOKP` (pedido do proprietário de 21/11/2026, "Sim, propor em PR próprio", sobre repetir as mesmas perguntas a cada entrega). Altera `.claude/hooks/perguntas_boas_praticas.py` (**arquivo de contrato**, `CODEOWNERS`): **exige a aprovação expressa do texto e do merge, citando PR e head.** Aprovação a registrar: `Aprovo o texto e o merge do PR #159, head <sha completo>.`

## O que muda

| Antes | Depois |
|---|---|
| Toda rodada com entrega bloqueia o fim e manda abrir `AskUserQuestion` com as três perguntas, mesmo com o estado igual ao da pergunta anterior | Se o **último estado** que o próprio hook emitiu (`Estado lido agora: ...`, lido do **transcript**) é **igual ao atual** e **já houve `AskUserQuestion` depois dele**, o hook **não bloqueia de novo** |
| O motivo só traz o estado atual | Se o estado mudou, o motivo diz **"O que mudou desde a última pergunta: antes — X; agora — Y"** e pede para perguntar só sobre isso |

**O que NÃO muda:** a detecção de entrega (commit, push, operação de PR), a sequência (1) pendências, (2) roadmap, (3) fila, a regra de lote do `AGENTS.md`, a trava `stop_hook_active`, a falha aberta e o prazo. **O hook continua só lendo:** não grava arquivo nem estado (testes proíbem escrita); por isso a memória do "já perguntei" vem do transcript, não de arquivo.

## Prioridade do hook de passagem: verificar o fim do lote, persistir sem pedir permissão (correções de 21/11/2026)

**Defeitos apontados pelo proprietário:** (1) depois dos 50% e do selo, a sessão seguia propondo continuidade por perguntas (o hook de passagem ficava em silêncio e o de perguntas continuava bloqueando); (2) o hook devia **obrigar a verificar o fim do lote antes de salvar, para não cortar ao meio**, e **atualizar e persistir o repositório sem pedir permissão**. **Verificado:** o hook de passagem já disparava; faltavam a ordem de verificação, a persistência autônoma e a cessão das perguntas.

**Ordem imposta aos 50% (nesta sequência, sem perguntar ao usuário e sem `AskUserQuestion`):**
1. **Verificar o fim do lote:** o script mede o git (branch, se é protegida, alterações não commitadas, commits não enviados) e injeta os fatos; se há micro tarefa em andamento, **não iniciar outra**, concluir só até o **ponto de corte consistente** (testes e gates passando) ou, se não der, deixar um commit `WIP:` na branch de trabalho com o que falta descrito.
2. **Persistir:** atualizar memória e estado pelas regras do próprio projeto, rodar os gates e **fazer commit e push na branch de trabalho atual, sem pedir permissão**. **Limites que não dependem de permissão:** nunca force push, nunca merge, nunca commit na branch principal ou destacada, nunca arquivo de contrato sem aprovação já dada; se um limite impedir, registrar a pendência no prompt.
3. **Selar** o prompt de start **só depois de persistir** (os fatos do git saem certos).

| Situação | Hook de passagem (`claude_context_guard`) | Hook de perguntas |
|---|---|---|
| Abaixo do limite | nada | como antes (e só o que mudou) |
| Acima do limite, sem selo | ordena as três etapas; **`Stop` bloqueia** até selar (máx. 3 vezes) | **cede** |
| Acima do limite, selado, **lote não persistido** (alteração não commitada ou commit não enviado, em branch de trabalho) | a cada prompt e ferramenta manda **concluir o corte e persistir sem pedir permissão**; **`Stop` bloqueia** até persistir (máx. 3 vezes) | **cede** |
| Acima do limite, selado, lote persistido | avisa: **não proponha novo lote nem pergunte; diga que a próxima sessão começa pelo prompt selado e encerre**; `Stop` libera | **cede** |
| Branch principal ou destacada | não bloqueia o `Stop` por pendência (não há como persistir lá) e a instrução diz para **não** comitar | **cede** |

**Interpretação a confirmar:** a regra anterior ("as perguntas só prevalecem se o lote ainda precisar ser finalizado") foi substituída pela de agora: com o lote pendente quem age é o hook de passagem, **que manda finalizar e persistir sem perguntar**; por isso o hook de perguntas **cede sempre** que o limite foi ultrapassado. Se a intenção era manter as perguntas com lote pendente, é uma linha para voltar.

**Como o hook de perguntas sabe:** só **lê** `~/.claude/context-guard/state/<sessão>.json` (`armed_at`). **Na dúvida, não cede** (estado ausente, ilegível, de outra sessão ou sem `armed_at`).

**Limites:** o aviso é instrução ao modelo (não impede o usuário de seguir conversando, nem prova que o commit foi bem feito: o `Stop` só confere que o git ficou limpo e enviado); a medição do contexto tem atraso de um turno; **o commit automático segue as regras de contrato: arquivos de contrato com aprovação pendente (como os deste PR) não devem ser comitados à revelia** — o hook manda "nunca arquivo de contrato sem aprovação já dada", e quem decide o que é contrato é o projeto. Observado ao vivo nesta sessão: o aviso de lote pendente listou os arquivos e mudou para "lote finalizado" ao push.

## Garantias e limites

- **Na dúvida, pergunta:** sem estado legível (`next_task.py` indisponível), sem aviso anterior no transcript ou sem pergunta depois do último aviso, o hook bloqueia como antes. Pergunta feita **antes** do aviso não conta.
- **Depende do formato do transcript:** o aviso do hook precisa aparecer como texto de mensagem no `transcript_path` (nos testes, mensagem de usuário em texto ou em bloco `text`). **Não foi observado num Claude Code real** neste PR; se o formato real for outro, o efeito é **voltar ao comportamento antigo** (pergunta sempre), nunca perguntar menos.
- **O estado inclui o número do PR e o próximo item da fila:** cada lote novo muda o estado e, portanto, **gera pergunta**; o que some é a repetição dentro do mesmo estado (vários commits no mesmo PR, rodadas sem mudança de fila).
- **Não substitui** a regra de aprovação humana de merge, contrato e flags.

## Testes

`tests/test_hook_perguntas.py` e `tests/test_claude_context_guard.py` (46): mesmo estado com pergunta depois não bloqueia; sem pergunta depois bloqueia; pergunta antes do aviso não conta (duas posições); estado mudado bloqueia e mostra o antes e o agora; aviso em bloco `text` é lido; sem histórico ou sem estado legível pergunta como antes; o hook continua sem escrever. **7 de 7 mutações mortas.**

## Como desfazer

Reverter este PR restaura o comportamento anterior.
