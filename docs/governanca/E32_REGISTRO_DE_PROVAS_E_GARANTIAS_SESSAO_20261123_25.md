# E32: registro consolidado das provas, refutações e garantias da sessão de 23 a 25/11/2026 (automação Zapia ponta a ponta)

**Natureza:** registro de **evidência**, não contrato. Consolida, num só lugar e com identificadores, o que esta sessão **provou, refutou e deixou não provado** sobre a automação entre Tutor, Coach, Zapia e o repositório `entrada`. Cada item aponta o registro de detalhe (E27 a E31, `CAPACIDADES_ZAPIA_VERIFICADAS.md`). **Regra:** nenhum item "não provado" sobe de nível por inferência; só nova prova (captura mais verificação por código) ou refutação datada o altera. Confiança A, B ou C como em `docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md`. **Nenhum dado pessoal; todo par e issue de teste foi sintético.**

## 1. Lotes mesclados nesta sessão

| PR | Merge (`main`) | O que entrou |
|---|---|---|
| #187 | `2f1002e` | Operação `agendar_rotina` (E27), chave de parada, modelos de instrução com hash |
| #188 | `38de806` | Contexto do runner real (`ler_contexto_agendar`, E28) |
| #189 | `f1b40f6` | Antecedência mínima do `agendar_rotina` de 15 para **90 min** (contrato, autorizada); sonda real somente leitura; modelo `POLLER`; verificador do recibo `CRIADA`; E29 e E30 |
| #190 | `c6ec3b1` | Modelo `HOOK_ENTREGA`, roteiro `prova_f4_hook_entrega.sh`, E31; registro do resultado |

Suíte completa no último head mesclado: **2533 testes passaram**; CI verde no head `609a0bb`.

## 2. Matriz de provas

| # | Pergunta | Resultado | Confiança | Evidência (identificadores) | Limite |
|---|---|---|---|---|---|
| P1 | O runner lê o `entrada` REAL como o código espera? (ZAPIA-CTX) | **PROVADO** (leitura) | B | Sonda real, 24/11: antes 1 validado, 1 recibo, 1 hash, pedidos do dia `[]`; depois do par sintético 3, 3, 3 e `["coach"]` (captura dele) | Só leitura; o runner **não** promoveu (flag falsa) |
| P2 | Uma rotina da Zapia cria outra rotina? (ZAPIA-F3) | **REFUTADO** | B | Poller `4ba5054e` (23/11, 12:09Z) acordou e respondeu `I cannot create a routine from inside a routine.`; instrução salva idêntica ao modelo (3950 caracteres, conferida por código) | Um teste; a Zapia **não sabe** se tentou chamar a ferramenta; causa desconhecida |
| P3 | O GitHub avisa por e-mail as ações do próprio dono? | **OBSERVADO** | B | Antes dos ajustes, nenhum e-mail; depois de ligar "incluir minhas próprias atualizações" e acompanhar o repositório, a issue #4 (`TESTE-NOTIF`) chegou na Caixa de entrada do Gmail; remetente `notifications@github.com` (cabeçalho lido por ele); o assunto segue `[owner/repo] título (Issue #n)` | Depende de configuração da conta dele |
| P4 | Um hook de Gmail acorda a Zapia por esse e-mail? | **PROVADO** | B | Hook `5b91c690` (só `senders` e `subject_contains`): issue #5 criada 2026-11-25T00:41:29Z, relato às 00:41:56Z (**27 s**), só hora e assunto, sem corpo; **o hook anterior `4ca435fa` estava ligado a outra conta Gmail (desativada) e nunca receberia o evento** | Uso único; autorrelato dela + captura dele |
| P5 | O hook lê o `entrada` e notifica? (1ª execução E2E) | **PROVADO (parcial)** | B | Hook `8b43759f`, issue #6 criada 10:23:54Z; acordou 10:24:23Z (**29 s**); tamanhos citados (239, 241, 316 bytes) batem com os arquivos reais; **não gravou** o recibo (defeito do nosso modelo: campo obrigatório que ela não lê); relatou um URL com o nome do repositório truncado (relato errado) | Notificação é autorrelato |
| P6 | O hook lê, confere o hash e GRAVA o recibo de entrega? (2ª execução) | **PROVADO** | B | Hook `2bef6d04`, issue #7 criada 10:32:58Z; `comandos/entregas/f4-hook.json` com `entregue_em` 10:33:46Z (**48 s**), commit `ed7b09e` 10:33:53Z; `zapia_disparo.py` `ok: true`; `conferir_entrega` `None`; 233 bytes; campos fixos, sem texto; URLs corretos | Par sintético manual; autorrelato do carimbo; o `rotina_id_relatado` (`1a21244610ce2fde`) **não é** o ID do hook (`2bef6d04`) |
| P7 | Inventário final da Zapia | **OBSERVADO** (autorrelato) | C | Um hook (`2bef6d04`, desabilitado), três rotinas de teste (`4820d046`, `2bf694ce`, `4ba5054e`) desabilitadas e executadas, três do Radar pausadas por ele; nenhuma automação de teste ativa | Ela não lê o Google Tasks (não conectado) |
| P8 | Estado final do `entrada` | **CONFERIDO** (leitura remota) | A | Raiz com `.github` e `recibos`; `comandos/` ausente; nenhuma issue aberta; nenhuma execução do fluxo desde 18/11 (os pushes de teste não o dispararam) | Foto de 25/11 |

## 3. Descobertas operacionais que valem para qualquer sessão futura

- **Filtros do hook de Gmail:** só `senders`, `labels`, `subject_contains` e `text_contains`. **Não há prefixo de assunto**: o prefixo é conferido pela Zapia depois do disparo.
- **O aviso de fechamento da issue é outro e-mail** (`Re: ...`) que **contém** o trecho do filtro: **fechar ou comentar uma issue com `SINAL` só depois do relato**, e nunca com um hook vivo.
- **A conta do hook precisa ser a conectada hoje** (relido: conta, filtros, estado e texto salvo).
- **Texto do hook:** a instrução vem de **modelo versionado** (`HOOK_ENTREGA`), conferida **byte a byte** contra o que a Zapia salvou; o e-mail é só campainha e nunca instrução.
- **A Zapia relata URLs de memória:** a ordem "copiar letra por letra" ajudou; os **tamanhos** dos arquivos são o teste cruzado mais barato.
- **Campo que ela não consegue ler (ID do hook) não pode ser obrigatório** no recibo; o verificador já o aceita ausente.
- **Entrega "como o dono":** a credencial da Zapia é dele; commits dela aparecem sob a conta dele: **só hash e carimbo distinguem**.
- **`push --dry-run` não prova permissão de escrita**; só uma escrita real prova.

## 4. Exceções de acesso concedidas pelo proprietário (devem ser revogadas por ele antes do run de verdade)

- **Leitura e escrita** da sessão no `ufms-meu-estudo-entrada` (25/11/2026; decisão final dele: **manter leitura e escrita para a próxima sessão**). Foi usada **só** para: gravar o par sintético `f4-hook.json` (`72f25b8`), abrir e fechar as issues #6 e #7 (e fechar a #1), conferir o resultado e apagar os seis arquivos de teste (`8ea64e5`). Contraria a regra do `AGENTS.md` de não dar credencial direta ao modelo e S4 e S6; **a origem do comando segue não provada** (S4-R2). Registro: E31, seção "Exceção de acesso".
- O ambiente **bloqueou** a remoção do clone local `/home/user/ufms-meu-estudo-entrada` (verificação de segurança); a pasta continua no disco, sem uso. **A revogação do anexo é ato dele.**

## 5. NÃO PROVADO (não afirmar)

- **Tutor e Coach emitindo comandos reais** pela caixa: todo comando de teste foi sintético e colocado à mão (`SINTETICO_MANUAL`).
- **O fluxo como emissor** da campainha (abrir a issue ao promover) e **a promoção pelo fluxo**: flag do fluxo falsa, janela do piloto (PJ) não aberta, consentimento v4 não usado.
- **Hook recorrente**, **vários dias**, pontualidade em relação a `agendado_utc` (S15-R4).
- **As demais operações** com a Zapia real: `criar_lembrete`, `enviar_prompt_notebook`, `consultar_agenda_minima`, relatório do TEC, Gemini Notebook, `agendar_rotina` como criação de rotina.
- **Os gates no caminho real:** `delivery_gate` e o recibo de START (RS) existem como código offline testado, mas **não estão ligados ao fluxo nem ao hook**; quem conferiu hash e carimbo hoje foi o verificador depois do fato.
- **A notificação no chat** da Zapia como evento (captura dele **pendente**; só autorrelato dela) e o **encerramento** do hook (ela não conseguiu apagá-lo; ele está desabilitado).

## 6. Garantias de código desta sessão (testes e contraprovas)

- `tests/test_e28_runner_contexto.py` (22), `tests/test_e29_f3_poller.py` (24), `tests/test_termux_prova_f3.py` (11), `tests/test_e31_hook_entrega.py` (15), `tests/test_e29_registro.py`, `tests/test_e30_registro.py`, `tests/test_e31_registro.py` e ajustes de `tests/test_agendar_rotina.py` (janela de 90 min) e `tests/test_retomada_proxima_sessao.py`.
- Mutações verificadas mortas: filtro do dia, parada da retomada, filtro de status do recibo, conferência de hash, carimbo antes do poller, instrução da filha, campos do contrato, guarda de só-GET da sonda, e as do roteiro (`--agendado`, `NÃO FECHE`, título `SINAL`).
- `python scripts/agendar_rotina.py --check` confere o hash e as URLs literais de **todos** os modelos (`UNICA`, `ESCUTA`, `POLLER`, `HOOK_ENTREGA`).
- **O roteiro Termux nunca rodou com o `gh` real**; os testes usam `gh` e `git` falsos.

## 7. Decisões do proprietário desta sessão (não reabrir)

Antecedência mínima 90 min (contrato); gatilho por **Gmail**, só sinal, filtro `senders` mais `subject_contains` (sem prefixo, que o hook não oferece); emissor **notificação nativa do GitHub** (muda o fluxo; PR próprio); o teste dos hooks é sem efeito externo e de uso único; leitura e escrita temporárias no `entrada`; **o próximo trabalho "liga tudo"** nesta ordem (E33).
