# HANDOFF vigente — UFMS MEU ESTUDO

**Checkpoint 05/11/2026.** Fonte operacional: `state/WORKFLOW.json` e leitura autenticada do GitHub.

## Estado confirmado
- Repositório público; `main` protegida com check obrigatório `validate`. Resultados pessoais permanecem bloqueados em eventos/projeções. Não gravar tokens, resultados individuais ou relatórios privados.
- PRs integrados: #9/SIM-04 (`7942771aea289afd4eab483c0a89d8144425966b`), #19/SIM-01 (`fefc821fe79333eedcd5a0dcb2fbedcf8ce0b56e`), #20/SIM-02 (`05c1900a09b4199d828fa20fbb73a17bec278119`), #21/SIM-03 (`9a10c86999c191f2bd5df8a1ceeb8d6f4da25c02`). CI pós-merge #21: **302 testes, success**, gate `awaiting_next_task=SIM-05`.
- Única frente: **SIM-05 / PR #22**, branch `audit/sim05-broker-reconciliation-20261105`, base `main`. Audita branches históricas #11/#12/#14/#15. Nenhuma branch histórica será mesclada em lote.
- Broker atual em `main`: `scripts/agent_entrypoint.py` com `ReadOnlyAgentBroker`, papéis de estudo e engenharia, START 4/5 arquivos, SHA confiável, checkout limpo, contexto/hash e bloqueio de escrita. Não é runtime universal e não intercepta clientes que o ignorem.
- Branches #11/#15 contêm implementação antiga: 10 arquivos mandatórios, regras RM-00..10, método/API `AgentBroker` e testes de composição que dependem de métodos ausentes na versão atual. Essa versão conflita com simplificação proporcional e com o bootstrap vigente; não copiar sobre a main. Branches #12/#14 têm snapshots de estado e handoffs obsoletos (main antiga, PRs antigos e fila ultrapassada), sem ganho funcional que justifique importação literal.
- Resultado SIM-05: manter código principal atual; registrar decisão e comparação, e somente acrescentar contraprovas se cobrirem lacuna ainda não testada. Refs históricos permanecem preservados.
- Próxima tarefa SIM-06 só depois do merge comprovado do PR #22; candidatos seguintes serão especificação cognitiva #5 (27 provas funcionais ainda pendentes) e demais branches, após auditoria de escopo. Oracle/Telegram/Calendar não homologados; monitor FAPEC é somente leitura e não tem execução agendada real comprovada.

## Retomada
1. Ler `AGENTS.md`, `ROADMAP.md`, `memory/HANDOFF.md`, `state/CURRENT.json` no mesmo HEAD; engenharia também lê `state/WORKFLOW.json` e executa `python scripts/bootstrap.py --mode engineering`.
2. Conferir PR único, HEAD e CI remota. Não avançar sem merge confirmado.
3. Para SIM-05, revisar diff/nota de reconciliação e suíte completa; assegurar que não reintroduziu bootstrap de 10 arquivos, gates por mensagem ou credenciais externas.
4. Preservar branches antigas até concluir a recuperação seletiva; não apagar dados nem branches por conveniência.

## Objetivo
Estudo UFMS cargos 523 e 324, edital 152/2026. Fonte, índices e chunks consultados sob demanda; resultados pessoais não persistidos no repositório público.
