# E29: teste real "rotina cria rotina" (ZAPIA-F3) e sonda real do contexto (ZAPIA-CTX) (lote ZAPIA-F3, 23/11/2026)

**Natureza:** preparo do **teste na prática real** pedido pelo proprietário em 23/11/2026. O repositório entrega o **roteiro, o verificador e a instrução do poller**; **a prova depende de ato dele** (Termux, `entrada` real e Zapia real). **Nada aqui está provado até o roteiro rodar.** Muda contrato em um ponto, já autorizado por ele (E25, seção F; resposta de 23/11/2026): a antecedência mínima do `agendar_rotina` sobe de 15 para **90 min** (`scripts/agendar_rotina.py`, E24, E27). O merge segue o pedido expresso dele, citando PR e head.

## Resultado (23/11/2026): **REFUTADO** para "rotina cria rotina"

- **A. Sonda real do contexto (ZAPIA-CTX): PROVADA para a leitura.** No `entrada` real, antes: 1 validado, 1 recibo, 1 hash promovido, pedidos do dia `[]`; depois do par sintético: 3, 3, 3 e `["coach"]` (captura do proprietário). Prova o formato da listagem e da leitura do GitHub real e a seleção por recibo com hash; **não** prova o runner promovendo (flag falsa).
- **B. Poller (ZAPIA-F3): REFUTADO.** O poller `4ba5054e` (12:09Z) acordou e respondeu `I cannot create a routine from inside a routine.` (captura). A instrução salva é idêntica byte a byte ao modelo versionado (3950 caracteres, conferido por código), então a recusa **não** vem de texto errado nosso; o app não expõe a instrução salva. Nenhum `criadas/` nem filha. **Não repetir** (S20-R9).
- **Consequência:** `agendar_rotina` **não** pode contar com a Zapia criando a rotina sozinha. Caminho que **funciona**: rotina criada **na conversa** (E23). Alternativa autônoma proposta: uma rotina **recorrente criada por você** (modelo `ESCUTA`, de hora em hora das 06h às 22h) que **lê e entrega** os comandos promovidos, sem criar outra. A decisão de desenho é dele (outro lote).

## O que o teste responde

| Pergunta | Como é medida | Estado hoje |
|---|---|---|
| **A.** O runner lê o `entrada` REAL como o código espera? (ZAPIA-CTX) | `scripts/ctx_leitura_real.py` (só GET): conta validados, recibos, hashes promovidos e pedidos do dia | **não provado** (só GitHub falso) |
| **B.** Uma rotina da Zapia consegue **criar outra** rotina nativa? (ZAPIA-F3) | poller de execução única grava `comandos/criadas/<pedido>` (CRIADA); `scripts/zapia_poller.py conferir` | **não provado** (a Zapia diz que nunca testou) |
| **C.** A rotina filha entrega o alvo no horário? | mesmo verificador do E23 (`zapia_disparo.conferir_pasta_unica`) | provado só para rotina criada **por você** (E23) |

## Como o teste funciona

1. `bash scripts/termux/prova_f3_zapia.sh preparar`: confere pré-condições, roda a **sonda real antes**, grava em `entrada` um **par sintético** (alvo `enviar_mensagem` do Coach e pedido `agendar_rotina` `F1_ENTREGA_UNICA` apontando para o alvo, recibos `SINTETICO_MANUAL`), roda a **sonda depois** (esperado: 2 validados, 2 recibos, 2 hashes promovidos, `agendamentos_do_dia` = `["coach"]`) e imprime o texto a enviar à Zapia.
2. Você envia o texto: a Zapia cria **um poller nativo de execução única** (daqui a ~25 min). A instrução (`config/rotina_instrucoes.json`, modelo `POLLER`, com hash) traz **URLs completos e literais**, o **commit público fixado** e o **hash do modelo da filha** (pin): o poller só cria a filha se o modelo lido nesse commit tiver exatamente o hash fixado.
3. No horário, o poller lê o pedido, confere hash, origem, validade e janela, **cria a rotina filha** (~105 min depois da preparação) com a instrução do modelo `UNICA` preenchida, **lê de volta** o texto salvo, calcula o SHA-256 e grava `comandos/criadas/f3-pedido.json` com `status` `CRIADA`, `criada_em`, `agendado_utc`, `rotina_id_relatado` e `instrucao_sha256` (sem texto).
4. A filha dispara e entrega o alvo como no E23 (`comandos/entregas/f3-alvo.json`).
5. `bash scripts/termux/prova_f3_zapia.sh conferir` baixa o estado, roda o verificador e pede **dois relatos seus** (rotina filha vista na lista do app; notificação recebida sem você na conversa). `limpar` apaga os seis arquivos.

## O que o verificador confere (código nosso)

`CRIADA` só passa se: campos exatamente os sete do contrato; `status` `CRIADA` e nome do pedido; `hash_corpo` = hash do pedido = recibo; `agendado_utc` igual ao do pedido; `criada_em` UTC **não anterior** ao poller, **até 900 s depois** (tolerância proposta) e **antes** do disparo da filha; `rotina_id_relatado` bem formado; e `instrucao_sha256` igual ao SHA-256 do texto que **nós** renderizamos do modelo `UNICA` com os mesmos valores (instrução traduzida ou alterada reprova). Depois, a entrega da filha passa pelo verificador do disparo único. Códigos de falha distintos por regra; tudo testado com contraprovas (`tests/test_e29_f3_poller.py`, `tests/test_termux_prova_f3.py` com `gh` e `git` falsos).

## Se a Zapia NÃO conseguir criar rotina de dentro de rotina

A instrução manda ela **dizer literalmente** que não consegue, **não gravar nada** e parar. Esse é um **resultado válido**: refuta a hipótese do poller e leva o desenho para o plano B (você ou um fluxo externo criam a rotina; a Zapia só entrega). **Não repita o teste em laço** (S20-R9).

## O que NÃO prova (declarado)

- **Carimbo e id da rotina são autorrelato** da Zapia. Só a **captura da lista de rotinas do app** (sua) separa rotina criada de entrega manual. O verificador não vê o app.
- **Promoção pelo fluxo** (flag do fluxo e janela PJ): o par é colocado à mão, recibo `SINTETICO_MANUAL`. **O runner real continua com a flag falsa.** A sonda lê o `entrada` real, **mas não roda o runner nem promove**: prova o formato da leitura, não o fluxo completo.
- Um dia, uma execução: **não** prova pontualidade em vários dias (S15-R4), modelos `ROTINA_ESTUDO_*` e `BRIEFING_DIARIO`, nem poller recorrente de hora em hora (06h a 22h, decisão dele, **outro lote**).
- O roteiro foi testado com `gh` falso; **não foi executado com o `gh` real**. Se algo divergir no aparelho, cole o texto literal no chat.
- O poller lê o modelo da filha por `api.github.com` do repositório **público** (mesmo host que a Zapia já usa); **não está provado** que a ferramenta HTTP dela aceite essa leitura sem credencial. Falha ali para o teste e vira registro.

## Para o proprietário

1. **Aprovar** o merge deste lote, citando PR e head (muda `agendar_rotina.py`, E24 e E27).
2. **Rodar** o roteiro no Termux, na revisão já enviada ao GitHub: `git pull`, `bash scripts/termux/prova_f3_zapia.sh preparar`, enviar o texto à Zapia, tirar as capturas, esperar a filha e `bash scripts/termux/prova_f3_zapia.sh conferir`.
3. Trazer ao chat a saída do `conferir`, o texto literal da Zapia (sucesso ou erro) e as capturas (não versionadas). Só então o item sobe de "não provado" no `CAPACIDADES_ZAPIA_VERIFICADAS.md`.
