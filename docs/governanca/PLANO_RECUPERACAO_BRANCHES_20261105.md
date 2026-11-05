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

 
## Atualização após SIM-01 a SIM-05 — 05/11/2026

**HEAD de referência atual:** `main@9a10c86999c191f2bd5df8a1ceeb8d6f4da25c02`; PR #19, #20 e #21 mesclados; PR #22 é a única frente ativa. O inventário acima é a fotografia inicial e suas descrições de SIM-02/SIM-03 e estado dos PRs estão históricas.

- `fix/api-postcommit-content-bound-20261105` (#18): recuperada seletivamente em SIM-02/PR #20; CI pós-merge 294 testes. Escrita real continua opt-in e não implantada.
- `automation/fapec-readonly-schedule-20261105` (#16): recuperada em SIM-03/PR #21; CI pós-merge 302 testes. Workflow somente leitura, execução agendada real ainda não comprovada.
- `security/agent-entrypoint-failclosed-20261104` (#11) e `security/compose-agent-broker-roadmap-20261105` (#15): **não mesclar**. O broker read-only atual já está na main; a versão histórica usa 10 documentos, regras RM rígidas e API antiga. Os testes de composição dependem de métodos que não existem no broker atual. Reimplementar esses métodos sem caso de uso demonstrado aumentaria escopo e regressaria a simplificação.
- `audit/governance-document-reconciliation-20261104` (#12) e `audit/compose-roadmap-document-reconciliation-20261105` (#14): **não copiar snapshots**. Status/handoff referem main `676dd5d...`, PRs #1–#14 e branches já mescladas/fechadas; são registros históricos, não estado atual. Conteúdo útil de autonomia proporcional já está presente em ROADMAP/OPERACAO da main.
- Decisão SIM-05: preservar as quatro branches, documentar a não reintegração por obsolescência e verificar que os testes atuais cobrem o broker vigente. Não é merge de branches #11/#12/#14/#15; é saneamento da fila para não reinserir código/documentos piores.
- Próxima recuperação potencial: SPEC cognitiva (#5), após definir quais dos 27 checks ainda são requisitos atuais e quais conflitam com a liberdade cognitiva; não importar gates de aprovação por mensagem. Oracle/Telegram/Calendar segue diferido.

A fotografia atual prevalece sobre qualquer tabela ou snapshot acima, e deve ser revalidada pela API GitHub em cada novo ciclo.

 
### Atualização SIM-06 / SIM-07 — 05/11/2026

- SPEC #5: PLAN v0.3-r2 e 27 CHECKS foram recuperados como especificação/documentação em SIM-06/PR #23. Não foi integrado motor funcional. Estado preservado: 0/27 E2E, GQ-D REPROVADA, GQ-C NOT_RUN, GQ-O BLOCKED; r3 não aprovada.
- Trusted Governance #10 (`audit/trusted-governance-p0-20261104`): candidata SIM-07/PR #24. Decisão de não instalar/importar App/Oracle, scripts, workflows ou segredos: a própria ADR reconhece check verde obsoleto por até sete dias e impossibilidade de revogação imediata com checker assíncrono. Não há implantação nem E2E. Preservar branch para referência.
- Próxima SIM-08: auditar `feature/oracle-telegram-calendar-bridge` (#3), sem presumir autorização para instalar serviços ou credenciais.
