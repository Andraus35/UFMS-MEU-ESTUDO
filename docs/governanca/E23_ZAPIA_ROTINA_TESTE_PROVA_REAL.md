# E23: prova real da rotina agendada da Zapia, execução única, par sintético (23/11/2026)

**Natureza:** registro da entrega oficial do item `ZAPIA-F2a` (RM-09, S20 F2a). Segue `ROTEIRO_ZAPIA_ROTINA_TESTE_20261122.md`; executado pelo proprietário. A sessão não tem acesso à Zapia nem ao repositório `entrada` (o ambiente negou anexá-lo). O `AUTORIZO` **não foi dito**: a E26 (D-31) estava em vigor desde o merge do #185. Nada altera `agents/`, `AGENTS.md` nem o esquema de comandos.

## O que foi feito

O proprietário gravou em `ufms-meu-estudo-entrada` um par **sintético manual** (`comandos/validados/f1-rotina.json`, 316 bytes, origem `coach`, `enviar_mensagem`, `issued_at` 04:01:52Z; `comandos/recibos/f1-rotina.json`, 241 bytes, `SINTETICO_MANUAL`, `hash_corpo` `71898de8...06d0`). Em seguida pediu, por prompt, à Zapia rotinas de **execução única** com o recurso **nativo** de rotina agendada do app dela. Tentativas de gravar o par falharam duas vezes por erro de pasta e de versão do script; uma delas deixou dois arquivos **vazios** (SHA de arquivo vazio) que a gravação final sobrescreveu.

## Linha do tempo (autorrelato da Zapia, com capturas do proprietário onde indicado)

| Hora (Campo Grande) | Rotina | Resultado |
|---|---|---|
| 00:15 (04:15Z) | `4820d046`, só lê e relata | **Acordou sozinha** às 04:15:04Z (captura das 00:17) e contou **0 comandos**, embora o par existisse desde 04:03Z. URLs da instrução estavam corretos. **Causa não determinada** (hipóteses: não buscou o conteúdo dos arquivos; a execução agendada não usou a mesma credencial ou ferramenta da conversa). |
| 00:2x | diagnóstico na conversa, só leitura | A Zapia **leu** os dois arquivos, decodificou e o SHA-256 **bateu** com `hash_corpo`. O erro não era do repositório, do formato nem do hash. |
| 00:30 (04:30Z) | `2bf694ce`, com efeito | **Acordou sozinha** e **parou sem agir**: "The GitHub API request to `commands/validados/` returned no response body" (captura das 00:31). A instrução gravada **traduziu `comandos` para `commands`** nos três caminhos. Falha segura correta: sem notificação, sem gravação. |
| 01:00 (05:00Z) | `2bf694ce`, instrução reescrita com URLs completos e literais | Relato: GETs às 05:00:01Z (316 e 241 bytes), hash igual, **notificação enviada** "Coach (origem declarada): Teste F1 do Coach: notificação sintética, sem dado pessoal." e recibo gravado em `comandos/entregas/f1-rotina.json` com `entregue_em` `2026-11-23T05:00:21Z`. |

## Conferência por código (terminal do proprietário, 01:02, captura)

- `python scripts/zapia_entrega.py --raiz <checkout de entrada>` -> `{"conferidas": 1, "falhas": {}}`.
- `python scripts/zapia_disparo.py --raiz <checkout> --nome f1-rotina.json --agendado 2026-11-23T05:00:00Z` -> `{"ok": true, "codigo": null, "entregas": 1}`.
- Isso confirma: recibo de volta com mesmo hash, `ENTREGUE`, só campos fixos, carimbo UTC bem formado, **não anterior** ao agendado, **21 s depois** dele (tolerância de 900 s), uma única entrega daquele hash e dentro do teto diário.

## O que fica provado (confiança B para o recibo, C para a notificação até a captura)

Uma rotina **nativa agendada** da Zapia **acordou sozinha** no horário, **leu** o comando e o recibo de `entrada` por HTTP, **conferiu o hash**, notificou e **gravou o recibo de volta**, **sem a frase `AUTORIZO`** e sem o proprietário na conversa (a relatar por ele). As duas rotinas anteriores **dispararam** no horário (captura), o que sustenta o gatilho nativo.

## O que NÃO está provado (S20-R1, R12)

- **A notificação chegar ao aparelho sem o proprietário na conversa:** o relato da Zapia é dela; **falta a captura do aparelho com o relógio visível** e a **lista de rotinas do app** com o identificador `2bf694ce`.
- **`rotina_id_relatado`:** o verificador confere só o **formato**; a comparação com `2bf694ce` é **manual** e **não consta** nas saídas anexadas.
- **Que o carimbo seja do relógio real:** é autorrelato; o código confere consistência com o horário anotado.
- **Pontualidade em vários dias** (S15-R4 pede 3), **rotina recorrente**, a **promoção pelo fluxo** (flag e janela PJ; o par foi colocado à mão), o **Tutor** com a Zapia real e o **Gemini Notebook**.
- A **causa do 0 das 00:15** segue desconhecida.

## Lições para o desenho (a levar ao lote de aplicação)

1. **A rotina agendada reescreve a instrução e traduziu os caminhos** (`comandos` virou `commands`). O modelo versionado da instrução deve trazer **URLs completos e literais** e a ordem de **não traduzir**; a verificação lê o texto salvo de volta.
2. **A rotina e a conversa podem divergir** (ambiente, credencial, ferramenta). Toda rotina nova deve **relatar cada chamada** (URL e resultado) para que um zero ou uma falha tenham causa visível.
3. **A credencial na Zapia se chama `github_ufms_repo_token`**, não "zapia token" (o nome é dela; o que importa é o escopo do repositório `entrada`).
4. A falha segura funcionou: **sem notificação e sem gravação** quando o caminho estava errado.
5. O verificador de 2 dias e o `rotina_id_relatado` ficam como estão; a **conferência do id** contra o app continua manual até haver captura.

## Próximo

Lote de aplicação (`agendar_rotina` nos dois perfis, chave de parada e modelo versionado da instrução com as lições acima), em PR próprio, com o pedido de merge dele citando PR e head. O Tutor com a Zapia real e a rotina de 2 dias seguem para depois.
