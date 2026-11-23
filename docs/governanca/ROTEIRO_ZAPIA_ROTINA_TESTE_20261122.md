# Roteiro da rotina de teste da Zapia, execução única (S20-R6, S15-R4, S8-R8) (22/11/2026)

**Quem executa:** o proprietário (a sessão não tem acesso à Zapia e não cria rotina). **Pré-requisito provado:** o F1 (E21): a Zapia lê comando e recibo em `entrada` por HTTP com o token dela, confere o hash, mostra a notificação e grava o recibo de volta. **Objetivo:** provar, **uma vez**, que a Zapia **acorda sozinha** na hora marcada e faz esse mesmo caminho, sem você colar prompt. **Sem dado pessoal.** Resultado: autorrelato dela **mais** conferência por código nosso (`scripts/zapia_disparo.py`); confiança B só onde o carimbo confere.

**Não prova:** pontualidade em vários dias (S15-R4 pede três dias, é outro lote), promoção pelo fluxo (flag e PJ: aqui o par continua colocado à mão e marcado `SINTETICO_MANUAL`), rotina diária do Coach (F3) nem notificação fora da conversa se o aparelho bloquear. O horário da Zapia é a palavra dela até o código conferir.

## Passo 0: anotar o horário agendado

Escolha um horário **daqui a pelo menos 15 minutos**, em UTC (Campo Grande = UTC-4: 10:00 local = 14:00Z). Anote `AGENDADO=AAAA-MM-DDTHH:MM:SSZ`. Esse é o valor que o verificador usa; **não o altere depois**.

## Passo 1: teste sem efeito (S20-R6 exige antes)

Diga `AUTORIZO` à Zapia e peça uma rotina **de teste, de execução única, no horário AGENDADO, que só relata**: "No horário agendado, leia `comandos/validados/` e `comandos/recibos/`, **não envie notificação e não grave nada**; apenas me diga no chat a hora UTC em que acordou e quantos comandos `enviar_mensagem` com recibo de mesmo hash viu". Use o formato de chamada da ferramenta dela: `curl` simples, uma chamada por vez, só `-X`, `-H` e `-d`; o token só no formulário seguro dela (se estiver vazio, ela para). Se acordar na hora e relatar, o gatilho funciona **sem efeito**: siga. Se não acordar, **pare** (S20-R9: nada de reenvio, nada de mensagem substituta) e traga o texto literal dela.

## Passo 2: o par sintético desta rotina

No clone do repositório público, branch do lote: `python scripts/zapia_f1_prep.py preparar --saida <pasta> --nome f1-rotina.json` (a pasta traz `validados/f1-rotina.json` e `recibos/f1-rotina.json`; o comando passa pelo mesmo validador da caixa). Envie os dois arquivos a `comandos/validados/f1-rotina.json` e `comandos/recibos/f1-rotina.json` em `entrada` (`gh api -X PUT`, como faz o `prova_f1_zapia.sh`; o recibo é marcado `SINTETICO_MANUAL`). **Atenção:** o comando vale **24 h** a partir de `issued_at`; gere o par no mesmo dia do horário AGENDADO.

## Passo 3: a rotina com efeito (frase `AUTORIZO` já dada em 22/11/2026; confirme se a Zapia a pedir)

Peça à Zapia a rotina de **execução única** no horário AGENDADO, com esta instrução: "No horário agendado, leia `comandos/validados/` e `comandos/recibos/` do repositório. Para o comando `enviar_mensagem` com recibo de **mesmo hash** (SHA-256 do JSON canônico: `sort_keys`, separadores `,` e `:`, `ensure_ascii=False`), emitido há menos de 24 h, de origem `tutor` ou `coach`, e que você ainda não entregou: me envie a notificação 'Coach (origem declarada): <texto>' e grave em `comandos/entregas/f1-rotina.json` um JSON com `entrada_id`, `hash_corpo`, `status` = `ENTREGUE`, `entregue_em` (UTC, AAAA-MM-DDTHH:MM:SSZ **lido do relógio no momento da entrega**), `origem_declarada`, **sem o texto**. No máximo 2 por dia, **uma única execução**: não repita, não reagende, não envie mensagem substituta. Se algo divergir, não envie nada e me avise com o texto literal do erro." Não passe token no chat.

## Passo 4: a conferência (código nosso)

Depois do horário, num checkout do repositório `entrada`:

```
python scripts/zapia_entrega.py --raiz <pasta>
python scripts/zapia_disparo.py --raiz <pasta> --nome f1-rotina.json --agendado <AGENDADO>
```

Passa se: o recibo de volta confere com o hash (F1), o carimbo `entregue_em` é UTC bem formado, **não é anterior** ao AGENDADO (anterior = entrega manual), cai **até 900 s depois** (tolerância **proposta**, ajustável por `--tolerancia`), é a **única** entrega daquele hash e o dia não passa de 2 entregas. Anexe ao registro (E23): a captura da notificação **recebida na hora** (com o relógio do aparelho visível), o relato do passo 1, as duas saídas acima e o AGENDADO anotado.

## Depois

Limpe os três arquivos de teste (`comandos/validados/`, `comandos/recibos/`, `comandos/entregas/` com o nome `f1-rotina.json`). Remova ou desative a rotina na Zapia (ela é de execução única; confira que não ficou recorrente). Qualquer falha de conector, disparo ou notificação **para o processo**: sem envio substituto e sem laço (S20-R9).

## Variante de 2 dias (indício, a pedido do proprietário de 23/11/2026)

Repita os passos 2 e 3 para **o dia seguinte**, com outro nome de par (por exemplo `f1-rotina-d2.json`), outro comando sintético (gerado no dia 2, por causa das 24 h) e outro horário agendado, **20 h a 28 h depois** do primeiro. Na instrução da Zapia acrescente: "grave também em `rotina_id_relatado` o identificador da rotina como o app a mostra (letras, números, `.`, `_`, `:` e `-`, até 64)" e "use o recurso **nativo** de rotina agendada do app; se não conseguir, pare e diga". Anexe a **captura da lista de rotinas do app**. Conferência:

```
python scripts/zapia_disparo.py --raiz <pasta> --nome f1-rotina.json --agendado <D1> --dia2-nome f1-rotina-d2.json --dia2-agendado <D2>
```

Passa só com os dois dias consistentes e o id relatado nos dois. **É indício, não a prova de 3 dias (S15-R4)**, e não distingue entrega manual logo após o horário: quem distingue é a captura do app e a notificação recebida sem você estar na conversa.
