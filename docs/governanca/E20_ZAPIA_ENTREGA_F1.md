# E20: ligação do Tutor e do Coach à Zapia, F0/F1 offline (22/11/2026)

**Natureza:** registro do lote `ZAPIA-F1` (RM-09, S20 F0/F1). Pedido do proprietário (22/11/2026): ligar Tutor e Coach à Zapia de forma **automatizada**, receber **notificação na Zapia em nome dos agentes**, e **não passar à tarefa seguinte (COR-E) até estar garantido, testado e validado**. Nada altera `agents/`, `AGENTS.md`, `PRODUCT.md` nem o esquema de comandos.

## Decisões do proprietário de 22/11/2026 (registradas aqui; viram `PRODUCT.md` só por PR próprio, S15-R13)

| # | Decisão |
|---|---|
| D1 | A Zapia lê a fila por um **conector de GitHub a pedir** (existência **não confirmada**; hoje ela relata hook só de Gmail, WhatsApp e Drive). |
| D2 | **Testar pela rotina da Zapia** como quem acorda o fluxo. |
| D3 | A chave e a promoção ficam no **fluxo do repositório privado** (C3/C5), fora do alcance do modelo. |

Registro da prova real (entrega oficial do item, ainda inexistente): `docs/governanca/E21_ZAPIA_F1_PROVA_REAL.md`, escrito só depois do roteiro.

## O que este lote entrega (código do nosso lado, offline)

- `scripts/zapia_entrega.py`: a regra do lado da Zapia como código testável. Lê só `comandos/validados/` com recibo de **mesmo hash** (`command_box.selecionar_executaveis`), aceita só `enviar_mensagem` do Tutor ou do Coach, remonta a notificação "**Tutor|Coach (origem declarada): texto**", reconfere o texto (segredo, URL, instrução, texto de questão, frases proibidas G-MOT), recusa comando com mais de 24 h, aplica teto de 2 por dia, nunca entrega o mesmo hash duas vezes, não reenvia em laço nem manda mensagem substituta, e devolve um **recibo de volta** (`comandos/entregas/<nome>`, hash e status, **sem o texto**).
- `conferir_entrega` e a CLI `python scripts/zapia_entrega.py --raiz <checkout de entrada>`: conferem os recibos de volta contra os recibos da promoção (falha se não houver nenhum).
- `tests/test_zapia_entrega.py` (15 testes): ponta a ponta com GitHub falso em memória e Zapia simulada (leitor e `enviar` injetados), Coach e Tutor, segunda rodada sem reenvio, sem recibo, hash alterado, falha no envio, expirado, teto, operação não suportada, texto ruim com hash correto, recibo de volta adulterado. **9 de 9 mutações do módulo mortas.**
- Roteiro da prova real: `docs/governanca/ROTEIRO_ZAPIA_IDA_F1_20261122.md`.

## O que NÃO está garantido (declarado, S20-R1 e R12)

- **A automação real ponta a ponta NÃO está provada.** Falta a prova com a Zapia de verdade: ela precisa ter o conector de GitHub (D1, não confirmado), a rotina precisa disparar e o envio precisa notificar o celular. Tudo isso é **autorrelato (confiança C)** até o roteiro rodar.
- A Zapia é um modelo: **não executa este Python**. O código é a especificação testável e o **verificador** do que ela devolve; a imposição do lado dela é a instrução da rotina e o escopo do token, e o que a Zapia fez só se confirma pelo recibo de volta.
- Criar a rotina na Zapia exige a frase **`AUTORIZO`** (S20-R6) e o teste sem efeito antes; o token da Zapia só de `entrada` e a janela PJ seguem atos do proprietário.
- Fases F2 (volta com resultado), F3 (rotina diária do Coach), F4 (Tutor→Notebook) e F5 **não** foram feitas; a COR-E fica para depois, por pedido do proprietário.
