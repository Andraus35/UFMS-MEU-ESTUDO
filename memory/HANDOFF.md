# HANDOFF vigente — UFMS MEU ESTUDO

**Data:** 05/11/2026. Conferir SHA e estado remoto no GitHub antes de toda operação. Este resumo indica a próxima tarefa; não substitui validação do commit/CI.

## Estado

- **Fonte da verdade:** `Andraus35/UFMS-MEU-ESTUDO`; a `main` estava em `676dd5d3259c66ba97c3e7e3338451cfc4e5cd68` na leitura inicial, protegida pelo check `validate`. A reforma SIM está no **PR #9 draft**, ainda não mesclada.
- **Privacidade:** repositório **público**; nunca armazenar desempenho individual, CPF, relatórios reais ou credenciais. A flag `personal_results_writes_enabled` continua `false`.
- **Estudo:** cargos 523 (manhã) e 324 (tarde), prova prevista 17/01/2027, sujeito a retificações oficiais. `state/CURRENT.json` informa 0 eventos e 0 resultados no estado inicial; reler sempre no HEAD atual.
- **Edital:** transcrição integral, manifesto, índices e 81 chunks preservados; consultar somente os recortes pertinentes. A página 13 contém divergência cronológica a acompanhar. Não substituir edital original silenciosamente.
- **Integrações:** Tutor/Coach podem recomendar livremente, mas não afirmar Zapia/agenda/Oracle/Gemini operacionais sem testes E2E. PR #5 tem especificação não homologada.

## Retomada determinística de engenharia

- **Fonte única de trabalho:** `state/WORKFLOW.json`, leitura obrigatória na engenharia. Não interpretar números antigos deste handoff como estado ativo; conferir o SHA do branch e a lista de PRs aberta no GitHub.
- **Tarefa única atual:** SIM-04 (saneamento de PRs e persistência da regra), branch `docs/roadmap-required-bootstrap-20261104`, **PR #9** draft. A reforma é candidata, não integrada à `main`.
- **Próxima tarefa após merge:** SIM-01 (privacidade). Não iniciar SIM-01, SIM-02 nem nenhuma outra frente enquanto #9 continuar aberto.
- **Inventário legado:** #5, #11, #12, #13, #14, #15, #16, #17 e #18, com HEAD, branch e trabalho exclusivo preservados no `state/WORKFLOW.json`. Encerrar sem merge e manter refs históricos até recuperação sequencial; não tratar encerramento como aprovação técnica.
- **Gate de início:** `python scripts/bootstrap.py --mode engineering` deve ler quatro arquivos comuns e `state/WORKFLOW.json`, com hashes; `python scripts/single_flow_gate.py --check` confirma a frente e a CI testa `--remote`. Múltiplos PRs abertos bloqueiam o fluxo de engenharia. **Não é enforcement universal dos agentes externos**: sem executor obrigatório, uma sessão pode ignorar scripts.
- **Fechamento de ciclo:** contraprovas negativas e testes aplicáveis → CI no HEAD → readback → revisão/autorizações cabíveis → **um merge** → próxima branch/PR. Uma branch para cada correção separada é proibida.

## Regras de entrega e rastreabilidade

- Para ALTA/MEDIA: identificar causa, correção, contraprovas negativas reais, regressão, HEAD/CI e riscos remanescentes. Uma referência a teste não demonstra que ele foi executado. Não promover status antes de comprovação.
- Evitar novo PR de saneamento enquanto **PR #9** puder acomodar mudanças. Cadeias empilhadas #9→#14→#15 e #13→#17→#18 precisam ser reconciliadas, não mescladas às cegas; PR #12 pode estar incorporado em #14, mas não deve ser descartado sem verificar equivalência final.
- Não mesclar nem deletar branches por inferência; manter `main` sem alterações até a integração explicitamente autorizada. Atualizar o topo deste handoff a cada nova entrega, preservando histórico no arquivo de referência.

## Histórico preservado

O conteúdo anterior completo (sem apagamentos) está em `memory/HANDOFF_ARCHIVE_2026-11-05.md`. Decisões em `memory/DECISIONS.md`; prova independente e detalhes históricos devem ser buscados apenas sob demanda.
