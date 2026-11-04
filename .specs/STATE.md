# Spec Lean — UFMS Cognitive Gates · decisions & handoff

**Feature:** `ufms-cognitive-gates`
**Approval:** 2026-11-04 — user: "APROVO"
**Original plan SHA-256:** `652cd14711d7f1997b8d2703dba81dca316a7245fcf4429bc903e8f86a94c297`
**Approved plan SHA-256:** `6e6977d6d9ffd964a2bf8e52720f8754773e6656b99c5808f7e7c3b6d950d0d8`

## Decisions

- **AD-001 — 04/11/2026:** Approved v0.2 PLAN and its 27 EARS criteria; exact user response: "APROVO". This is specification approval, not deployment permission.
- **AD-002 — 04/11/2026:** D2 approved as one-way door: isolated gateway, single-use action binding and no LLM credentials. Operation details still require a specific go-live plan.
- **AD-003 — 04/11/2026:** D4 approved: only `safe_renderer` may publish generated responses, with run/proposal/policy binding; no channel deployed yet.
- **AD-004 — 04/11/2026:** Critical normative claims require checked source facts, independent of citation-existence validation; abstain/review if missing.
- **AD-005 — 04/11/2026:** D1 (minimal receipt) and D3 (risk classes) approved as policy contracts; personal result writes remain blocked.

## Handoff

- **Phase:** CHECKS derived; official validators unavailable in this execution environment (npm registry DNS failure), local structure-only check is **not** official.
- **Next:** run installed skill validators against an authenticated checkout and build a red-first test suite; do not claim C1–C27 completed until the tests prove them.
- **Scopes:** PR #1 and #2 were not edited; no push or merge; no personal data or production tools.
- **Go-live unresolved:** operator/provider, secret isolation, nonce/TTL persistence, receipt retention, costs and access.

## Adaptação de fases aprovada na conversa (AD-006)

- **Origem da decisão:** usuário em 04/11/2026: "O VERFY ME PARECE UTIL" e "VAMOS LA" após proposta explícita de conservar VERIFY sem BUILD de software tradicional.
- **Interpretação limitada:** autoriza prosseguir com a auditoria da especificação (VERIFY-D) e a preparação de VERIFY-C; não aprova deploy, escrita remota, migração de dados, segredos, publicação de modelo ou execução externa.
- **Regra de versão:** PLAN v0.2 e CHECKS derivados **não são modificados silenciosamente**. Alterações de obrigações EARS exigem revisão humana e rederivação dos CHECKS.
- **Diferenciação:** GQ-D: integridade documental; GQ-C: comportamento de um LLM realmente submetido ao harness; GQ-O: enforcement operacional em ferramentas/canais. Nenhum teste documental prova GQ-C ou GQ-O.
- **BUILD:** opcional no escopo documental apenas; necessário se um requisito de enforcement (gateway, token, renderer, nonce, autorização) ainda não tiver implementação equivalente demonstrável.
- **Verifier independente:** ainda não designado. O relatório desta sessão é autoauditoria com verificador determinístico auxiliar; homologação independente permanece pendente.
