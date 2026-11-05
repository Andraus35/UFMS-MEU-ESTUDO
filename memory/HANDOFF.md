# HANDOFF vigente — UFMS MEU ESTUDO

**Checkpoint 05/11/2026.** Fonte operacional: GitHub autenticado + `state/WORKFLOW.json`. Repositório público; resultados pessoais permanecem bloqueados.

## Estado confirmado
- `main` = `1ccde9571e59dcf9e241df9ac0a32fbc8e50c73d`.
- PR #31 / SIM-07 mesclado em `1ccde9571e59dcf9e241df9ac0a32fbc8e50c73d`; CI pós-merge run `42071106275`, `validate=success`, **326 testes**.
- PRs abertos após o merge #31: zero. Nenhuma branch histórica foi apagada.
- SIM-07 adicionou política local que separa orientação NONE, rotina TOOL com consentimento por escopo e ação sensível com aprovação explícita. Não implementa Zapia nem runtime Tutor/Coach.
- Única frente: SIM-08 / `fix/sim08-ci-duplicate-gates-20261105`. Quatro comandos CI repetiam validações já executadas por `scripts/validate.py`; a mudança remove somente as repetições e reforça contraprovas para manter as chamadas consolidadas.
- Preservar CI de privacidade, roadmap, fluxo serial, START/broker, suíte de testes, benchmarks e rebuild. Próxima tarefa após SIM-08: SIM-09.
- SIM-03: cron FAPEC permanece **NOT_VERIFIED** até run com `event=schedule`; a sonda cobre uma página. SPEC Cognitive Gates r2 continua documental: 0/27 provas E2E; GQ-D REPROVADA, GQ-C NOT_RUN, GQ-O BLOCKED.
- `state/CURRENT.json`, eventos, resultados pessoais e PDF canônico permanecem intocados.

## START desta sessão — somente API GitHub
- HEAD confirmado: `1ccde9571e59dcf9e241df9ac0a32fbc8e50c73d`.
- Os quatro arquivos obrigatórios e `state/WORKFLOW.json` foram lidos no mesmo HEAD; `settings.json` confirma `personal_results_writes_enabled=false`.
- Limite: sessão via API, sem checkout local; bootstrap e hooks locais não foram executados. CI remota é evidência do checkout remoto, não equivalência aos hooks locais.

## Retomada
1. Continuar somente SIM-08 na branch declarada em `state/WORKFLOW.json`.
2. Confirmar que `validate.py` retém todas as quatro validações e a CI não as repete.
3. Testar mutantes: remover uma validação consolidada ou reintroduzir etapa duplicada deve falhar.
4. Mesclar somente com check obrigatório verde e SHA esperado.
5. Após merge, confirmar novo HEAD, CI pós-merge e zero PRs abertos.
6. Preservar branches históricas; exclusão exige backup e pedido específico.

## Objetivo
Estudo UFMS cargos 523 e 324, edital 152/2026. O repositório é público; resultados individuais não são persistidos.
