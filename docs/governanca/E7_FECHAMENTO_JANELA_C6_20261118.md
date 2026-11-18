# E7 — Fechamento da janela da C6 e resultado da prova real (18/11/2026)

**Natureza:** registro do fechamento da janela aberta pela C6 (E6). **Situação: proposta aguardando a aprovação expressa do proprietário; o merge só sai por pedido dele, citando PR e head.** O fechamento só vale depois que o fluxo for **reinstalado** com o SHA do merge deste PR.

## Resultado da prova real da segunda metade da C5 (relato do proprietário, com captura, 18/11/2026)
Com o fluxo fixado no SHA `b74be9cce027` (C5G), a flag do fluxo ligada nele, o consentimento v4 presente, o segredo e a variável presentes:
- a Zapia (token `zapia token`, só `entrada`) gravou **uma** entrada sintética (`c5-sintetica-20261118T192903.json`);
- o fluxo terminou em **sucesso** (execução 44421234167) e o runner **não parou na flag**;
- `dados` passou de **0 para 1 evento** (`eventos/2026-11/20261118-0b7b03d66dfc.json`), com a cabeça avançando;
- o envelope do evento tem `sintetico=true`, `escritor=fluxo` e `entregue_por=zapia`;
- a entrada saiu da fila e o recibo `recibos/c5-sintetica-20261118T192903.json` existe.

**O que fica provado:** gatilho, pino do validador por SHA e hash, v4 exigido, flag do fluxo lida no SHA fixado, escopo do token da Zapia, promoção até `dados` com marca de teste, recibo e fila consumida. **Não provado:** projeções lidas por sessões (não há gerador), resultado real consentido, fluxo com mais de uma entrada.

## O que muda neste PR
| Onde | Antes | Depois |
|---|---|---|
| `settings.json`, `storage.private_flow_promotion_enabled` | `true` | **`false`** |
| `settings.json`, `storage.personal_results_writes_enabled` | `false` | **`false`** (nunca liga) |
| `tests/test_promotion_runner.py`, `tests/test_e6_c6_flag_do_fluxo.py` | esperavam a janela aberta | esperam as duas flags falsas |

## Para o fechamento valer (ato do proprietário)
1. Mesclar este PR e atualizar o clone na `main`.
2. **Reinstalar o fluxo** (`bash scripts/termux/prepara_entrada.sh`, etapa 4, frase **`ATUALIZAR`**). **Mesclar sem reinstalar NÃO desliga o fluxo**: ele lê a flag do `settings.json` do SHA que fixa.
3. **Remover `ufms-meu-estudo-entrada` do Claude GitHub App** (https://github.com/apps/claude/installations/select_target): a leitura foi concedida só para o diagnóstico (18/11/2026) e nunca vale para `dados`.

## Permanece no histórico
O evento sintético fica em `dados` (histórico só de acréscimo), marcado como teste: as projeções o descartam (`session_read_guard.descartar_sinteticos`).

## Limites
Relato com captura, sem prova independente. A flag em repouso é falsa; religar é PR de janela com aprovação expressa. O gerador de projeções ainda não existe.
