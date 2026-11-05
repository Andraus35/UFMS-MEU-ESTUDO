# HANDOFF vigente — UFMS MEU ESTUDO

**Checkpoint 05/11/2026.** Autoridade operacional: `state/WORKFLOW.json` e GitHub autenticado.

## Estado
- Repositório público; `main` protegida por check `validate`. Dados individuais, tokens e relatórios privados não podem ser gravados.
- PRs integrados: #9, #19, #20, #21, #22, #23, #24 e #27. Último merge #27: `3f9411ca00c35713f8b140df6091d92b73ed31d9`; CI pós-merge **314 testes, success**, gate `awaiting_next_task=SIM-09`.
- Única frente: SIM-09 / PR #28, branch `audit/sim09-final-branch-inventory-20261105`.
- Inventário: 20 branches de trabalho além de `main`: oito branches de PRs integrados e 12 branches históricas fechadas sem merge. Nenhuma branch foi apagada. Lista, SHAs e destinos: `docs/governanca/STATUS_BRANCHES_20261105.md`; refs diferidas: `state/WORKFLOW.json`.
- Funcionalidades recuperadas seletivamente: bootstrap START (#9), privacidade (#19), API write guard (#20; writer real inativo), monitor FAPEC (#21; cron real não comprovado), broker atual e decisões (#22), SPEC r2 documental (#23; 0/27 E2E), decisão Trusted Governance (#24), decisão de adiar ponte Oracle/Telegram (#27).
- Branches preservadas sem merge bruto: #3/#4/#5/#10/#11/#12/#13/#14/#15/#16/#17/#18. Algumas capacidades foram recuperadas por PRs mais novos; branch preservada não significa código pendente.
- Próxima tarefa SIM-10 após merge #28: revisar provas funcionais pendentes da SPEC cognitiva e escolher um recorte E2E pequeno; sem instalar Oracle, Telegram, App externa ou credenciais.

## Retomada
1. START na mesma revisão: AGENTS, ROADMAP, HANDOFF e CURRENT; engenharia inclui WORKFLOW e bootstrap engineering.
2. Confirmar PR único, HEAD, check validate e CI remota.
3. SIM-09: validar inventário contra API GitHub, conferir 20 refs, 8 merges, 12 preservadas e nenhum PR aberto paralelo.
4. Não apagar refs sem backup e pedido específico.

## Objetivo
Estudo UFMS cargos 523 e 324, edital 152/2026. O repositório é público; resultados individuais não são persistidos.
