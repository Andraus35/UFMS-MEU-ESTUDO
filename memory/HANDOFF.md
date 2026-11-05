# HANDOFF vigente — UFMS MEU ESTUDO

**Checkpoint 05/11/2026.** Fonte operacional: GitHub autenticado + `state/WORKFLOW.json`. Repositório público; resultados pessoais permanecem bloqueados.

## Estado confirmado
- `main` = `8fda9754846b4fba65cd88244260653cbb606720`.
- PR #43 / RM-06 mesclado em `8fda9754846b4fba65cd88244260653cbb606720`; CI pós-merge run `42085633053`, `validate=success`.
- PR #42 / RM-05 mesclado em `4425939488bb39291adf63184e33a132c6b461b3`; CI pós-merge run `42084811834`, `validate=success`.
- PR #41 / RM-04 mesclado em `3cbe6ffe74babf9f778216c52596994830e64143`; CI pós-merge run `42083859206`, `validate=success`.
- PR #40 / RM-03 mesclado em `e03c086bcd6b60e5bd60273cf2d50979775a4775`; CI pós-merge run `42083036692`, `validate=success`.
- PR #39 / RM-02 mesclado em `4052a06d530b269410f0300a8ae503e822672caa`; CI pós-merge run `42082155852`, `validate=success`.
- PR #38 / RM-01 mesclado em `725858292ecc1e3e0ad7a85a0ae9a91966d112ee`; CI pós-merge run `42080519973`, `validate=success`.
- PR #37 / RM-00 mesclado em `1ab0c25a8b0084034fb1987097bfcb6b38ccea44`; CI pós-merge run `42079838224`, `validate=success`.
- Única frente ativa: RM-07 / PR draft #44, `audit/rm07-functional-gates-20261105`. Escopo: reauditar 9 NCs e os 27 checks funcionais do PR #5.
- Proteção administrativa confirmada pelo proprietário via Termux: required check `validate`; `strict=true`; `reviews=0`; `enforce_admins=true`.
- RM-01 permanece `implementado_nao_homologado`: nenhum run `event=schedule`, hashes remotos ausentes e `ALERTA-DOC-01` aberto.
- RM-02 permanece `implementado_nao_homologado`: IGP-12/13/14 implementados por schema aditivo; integração real TEC/Qconcursos não testada.
- RM-03 permanece `implementado_nao_homologado`: E0–E4 reconstruíveis; `CURRENT.json` E0, sem evidência real.
- RM-04 permanece `implementado_nao_homologado`: ranking determinístico; pesos provisórios não calibrados.
- RM-05 permanece `implementado_nao_homologado`: prescrição sem efeitos externos; plataforma real não validada.
- RM-06 permanece `implementado_nao_homologado`: matriz 102 IDs, 42 parciais, 60 sem teste canônico; 0 cenários end-to-end PASS.
- RM-07: 9 NCs reavaliadas; 3 OPEN, 5 PARTIAL em branch candidata, 1 PARTIAL_IN_MAIN (recibo de aprovação r2 documental); 0/27 checks end-to-end PASS. GQ-D REPROVADA, GQ-C NOT_RUN, GQ-O BLOCKED.
- PR #5 está fechado sem merge. Sua branch tem 22 commits ahead e 587 behind da main atual; não fazer merge em lote.
- `state/CURRENT.json`, eventos pessoais, resultados pessoais e PDF canônico permanecem intocados.

## START desta sessão — somente API GitHub
- HEAD-base confirmado: `8fda9754846b4fba65cd88244260653cbb606720`.
- PR #5 e documentos v0.3/r2 foram lidos por SHA; a comparação de branches foi feita independentemente.
- Runs do candidato PR5: composição sintética `41952566820=success`, Spec Lean documental `41952566886=success`, harness `41952566861=success`; não são os 27 checks end-to-end.
- Main contém `approved-r2/approval-receipt.json` e `verify_approval_snapshot.py`; o recibo limita aprovação a derivação documental e registra GQ-D REPROVADA, GQ-C NOT_RUN, GQ-O BLOCKED e 0/27.
- CI pós-merge #43: run `42085633053`, `validate=success`.

## Retomada
1. Continuar somente RM-07 / PR #44 na branch declarada em `state/WORKFLOW.json`.
2. Validar matriz das 9 NCs e 27 checks; não tratar aprovação documental r2 como GQ-D ou aprovação de BUILD.
3. Não mesclar PR5 em bloco; qualquer extração deve ser por arquivo/contrato e testada no HEAD atual.
4. Após merge do relatório, manter GP-3 bloqueado e seguir somente para a próxima frente permitida pelo ROADMAP.
5. Preservar branches históricas divergentes; não apagar refs sem backup e autorização específica.

## Objetivo
Estudo UFMS cargos 523 e 324, edital 152/2026. O repositório é público; resultados individuais não são persistidos.
