# Capacidades da Zapia: o que está PROVADO e o que NÃO está (registro de leitura obrigatória)

**Leitura obrigatória por toda sessão** (estudo ou engenharia): o `scripts/bootstrap.py` imprime o resumo abaixo e o hash deste arquivo em toda execução, e o `memory/HANDOFF.md` aponta para cá. **Decisão do proprietário de 22/11/2026:** a prova abaixo fica gravada e deve ser lida por qualquer sessão, para que não volte a haver confusão sobre a capacidade da Zapia. Este arquivo só muda com **nova prova** (relato do proprietário com captura, mais verificação por código) ou nova refutação; opinião e autorrelato sem prova não o alteram.

<!-- RESUMO-START -->
- **PROVADO (22/11/2026, sonda de leitura):** a Zapia, pela **ferramenta HTTP dela com a credencial "zapia token"**, **leu um arquivo privado** do repositório `entrada` e **gravou um arquivo novo** com o valor aleatório lido; o conferidor por código deu `IGUAL` e `POSTERIOR`. **Ela lê e escreve no GitHub por HTTP com token. NÃO precisa de conector de GitHub.**
- **Formato de chamada que a ferramenta dela aceita:** `curl` restrito, **uma chamada simples por vez**, sem `;`, sem `&&`, sem pipe, **só as flags `-X`, `-H` e `-d`** (bloqueadas: `-sS`, `--fail-with-body`). Ela para no primeiro bloqueio e relata o erro literal (falha segura).
- **A credencial precisa estar preenchida no formulário seguro dela.** Estado `Requested, not filled in by the user` = vazia: ela para antes de tocar o GitHub. O token nunca vai ao chat.
- **A Zapia é um modelo: NÃO executa o Python do repositório**; o código do repositório é a especificação e o verificador do que ela devolve. Ela tem Python próprio e HTTP, sem Git.
- **PROVADO (22/11/2026, teste F1, confiança B):** com um par sintético colocado à mão em `entrada`, a Zapia **leu o comando e o recibo, conferiu o hash, mostrou a notificação "Coach (origem declarada): ..." no chat e gravou o recibo de volta** (conferido por código; notificação por relato e captura do proprietário). Registro: `docs/governanca/E21_ZAPIA_F1_PROVA_REAL.md`. Só dentro da conversa, disparada por ele.
- **NÃO PROVADO (não afirme):** a promoção do comando pelo fluxo (flag do fluxo e janela PJ); a **rotina agendada** da Zapia; a **notificação espontânea** (ela só respondeu dentro da conversa); o canal WhatsApp/Gmail. Autoria do commit = conta do proprietário (não distingue a Zapia dele).
- **Substitui (não repita):** "a Zapia não tem conector de GitHub, logo não lê o repositório" (S20 P4, D1(c) como "conector a pedir"), "não lê o repositório sozinha" (R14) e "token escopo desconhecido" no que diz respeito à LEITURA/ESCRITA em `entrada`. O mecanismo é HTTP com token e funciona.
<!-- RESUMO-END -->

## Evidência (22/11/2026)

- **Como foi feito:** o proprietário rodou no Termux `scripts/termux/sonda_zapia_do_zero.sh` (cria `sondas/nonce.json` com um valor aleatório de 128 bits em `entrada`), colou o prompt na conversa com a Zapia, e rodou `scripts/termux/sonda_conferir.sh`.
- **Resultado impresso pelo conferidor (captura do proprietário):** `OK  o valor lido é IGUAL ao nonce: a Zapia leu o arquivo privado.` e `OK  a resposta é POSTERIOR ao nonce.` A Zapia respondeu "Sonda concluída e conferida na releitura de `sondas/resposta.json`" com `nonce_lido` iniciando em `31d56f024f38…`, o mesmo valor gerado pelo script (`31d56f…`).
- **Por que não foi inventado:** o valor foi gerado no aparelho do proprietário na hora, está só no repositório privado e a resposta só é aceita se for idêntica e gravada depois.
- **Confiança:** B. Relato do proprietário com capturas (não versionadas, por conterem a tela dele) e conferência por código do repositório; a captura da Zapia é autorrelato dela confirmado pelo arquivo gravado.
- **Tentativas que falharam antes (também são prova do comportamento):** (1) `curl parse error: Blocked curl flag: -sS`; (2) `Requested, not filled in by the user` (credencial vazia); (3) `Command parse error: Empty segment at operator ';'`; (4) `Blocked curl flag: --fail-with-body`. Em todas ela parou sem alterar arquivo.

## Como reproduzir e o que vem depois

`scripts/termux/sonda_zapia_do_zero.sh` e `sonda_conferir.sh` (sonda de leitura); `scripts/termux/prova_f1_zapia.sh` com `scripts/zapia_f1_prep.py` e `scripts/zapia_entrega.py` (teste F1 de entrega, **rodado em 22/11/2026**, ver E21). Registro técnico: `docs/governanca/E22_SONDA_DE_LEITURA_ZAPIA_20261122.md`. A rotina da Zapia (D2) foi **autorizada** pelo proprietário em 22/11/2026 com a frase `AUTORIZO rotina automática agora`; **criá-la e provar seu disparo é ato dele na Zapia** e só passa a constar como PROVADO aqui depois de relato com captura e conferência por código (o S20-R6 pede teste sem efeito antes: o F1).

## Regra de atualização

Para mudar o resumo: nova prova (captura mais verificação) ou refutação datada. Nunca promover "não provado" a "provado" por inferência, por documentação pública da Zapia (ela não lista GitHub e isso não refuta o HTTP) nem por relato sem verificação.
