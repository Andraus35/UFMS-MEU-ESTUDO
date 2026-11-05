# HANDOFF vigente — UFMS MEU ESTUDO

**Checkpoint 05/11/2026.** Fonte operacional: GitHub autenticado + `state/WORKFLOW.json`. Repositório público; resultados pessoais permanecem bloqueados.

## Estado confirmado
- `main` = `7ad47beb76adae46a6abf44c7b14bcb5b04fd301`.
- PR #29 / SIM-03 mesclado em `7ad47beb76adae46a6abf44c7b14bcb5b04fd301`; branch `fix/sim03-fapec-cli-e2e-20261105`.
- CI do HEAD do PR: run `42068807594`, `validate=success`; CI pós-merge: run `42069852620`, `validate=success`, **320 testes**.
- PRs abertos no momento da retomada: zero. Nenhuma branch histórica foi apagada.
- SIM-03 adicionou prova CLI offline FAPEC para códigos 0/2/3 e não mutação dos arquivos canônicos. O cron real permanece **NOT_VERIFIED** até run com `event=schedule`; a sonda cobre uma página FAPEC.
- Única frente seguinte: SIM-06 / `fix/sim06-handoff-reconciliation-20261105`. Objetivo: resumir o estado vigente no topo, separar histórico imutável e testar retomada usando somente AGENTS, ROADMAP, HANDOFF e CURRENT.
- Próxima tarefa após SIM-06: SIM-07. SPEC Cognitive Gates r2 permanece documental: 0/27 provas funcionais E2E; GQ-D REPROVADA, GQ-C NOT_RUN, GQ-O BLOCKED.
- `state/CURRENT.json`, eventos, resultados pessoais e PDF canônico permanecem intocados.

## START desta sessão — somente API GitHub
- HEAD confirmado: `7ad47beb76adae46a6abf44c7b14bcb5b04fd301`.
- `AGENTS.md`: `047176c3a21befc6c1f85612e85a32f7d380ba69`; `ROADMAP.md`: `9fa088cf5f8a2c833b6f1e52678e7d5d50933066`; `memory/HANDOFF.md`: `e945a44c96720c55ea2ca65a1d02599cbbb411e5`; `state/CURRENT.json`: `f2df048a2bf5ffa4876298a4ebf66bed1767c45a`; `state/WORKFLOW.json`: `43726795f87f30c8960286395b64a1dfa79d02b1`.
- `settings.json` confirma `personal_results_writes_enabled=false`.
- Limite: sessão via API, sem checkout local; bootstrap e hooks locais não foram executados. CI remota é evidência do checkout remoto, não equivalência aos hooks locais.

## Retomada
1. Continuar somente SIM-06 na branch declarada em `state/WORKFLOW.json`.
2. Manter um PR draft aberto; validar CI no HEAD exato e os quatro arquivos mínimos.
3. Mesclar somente com check obrigatório verde e SHA esperado.
4. Após merge, confirmar novo HEAD, CI pós-merge e zero PRs abertos.
5. Preservar branches históricas; exclusão exige backup e pedido específico.

## Objetivo
Estudo UFMS cargos 523 e 324, edital 152/2026. O repositório é público; resultados individuais não são persistidos.
