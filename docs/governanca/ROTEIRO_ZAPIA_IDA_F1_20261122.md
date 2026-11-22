# Roteiro da prova real do caminho de ida (F1): uma notificação sintética do Coach na Zapia (22/11/2026)

**Quem executa:** o proprietário (a sessão não executa nenhum passo; não tem acesso à Zapia). **Objetivo:** provar, uma vez, que um comando validado pelo fluxo vira **notificação na Zapia em nome do Coach**, com recibo de volta de mesmo hash. **Sem dado pessoal**: texto sintético. Resultado: autorrelato dela **mais** verificação por código nosso (confiança sobe de C para B só onde o recibo confere).

## Passo 1: o conector (decisão D1, a pedir)

Pergunte à Zapia (ou ao suporte), sem enviar token nem dado: "Você consegue ler arquivos de um repositório **privado** do GitHub por conector, só leitura da pasta `comandos/`? Se não, qual é o canal que você consegue ler sozinha?" Registre a resposta literal. **Se ela não tiver conector, pare aqui**: a decisão D1 volta para você (S20: WhatsApp ou Gmail como alternativas); nada abaixo vale.

## Passo 2: o comando sintético (pelo fluxo, sem manual além do disparo)

No repositório `entrada`, o Coach (ou você, como teste) grava um comando `enviar_mensagem` sintético em `comandos/`, com o texto "Teste F1 do Coach, sem dado pessoal." e a chave `rotina-AAAA-MM-DD-briefing-dia` do dia. O fluxo valida, promove para `comandos/validados/` e grava o recibo em `comandos/recibos/` (já provado na C5, com a flag do fluxo ligada só na janela PJ).

## Passo 3: a rotina da Zapia (exige a sua frase `AUTORIZO`)

Diga `AUTORIZO` à Zapia e peça uma rotina **de teste, de execução única**, com esta instrução: "Leia `comandos/validados/` e `comandos/recibos/` do repositório. Para cada comando `enviar_mensagem` com recibo de **mesmo hash** (hash canônico do JSON), emitido há menos de 24 h, de origem `tutor` ou `coach`, e que você ainda não entregou: me envie a notificação 'Coach (origem declarada): <texto>' e grave em `comandos/entregas/<mesmo nome>` um JSON com `entrada_id`, `hash_corpo`, `status` = `ENTREGUE`, `entregue_em` (UTC) e `origem_declarada`, **sem o texto**. No máximo 2 por dia. Se algo divergir, não envie nada, não tente de novo e me avise." Não passe token no chat.

## Passo 4: a conferência (código nosso)

Num checkout do repositório `entrada`: `python scripts/zapia_entrega.py --raiz <pasta>`. **Passa** só se houver pelo menos um recibo de volta e todos conferirem com o hash da promoção. Anexe: a notificação recebida (captura sem dado pessoal), o resultado do comando e o recibo da promoção.

## O que fecha e o que não fecha

- **Fecha:** F1 para o Coach, **uma** mensagem, **ida** (e o recibo de volta). O Tutor usa o mesmo caminho (origem `tutor`), provado no código e **não** com a Zapia real.
- **Não fecha:** rotina diária (F3), resultado de caderno (F2), Notebook (F4), nem a pontualidade do gatilho (S15-R4: carimbo por 3 dias). Qualquer falha de conector, disparo ou notificação **para o processo**: sem envio substituto e sem laço (S20-R9).
