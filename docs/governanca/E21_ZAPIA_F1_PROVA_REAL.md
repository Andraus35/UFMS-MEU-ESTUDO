# E21: prova real do caminho de ida F1 com a Zapia (22/11/2026)

**Natureza:** registro da entrega oficial do item `ZAPIA-F1` (RM-09, S20 F1). Segue o roteiro `ROTEIRO_ZAPIA_IDA_F1_20261122.md` e o script `scripts/termux/prova_f1_zapia.sh`. Executado pelo proprietário; a sessão não tem acesso à Zapia. Nada altera `agents/`, `AGENTS.md`, `PRODUCT.md` nem o esquema de comandos.

## O que foi feito

O proprietário rodou `prova_f1_zapia.sh` no Termux, dentro do clone do repositório público, na branch do PR #184. O script gravou em `ufms-meu-estudo-entrada` (privado) um comando `enviar_mensagem` **sintético** (origem `coach`, texto "Teste F1 do Coach, sem dado pessoal.", aprovado pelo validador da caixa) e o recibo correspondente. O comando e o recibo entraram **à mão**, marcados `SINTETICO_MANUAL`. O proprietário colou o prompt do script na conversa da Zapia.

## Evidência (capturas do proprietário de 22/11/2026, 15:51; não versionadas, por mostrarem a tela dele)

- **Zapia (autorrelato):** "Entrega F1 concluída. O hash conferiu; o comando era `enviar_mensagem`, com origem declarada `coach`, e tinha menos de 24 horas. Mostrei a notificação exatamente como solicitado e gravei o recibo `ENTREGUE` em `comandos/entregas/f1-teste.json`, no commit `01841919175cba0aff5e7bade412776856a864bb`." Trabalhou por 27 s.
- **Conferência por código nosso (saída do terminal do proprietário):** `OK o recibo de volta confere com o hash do comando (mesmo hash, ENTREGUE, só campos fixos).` (`scripts/zapia_f1_prep.py conferir`).
- **Relato do proprietário:** `SIM`, viu a notificação "Coach (origem declarada): ..." no chat da Zapia (confirmado no terminal: `OK você confirmou ter visto a notificação`).
- **Confiança: B.** O que a Zapia grava é verificado por código (hash, status e campos fixos do recibo de volta); a notificação visível no chat é relato do proprietário com captura.

## O que fica provado

Uma vez, com dado sintético: a Zapia **leu** um comando e o recibo de `entrada` por HTTP com o token dela, **conferiu o hash canônico**, **mostrou a notificação** em nome do Coach no chat e **gravou o recibo de volta** sem o texto, com o mesmo hash. O caminho de ida F1 para o Coach funciona com o par colocado à mão.

## O que NÃO está provado (S20-R1, R12)

- **A promoção do comando pelo fluxo** (flag do fluxo e janela PJ): o par foi gravado à mão. O recibo da promoção real não foi exercitado.
- **Rotina agendada** e **notificação espontânea**: a Zapia respondeu **dentro da conversa**, disparada pelo proprietário. Nada foi agendado; o gatilho segue não provado (S15-R4).
- O **Tutor** usa o mesmo caminho (origem `tutor`), provado só no código, não com a Zapia real.
- Resultado de caderno (F2), rotina diária (F3), Notebook (F4) e F5.
- O texto final do script (`RESULTADO: PROVADO` e a limpeza dos três arquivos) **não** aparece nas capturas; vale só o que está listado em "Evidência".
- Autoria dos commits na conta do proprietário: não distingue a Zapia dele.

## Próximo

Promoção real pelo fluxo (flag e janela PJ, com P9 e aprovação expressa citando PR e head) e rotina de teste de execução única na Zapia (S20-R6), ambos atos do proprietário.
