# Versão normativa atual — UFMS Cognitive Gates

**PLAN vigente aprovado:** `revisions/v0.3/approved-r2/plan.md` (fonte exata `revisions/v0.3/proposals/r2/plan.md`, mensagem humana “APROVO” em 04/11/2026, SHA de origem `426286a913ea17adddb2cdb951120b45282ad938`).
**CHECKS vigentes derivados:** `revisions/v0.3/approved-r2/checks.md`; 27 critérios previstos, **0/27 provas de ponta a ponta Tutor/Coach executadas**. Há **43/43 testes funcionais isolados para C2/C3/C25/C26** (12 de resolução de referência, 13 de fatos críticos curados, 18 do renderer em prévia local), sem publicação externa nem comprovação de raciocínio semântico universal; detalhes em `revisions/v0.3/functional-tests/README.md`.
**Recibo e decisão:** `revisions/v0.3/approved-r2/APPROVAL_v0.3-r2.md` e `approval-receipt.json`.
**Status resolvido:** as expressões “NOVA PROPOSTA — NÃO APROVADA” no snapshot original r2 registram seu estado **no momento da autoria**, antes do aceite humano. O estado vigente só é **APROVADO PARA ESPECIFICAÇÃO** após conferir a cadeia original SHA/árvore, o recibo de escopo limitado e o aceite real. Metadados sem vínculo verificado não prevalecem; em conflito: `NOT_VERIFIABLE` e sem efeitos externos. Ver `revisions/v0.3/proposals/r3/APPROVAL_PRECEDENCE.md`.
**Proposta posterior:** `revisions/v0.3/proposals/r3/plan.md` — **NÃO APROVADA**, e `checks-preview.md` — **NÃO CONGELADOS**. Não substituir a r2 nem aproveitar sua aprovação para a r3.
**Dependências observadas:** PRs técnicos #1 e pedagógico #2 constam **mesclados na main**. Snapshot fixo usado na preparação: `main` SHA `2b09c08036035bfff334e84ee0b976efaed577a8`, árvore `9cf12e9550ae2e04840823e8b080be3f91e6fc2b`. O PR #5 permanece em draft. O manifesto r3 original é documental (snapshot histórico). **Prova sintética posterior:** GitHub Actions [run 41939869665](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41939869665), no HEAD `a5c94ef69d231283c2851abc8b5a361e284a4832`, testou `refs/pull/5/merge` SHA `dd9b2bc7ebf01d08e038689697541b13ca7e77df`, pais `main 676dd5d3259c66ba97c3e7e3338451cfc4e5cd68` + HEAD #5; 8/8 contraprovas de composição e 171/171 testes do harness passaram, com recibo. **Não constitui homologação GQD-03 nem prova funcional C1–C27.**

**Gate de homologação:** GQ-D **REPROVADA** no parecer independente do objeto PR #5 SHA `652634b70a411ed4641cb7a202b0ae2f9a19ed1b`. GQ-C `NOT_RUN`; GQ-O `BLOCKED`. Nenhum merge do PR #5, deploy, credenciais, Calendar/Telegram ou escrita pessoal autorizados.

**Histórico:** PLAN v0.3-r1 e CHECKS preservados em `revisions/v0.3/`; objeto original PR #4 preservado como auditado. A CI formal TLC aprovada da r2 não é homologação de segurança.

**Checkpoint posterior de C2/C3:** HEAD `dffc56625c92e7a563f81806ac07a91c920b3174`, CI de composição [41941588161](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41941588161), 12/12 testes isolados; r2 imutável, r3 não aprovada, GQ-D independente pendente. O novo checkpoint documental exigirá outra leitura de CI no HEAD que o publicar.

**Checkpoint posterior C25:** o HEAD `76d9239816baa98fa71b72426a228186e8365482` passou [CI 41945361675](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41945361675), com 25 testes isolados; nenhum gate de produção foi promovido por essa prova.

**Checkpoint C26 isolado:** HEAD `9192455c59b9582eed0f458e7f61a4e2078af7dc`, [CI 41952389995](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41952389995) com 43/43 testes isolados, somente no canal local_preview; não equivale a renderer de produção nem aprova r3.
