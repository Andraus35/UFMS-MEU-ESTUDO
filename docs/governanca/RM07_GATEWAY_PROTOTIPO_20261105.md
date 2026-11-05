# RM-07 — gateway fail-closed (protótipo offline)

**Data:** 05/11/2026  
**Base:** `main@c0683804038b197333bcf91af13bada40cf80464`  
**Tarefa:** continuação GQ-D / NCs 01, 05, 06 e 08  
**Natureza:** protótipo testável sem integração externa.

## Controles implementados

- Aprovação separada e assinada por HMAC; token de gateway tem assinatura distinta.
- Token vincula ator, ferramenta, destinatário, hash da ação/parâmetros, policy SHA, state revision, run, proposal, source set, output kind, authorization epoch, nonce, approval ID, approver ID e expiração.
- TTL máximo de 300 segundos.
- Allowlist de ferramentas; caller identity precisa ser `trusted_supervisor`.
- Validação de política, estado e epoch antes de reservar efeito.
- SQLite `BEGIN IMMEDIATE` para nonce único, event_id idempotente e rate limit por ator/ferramenta.
- Limite de payload, falha de dependência pré-execução, timeout `UNCONFIRMED` sem retry cego.
- Recibo com decisão, reason codes, policy SHA, source refs e hash da ação; não armazena parâmetros brutos.
- Exit codes: 0 COMMITTED, 1 DENIED/STALE_STATE, 2 NEEDS_APPROVAL/NEEDS_EVIDENCE, 3 DEPENDENCY_FAILED/UNCONFIRMED.

## Contraprovas

`tests/test_tool_gateway.py` cobre assinatura inválida, ator/aprovador iguais, adulteração de destino/parâmetros, expiração/TTL, bypass de caller, allowlist, policy/state/epoch stale, fonte ausente, dependência indisponível, input acima do limite, idempotência, conflito de event_id, replay de nonce concorrente, rate limit e timeout sem retry.

## Limites não resolvidos

- `caller_identity` é uma fronteira simulada no protótipo; não prova identidade de processo/OS nem impede que um LLM acesse diretamente o emissor.
- A chave de aprovação e a chave de gateway precisam ficar em serviços/processos isolados; este repositório não prova isolamento de segredos.
- `SQLiteLedger` usa memória por padrão; produção exige armazenamento transacional durável, retenção e recuperação auditada.
- Serialização usa subconjunto JSON determinístico de Python, não implementação certificada de RFC 8785/JCS.
- Não há adapters externos, Zapia, Telegram, Agenda, renderer ou rota de publicação. Nenhum efeito externo foi executado.
- O token não é uma autorização humana real até a assinatura vir de UI/serviço confiável fora do processo LLM.
- O PR não fecha GQ-D; NCs 01/05/06/08 ficam apenas parcialmente mitigadas no protótipo. Os 27 checks end-to-end continuam NOT_RUN.

## Decisão

Aprovar somente como incremento técnico offline se CI completa e readback passarem. Não promover status para homologado nem habilitar ferramentas externas, escrita pessoal, publicação ou credenciais.
