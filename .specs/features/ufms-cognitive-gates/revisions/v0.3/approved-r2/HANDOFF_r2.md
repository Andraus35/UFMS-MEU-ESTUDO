# HANDOFF — PLAN v0.3-r2 aprovado / CHECKS derivados

**Fonte:** PR #5, commit `426286a913ea17adddb2cdb951120b45282ad938`, `proposals/r2/plan.md`; usuário disse “APROVO” em 04/11/2026.

**Versão atual:** `revisions/v0.3/approved-r2/` (PLAN com metadado externo TLC; CHECKS C1–C27 derivados da prévia r2). O legado r1 continua sem modificações em `revisions/v0.3/` e nos respectivos commits históricos; não sobrescrever sem outra aprovação.

**Regra de equivalência:** `approved-r2/plan.md == proposals/r2/plan.md + marcador de aprovação`; `approved-r2/checks.md` conserva integralmente a seção `## Checks` da prévia. A matriz continua **27/27 rastreados, 0/27 provas funcionais executadas**.

**Próximo gate:** executar `validate_plan.py`, `validate_checks.py` oficiais de versão pinada sem `--execute` (BUILD fora do escopo documental); registrar resultados e advertências; depois requisitar reauditoria independente GQ-D das 9 NCs originais no HEAD novo. Não presumir PASS a partir de CI de formato.

**Segurança:** GQ-D REPROVADA até novo parecer; GQ-C NOT_RUN; GQ-O BLOCKED. Sem merge, deploy, segredos, ferramenta produtiva ou gravação pessoal. PRs #1, #2 e #4 intocados.
