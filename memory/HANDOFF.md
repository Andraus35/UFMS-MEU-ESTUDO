# HANDOFF vigente — UFMS MEU ESTUDO

## Checkpoint de retomada — 06/11/2026 (API GitHub)

- `main` = `50ced2966293f0e714fed8a9325f83a4dd79cc09` (squash merge do PR #49 / RM-06 GP-3-MVP8).
- PR #49: fechado com merge; HEAD `530a06c69ce3e2e9400e5f85673c93172b688ea9`; CI run `42096451811`, job `validate=success`. Isso valida a suíte/contratos executados, não homologa GP-3 integral, Tutor/Coach E2E ou GQ-D.
- PR #50: reaberto; único PR aberto; base `main`; branch `docs/saneamento-inventario-branches-20261105`.
- CI run `42102466006` falhou no `single_flow_gate.py --remote` porque `state/WORKFLOW.json` ainda declarava PR #49 como ativo. A transição foi corrigida no commit `f33572255603056e6e53ad7d0d0d4a17fe6b5bc1`; CI desse commit `42154123481=success`.
- A tentativa seguinte alterou indevidamente a linha-base formal de RM-08. CI run `42154172514` falhou em `roadmap_gate.py` com `Mudança estratégica exige baseline auditada: RM-08`. A baseline formal foi restaurada para `bloqueado`; o escopo offline sintético foi registrado como preparação limitada, sem promoção de status, no commit `2324741e19bc14442f7eeaa13c0c0a9bf28ee0e0`.
- CI após a restauração da baseline: run `42154286076` no commit `60265c2ccb2ad8ed5795c882c220f0f71b3ca6df`, job `validate=success`; todos os passos, inclusive `roadmap_gate`, `single_flow_gate`, testes unitários e benchmarks, concluíram com sucesso. O PR #50 continua aberto e não foi mesclado. Revisão do diff concluída: somente `state/WORKFLOW.json`, `ROADMAP.md`, `memory/HANDOFF.md` e o inventário foram alterados; nenhum código funcional ou branch foi removido. A linha formal RM-08 permanece `bloqueado`; preparação offline sintética é o único escopo futuro autorizado após o PR #50. Próxima decisão: autorização explícita para merge do PR #50; não mesclar automaticamente.
- Inventário: 42 branches originais, 42 backups verificados 42/42 idênticos; 29 branches sem commits exclusivos; 13 com histórico exclusivo; nenhuma branch excluída. Preservar as 13 históricas e não excluir as 29 sem autorização específica.
- Após merge do PR #50, iniciar RM-08 somente no recorte offline sintético. GP-4 real, persistência de dados pessoais, integrações externas e homologação permanecem bloqueados.
- `state/CURRENT.json`, eventos pessoais e resultados individuais permanecem intocados. Esta retomada foi feita pela API GitHub; hooks locais `bootstrap`, `before_write` e `after_write` não foram executados e não devem ser declarados como executados.


**Checkpoint histórico 05/11/2026.** Fonte operacional atualizada no bloco de retomada acima: GitHub autenticado + `state/WORKFLOW.json`. Repositório público; resultados pessoais permanecem bloqueados.

## Estado confirmado
- `main` = `e5560d452e2cf3ddb1c4e8cc8d6594a4c1cb96f2` (PR #48 / fechamento documental RM-07).
- PR #43 / RM-06 mesclado em `8fda9754846b4fba65cd88244260653cbb606720`; CI pós-merge run `42085633053`, `validate=success`.
- PR #45 / RM-07 gateway offline mesclado em `d559f5a7789bf7a85d577bf606cc38baa48049f8`; CI pós-merge run `42088288929`, `validate=success`.
- PR #46 / RM-07 source/fact gates e renderer local mesclado em `f64fb3f538ac34c83202565b2fc7b6c6e25f5757`; CI pós-merge run `42089150563`, `validate=success`.
- PR #47 / RM-07 composição por SHA e verificador documental r2 mesclado em `8107e3dff1b96354aedbd629ffb0cc8519859816`; CI pós-merge run `42092410857`, `validate=success`.
- PR #42 / RM-05 mesclado em `4425939488bb39291adf63184e33a132c6b461b3`; CI pós-merge run `42084811834`, `validate=success`.
- PR #41 / RM-04 mesclado em `3cbe6ffe74babf9f778216c52596994830e64143`; CI pós-merge run `42083859206`, `validate=success`.
- PR #40 / RM-03 mesclado em `e03c086bcd6b60e5bd60273cf2d50979775a4775`; CI pós-merge run `42083036692`, `validate=success`.
- PR #39 / RM-02 mesclado em `4052a06d530b269410f0300a8ae503e822672caa`; CI pós-merge run `42082155852`, `validate=success`.
- PR #38 / RM-01 mesclado em `725858292ecc1e3e0ad7a85a0ae9a91966d112ee`; CI pós-merge run `42080519973`, `validate=success`.
- PR #37 / RM-00 mesclado em `1ab0c25a8b0084034fb1987097bfcb6b38ccea44`; CI pós-merge run `42079838224`, `validate=success`.
- Única frente ativa: PR #49 / RM-06 GP-3-MVP8, `docs/gp3-personal-mvp-8-20261105`. O recorte seleciona oito testes canônicos existentes; os outros 94 cenários permanecem no backlog. GP-3 integral não é homologado. Após merge, RM-08 pode iniciar como ciclo offline sintético, sem dados pessoais nem integração real.
- Proteção administrativa confirmada pelo proprietário via Termux: required check `validate`; `strict=true`; `reviews=0`; `enforce_admins=true`.
- RM-01 permanece `implementado_nao_homologado`: nenhum run `event=schedule`, hashes remotos ausentes e `ALERTA-DOC-01` aberto.
- RM-02 permanece `implementado_nao_homologado`: IGP-12/13/14 implementados por schema aditivo; integração real TEC/Qconcursos não testada.
- RM-03 permanece `implementado_nao_homologado`: E0–E4 reconstruíveis; `CURRENT.json` E0, sem evidência real.
- RM-04 permanece `implementado_nao_homologado`: ranking determinístico; pesos provisórios não calibrados.
- RM-05 permanece `implementado_nao_homologado`: prescrição sem efeitos externos; plataforma real não validada.
- RM-06 permanece `implementado_nao_homologado`: matriz 102 IDs, 42 parciais, 60 sem teste canônico; 0 cenários end-to-end PASS.
- RM-07: após PR #45/#46, 9 NCs: 1 OPEN, 6 PARTIAL_IN_MAIN, 2 PARTIAL_CANDIDATE_NOT_MAIN; 0/27 checks end-to-end PASS. GQ-D REPROVADA/PENDENTE DE REAUDITORIA, GQ-C NOT_RUN, GQ-O BLOCKED. PR #47 acrescenta integridade de composição; não promove nenhum gate.
- PR #5 está fechado sem merge. Sua branch tem 22 commits ahead e 587 behind da main atual; não fazer merge em lote.
- `state/CURRENT.json`, eventos pessoais, resultados pessoais e PDF canônico permanecem intocados.

## START desta sessão — somente API GitHub
- HEAD-base confirmado para PR #49: `e5560d452e2cf3ddb1c4e8cc8d6594a4c1cb96f2`.
- PR #5 e documentos v0.3/r2 foram lidos por SHA; a comparação de branches foi feita independentemente.
- Runs do candidato PR5: composição sintética `41952566820=success`, Spec Lean documental `41952566886=success`, harness `41952566861=success`; não são os 27 checks end-to-end.
- Main contém `approved-r2/approval-receipt.json` e `verify_approval_snapshot.py`; o recibo limita aprovação a derivação documental e registra GQ-D REPROVADA, GQ-C NOT_RUN, GQ-O BLOCKED e 0/27.
- CI pós-merge #43: run `42085633053`, `validate=success`.

## Retomada
1. Continuar somente RM-06 / PR #49 na branch declarada em `state/WORKFLOW.json`.
2. Validar os oito testes do GP-3-MVP8 na CI; não tratar isso como homologação dos 102 cenários, GP-3 integral ou GQ-D.
3. Não mesclar PR5 em bloco; qualquer extração deve ser por arquivo/contrato e testada no HEAD atual.
4. Após merge do relatório, manter GP-3 bloqueado e seguir somente para a próxima frente permitida pelo ROADMAP.
5. Preservar branches históricas divergentes; não apagar refs sem backup e autorização específica.

## Objetivo
Estudo UFMS cargos 523 e 324, edital 152/2026. O repositório é público; resultados individuais não são persistidos.

## Recorte GP-3 para uso pessoal

- Documento: `docs/pedagogia/GP3_MVP_PESSOAL_8_20261105.md`.
- Oito testes canônicos sintéticos reutilizados; nenhum teste duplicado ou framework novo.
- 94 cenários ficam em backlog. GP-3 integral, GP-4 real e GP-5 não são promovidos.
- `state/CURRENT.json`, eventos e resultados pessoais não foram alterados.
