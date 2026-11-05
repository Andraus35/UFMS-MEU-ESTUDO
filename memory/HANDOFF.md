# HANDOFF vigente — UFMS MEU ESTUDO

**Data:** 05/11/2026. **Este resumo não é o estado operacional.** Para qualquer trabalho de engenharia, recuperar `state/WORKFLOW.json` e verificar o GitHub no mesmo HEAD. O conteúdo histórico integral permanece em `memory/HANDOFF_ARCHIVE_2026-11-05.md`.

## Retomada em uma única frente

- **Repositório:** `Andraus35/UFMS-MEU-ESTUDO`; `main` protegida por `validate`. A visibilidade verificada é **pública**: gravação de desempenho pessoal e segredos continua bloqueada.
- **Única proposta aberta na última verificação:** PR #9, branch `docs/roadmap-required-bootstrap-20261104`, base `main`, ainda **draft e sem merge**. Não criar branch/PR adicional enquanto estiver aberto.
- **Fonte de verdade operacional:** `state/WORKFLOW.json`. Seu ciclo registrado é SIM-04 / PR #9 em fase **review**; `next_task_after_merge=SIM-01` é apenas fila futura. O campo `active` representa a **candidata anterior** após seu merge, não uma tarefa ainda em andamento na `main`.
- **Resolução obrigatória:** consultar PRs abertos no GitHub. Com #9 aberto, `active_pr`. Sem PR aberto, **somente** confirmar `awaiting_next_task` depois de consultar o PR #9 e verificar `state=closed`, `merged_at` real, head/base esperados e fase de revisão. **PR fechado sem merge, erro de API ou resultado incerto não autoriza avançar.**
- **Bootstrap:** estudo lê `AGENTS.md`, `ROADMAP.md`, este `memory/HANDOFF.md`, `state/CURRENT.json`. Engenharia lê também `state/WORKFLOW.json`; execução local `python scripts/bootstrap.py --mode engineering`, verificação remota `python scripts/single_flow_gate.py --remote`.
- **Broker:** `scripts/agent_entrypoint.py` é somente leitura, testado localmente, mas ainda **não é executor de Tutor/Coach/Zapia implantado**. Não confundir bytes verificados com leitura semântica universal.
- **Estudo:** cargos 523 e 324; `state/CURRENT.json` tem zero eventos e zero resultados no último checkpoint; consultar HEAD atual. Edital e seus 81 chunks sob demanda, com alerta de cronologia na página 13; integrações externas não comprovadas permanecem não implementadas.

## Protocolo de execução e entrega

1. **START:** ler os quatro arquivos básicos, mais `state/WORKFLOW.json` para engenharia, de uma mesma revisão. Conferir PRs, HEAD e verificações remotas antes de decisões com efeito.
2. **Somente SIM-04 no PR #9:** finalizar saneamento da transição pós-merge, referências documentais e contraprovas. Não iniciar SIM-01 antes de integrar #9.
3. **Gates:** testar PR aberto, PR fechado sem merge, merge comprovado, API indisponível, múltiplos PRs e divergência da próxima tarefa. Exigir CI `validate` e readback do commit exato; CI verde não constitui homologação externa do Tutor/Coach.
4. **Integração:** só mesclar após gates e autorização aplicável. Após merge, verificar `main` e o PR real; o estado efetivo passa a `awaiting_next_task`. O ciclo seguinte cria uma nova branch e PR somente depois disso.
5. **Arquivos históricos:** PRs #5, #11–#18 encerrados sem merge preservam SHAs no `state/WORKFLOW.json`. Branches históricas não são frentes ativas; excluir apenas com preservação e análise de dependências. Nenhuma exclusão/merge automático.
6. **Persistência:** registrar novas evidências no corpo do PR #9 e só atualizar ROADMAP/HANDOFF quando muda o significado; jamais usar uma fotografia histórica como status vigente.

## Limitações

Em acesso GitHub via API, hooks locais não são interceptadores globais. O gate de CI ocorre após o push; não bloqueia fisicamente alguém com credenciais de criar PR, fazer push ou pular o bootstrap. Não afirmar implantação externa, autorização de merge ou resultados pessoais sem evidência e readback.
