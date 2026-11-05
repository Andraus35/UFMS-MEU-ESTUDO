# Inventário autenticado de branches — 05/11/2026

**Repositório:** `Andraus35/UFMS-MEU-ESTUDO`  
**HEAD base da auditoria:** `2ec4d355a3da52d22a340a8055e482f38942cde5`  
**Método:** API GitHub autenticada; comparação de cada ref com `main`; nenhuma exclusão, force-push ou merge de branch histórica.

## Resumo verificável

- Antes desta entrega: **26 refs** (25 branches de trabalho + `main`); depois de criar a branch desta entrega: **27 refs** (26 branches de trabalho + `main`).
- PRs existentes: **32**, todos fechados; **18 merged**, **14 closed without merge**. PRs #25 e #26 são tentativas sobre a mesma branch final #27 e não representam refs adicionais.
- PRs abertos antes desta entrega: **zero**.
- Das 25 branches preexistentes: **13 refs têm HEAD contido em `main`** (compare da branch contra `main`: zero commits exclusivos); **12 refs preservam commits exclusivos e estão fechadas sem merge**.
- Branch desta entrega: `audit/sim09-branch-inventory-reconciliation-20261105`, PR #33, única frente ativa.
- **Decisão:** branches contidas em `main` são candidatas a exclusão pós-backup; branches divergentes permanecem preservadas. Esta entrega não apaga refs e não integra os 12 históricos em bloco.

## Branches cujo HEAD está contido em main

| Branch | PR integrado | HEAD preservado | Evidência de comparação |
|---|---:|---|---|
| `audit/sim05-broker-reconciliation-20261105` | #22 | `d68bab62141073592f8308bc6f01efcd818632bc` | 0 commits exclusivos |
| `audit/sim07-trusted-governance-decision-20261105` | #24 | `f07c242eed44db335faf5039b7c2d0a8589c0c4b` | 0 commits exclusivos |
| `audit/sim08-oracle-telegram-bridge-decision-20261105` | #27 | `fe2386bae0f4ae952a0662325a57ba5f845cd2dc` | 0 commits exclusivos |
| `audit/sim09-final-branch-inventory-20261105` | #28 | `591c5a3350d9ea902594ca6100427cee79ba3c82` | 0 commits exclusivos |
| `automation/sim03-fapec-readonly-20261105` | #21 | `936df5fddae89b77eb730088cf06c96608933345` | 0 commits exclusivos |
| `docs/roadmap-required-bootstrap-20261104` | #9 | `b07880dc3f790eb1060e31de30c12b388118ff25` | 0 commits exclusivos |
| `fix/sim01-privacy-integration-20261105` | #19 | `bf9fc575a83067a18829e66af4e1e2e8c979bd97` | 0 commits exclusivos |
| `fix/sim02-api-write-integrate-20261105` | #20 | `f157acb0a6accf3ae5374b459ec83dcc8dd6f264` | 0 commits exclusivos |
| `fix/sim03-fapec-cli-e2e-20261105` | #29 | `48722b83fd83ada401823c5a7ee25819910bf970` | 0 commits exclusivos |
| `fix/sim06-handoff-reconciliation-20261105` | #30 | `c6f5e9bdd9791d93a9f63de233988189ac68d818` | 0 commits exclusivos |
| `fix/sim07-cognitive-effects-policy-20261105` | #31 | `05e54fc3bf9917d8fd3d9802b5e9d00a738ba4fc` | 0 commits exclusivos |
| `fix/sim08-ci-duplicate-gates-20261105` | #32 | `11e6ba0ce8740f0e4c3ac7954167c3affb3e582b` | 0 commits exclusivos |
| `spec/sim06-cognitive-gates-r2-20261105` | #23 | `8bde29b58ee891ee34617a838a458b7124782559` | 0 commits exclusivos |

## Branches históricas divergentes — preservar, não mesclar em lote

| Branch | PR encerrado | SHA preservado | Commits exclusivos vs main | Decisão |
|---|---:|---|---:|---|
| `audit/compose-roadmap-document-reconciliation-20261105` | #14 | `ae8edf3a91d62dff431ea6db2ea88d55b2edc65e` | 6 | composição documental antiga; não copiar snapshots |
| `audit/governance-document-reconciliation-20261104` | #12 | `36e81390d8b41cf5c62a071e067779d2aed1d805` | 4 | snapshots/handoff obsoletos |
| `audit/postcommit-exact-diff-20261105` | #17 | `538909435a945b3801fa6fdd39b9e98b659a34d3` | 3 | intermediária API; controles recuperados seletivamente no #20 |
| `audit/trusted-governance-p0-20261104` | #10 | `9e928a31d626c174a813e54461d408271d531c65` | 44 | App/Oracle não instaladas; proposta não homologada |
| `automation/fapec-readonly-schedule-20261105` | #16 | `fd0a81823405e72a0b5fb91abf2a73cb5af685dc` | 1 | monitor recuperado via #21; cron real ainda NOT_VERIFIED |
| `feature/oracle-telegram-calendar-bridge` | #3 | `757e61c7e880fb8b38c4b215eb063c6c9f1e7cbe` | 21 | fora de escopo; sem implantação/E2E |
| `fix/api-postcommit-content-bound-20261105` | #18 | `daec1f626c0bf43a22a565eaac3a290bc71f83c5` | 11 | candidata terminal recuperada seletivamente no #20 |
| `fix/api-write-draft-pr-preflight-20261105` | #13 | `27024250463cbc5fa28c50ed5d10323b987f0abd` | 2 | branch intermediária da cadeia API |
| `security/agent-entrypoint-failclosed-20261104` | #11 | `c7213f1ac512ede8760f8025a0f5d3db4aa7c288` | 10 | broker antigo substituído pelo broker atual |
| `security/compose-agent-broker-roadmap-20261105` | #15 | `e3a32b92c4c16a98456008718f145d5175f564b3` | 7 | API de broker antiga e duplicada |
| `spec/ufms-cognitive-gates-gqd-correction-v0-3` | #5 | `9f1b347e755c82f15089470749d9d33524167c1f` | 22 | apenas PLAN r2/CHECKS recuperados; 0/27 E2E |
| `spec/ufms-cognitive-gates-verify-d-20261104` | #4 | `0db458a50447c2a9f8e7131f402dc3be9c0db313` | 1 | snapshot histórico; não reintegrar isoladamente |

## Regras de limpeza

1. Branch com zero commits exclusivos é apenas **candidata** à exclusão; antes, confirmar que o PR está merged e criar backup/ref imutável.
2. Branch com commits exclusivos não é descartável automaticamente. Revisar árvore/diff e a justificativa histórica; recuperar somente conteúdo ainda necessário em um PR serial.
3. PR fechado sem merge não equivale a código mesclado; seus commits exclusivos permanecem preservados nos refs acima.
4. Não fazer merge bruto dos 12 históricos: várias propostas foram explicitamente substituídas, rejeitadas ou diferidas.
5. Nenhuma branch foi apagada nesta entrega. Exclusão requer autorização específica após backup e readback.
6. Revalidar o inventário via API imediatamente antes de qualquer futura exclusão; este documento é fotografia do HEAD indicado.

## Branch ativa desta entrega

`audit/sim09-branch-inventory-reconciliation-20261105` — PR #33, atualização documental do inventário; não inclui remoção de refs.
