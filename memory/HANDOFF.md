# HANDOFF vigente — UFMS MEU ESTUDO

## Checkpoint vigente — 06/11/2026 (reconciliação autenticada)

- Repositório: `Andraus35/UFMS-MEU-ESTUDO`; branch padrão `main`.
- `main` = `4ca27e8db66073ce8ad57b812070094d6c4dca1e`.
- PR #50 integrado; CI pós-merge run `42158000977`, conclusão `success`, no SHA acima.
- PR #51 permanece aberto na branch `docs/post-saneamento-governance-20261106`; é a única frente documental ativa identificada nesta reconciliação.
- A listagem remota contém 59 branches: 43 backups em `archive/pre-saneamento-20261105/*`, 13 refs históricas ainda fora de `archive/*`, duas refs documentais (#50 e #51) e `main`.
- As 13 branches históricas têm backups correspondentes; os 13 pares foram comparados como `identical`. A branch documental do PR #50 também recebeu backup suplementar no SHA `186f0aa289fee780d765ec410173cb402506bc67`, comparado como `identical` com a origem. Total atual: 43 backups; a fotografia original de 42 permanece preservada no inventário, com este 43º backup registrado como complemento posterior.
- O inventário registra 29 exclusões confirmadas pelo proprietário via Termux; a consulta remota confirma ausência dessas 29 refs candidatas.
- Pendências de saneamento do PR #51: corrigir a fotografia/base de classificação no inventário; definir a migração das 13 refs históricas e da ref documental do PR #50 para `archive/*`, sem perda de SHA. A branch do PR #51 continua sendo a única branch de trabalho ativa. O `state/WORKFLOW.json` já enumera as 13 referências históricas, incluindo a branch pós-squash do PR #49.
- Nenhuma branch histórica ou documental será excluída antes de validar o SHA exato do backup, verificar PRs/dependências e registrar o procedimento de retenção. A migração dos nomes originais ainda não foi executada.
- RM-06 encerrado. `state/WORKFLOW.json` aponta RM-08 como próxima tarefa, mas **RM-08 permanece formalmente bloqueado** pela baseline/gates do ROADMAP. Não iniciar implementação nem alterar baseline.
- GP-3 integral, Tutor/Coach E2E, GQ-D, GP-4 real e GP-5 não homologados. Dados pessoais, eventos pessoais, `state/CURRENT.json` e integrações reais permanecem bloqueados.
- CI verde valida apenas os checks executados no SHA correspondente; não substitui auditoria nem homologação de gates.
- Esta reconciliação foi feita pela API GitHub. Hooks locais `bootstrap`, `before_write`, `after_write` e `checkpoint` não foram executados; não declarar equivalência com execução local.

---

## Registro histórico — checkpoints anteriores a 06/11/2026

Os registros abaixo são históricos e não representam o estado vigente. Para retomada, prevalece exclusivamente o checkpoint vigente no topo deste arquivo.

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
