# P0 — Escritas por API, proteção de `main` e limites do gate

> **ATUALIZAÇÃO DE ESTADO — 04/11/2026 (vigente):** PR #1 foi mesclado à `main`; a descrição abaixo do PR #1 como draft é **histórica**. O PR #9 está aberto como draft, sujeito a auditoria. A API confirma `main.protected=true` e o check `validate` obrigatório. O adaptador `scripts/api_write_guard.py` continua limitado explicitamente ao **PR #1** e rejeita caminhos de governança; **não serve como autorização genérica para o PR #9**. Este último utiliza revisão humana/PR/CI e readback do HEAD, mas **não recebe atestado de preflight pelo adaptador legado**. Não alterar os bloqueios silenciosamente: uma revisão específica desse contrato deve tratar a generalização futura.


**Status atual:** adaptador legado de PR #1 incorporado à `main`; **não homologado como controle preventivo universal**; o PR #9 foi mesclado, mas não transformou esse adaptador em enforcement externo. O repositório está **público** na verificação autenticada de 04/11/2026; o Project #2 é painel opcional e não substitui eventos versionados. Escritas pessoais permanecem bloqueadas.

## Modelo de ameaças e garantias reais

1. **Agente cooperativo com acesso à API.** Pode executar `scripts/api_write_guard.py` apenas nas hipóteses do contrato legado, que exige literalmente PR #1 aberto em draft. **Como PR #1 já está mesclado, o adaptador atualmente não autoriza propostas novas em PR #9 ou outros PRs.** Verifica branch, SHA observado, caminhos permitidos e SHA de blob para atualização. A leitura da API precisa ser **autenticada, recente e independente dos valores enviados pelo próprio agente**.
2. **Operação fora do contrato.** Este adaptador bloqueia caminhos conhecidos de estado de estudo, edital, credenciais e governança; não analisa todo o conteúdo semântico de um arquivo permitido. Um agente pode ignorá-lo, preencher metadados falsos ou escrever por outra ferramenta. **O adaptador não intercepta GitHub, não é autorização remota, não substitui revisão humana e não impede vazamento por um arquivo permitido.**
3. **Depois da escrita.** O chamador deve conferir SHA do commit e HEAD remoto e exigir CI `success` no mesmo SHA (`check_readback`). Um resultado de CI anterior ou de outro commit não satisfaz esse requisito. Um novo commit concorrente exige reconciliação, não `force push`.
4. **CI do próprio PR.** `scripts/ci_gate_contract.py --check` inspeciona os gatilhos, permissões e etapas obrigatórias da `.github/workflows/validate.yml`. `scripts/write_policy.py --check` rejeita resultados individuais e mudança da flag de bloqueio. Contraprovas ficam em `tests/test_api_write_guard.py` e `tests/test_ci_gate_contract.py`. **Uma pessoa com escrita pode mudar o script e o workflow na mesma branch**, eliminando o controle. CI é detector *após* o push, não gate do servidor antes de registrar o commit.
5. **Fronteira de confiança.** Não guardar dados individuais, CPF, tokens, exports ou resultados reais no GitHub nesta fase; `personal_results_writes_enabled` permanece `false`. O token autenticado nunca deve ser armazenado no repositório ou exposto em logs.

## Procedimento de operação para cada mudança autorizada

1. Consultar repositório, PR, HEAD, base e blob SHA pelo GitHub autenticado; confirmar `draft=true`, `merged=false` e branch diferente de `main`.
2. Aplicar o adaptador para **propostas de rotina permitidas**. Arquivos bloqueados (incluindo `AGENTS.md`, `settings.json`, `.github/workflows/`, `rules/`, `guardrails/` e `state/`) exigem processo separado de revisão humana e auditoria independente; não reinterpretar rejeição como autorização.
3. Gravar em branch de trabalho por CAS/lease quando disponível. Se houver HTTP 409 ou HEAD divergente, parar, reler e reconciliar; nunca forçar sobrescrita.
4. Confirmar o commit exato no GitHub e o readback do conteúdo. Confirmar sucesso de **todas as verificações esperadas** para esse SHA; não inferir aprovação só por status textual sem vínculo ao commit.
5. Atualizar `memory/HANDOFF.md` com resultado efetivamente confirmado e divergências. Preservar PR em draft; nenhuma aprovação automática, merge ou habilitação de resultados privados.

## Proteção administrativa de `main`

**Situação atual (04/11/2026):** repositório **público** e `main.protected=true`, com `validate` obrigatório para todos, confirmado por leitura autenticada. O proprietário relatou `scripts/protect_main.py --check` OK no Termux. A integração GitHub recebeu 403 ao consultar o endpoint administrativo detalhado, que continua **não verificável independentemente**. Histórico: anteriormente, no mesmo dia, `main.protected=false` antes da aplicação pelo proprietário. A restrição de rulesets em repositórios privados no plano Free não deve ser aplicada indevidamente ao repositório público atual. O proprietário deve avaliar e habilitar as proteções disponíveis e confirmar por readback antes de declarar a `main` protegida. Em qualquer visibilidade, resultados pessoais seguem bloqueados até revisão de privacidade e autorização própria.

Quando o plano permitir, configurar administrativamente e comprovar por readback: exigência de PR, revisão humana, status check `validate` do GitHub Actions, bloqueio de force-push e exclusão, restrição de push direto e bypass mínimo. O proprietário deverá autorizar qualquer mudança administrativa; **não presumir que `mergeStateStatus=CLEAN` equivale a aprovação humana ou proteção efetiva.**

**Gate pendente:** a proteção administrativa já foi aplicada, mas a origem imutável dos checks e a integração mandatória do preflight a **cada cliente de escrita** não foram comprovadas. Os históricos PRs #10/#11 propuseram âncora externa e broker; somente o broker read-only mínimo do PR #9 está na main. O PR #19 trata a privacidade e o PR seguinte SIM-02 revisará a cadeia API #13/#17/#18. O risco de bypass por agentes externos permanece aberto.

## Comandos de diagnóstico somente leitura no Windows CMD

```bat
gh pr view 1 -R Andraus35/UFMS-MEU-ESTUDO --json headRefOid,isDraft,mergeStateStatus,statusCheckRollup
gh api repos/Andraus35/UFMS-MEU-ESTUDO/branches/main --jq ".commit.sha"
gh api repos/Andraus35/UFMS-MEU-ESTUDO/actions/permissions/workflow
```

Não executar `gh pr merge`, `gh api -X PUT` de proteção, `gh api -X PATCH` de políticas ou `git push --force` nesta etapa.

## Candidata de recuperação SIM-02 / PR #20 — 05/11/2026

O PR #19 foi mesclado e manteve escrita pessoal bloqueada. A candidata atual #20 recupera seletivamente o trabalho dos PRs históricos #13→#17→#18, sem retarget/rebase das branches antigas. Ver `docs/governanca/CONTRATO_API_PR_ATUAL.md`: preflight por leitura autenticada, SHA exato do blob final e transação Git com ref não forçado. A presença de código na `main` **não** habilita efeitos externos: a execução real requer opt-in, host isolado com token próprio e teste E2E. A CI mede o código com mocks e confirma `merge_authorized=false`, não prova instalação de gateway. Os parágrafos históricos acima descrevem o adaptador anterior.
