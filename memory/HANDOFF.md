# HANDOFF vigente — UFMS MEU ESTUDO

**Checkpoint:** 05/11/2026. A autoridade operacional é `state/WORKFLOW.json` verificada contra o GitHub; este handoff é um resumo. Histórico preservado em `memory/HANDOFF_ARCHIVE_2026-11-05.md`.

## Estado de trabalho e integração

- `Andraus35/UFMS-MEU-ESTUDO` permanece **público**, com `main` protegida pelo check `validate`. **Proibida** persistência de desempenho individual, CPF, exports e credenciais. `settings.json` mantém `personal_results_writes_enabled=false`.
- **Ciclo anterior:** SIM-04 / PR #9 foi mesclado em `7942771aea289afd4eab483c0a89d8144425966b`; CI pós-merge passou com 238 testes e o gate remoto declarou `awaiting_next_task`.
- **Ciclo atual:** SIM-01 / PR **#19 draft**, única branch `fix/sim01-privacy-integration-20261105`; objetivo é fechar lacunas de privacidade e organizar a recuperação das 13 branches históricas remanescentes. A próxima tarefa é **SIM-02, apenas após merge comprovado do PR #19**.
- **Recuperação histórica:** ler `docs/governanca/PLANO_RECUPERACAO_BRANCHES_20261105.md` (13 branches, 12 com histórico exclusivo). Cadeia API #13→#17→#18 candidata a SIM-02; FAPEC #16 candidata a SIM-03; broker/docs e SPEC/Oracle exigem reconciliação seletiva. A branch do PR #9 já é ancestral da main. Não fazer merges brutos de refs divergentes.
- **Alterações SIM-01:** proibir resultados em eventos e também em `state/CURRENT.json` e `state/PROGRESS.csv` sem depender de id do evento. Criar contraprovas de contagens, revisões e dados de resultado; não habilitar dados pessoais.
- **Limites:** checks de CI não provam ferramentas externas implantadas, leitura semântica por LLM ou autenticação administrativa completa. O broker vigente é somente leitura.

## Retomada e entrega

1. **START:** conferir a revisão exata e ler `AGENTS.md`, `ROADMAP.md`, `memory/HANDOFF.md`, `state/CURRENT.json`. Para engenharia, ler `state/WORKFLOW.json` e executar `python scripts/bootstrap.py --mode engineering`; CI verifica `python scripts/single_flow_gate.py --remote`.
2. **Um ciclo de cada vez:** continuar somente SIM-01 / PR #19; PRs legados fechados não são frentes de trabalho. Verificar GitHub antes de qualquer escrita.
3. **Testes e readback:** regressão focada `tests/test_write_policy.py`, casos negativos, suíte completa `validate`, CI do HEAD final, comparação do diff e verificação de privacidade.
4. **Merge:** somente depois de revisão, gates e autorização cabível. Na `main`, o gate deve comprovar `merged_at` do PR #19 e ausência de PRs abertos antes de permitir iniciar SIM-02.
5. **Estudo:** cargos 523 e 324; `state/CURRENT.json` ainda sem resultados individuais. Usar índices/chunks do edital de 152/2026 e manter monitoramento de retificações como frente futura. Não afirmar integração Zapia/Oracle/Calendar pronta.
