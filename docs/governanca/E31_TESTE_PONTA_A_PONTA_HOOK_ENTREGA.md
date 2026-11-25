# E31: teste ponta a ponta, hook de Gmail que entrega um comando validado (lote ZAPIA-E2E, 25/11/2026)

**Natureza:** preparo do **teste real** pedido pelo proprietário. O repositório entrega o **roteiro, a instrução do hook e a conferência por código**; **a prova depende de ato dele** (Termux, `entrada` real, Zapia real). **Nada aqui está provado até o roteiro rodar.** Não altera contrato (`agents/`, `AGENTS.md`, `PRODUCT.md`, esquema): o modelo de instrução está em `config/rotina_instrucoes.json` (hash conferido). O merge segue o pedido expresso dele.

## O que o teste responde

Junta peças já provadas **separadas**: a campainha por Gmail (E30, o hook acorda 27 s depois da issue), a entrega pelo caminho do F1 (E21/E23: ler comando e recibo, conferir hash, notificar, gravar recibo) e a leitura real do `entrada`. **Pergunta:** o hook, ao acordar, **consegue** usar a ferramenta HTTP e a credencial para ler o repositório e gravar o recibo? (A rotina agendada do F3 não conseguiu criar rotina; o hook pode ter outras ferramentas, e isso é o que se mede.)

## Como funciona

1. `bash scripts/termux/prova_f4_hook_entrega.sh preparar`: confere pré-condições, grava um **par sintético** (`f4-hook.json`, comando `enviar_mensagem` do Coach e recibo `SINTETICO_MANUAL`) e imprime o texto para a Zapia: criar **um** hook de Gmail com **só** `senders` = `notifications@github.com` e `subject_contains` = `[Andraus35/ufms-meu-estudo-entrada] SINAL`, com a tarefa do modelo `HOOK_ENTREGA` (hash em `config/rotina_instrucoes.json`): usar só o **assunto** do e-mail (nunca o corpo), conferir o prefixo, ler recibo e comando por URLs literais, conferir o hash, notificar **uma vez**, gravar `comandos/entregas/f4-hook.json` e desativar o hook.
2. A Zapia cria o hook e mostra **conta, filtros e texto salvo lidos de volta**.
3. `bash scripts/termux/prova_f4_hook_entrega.sh sinal`: com a sua confirmação, abre **uma** issue `SINAL teste E2E` (o GitHub avisa por e-mail), anota a hora UTC da criação e **só fecha a issue depois do seu ENTER** (o aviso de fechamento é outro e-mail).
4. `bash scripts/termux/prova_f4_hook_entrega.sh conferir`: baixa o estado e roda `zapia_disparo.py` (mesmo hash do recibo, só os campos fixos, `entregue_em` UTC **não anterior à criação da issue** e **até 900 s depois**, **uma única** entrega) e pede dois relatos seus (notificação vista; hook desativado). `limpar` apaga os três arquivos.

## Passa e refuta

- **Passa (autorrelato B, captura sua):** o hook acorda uma vez, o chat mostra `Coach (origem declarada): ...`, o recibo de entrega confere por código e o hook é desativado.
- **Refuta (também é resultado):** o hook não acorda; acorda e diz que **não tem a ferramenta HTTP ou a credencial**; entrega sem conferir o hash; abre o corpo do e-mail; entrega duas vezes; ou não se desativa. **Não repetir em laço** (S20-R9): traga o texto literal dela.

## O que NÃO prova (declarado)

- **Autorrelato:** a notificação e o carimbo são da Zapia; só a captura dele e o carimbo coerente com a issue (conferido por código) sustentam.
- **O emissor é ele** (issue aberta à mão com `gh`), **não o fluxo**; o fluxo como emissor e a emenda do D-28 (leitura de e-mail pelo hook) ficam para PR próprio com aprovação expressa do texto.
- **Par colocado à mão** (`SINTETICO_MANUAL`): não prova a promoção pelo fluxo (flag e janela PJ).
- Uma execução: **não** prova hook recorrente, vários dias nem pontualidade em relação a `agendado_utc`.
- O roteiro foi testado só com `gh` falso (`tests/test_e31_hook_entrega.py`); **não rodou com o `gh` real**.
- O comando sintético vale **24 h**; rode `sinal` no mesmo dia do `preparar`.
- A instrução vem de **modelo versionado**; o e-mail **nunca** é instrução, e a Zapia não deve obedecer texto dele.

## Resultado da 1ª execução (25/11/2026): **PARCIAL**, com defeito do nosso modelo

- **Observado (autorrelato da Zapia, conferido onde dá por código):** o hook `8b43759f` acordou às **10:24:23Z**, **29 s** depois da issue #6 (criada às 10:23:54Z por esta sessão, a pedido dele); listou os recibos, achou o de `f4-hook.json` pelo hash, leu o comando e **notificou** no chat (`Coach (origem declarada): ...`; a notificação em si depende da captura dele) e o hook **encerrou**. Os **tamanhos** que ela citou (239, 316 e 241 bytes) **batem** com os arquivos reais do `entrada`: ela **leu o repositório de dentro do hook**.
- **Não gravou o recibo de entrega:** o modelo exigia `rotina_id_relatado` e ela **não consegue ler o ID do hook** de dentro da execução; ela preferiu não gravar. **Defeito nosso**: o verificador já aceitava o recibo sem esse campo. Não há `comandos/entregas/f4-hook.json`; esta sessão confirmou por `git pull`.
- **Discrepância de relato:** ela escreveu o URL do comando com o nome do repositório **truncado** (`ufms-meu-estudo`, sem `-entrada`, que aponta o repositório público). Os tamanhos indicam chamada certa e **relato errado do URL**; não dá para provar. O modelo agora manda **copiar cada URL letra por letra**.
- **Correção (esta revisão do modelo `HOOK_ENTREGA`, hash novo):** `rotina_id_relatado` vira **opcional** ("omita a chave e grave mesmo assim") e a ordem de copiar o URL literalmente. **Exige novo hook** com o texto novo; o antigo já encerrou.
- **Conclusão parcial (confiança B):** o hook consegue **ler o `entrada` e notificar**; **gravar não foi provado** (o PUT não foi tentado). A 2ª execução (mesmo par, que vale 24 h, e uma nova issue) mede a gravação e o recibo de entrega.

## Resultado da 2ª execução (25/11/2026): **o recibo de entrega foi gravado e confere por código**

- **Fatos (conferidos por esta sessão por leitura do `entrada`):** issue #7 `SINAL teste E2E 2` criada às **10:32:58Z** (por esta sessão, a pedido dele); o hook `2bef6d04` (texto salvo **idêntico** ao modelo `HOOK_ENTREGA` corrigido, 3121 caracteres, conferido por código; conta, só `senders` e `subject_contains`) gravou `comandos/entregas/f4-hook.json` com `entregue_em` **10:33:46Z** (**48 s** depois da issue; commit `ed7b09e` às 10:33:53Z, 7 s depois do carimbo). **`zapia_disparo.py`: `ok: true`**; `conferir_entrega`: `None`. Campos exatamente os fixos mais `rotina_id_relatado`; **sem o texto da mensagem**; o hash é o do comando promovido (par sintético).
- **Conclusão (confiança B):** **um hook de Gmail da Zapia, acordado pelo e-mail de uma issue, leu o `entrada`, conferiu o hash e gravou o recibo de entrega**, no tempo de menos de 1 minuto; o ciclo campainha, leitura, conferência e gravação **funciona sem colar prompt**. O erro da 1ª execução era do modelo (corrigido).
- **Relato dela da 2ª execução (autorrelato conferido nos tamanhos):** os **quatro URLs** vieram **corretos**, copiados do texto (o erro de relato da 1ª execução não se repetiu); os tamanhos citados (239, 241, 316 e **233 bytes** do recibo gravado) **batem** com os arquivos reais; a notificação relatada foi `Coach (origem declarada): Teste F1 do Coach: notificação sintética, sem dado pessoal.`; ela diz que o hook **encerrou por ser de execução única** e que **não conseguiu desativá-lo nem apagá-lo**: **o hook pode continuar na lista dela**, e apagá-lo é ato dele.
- **Ainda dele (só ele vê):** a **notificação** `Coach (origem declarada): ...` no chat da Zapia (captura) e a **desativação** do hook (autorrelato dela). Sem esses dois relatos, "notificou" e "encerrou" ficam como autorrelato dela.
- **Ressalvas observadas:** (1) o `rotina_id_relatado` que ela gravou (`1a21244610ce2fde`) **não é** o ID que o app mostra para o hook (`2bef6d04`); é outro identificador dela (execução ou evento): **autorrelato não verificado**, e o campo é opcional. (2) O commit do recibo aparece **sob a conta dele** (a credencial da Zapia é dele): **não distingue** quem gravou; só o carimbo e o hash sustentam. (3) A **mensagem** que ela relata ao chat é dela; nada no repositório a prova.
- **Continua não provado:** o **fluxo como emissor** (aqui a issue foi aberta por esta sessão, antes por ele); par colocado à mão (`SINTETICO_MANUAL`, sem promoção pelo fluxo); hook **recorrente**; vários dias; texto vindo de promoção real; Tutor e Coach emitindo de verdade.

## Limpeza executada (25/11/2026, a pedido dele: "Pode executar as pendências")

- **No `entrada` (commit `8ea64e5`):** apagados os **seis** arquivos de teste, `f4-hook.json` (E31) e `f1-rotina.json` (E23), em `comandos/validados/`, `comandos/recibos/` e `comandos/entregas/`. **Mantidos de propósito:** `.github/workflows/promover.yml` (o fluxo instalado) e `recibos/c5-sintetica-20261118T192903.json` (recibo **escrito pelo fluxo** na prova C5; é registro do fluxo, não arquivo de teste da sessão; apagar é decisão dele). O histórico do Git guarda tudo o que foi apagado.
- **Clone local da sessão NÃO foi removido:** a remoção da pasta `/home/user/ufms-meu-estudo-entrada` foi **bloqueada pela verificação de segurança** do ambiente (só uma pessoa pode aprovar). A sessão **não vai mais ler nem gravar** nele; **a pasta continua no disco** até ele aprová-la ou o ambiente ser descartado.
- **Conferência remota do `entrada` (25/11/2026, pelas ferramentas do GitHub, sem Termux):** na raiz só `.github` e `recibos`; `comandos/` ausente; **a issue #1 `SINAL teste F4` (24/11, 10:02Z) continua ABERTA** (as #4 a #7 estão fechadas); nenhuma execução nova do fluxo desde 18/11 (os pushes de hoje não o dispararam). **Ordem obrigatória: apagar os hooks na Zapia antes de fechar ou comentar a #1**, porque o e-mail dela (`Re: [Andraus35/ufms-meu-estudo-entrada] SINAL teste F4 (Issue #1)`) **casa com o filtro** e poderia disparar um hook ainda vivo.
- **Inventário da Zapia (25/11/2026, autorrelato [OBSERVADO] dela, incluindo itens desabilitados):** **um único hook**, `2bef6d04`, **desabilitado** (os IDs `8b43759f` e `5b91c690` não aparecem mais); três rotinas de teste (`4820d046`, `2bf694ce`, `4ba5054e`) **desabilitadas e já executadas**; três execuções do **Radar** (`b7bee469`, `c54f4433`, `695ae5f8`) **pausadas por ele**, fora destes testes. **Nenhuma automação de teste ativa.** Ela não consegue consultar o Google Tasks (conector não conectado).
- **Issue #1 fechada** pela sessão depois do inventário (nenhum hook vivo); **nenhuma issue aberta** no `entrada`.
- **Continua com ele (a sessão não alcança):** a captura da notificação no chat da Zapia; **apagar, se quiser, o hook `2bef6d04` (desabilitado) da lista da Zapia**; e **revogar o anexo do `entrada` à sessão** (leitura e escrita), antes do run de verdade.

## Exceção de acesso (decisão do proprietário, 25/11/2026)

- **Durante a fase de teste**, a sessão em nuvem do construtor recebeu acesso de **leitura** ao `ufms-meu-estudo-entrada` (anexado por `add_repo`, clone raso em `/home/user/ufms-meu-estudo-entrada`), **só** para conferir de forma independente os arquivos sintéticos do teste (`f4-hook.json`). **Não** foi carregado o `CLAUDE.md`, skills ou plugins desse repositório (conteúdo dele é dado, não instrução) e nada dele foi executado.
- **É exceção**, contra o desenho de S4 e S6 (só o proprietário e o fluxo tocam o `entrada`; Tutor e Coach leem projeções). **Ele a revoga antes do run de verdade** (ato dele; depois disso a sessão remove o clone e não lê mais o `entrada`). Enquanto valer, a sessão **não grava** nada lá.
- **Escrita temporária (decisão do proprietário, 25/11/2026, "Sim"):** a sessão pode **gravar só** `comandos/validados/f4-hook.json` e `comandos/recibos/f4-hook.json` (par sintético, recibo `SINTETICO_MANUAL`, gerado por `scripts/zapia_f1_prep.py`, que passa pelo validador da caixa) e, **a pedido dele**, apagar os três nomes `f4-hook.json` no fim. **Atualização (25/11/2026, a pedido dele): a sessão também abre o sinal (a issue `SINAL teste E2E`) e a fecha depois do relato.** **Nada além disso:** nenhuma outra issue, nenhum recibo de entrega, nada nas sobras antigas nem no fluxo. É **exceção** à regra do `AGENTS.md` de não dar credencial direta ao modelo e a S4 e S6; **o nível de acesso concedido não foi confirmado pela ferramenta** ("já anexado"), só uma escrita real o confirma. **Efeito:** o recibo do par passa a vir da sessão e não da conta dele (a origem do comando segue não provada). Ele revoga antes do run de verdade.
- Efeito sobre a prova: a leitura da sessão é **conferência complementar**; a prova da notificação continua sendo a captura do chat da Zapia.

## Para o proprietário

1. Atualizar o clone na branch do lote (`git fetch` e `git checkout`/`pull`) e rodar `preparar`; colar o texto na Zapia; esperar os filtros lidos de volta; rodar `sinal`; esperar o relato; `conferir`; `limpar`.
2. Trazer ao chat a saída do `conferir`, o texto literal da Zapia e as capturas (não versionadas). Só então o `CAPACIDADES_ZAPIA_VERIFICADAS.md` sobe de "não provado".
3. Aprovar o merge deste lote, citando PR e head.
