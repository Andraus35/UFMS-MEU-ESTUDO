# HANDOFF vigente — UFMS MEU ESTUDO

**Checkpoint 05/11/2026.** Autoridade: `state/WORKFLOW.json` + leitura remota autenticada do GitHub. Este documento resume a frente; histórico em `memory/HANDOFF_ARCHIVE_2026-11-05.md`.

## Ciclo atual

- Repositório `Andraus35/UFMS-MEU-ESTUDO` **público**, `main` protegida por `validate`. Gravação de dados pessoais/resultados individuais continua proibida em settings, eventos e projeções `CURRENT/PROGRESS`.
- **Integrados:** PR #9 / SIM-04 (merge `7942771aea289afd4eab483c0a89d8144425966b`), PR #19 / SIM-01 (merge `fefc821fe79333eedcd5a0dcb2fbedcf8ce0b56e`), PR #20 / SIM-02 (merge `05c1900a09b4199d828fa20fbb73a17bec278119`). Pós-merge #20: CI `success`, 294 testes e gate `awaiting_next_task=SIM-03`.
- **Única frente:** SIM-03, PR **#21** draft, branch `automation/sim03-fapec-readonly-20261105`. Recupera a branch histórica `automation/fapec-readonly-schedule-20261105` (#16): agendamento FAPEC com permissão de leitura, sem gravação/revisão automática do edital.
- **Escopo de sonda:** página pública de um concurso, uma verificação por execução. Um job falho sinaliza provável mudança **ou** inconclusão, nunca comprova retificação. Cron `17 12 * * *` em UTC e `workflow_dispatch` manual; GitHub pode atrasar a execução.
- **Próxima tarefa:** SIM-05 (broker/START e documentação), somente após PR #21 realmente mesclado. Matriz de recuperação de branches: `docs/governanca/PLANO_RECUPERACAO_BRANCHES_20261105.md`.
- Código da escrita API recém-integrado permanece **desabilitado para writes reais por padrão**, requer host confiável, token fora do LLM e testes de integração externos; não ativar apenas por ter chegado à `main`. Zapia/Oracle/Calendar não homologados.

## Retomada determinística

1. **START:** mesma revisão Git para `AGENTS.md`, `ROADMAP.md`, `memory/HANDOFF.md`, `state/CURRENT.json`; na engenharia, também `state/WORKFLOW.json`, executando `python scripts/bootstrap.py --mode engineering`.
2. Conferir PR único e HEAD via GitHub; CI `python scripts/single_flow_gate.py --remote`; sem merge provado, não avançar SIM.
3. PR #21: testar `.github/workflows/monitor-fapec.yml` com `tests/test_monitor_fapec_schedule.py`; confirmar permissão read-only, nenhum token, exit 1 em resultado inconclusivo/candidato, nenhum disparo de CI por push/PR; comparar origem histórica.
4. Sem claims de serviço já implantado a partir de teste offline. Após revisão e CI `validate` no HEAD final, só mesclar mediante gate e autorização aplicável; confirmar CI da `main`, próximo SIM-05.
5. Preservar refs de branches antigas com trabalho exclusivo até recuperação funcional; não mesclar tudo em lote nem reintroduzir regras obsoletas. Nunca divulgar dados pessoais ou chaves.

## Objetivo de estudo

UFMS cargos 523 e 324; edital 152/2026 com índice e chunks. A sonda não substitui inspeção de outras fontes ou revisão normativa humana.
