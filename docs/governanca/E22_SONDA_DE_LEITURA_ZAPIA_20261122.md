# E22: sonda de leitura da Zapia provada e teste F1 de entrega (22/11/2026)

**Natureza:** registro do lote `ZAPIA-F1b` (RM-09, S20 F1), continuação do E20. Nada altera `agents/`, `AGENTS.md`, `PRODUCT.md` nem o esquema de comandos. Evidência de relato do proprietário com capturas de tela (confiança B: o repositório confere o resultado por código; a autoria no GitHub é a conta do proprietário).

## O que está PROVADO (sonda de leitura, 22/11/2026)

A Zapia, pela **ferramenta HTTP dela com a credencial "zapia token"**, **leu `sondas/nonce.json`** do repositório privado `entrada` e **gravou `sondas/resposta.json`** com o mesmo valor aleatório (`nonce_lido` igual ao `nonce`, gerado na hora por `sonda_zapia_do_zero.sh`), em commit posterior ao nonce. O conferidor (`sonda_conferir.sh`) imprimiu as duas linhas `OK` (valor igual e resposta posterior). **Conclusão: a integração por HTTP com token funciona; NÃO precisa de conector de GitHub** (a documentação pública da Zapia também não lista GitHub; a D1(c) vale pelo mecanismo HTTP, não por conector).

## O que a sonda revelou (formato de chamada real)

- A ferramenta HTTP é um `curl` **restrito**: um comando simples por chamada, **sem `;`**, e com **lista fechada de flags**. Foram bloqueados `-sS` e `--fail-with-body` ("Blocked curl flag"); funcionaram `-X`, `-H` e `-d`. O interpretador recusa segmento vazio em `;`.
- A credencial precisa estar **preenchida no formulário seguro** da Zapia; antes estava `Requested, not filled in by the user` e ela parou sem tocar o GitHub. O proprietário regenerou o token no GitHub e o preencheu.
- A Zapia parou em cada bloqueio, sem outro caminho, sem outra credencial e sem alterar arquivo (falha segura, S20-R9).
- Bug de script achado e corrigido: o `gh` imprime o corpo do erro na saída normal e sai com código 1 em 404; o script tratava isso como "arquivo já existe". Agora `gget` só aceita a saída com código 0 (teste de regressão).

## O que o lote entrega

- `scripts/termux/sonda_zapia_do_zero.sh` (instala o que faltar, loga, roda a sonda) e `scripts/termux/sonda_conferir.sh` (só leitura até o `LIMPAR`); o prompt já usa o formato de chamada aceito.
- `scripts/zapia_f1_prep.py` e `scripts/termux/prova_f1_zapia.sh`: **teste F1** (a Zapia lê um comando validado SINTÉTICO e o recibo em `entrada`, confere o hash canônico, entrega a mensagem na conversa e grava o recibo de volta, que o script confere). O par entra **à mão** (recibo `SINTETICO_MANUAL`): o fluxo real só promove com a flag ligada.
- `tests/test_termux_sondas_zapia.py` (17 testes, `gh` falso com o comportamento real de erro, Zapia simulada).

## O que NÃO está provado

- O teste F1 **ainda não foi rodado** no GitHub real (os scripts foram testados só contra o `gh` falso).
- Promoção do comando pelo fluxo (flag e janela PJ), **rotina agendada** (exige a frase `AUTORIZO`) e **notificação espontânea**: a Zapia só respondeu dentro da conversa; o envio por rotina é a F3.
- A autoria do commit não distingue a Zapia do proprietário; a prova está no valor aleatório.
- O item `ZAPIA-F1` da fila segue pendente: só conta como feito quando existir `E21_ZAPIA_F1_PROVA_REAL.md`, escrito depois do F1 real.
