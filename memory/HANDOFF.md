# HANDOFF vigente — UFMS MEU ESTUDO

**Checkpoint:** 05/11/2026. A fonte operacional é `state/WORKFLOW.json`; este handoff é um resumo a verificar no GitHub. Histórico preservado em `memory/HANDOFF_ARCHIVE_2026-11-05.md`.

## Estado

- Repositório `Andraus35/UFMS-MEU-ESTUDO` **público**, com `main` protegida por `validate`. **Nenhum resultado individual, token ou dado privado pode ser gravado neste repositório.** `settings.json` mantém gravação pessoal desabilitada e `scripts/write_policy.py` bloqueia eventos e projeções de desempenho.
- **Integrado:** SIM-04 / PR #9 (SHA `7942771aea289afd4eab483c0a89d8144425966b`), SIM-01 / PR #19 (SHA `fefc821fe79333eedcd5a0dcb2fbedcf8ce0b56e`). Após o segundo merge, CI da `main` aprovou **244 testes** e o gate declarou `awaiting_next_task=SIM-02`.
- **Único PR ativo:** **#20, SIM-02**, branch `fix/sim02-api-write-integrate-20261105`, base `main`. Recuperação de escrita API da candidata histórica `fix/api-postcommit-content-bound-20261105` (#13→#17→#18), com readback autenticado, digest do blob final, transação sem força e rejeição de reenvio após ACK perdido.
- O escritor HTTP **não está implantado**: exige opt-in explícito `UFMS_ENABLE_GITHUB_WRITE=1`, token `GH_TOKEN` restrito somente no host confiável e revisão do fluxo. Não entregar token a Tutor/Coach/LLM. Nenhum write real é executado por teste.
- **Próxima tarefa:** SIM-03 (FAPEC, read-only) **somente após merge comprovado do PR #20**. Inventário de branches e precedência: `docs/governanca/PLANO_RECUPERACAO_BRANCHES_20261105.md`. Preservar todas as branches de commits exclusivos.
- Tutor/Coach são livres para orientar cognitivamente sem autorização por mensagem. O broker `scripts/agent_entrypoint.py` é somente leitura e ainda não é executor externo obrigatório. Integração Zapia/Oracle/Calendar não está demonstrada.

## Procedimento de retomada e entrega

1. Ler `AGENTS.md`, `ROADMAP.md`, `memory/HANDOFF.md`, `state/CURRENT.json` na mesma revisão. Engenharia também lê `state/WORKFLOW.json` e executa `python scripts/bootstrap.py --mode engineering`.
2. Conferir PRs GitHub, HEAD, `python scripts/single_flow_gate.py --remote` em CI e uma única branch/PR ativos. PR fechado sem merge não autoriza próxima tarefa.
3. Validar fluxo SIM-02 com testes adversariais em `tests/test_api_write_guard.py`, `tests/test_api_write_guard_remote.py`, `tests/test_api_write_transaction.py`; CI completa, leitura do diff e SHA exato.
4. Exigir fail-closed para HEAD obsoleto, arquivo alterado, base divergente, SHA errado, blob adicional, ACK perdido, erro 403/429, ausência de credenciais ou tentativa de escrita em `state/` e `settings.json`. Não confundir pré-validação cooperativa com autorização administrativa.
5. Somente após revisão e decisão de integração, mesclar PR #20, verificar CI na `main` e avanço para SIM-03. Não criar outra frente antes de concluir esse ciclo.

## Estudo

Cargos UFMS 523 e 324; estado projetado permanece sem resultados individuais. Edital 152/2026, índices e chunks imutáveis; retificações oficiais sob monitoramento posterior, sem correção silenciosa.
