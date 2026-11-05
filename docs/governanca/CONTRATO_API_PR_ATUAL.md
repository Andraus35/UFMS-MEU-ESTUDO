# SIM-02 — contrato de escrita GitHub API (candidata PR #20)

**Situação:** integração seletiva proposta, não implantada como gateway universal. Código recuperado da branch `fix/api-postcommit-content-bound-20261105` (SHA `daec1f626c0bf43a22a565eaac3a290bc71f83c5`), descendente dos trabalhos legados #13→#17→#18. Nenhum write real está habilitado ou executado pela CI.

## Limites e objetivos

1. `scripts/api_write_guard.py` valida propostas de escrita em PRs **draft abertos**, no repositório exato, com base `main`, branch de trabalho permitida e HEAD coerente. Não aceitar PR #1 fixo; qualquer número positivo precisa ser conferido remotamente.
2. `check_authenticated_proposal` confere por leitura autenticada GitHub: PR, branch, base, SHA do HEAD e versão dos arquivos, inclusive 404 em `create`. Falhas 403/429, dados incompletos, concorrência e divergência bloqueiam.
3. Cada arquivo requer SHA-1 do objeto Git blob do **conteúdo final exato**, computado em host confiável a partir dos bytes efetivamente enviados. O readback confere commit descendente, delta exato, caminhos, operações e SHA de cada blob no novo HEAD.
4. `scripts/api_write_transaction.py` só escreve em host confiável e com `UFMS_ENABLE_GITHUB_WRITE=1` + `GH_TOKEN` fora do LLM. Cria blobs, árvore, commit e atualiza ref por PATCH `force=false`. Um conflito ou atualização sem confirmação **não** autoriza retry cego: `UnconfirmedWrite` obriga reconciliação autenticada.
5. O retorno permanece `ci_verified=false`, `merge_authorized=false`. Exige-se CI separada no SHA final e revisão de segurança. Cliente com acesso direto a token pode ignorar o guard: **não declarar enforcement universal**.

## Invariantes permanentes

- Nunca habilitar resultados pessoais/estatísticas individualizadas no repositório público; `settings.json` mantém `personal_results_writes_enabled=false`, e `scripts/write_policy.py` bloqueia `state/CURRENT.json` e `state/PROGRESS.csv` com resultados.
- Rotas `state/`, `edital/`, `rules/`, `guardrails/`, `.github/`, segredos, políticas e settings não são graváveis pela escrita API ordinária.
- Nenhum token aparece em arquivos, mensagens de PR ou no contexto do Tutor/Coach; simulações de teste usam fake GET/WRITE e não trafegam para o GitHub.

## Verificação e rastreabilidade

Testes: `tests/test_api_write_guard.py`, `tests/test_api_write_guard_remote.py`, `tests/test_api_write_transaction.py` e suíte de regressão `python -m unittest discover -s tests -v`. A homologação deste código como operação **real** depende de executor confiável, instalação com credenciais segregadas e contraprovas E2E; o PR #20 integra somente a biblioteca e testes. O código dos PRs históricos continua preservado pelos seus refs Git até reconciliar as dependências.

**Próxima frente após o merge confirmado do PR #20:** SIM-03 — monitoramento FAPEC somente leitura, recuperando seletivamente a branch histórica `automation/fapec-readonly-schedule-20261105`.
