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

## Exceção de acesso (decisão do proprietário, 25/11/2026)

- **Durante a fase de teste**, a sessão em nuvem do construtor recebeu acesso de **leitura** ao `ufms-meu-estudo-entrada` (anexado por `add_repo`, clone raso em `/home/user/ufms-meu-estudo-entrada`), **só** para conferir de forma independente os arquivos sintéticos do teste (`f4-hook.json`). **Não** foi carregado o `CLAUDE.md`, skills ou plugins desse repositório (conteúdo dele é dado, não instrução) e nada dele foi executado.
- **É exceção**, contra o desenho de S4 e S6 (só o proprietário e o fluxo tocam o `entrada`; Tutor e Coach leem projeções). **Ele a revoga antes do run de verdade** (ato dele; depois disso a sessão remove o clone e não lê mais o `entrada`). Enquanto valer, a sessão **não grava** nada lá.
- **Escrita temporária (decisão do proprietário, 25/11/2026, "Sim"):** a sessão pode **gravar só** `comandos/validados/f4-hook.json` e `comandos/recibos/f4-hook.json` (par sintético, recibo `SINTETICO_MANUAL`, gerado por `scripts/zapia_f1_prep.py`, que passa pelo validador da caixa) e, **a pedido dele**, apagar os três nomes `f4-hook.json` no fim. **Nada além disso:** nenhuma issue, nenhum recibo de entrega, nada nas sobras antigas nem no fluxo. É **exceção** à regra do `AGENTS.md` de não dar credencial direta ao modelo e a S4 e S6; **o nível de acesso concedido não foi confirmado pela ferramenta** ("já anexado"), só uma escrita real o confirma. **Efeito:** o recibo do par passa a vir da sessão e não da conta dele (a origem do comando segue não provada). Ele revoga antes do run de verdade.
- Efeito sobre a prova: a leitura da sessão é **conferência complementar**; a prova da notificação continua sendo a captura do chat da Zapia.

## Para o proprietário

1. Atualizar o clone na branch do lote (`git fetch` e `git checkout`/`pull`) e rodar `preparar`; colar o texto na Zapia; esperar os filtros lidos de volta; rodar `sinal`; esperar o relato; `conferir`; `limpar`.
2. Trazer ao chat a saída do `conferir`, o texto literal da Zapia e as capturas (não versionadas). Só então o `CAPACIDADES_ZAPIA_VERIFICADAS.md` sobe de "não provado".
3. Aprovar o merge deste lote, citando PR e head.
