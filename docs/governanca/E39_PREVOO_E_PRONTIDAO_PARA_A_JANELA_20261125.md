# E39: pré-voo e prontidão para a janela do piloto (lote 3, ZAPIA-LIGAR)

**Natureza:** registro e **roteiro de coleta somente leitura**. Nada foi ligado, nenhuma flag mudou, nenhuma janela foi aberta, e a sessão **não** executou o pré-voo contra o GitHub real (isso é ato do proprietário, no Termux). Base: `docs/governanca/ROTEIRO_PJ_JANELA_PILOTO_20261121.md`, `docs/governanca/E33_PLANO_PROXIMA_SESSAO_LIGAR_TUDO_E_SUBAGENTS.md` e `scripts/piloto_preflight.py`.

## O que este lote entrega

- `scripts/termux/coleta_preflight.sh`: coleta **só por leitura** (`gh api` GET) as leituras que o `scripts/piloto_preflight.py` precisa (HEAD da main, SHA fixado e hash do fluxo instalado, hash esperado para esse SHA, flags, repositórios privados, consentimento v4, CI do HEAD) e roda o pré-voo. A validade dos tokens é **informada por você** (o script não lê token). Não grava, não liga flag, não imprime segredo; o arquivo de leituras é temporário, modo 0600, e é apagado ao sair.
- `tests/test_termux_coleta_preflight.py`: contrato estático e execução com um `gh` falso (nenhuma chamada de escrita; fluxo adulterado vira vermelho; validade curta vira âmbar).

## Achado de prontidão (o que está vermelho de propósito hoje)

O pré-voo exige **SHA fixado no fluxo igual ao HEAD da main** (`sha_fixado`). O fluxo instalado em 25/11/2026 está fixado em `a4f8084`; a `main` já passou dele (cada merge move o HEAD). Portanto, **o pré-voo de abertura dará VERMELHO até a reinstalação do fluxo no HEAD atual**, e a reinstalação tem de ser **a última coisa antes do pré-voo, sem merge no meio**:

1. Mesclar tudo o que for ser mesclado antes da janela (esta frente incluída).
2. `bash scripts/termux/ufms.sh atualizar` (clone na main) e `bash scripts/termux/prepara_entrada.sh`, etapa 4, frase `ATUALIZAR` (reinstala o fluxo no HEAD e atualiza `FLUXO_SHA256`).
3. `bash scripts/termux/coleta_preflight.sh abertura` e só então pedir a janela.

Cada PR mesclado depois do passo 2 exige repetir o 2 e o 3. O PR da janela em si move a main e é tratado pelo roteiro PJ (passo 5, `pos_janela`).

## Prontidão por pré-condição (estado em 25/11/2026)

| Pré-condição | Estado | Quem prova |
|---|---|---|
| Tokens renovados (P9) | declarado por ele: validade até 31/07/2027 nos dois | relato; o pré-voo usa a validade que ele informar |
| Consentimento v4 | registrado como feito no `state/WORKFLOW.json` (P4); o pré-voo confere o arquivo `consent-v4.json` do privado | pré-voo |
| Fluxo instalado e `FLUXO_SHA256` | fluxo gravado e variável definida em 25/11/2026 (relato dele, com captura; hash `0b08e17b…`); **fixado em `a4f8084`, hoje defasado** | pré-voo (`fluxo_hash`, `sha_fixado`) |
| Repositórios privados sem forks e convites | não conferido nesta sessão | pré-voo (`repo_entrada`, `repo_dados`) |
| Flags em repouso (as duas falsas) | `personal_results_writes_enabled=false` no público; a do fluxo falsa no SHA fixado | pré-voo (`flags`) |
| CI verde no HEAD | verde no último merge conferido | pré-voo (`ci`) |
| Caderno real resolvido por ele (entrada manual) | **pendente, ato dele** | ele |
| Anexo do `entrada` à sessão | **ainda não revogado** (ato dele; antes do run de verdade) | relato dele |
| Frase da janela | **pendente**: `Aprovo a janela do piloto: PR #<n>, head <sha completo>.` ("Mesclar" não vale) | ele |

## Limites

- A coleta é **autorrelato do GitHub lido por `gh` na conta dele**; a sessão não vê o resultado, só o que ele colar (sem valores). O teste prova o script com `gh` falso, **não** a leitura real.
- O hash esperado é recalculado **a partir do modelo, do portão e do emissor lidos no SHA fixado**; se o SHA fixado for anterior ao emissor, o marcador do emissor simplesmente não é substituído.
- Não prova pontualidade, funcionamento do hook nem a promoção: isso é o lote 3 (E36), na janela.
- O texto do PR de janela (`docs/governanca/E8_JANELA_PILOTO.md`, item PJ da fila) **ainda não foi escrito**: ele nasce quando o proprietário disser que quer abrir a janela.
