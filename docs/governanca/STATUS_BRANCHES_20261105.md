# Inventário final das branches preservadas — 05/11/2026

**Base autenticada:** `main@3f9411ca00c35713f8b140df6091d92b73ed31d9` antes do PR #28. Branch protection: `protected=true`, check obrigatório `validate`. PRs abertos antes desta tarefa: zero. O inventário lista 20 branches de trabalho ainda existentes; nenhuma foi apagada.

## Branches de integração concluída

| Branch | PR | SHA preservado | Situação | Destino |
|---|---:|---|---|---|
| `docs/roadmap-required-bootstrap-20261104` | #9 | `b07880dc3f790eb1060e31de30c12b388118ff25` | Merge | START/ROADMAP integrado |
| `fix/sim01-privacy-integration-20261105` | #19 | `bf9fc575a83067a18829e66af4e1e2e8c979bd97` | Merge | Privacidade e proteção de projeções |
| `fix/sim02-api-write-integrate-20261105` | #20 | `f157acb0a6accf3ae5374b459ec83dcc8dd6f264` | Merge | Guard e transação API opt-in, sem writer real habilitado |
| `automation/sim03-fapec-readonly-20261105` | #21 | `936df5fddae89b77eb730088cf06c96608933345` | Merge | Monitor FAPEC read-only; cron real ainda não comprovado |
| `audit/sim05-broker-reconciliation-20261105` | #22 | `d68bab62141073592f8308bc6f01efcd818632bc` | Merge | Não reintegrar broker legado; ADR-010 |
| `spec/sim06-cognitive-gates-r2-20261105` | #23 | `8bde29b58ee891ee34617a838a458b7124782559` | Merge | PLAN r2 e CHECKS como especificação; 0/27 E2E |
| `audit/sim07-trusted-governance-decision-20261105` | #24 | `f07c242eed44db335faf5039b7c2d0a8589c0c4b` | Merge | Não instalar GitHub App/Oracle; ADR-011 |
| `audit/sim08-oracle-telegram-bridge-decision-20261105` | #27 | `fe2386bae0f4ae952a0662325a57ba5f845cd2dc` | Merge | Não importar ponte Telegram/Calendar; ADR-012 |

## Branches históricas preservadas, sem merge bruto

| Branch | PR histórico | SHA preservado | Decisão atual |
|---|---:|---|---|
| `feature/oracle-telegram-calendar-bridge` | #3 | `757e61c7e880fb8b38c4b215eb063c6c9f1e7cbe` | Diferida: sem implantação, bots/OAuth, integração Tutor/Coach ou E2E; ADR-012 |
| `spec/ufms-cognitive-gates-verify-d-20261104` | #4 | `0db458a50447c2a9f8e7131f402dc3be9c0db313` | Base histórica da SPEC; não reintegrar isoladamente |
| `spec/ufms-cognitive-gates-gqd-correction-v0-3` | #5 | `9f1b347e755c82f15089470749d9d33524167c1f` | Parcialmente recuperada: somente PLAN r2, CHECKS, recibo e verificador; motor não homologado |
| `audit/trusted-governance-p0-20261104` | #10 | `9e928a31d626c174a813e54461d408271d531c65` | Diferida: App/Oracle não instaladas; check verde obsoleto sem revogação imediata; ADR-011 |
| `security/agent-entrypoint-failclosed-20261104` | #11 | `c7213f1ac512ede8760f8025a0f5d3db4aa7c288` | Não importar: broker antigo de dez arquivos substituído pelo broker atual |
| `audit/governance-document-reconciliation-20261104` | #12 | `36e81390d8b41cf5c62a071e067779d2aed1d805` | Não copiar snapshots de status/handoff obsoletos |
| `fix/api-write-draft-pr-preflight-20261105` | #13 | `27024250463cbc5fa28c50ed5d10323b987f0abd` | Intermediária da cadeia API; recuperada via PR #20 |
| `audit/compose-roadmap-document-reconciliation-20261105` | #14 | `ae8edf3a91d62dff431ea6db2ea88d55b2edc65e` | Não copiar composição documental antiga |
| `security/compose-agent-broker-roadmap-20261105` | #15 | `e3a32b92c4c16a98456008718f145d5175f564b3` | Não importar: API de broker antiga e duplicada |
| `automation/fapec-readonly-schedule-20261105` | #16 | `fd0a81823405e72a0b5fb91abf2a73cb5af685dc` | Funcionalidade recuperada via PR #21; branch histórica mantida |
| `audit/postcommit-exact-diff-20261105` | #17 | `538909435a945b3801fa6fdd39b9e98b659a34d3` | Intermediária API; recuperada via candidata terminal e PR #20 |
| `fix/api-postcommit-content-bound-20261105` | #18 | `daec1f626c0bf43a22a565eaac3a290bc71f83c5` | Candidata terminal recuperada seletivamente via PR #20 |

## Fechamento e cautelas

- **20 branches de trabalho preservadas** (além da `main`): 8 branches associadas a PRs integrados e 12 branches históricas fechadas sem merge.
- PRs #25 e #26 foram tentativas fechadas sem merge durante sincronização de HEAD da auditoria da ponte; a decisão final está no PR #27. Não contam como branches adicionais.
- Os PRs #13/#17/#18 e #16 continuam fechados sem merge; as capacidades foram recuperadas seletivamente nos PRs #20 e #21. Preservar os refs não implica que sejam código pendente de integração.
- Branches #11/#12/#14/#15/#10/#3 não devem ser mescladas por lote. Suas decisões e motivos estão nos ADRs e notas de governança atuais.
- **Não apagar branches neste ciclo.** A remoção de refs exige pedido separado após backup e confirmação de que nenhum commit exclusivo permanece sem destino.
- Este inventário é fotografia; antes de qualquer ação futura, consultar API GitHub, HEADs e PRs novamente.
