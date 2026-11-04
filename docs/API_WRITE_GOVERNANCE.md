# P0 — Escritas por API, proteção de `main` e limites do gate

> **ATUALIZAÇÃO DE ESTADO — 04/11/2026 (vigente):** PR #1 foi mesclado à `main`; a descrição abaixo do PR #1 como draft é **histórica**. O PR #9 está aberto como draft, sujeito a auditoria. A API confirma `main.protected=true` e o check `validate` obrigatório. O adaptador `scripts/api_write_guard.py` continua limitado explicitamente ao **PR #1** e rejeita caminhos de governança; **não serve como autorização genérica para o PR #9**. Este último utiliza revisão humana/PR/CI e readback do HEAD, mas **não recebe atestado de preflight pelo adaptador legado**. Não alterar os bloqueios silenciosamente: uma revisão específica desse contrato deve tratar a generalização futura.


**Status:** mitigação em PR #1 draft; **não homologado como controle preventivo universal**. O repositório está **público** na verificação autenticada de 04/11/2026; o Project #2 é painel opcional e não substitui eventos versionados. Escritas pessoais permanecem bloqueadas.

## Modelo de ameaças e garantias reais

1. **Agente cooperativo com acesso à API.** Pode executar `scripts/api_write_guard.py` como pré-validação lógica ou reproduzir seu contrato antes de enviar uma proposta. Confirma branch de trabalho, PR #1 draft, HEAD exato observado, caminhos permitidos e SHA de blob para atualização. A leitura da API precisa ser **autenticada, recente e independente dos valores enviados pelo próprio agente**.
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

**Situação atual:** o repositório está **público** e `main` foi observada com `protected=false` em 04/11/2026. A integração GitHub recebeu 403 ao consultar o endpoint administrativo de proteção; isso não prova impossibilidade de configurar proteção como proprietário. A restrição de rulesets em repositórios privados no plano Free não deve ser aplicada indevidamente ao repositório público atual. O proprietário deve avaliar e habilitar as proteções disponíveis e confirmar por readback antes de declarar a `main` protegida. Em qualquer visibilidade, resultados pessoais seguem bloqueados até revisão de privacidade e autorização própria.

Quando o plano permitir, configurar administrativamente e comprovar por readback: exigência de PR, revisão humana, status check `validate` do GitHub Actions, bloqueio de force-push e exclusão, restrição de push direto e bypass mínimo. O proprietário deverá autorizar qualquer mudança administrativa; **não presumir que `mergeStateStatus=CLEAN` equivale a aprovação humana ou proteção efetiva.**

**Gate pendente:** controle administrativo GitHub realmente aplicado em `main`, mais integração mandatória do preflight a cada cliente de escrita. Até lá, o risco de bypass por API permanece aberto e é reportado como tal.

## Comandos de diagnóstico somente leitura no Windows CMD

```bat
gh pr view 1 -R Andraus35/UFMS-MEU-ESTUDO --json headRefOid,isDraft,mergeStateStatus,statusCheckRollup
gh api repos/Andraus35/UFMS-MEU-ESTUDO/branches/main --jq ".commit.sha"
gh api repos/Andraus35/UFMS-MEU-ESTUDO/actions/permissions/workflow
```

Não executar `gh pr merge`, `gh api -X PUT` de proteção, `gh api -X PATCH` de políticas ou `git push --force` nesta etapa.
