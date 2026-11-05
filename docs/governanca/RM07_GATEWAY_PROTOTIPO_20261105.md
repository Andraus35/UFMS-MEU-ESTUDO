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

## Follow-up PR #46 — source/fact gates e renderer local

A PR #46 integra, seletivamente, os módulos `source_gate.py`, `fact_gate.py` e `safe_renderer.py` da PR5 à main atual, com testes adaptados em `tests/`.

- C2/C3: fonte original pinada por Git blob, manifesto, 47 páginas, 81 chunks e intervalo literal por página. Referência válida ainda retorna `semantic_support=NOT_CHECKED`.
- C25: três fatos normativos curados e preservação do conflito ALERTA-DOC-01. Claims fora do catálogo permanecem NEEDS_EVIDENCE; não é interpretador semântico geral.
- C26: emissão somente em `local_preview`, papéis Tutor/Coach, token vinculado ao contexto, nonce/release atômicos e sem canal externo.
- Limites: renderer não ligado ao gateway como processo isolado; emissor/supervisor ainda são fronteiras simuladas; sem adapters Zapia/Telegram/Agenda, publicação ou persistência pessoal.

### Estado atualizado das 9 NCs após PR #45/#46

| NC | Estado | Limite remanescente |
|---|---|---|
| GQD-01 | PARTIAL_IN_MAIN | Gateway protótipo; caller/issuer sem isolamento OS/secret comprovado |
| GQD-02 | OPEN | Quatro mutantes semânticos e oráculos humanos independentes ausentes |
| GQD-03 | PARTIAL_CANDIDATE_NOT_MAIN | Manifesto/CI composição apenas na branch PR5 obsoleta |
| GQD-04 | PARTIAL_IN_MAIN | Source/fact gates curados; não cobre claims arbitrárias |
| GQD-05 | PARTIAL_IN_MAIN | Rate limit atômico local; sem store durável nem chamadas externas reais |
| GQD-06 | PARTIAL_IN_MAIN | Renderer local; runner completo de cinco estados/four exits ainda não integrado |
| GQD-07 | PARTIAL_IN_MAIN | Recibo r2 documental; não é GQ-D nem autorização de BUILD |
| GQD-08 | PARTIAL_IN_MAIN | Context binding apenas em prévia local, sem rota externa |
| GQD-09 | PARTIAL_CANDIDATE_NOT_MAIN | Validadores oficiais executados na branch PR5, ainda não integrados ao pipeline main |

**Contagem:** 1 OPEN, 6 PARTIAL_IN_MAIN, 2 PARTIAL_CANDIDATE_NOT_MAIN, 0 CLOSED.

**27 checks funcionais:** continuam 0/27 PASS end-to-end. Testes unitários isolados de source_gate, fact_gate, safe_renderer e tool_gateway não equivalem ao fluxo Tutor/Coach/Zapia. GQ-D continua pendente de reauditoria independente; GQ-C NOT_RUN; GQ-O BLOCKED.

Nenhum efeito externo foi executado. Não foram usados dados pessoais.
