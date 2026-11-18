# E4 — Emenda do D-21: Outlook conectado (18/11/2026)

**Natureza:** registro da emenda do `PRODUCT.md` (D-28), tarefa E4. **Situação: proposta aguardando a revisão do proprietário no diff do PR; o merge só sai por pedido explícito dele.**

## O que muda
| Onde | Antes | Depois |
|---|---|---|
| `PRODUCT.md`, D-21 | Mantém Drive e Calendar e **exclui o Outlook** | Marcada "emendada pela D-28"; o texto antigo permanece |
| `PRODUCT.md`, D-28 (nova) | — | O proprietário **precisa do Outlook conectado**; a conexão **não autoriza** abrir, ler, enviar, apagar nem processar e-mail ou anexo; isso exige `AUTORIZO` própria, finalidade e consulta mínima; finalidade **ainda não declarada** |

## Origem
Resposta do proprietário em pergunta de fim de rodada (18/11/2026): "Preciso dele conectado". Rodadas 7 e 8 da Zapia (autorrelato): há caixa Outlook conectada; ela não sabe quem a autorizou nem quando (`RESPOSTA_RODADAS7_8_ZAPIA_Z1_20261118.md`).

## O que a E4 NÃO faz
- **Não autoriza** a Zapia a ler ou enviar e-mail; **não declara** finalidade (pendência dele).
- **Não altera** `AGENTS.md`, `agents/`, `settings.json`, S5 nem S9.
- **Não prova** a conexão: é relato (dele e da Zapia).

## Limites
O gate confere estrutura, não o sentido; a revisão do diff é humana. `PRODUCT.md` tem orçamento de 38 KiB em teste.
