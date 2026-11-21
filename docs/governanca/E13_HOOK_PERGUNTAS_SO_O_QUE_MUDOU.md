# E13 — Hook de perguntas de fim de rodada: perguntar só o que mudou

**Natureza:** registro do item `HOOKP` (pedido do proprietário de 21/11/2026, "Sim, propor em PR próprio", sobre repetir as mesmas perguntas a cada entrega). Altera `.claude/hooks/perguntas_boas_praticas.py` (**arquivo de contrato**, `CODEOWNERS`): **exige a aprovação expressa do texto e do merge, citando PR e head.** Aprovação a registrar: `Aprovo o texto e o merge do PR #159, head <sha completo>.`

## O que muda

| Antes | Depois |
|---|---|
| Toda rodada com entrega bloqueia o fim e manda abrir `AskUserQuestion` com as três perguntas, mesmo com o estado igual ao da pergunta anterior | Se o **último estado** que o próprio hook emitiu (`Estado lido agora: ...`, lido do **transcript**) é **igual ao atual** e **já houve `AskUserQuestion` depois dele**, o hook **não bloqueia de novo** |
| O motivo só traz o estado atual | Se o estado mudou, o motivo diz **"O que mudou desde a última pergunta: antes — X; agora — Y"** e pede para perguntar só sobre isso |

**O que NÃO muda:** a detecção de entrega (commit, push, operação de PR), a sequência (1) pendências, (2) roadmap, (3) fila, a regra de lote do `AGENTS.md`, a trava `stop_hook_active`, a falha aberta e o prazo. **O hook continua só lendo:** não grava arquivo nem estado (testes proíbem escrita); por isso a memória do "já perguntei" vem do transcript, não de arquivo.

## Garantias e limites

- **Na dúvida, pergunta:** sem estado legível (`next_task.py` indisponível), sem aviso anterior no transcript ou sem pergunta depois do último aviso, o hook bloqueia como antes. Pergunta feita **antes** do aviso não conta.
- **Depende do formato do transcript:** o aviso do hook precisa aparecer como texto de mensagem no `transcript_path` (nos testes, mensagem de usuário em texto ou em bloco `text`). **Não foi observado num Claude Code real** neste PR; se o formato real for outro, o efeito é **voltar ao comportamento antigo** (pergunta sempre), nunca perguntar menos.
- **O estado inclui o número do PR e o próximo item da fila:** cada lote novo muda o estado e, portanto, **gera pergunta**; o que some é a repetição dentro do mesmo estado (vários commits no mesmo PR, rodadas sem mudança de fila).
- **Não substitui** a regra de aprovação humana de merge, contrato e flags.

## Testes

`tests/test_hook_perguntas.py` (28): mesmo estado com pergunta depois não bloqueia; sem pergunta depois bloqueia; pergunta antes do aviso não conta (duas posições); estado mudado bloqueia e mostra o antes e o agora; aviso em bloco `text` é lido; sem histórico ou sem estado legível pergunta como antes; o hook continua sem escrever. **7 de 7 mutações mortas.**

## Como desfazer

Reverter este PR restaura o comportamento anterior.
