# HANDOFF vigente — UFMS MEU ESTUDO

**Checkpoint 05/11/2026.** Fonte operacional: `state/WORKFLOW.json` e GitHub autenticado.

## Estado
- Repositório público, `main` protegida pelo check `validate`; resultados individuais, tokens e relatórios pessoais não podem ser gravados.
- PRs integrados: #9/SIM-04 (`7942771aea289afd4eab483c0a89d8144425966b`), #19/SIM-01 (`fefc821fe79333eedcd5a0dcb2fbedcf8ce0b56e`), #20/SIM-02 (`05c1900a09b4199d828fa20fbb73a17bec278119`), #21/SIM-03 (`9a10c86999c191f2bd5df8a1ceeb8d6f4da25c02`), #22/SIM-05 (`ace048a05d3a0100ef5f05884745969ff7221d83`). CI pós-merge #22: **307 testes, success**, gate `awaiting_next_task=SIM-06`.
- Única frente: **SIM-06 / PR #23**, branch `spec/sim06-cognitive-gates-r2-20261105`. Recupera apenas especificação v0.3-r2 aprovada e recibo/verificador, sem implementação do motor.
- Escopo do aceite humano: PLAN v0.3-r2 para especificação e derivação dos CHECKS; não equivale a GQD/GQC/GQO, implementação, deploy ou escrita pessoal.
- Situação registrada: **27 requisitos/checks documentais; 0/27 provas funcionais E2E; GQ-D REPROVADA; GQ-C NOT_RUN; GQ-O BLOCKED**. Há testes isolados em subconjuntos (C2/C3/C25/C26), que não são homologação E2E. Proposta r3 e seus checks preview não aprovados e não serão integrados.
- O broker atual é read-only e não impõe enforcement universal; o writer API continua inativo para escrita real; monitor FAPEC é somente leitura e execução agendada real não comprovada.
- Próxima tarefa SIM-07 somente após merge confirmado do PR #23. Branches #5, #10, #3 e #4 preservadas; avaliar depois as 27 provas, o pacote de governança confiável e a ponte Oracle/Telegram/Calendar com escopo proporcional.

## Retomada
1. START na mesma revisão: `AGENTS.md`, `ROADMAP.md`, `memory/HANDOFF.md`, `state/CURRENT.json`; engenharia inclui `state/WORKFLOW.json` e bootstrap engineering.
2. Verificar PR único, HEAD e CI remota. Sem merge confirmado, não avançar.
3. Para SIM-06, executar testes de recibo e verificador de snapshot; confirmar bytes originais, aprovação r2, 27 checks e limites do recibo. Não promover status funcional.
4. Preservar branches históricas; não importar r3, credenciais, workflow de produção ou aprovação por mensagem.

## Objetivo
Estudo UFMS cargos 523 e 324, edital 152/2026; resultados individuais não persistidos no repositório público.
