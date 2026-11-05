# Recuperação seletiva das branches históricas — 05/11/2026

**Fonte operacional:** `state/WORKFLOW.json`, PRs e SHAs autenticados do GitHub. Referência de base da inspeção: `main@7942771aea289afd4eab483c0a89d8144425966b`. O repositório está **público**. Este inventário não autoriza importação indiscriminada, merge, implantação ou escrita de resultados pessoais.

## Regra da reconciliação

Uma tarefa → branch nova desde a `main` → PR draft → diferença seletiva → testes negativos e CI no SHA exato → revisão → merge → próxima tarefa. Os refs históricos são **fontes de recuperação, não PRs ativos**. Recuperar arquivos compatíveis mediante cópia/cherry-pick seletivo; jamais mesclar árvores divergentes em bloco sem prova de equivalência. Não apagar branches exclusivas antes da integração e da auditoria.

## Branches preservadas e destino

| Branch | SHA abreviado | Comparação contra main | Tratamento |
| --- | --- | --- | --- |
| `docs/roadmap-required-bootstrap-20261104` | `b07880dc` | Ancestral de main | **Já integrada no PR #9**. Não reintegrar |
| `audit/governance-document-reconciliation-20261104` | `36e81390` | Divergente, 4 commits exclusivos | Base documental. Extrair apenas contratos atuais, sem restaurar handoff antigo |
| `audit/compose-roadmap-document-reconciliation-20261105` | `ae8edf3a` | Divergente, 6 commits exclusivos | Composição anterior; comparar com a versão posterior do broker |
| `security/agent-entrypoint-failclosed-20261104` | `c7213f1a` | Divergente, 10 commits exclusivos | Parte útil do broker já reimplementada na main; comparar testes remanescentes |
| `security/compose-agent-broker-roadmap-20261105` | `e3a32b92` | Divergente, 7 commits exclusivos; descendente de audit/compose | Consolidar com o broker read-only já vigente, sem duplicação nem liberar credenciais |
| `fix/api-write-draft-pr-preflight-20261105` | `27024250` | Divergente, 2 commits exclusivos | Ancestral da cadeia API; não integrar isoladamente |
| `audit/postcommit-exact-diff-20261105` | `53890943` | Divergente, 3 commits exclusivos | Intermediária da cadeia API; não integrar isoladamente |
| `fix/api-postcommit-content-bound-20261105` | `daec1f62` | Divergente, 11 commits exclusivos | **SIM-02**: examinar candidato terminal da cadeia #13→#17→#18, contraprovar ACK perdido, SHA/CAS e readback |
| `spec/ufms-cognitive-gates-verify-d-20261104` | `0db458a5` | Divergente, 1 commit exclusivo | Ancestre da SPEC; não integrar isoladamente |
| `spec/ufms-cognitive-gates-gqd-correction-v0-3` | `9f1b347e` | Divergente, 22 commits exclusivos | SPEC/GP: auditar especificação e 27 provas antes de integração; não confundir documento com motor operante |
| `automation/fapec-readonly-schedule-20261105` | `fd0a8182` | Divergente, 1 commit exclusivo | **SIM-03**: workflow de monitoramento somente leitura, checar falsos negativos, limites e cronograma |
| `audit/trusted-governance-p0-20261104` | `9e928a31` | Divergente, 44 commits exclusivos | Grande implementação de App/check externo; **não importar automaticamente** para projeto pessoal; revisar necessidade proporcional |
| `feature/oracle-telegram-calendar-bridge` | `757e61c7` | Divergente, 21 commits exclusivos | Integração de infraestrutura e credenciais externas; exigir isolamento, privacidade e ensaio E2E antes da integração |

## Ordem controlada

1. **SIM-01**: reconciliar a visibilidade pública, guardas de dados pessoais e documentos que ainda falam do PR #9 no presente; testes negativos para vazamentos no estado projetado. Nenhuma branch antiga deve substituir `settings.json` ou o bloqueio já vigente.
2. **SIM-02**: aproveitar a candidata terminal `fix/api-postcommit-content-bound-20261105` após análise de diferença e regressão, sem mesclar intermediárias.
3. **SIM-03**: verificar e incorporar, se aprovado, o agendamento FAPEC somente leitura.
4. **Broker/documentação**: fazer diff funcional das branches de auditoria/segurança contra `scripts/agent_entrypoint.py`; importar somente contraprovas ou documentos atuais.
5. **Cognitive gates e integração Oracle/Telegram**: aplicar requisitos de dados/credenciais/E2E e mínimo necessário à finalidade pessoal. Trabalho exclusivo não aproveitado permanece no Git.

## Evidência, limites e proteção

As relações de ancestralidade e as contagens acima foram lidas da API GitHub nesta data; números não são gates permanentes. A CI de uma branch antiga **não** valida seu código reintroduzido na `main` atual. Repositório público, sem resultados individuais, tokens ou relatórios pessoais. Nunca usar token GitHub dentro do prompt de modelo ou comprometer a regra de um PR ativo.
