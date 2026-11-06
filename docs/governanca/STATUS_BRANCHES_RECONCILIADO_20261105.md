# Inventário reconciliado de branches — saneamento 05/11/2026

**Repositório:** `Andraus35/UFMS-MEU-ESTUDO`  
**Base usada na classificação original (pré-PR #50):** `50ced2966293f0e714fed8a9325f83a4dd79cc09`  
**`main` vigente após PR #50:** `4ca27e8db66073ce8ad57b812070094d6c4dca1e`  
**Último marco integrado:** PR #49 (squash merge).  
**Método:** comparação autenticada de cada branch de trabalho com `main`; criação de cópia de segurança em `archive/pre-saneamento-20261105/` e comparação de cada origem com sua cópia.

## Fotografia de classificação e situação remota em 06/11/2026

- Branches de trabalho originais inventariadas: **42**.
- Cópias de segurança criadas: **42**.
- Cópias verificadas por comparação origem → backup: **42/42 idênticas** (0 à frente, 0 atrás).
- Branches originais classificadas como contidas na `main` da base pré-PR #50 (zero commits exclusivos naquele momento): **29**.
- Branches originais com commits exclusivos: **13**.
- PRs abertos na consulta que produziu a classificação original: **0** (fotografia histórica; PR #51 foi aberto depois).
- Exclusões de branches executadas após o inventário: **29/29 confirmadas** (revalidação individual imediatamente antes de cada exclusão).

As 42 cópias de segurança preservam o HEAD exato de cada branch original no momento da auditoria. A classificação de ancestralidade das 29/13 foi feita contra a base pré-PR #50; não deve ser interpretada como uma nova comparação de ancestralidade contra a `main` atual. O backup da branch `docs/gp3-personal-mvp-8-20261105` também foi criado; sua divergência em relação a `main` decorre do histórico original após squash merge do PR #49, não de conteúdo necessariamente pendente.

## A. Branches contidas em main — classificação histórica das 29 branches posteriormente excluídas

Estas branches foram comparadas com `main` e não possuíam commits exclusivos no momento do inventário. Todas tinham backup verificado. A execução posterior e sua confirmação estão registradas ao final deste documento.

| Branch original | Backup |
|---|---|
| `audit/rm01-source-monitoring-20261105` | `archive/pre-saneamento-20261105/audit--rm01-source-monitoring-20261105` |
| `audit/rm07-functional-gates-20261105` | `archive/pre-saneamento-20261105/audit--rm07-functional-gates-20261105` |
| `audit/sim05-broker-reconciliation-20261105` | `archive/pre-saneamento-20261105/audit--sim05-broker-reconciliation-20261105` |
| `audit/sim07-trusted-governance-decision-20261105` | `archive/pre-saneamento-20261105/audit--sim07-trusted-governance-decision-20261105` |
| `audit/sim08-oracle-telegram-bridge-decision-20261105` | `archive/pre-saneamento-20261105/audit--sim08-oracle-telegram-bridge-decision-20261105` |
| `audit/sim09-branch-inventory-reconciliation-20261105` | `archive/pre-saneamento-20261105/audit--sim09-branch-inventory-reconciliation-20261105` |
| `audit/sim09-final-branch-inventory-20261105` | `archive/pre-saneamento-20261105/audit--sim09-final-branch-inventory-20261105` |
| `audit/sim11-post-merge-state-reconciliation-20261105` | `archive/pre-saneamento-20261105/audit--sim11-post-merge-state-reconciliation-20261105` |
| `automation/sim03-fapec-readonly-20261105` | `archive/pre-saneamento-20261105/automation--sim03-fapec-readonly-20261105` |
| `docs/rm07-closeout-rm08-readiness-20261105` | `archive/pre-saneamento-20261105/docs--rm07-closeout-rm08-readiness-20261105` |
| `docs/roadmap-required-bootstrap-20261104` | `archive/pre-saneamento-20261105/docs--roadmap-required-bootstrap-20261104` |
| `docs/sim10-pedagogia-archive-and-queue-close-20261105` | `archive/pre-saneamento-20261105/docs--sim10-pedagogia-archive-and-queue-close-20261105` |
| `feat/rm03-evidence-projection-20261105` | `archive/pre-saneamento-20261105/feat--rm03-evidence-projection-20261105` |
| `feat/rm04-deterministic-queue-20261105` | `archive/pre-saneamento-20261105/feat--rm04-deterministic-queue-20261105` |
| `feat/rm05-notebook-prescriber-20261105` | `archive/pre-saneamento-20261105/feat--rm05-notebook-prescriber-20261105` |
| `feat/rm07-source-renderer-gates-20261105` | `archive/pre-saneamento-20261105/feat--rm07-source-renderer-gates-20261105` |
| `feat/rm07-spec-composition-validators-20261105` | `archive/pre-saneamento-20261105/feat--rm07-spec-composition-validators-20261105` |
| `feat/rm07-trusted-tool-gateway-20261105` | `archive/pre-saneamento-20261105/feat--rm07-trusted-tool-gateway-20261105` |
| `fix/rm00-delivery-gates-20261105` | `archive/pre-saneamento-20261105/fix--rm00-delivery-gates-20261105` |
| `fix/rm00-head-bound-delivery-gate-20261105` | `archive/pre-saneamento-20261105/fix--rm00-head-bound-delivery-gate-20261105` |
| `fix/rm02-igp-contracts-migration-20261105` | `archive/pre-saneamento-20261105/fix--rm02-igp-contracts-migration-20261105` |
| `fix/sim01-privacy-integration-20261105` | `archive/pre-saneamento-20261105/fix--sim01-privacy-integration-20261105` |
| `fix/sim02-api-write-integrate-20261105` | `archive/pre-saneamento-20261105/fix--sim02-api-write-integrate-20261105` |
| `fix/sim03-fapec-cli-e2e-20261105` | `archive/pre-saneamento-20261105/fix--sim03-fapec-cli-e2e-20261105` |
| `fix/sim06-handoff-reconciliation-20261105` | `archive/pre-saneamento-20261105/fix--sim06-handoff-reconciliation-20261105` |
| `fix/sim07-cognitive-effects-policy-20261105` | `archive/pre-saneamento-20261105/fix--sim07-cognitive-effects-policy-20261105` |
| `fix/sim08-ci-duplicate-gates-20261105` | `archive/pre-saneamento-20261105/fix--sim08-ci-duplicate-gates-20261105` |
| `spec/sim06-cognitive-gates-r2-20261105` | `archive/pre-saneamento-20261105/spec--sim06-cognitive-gates-r2-20261105` |
| `test/rm06-adversarial-102-traceability-20261105` | `archive/pre-saneamento-20261105/test--rm06-adversarial-102-traceability-20261105` |

## B. Branches com commits exclusivos — preservar e não integrar em lote

| Branch original | PR histórico | Commits exclusivos vs main | Backup |
|---|---:|---:|---|
| `audit/compose-roadmap-document-reconciliation-20261105` | #14 | 6 | `archive/pre-saneamento-20261105/audit--compose-roadmap-document-reconciliation-20261105` |
| `audit/governance-document-reconciliation-20261104` | #12 | 4 | `archive/pre-saneamento-20261105/audit--governance-document-reconciliation-20261104` |
| `audit/postcommit-exact-diff-20261105` | #17 | 3 | `archive/pre-saneamento-20261105/audit--postcommit-exact-diff-20261105` |
| `audit/trusted-governance-p0-20261104` | #10 | 44 | `archive/pre-saneamento-20261105/audit--trusted-governance-p0-20261104` |
| `automation/fapec-readonly-schedule-20261105` | #16 | 1 | `archive/pre-saneamento-20261105/automation--fapec-readonly-schedule-20261105` |
| `feature/oracle-telegram-calendar-bridge` | #3 | 21 | `archive/pre-saneamento-20261105/feature--oracle-telegram-calendar-bridge` |
| `fix/api-postcommit-content-bound-20261105` | #18 | 11 | `archive/pre-saneamento-20261105/fix--api-postcommit-content-bound-20261105` |
| `fix/api-write-draft-pr-preflight-20261105` | #13 | 2 | `archive/pre-saneamento-20261105/fix--api-write-draft-pr-preflight-20261105` |
| `security/agent-entrypoint-failclosed-20261104` | #11 | 10 | `archive/pre-saneamento-20261105/security--agent-entrypoint-failclosed-20261104` |
| `security/compose-agent-broker-roadmap-20261105` | #15 | 7 | `archive/pre-saneamento-20261105/security--compose-agent-broker-roadmap-20261105` |
| `spec/ufms-cognitive-gates-gqd-correction-v0-3` | #5 | 22 | `archive/pre-saneamento-20261105/spec--ufms-cognitive-gates-gqd-correction-v0-3` |
| `spec/ufms-cognitive-gates-verify-d-20261104` | #4 | 1 | `archive/pre-saneamento-20261105/spec--ufms-cognitive-gates-verify-d-20261104` |
| `docs/gp3-personal-mvp-8-20261105` | #49 | histórico pós-squash | `archive/pre-saneamento-20261105/docs--gp3-personal-mvp-8-20261105` |

A classificação de 12 históricos conserva as justificativas registradas no inventário anterior: snapshots/handoffs antigos, propostas substituídas ou fora de escopo, controles recuperados seletivamente e funcionalidades ainda sem homologação/E2E. A branch de #49 é separada por causa do squash merge e deve ser tratada como histórico preservado, não como prova automática de código pendente.

## Critérios para a próxima etapa

1. As 29 branches da seção A foram excluídas após autorização expressa e revalidação individual imediatamente antes de cada exclusão; ver relatório de execução ao final.
2. As 13 branches da seção B permanecem preservadas; qualquer recuperação de conteúdo deve ser seletiva, em PR próprio e com testes.
3. O inventário anterior `STATUS_BRANCHES_20261105.md` é fotografia pós-#35 e permanece como registro histórico. Este arquivo é a reconciliação posterior ao PR #49.
4. As 29 branches da seção A foram removidas; as 13 branches da seção B e as 42 cópias de segurança foram preservadas.
5. A exclusão foi executada pelo proprietário no Termux, com validação de elegibilidade, igualdade com backup, ancestralidade em `main`, ausência de PR aberto e readback da exclusão.

## Estado

**Inventário original preservado como fotografia da classificação pré-exclusão. Execução posterior: 29/29 exclusões confirmadas; 13 históricas e 42 backups preservados; `main` preservada.**


## Relatório de execução pós-inventário — 06/11/2026

- PR #50 integrado em `main` no commit `4ca27e8db66073ce8ad57b812070094d6c4dca1e`.
- Conforme saída final do script Termux fornecida pelo proprietário, foram excluídas e confirmadas **29 branches**, com **0 impedimentos**. Cada branch foi revalidada imediatamente antes da exclusão.
- Resultado final do script: **13 históricas preservadas; 42 backups preservados; `main` preservada** no SHA `4ca27e8db66073ce8ad57b812070094d6c4dca1e`.
- A consulta remota posterior confirmou ausência das 29 candidatas na listagem de branches e ausência de PRs abertos.
- CI pós-merge do PR #50: run `42158000977`, conclusão `success` no SHA informado.
- Proveniência: totais operacionais de exclusão/preservação conforme saída do Termux enviada pelo proprietário; estado de PR, HEAD, branches listadas e CI conforme consulta autenticada ao GitHub.
