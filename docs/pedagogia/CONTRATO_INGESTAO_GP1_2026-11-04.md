# Contrato de compatibilidade da ingestão — UFMS GP-1, ciclo 4

**Data:** 04/11/2026, America/Campo_Grande.  
**Modalidade:** diagnóstico de compatibilidade com fixtures **FICTÍCIAS** e projeto de contrato; **não é teste executado, importador implementado ou autorização de escrita**.  
**Repositório:** `Andraus35/UFMS-MEU-ESTUDO`; PR pedagógico #2, a partir de `ceb40c36a9b8e85e0bf2819786a964128260053d`.  
**HEAD técnico #1 efetivamente lido:** `42530c1680fb328fb9064235d475d2951c3a7c51`.  
**Arquivos técnicos inspecionados nesse SHA:** `scripts/core.py`, `tests/test_harness.py`, `scripts/write_policy.py`, `templates/RESULTADO.md`, `docs/OPERACAO.md`, `settings.json`, `config/topics.csv`, `scripts/api_write_guard.py`.  
**Evidência CI do HEAD:** [Validar harness — run 41819517497](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41819517497), `completed/success`. Esta CI não valida automaticamente as fixtures deste documento.

## 1. Constatações novas sem duplicar o backlog

A leitura do validador atual confirma que ele:
- valida `event_id` único, tipo permitido, timestamp com fuso e `caderno_id` para recomendação/resultado/correção;
- recusa valores negativos, incoerência `acertos + erros + nao_respondidas != total` e subtotais por tema que superem totais de respondidas, acertos ou erros;
- exige que tópicos discriminados permaneçam no conjunto recomendado, **se já existir recomendação anterior para o mesmo ID**;
- rejeita segundo `resultado_recebido` para o mesmo `caderno_id`; exige `resultado_corrigido` com `corrects_event_id` vinculando o último resultado;
- reconstrói projeções por `topic_results` informado, nunca distribuindo acertos agregados por subtópicos;
- não expõe, nesse módulo, `attempt_id`, `recommendation_id` e `platform_notebook_id` independentes.

`tests/test_harness.py` já contém testes de recomendação pendente, números, rejeição de totais, duplicidade, correção, subtotais, escopo e fuso. **Não reimplementar testes equivalentes.** Este documento detalha somente pontos de integração com o modelo v1.6–v1.7, sem mudar o número de **102 cenários pedagógicos**.

## 2. Mapeamento de identidades: estado atual vs. decisão pendente

| Conceito pedagógico | Campo técnico atual | Decisão para ENG-01/02 |
|---|---|---|
| `recommendation_id`: decisão de prescrição | `caderno_id` identifica o caderno, mas não separa recomendação e plataforma | Criar mapeamento explícito e estável, mantendo compatibilidade com eventos anteriores |
| `platform_notebook_id`: ID real TEC/Qconcursos | Não há campo específico exigido pelo validador atual | Preservar como desconhecido até informado; nunca gerar ID externo ficticiamente |
| `attempt_id`: tentativa independente | Um resultado corrente por `caderno_id`; segunda tentativa é interpretada como duplicada | Definir se nova tentativa cria uma nova entidade interna ou se haverá esquema versionado; **não** mascarar repetição como correção |
| `event_id`: mutação do histórico | `event_id` obrigatório e único | Preservar unicidade, vínculo de correções e ordenação sem reescrever eventos históricos |
| `recorded_at`: instante efetivo de registro | `timestamp` com fuso | Definir semântica formal de registro e origem do relógio; não assumir que é a data da resolução |
| `attempt_at`: instante da tentativa do estudante | Não há campo obrigatório distinto | Guardar como `unknown` se ausente; não derivar do commit ou da hora do relato |
| Cargo e subtópico | `topic_ids` e `topic_results` | Validar cargo e interseções pela fonte, sem duplicar um resultado ou presumir proficiência |

**Política de migração:** esquema novo deve explicitar versionamento, mecanismo de leitura do legado e prova de reconstrução idêntica para dados canônicos antigos. Não modificar, renumerar nem rehashar eventos anteriores para acomodar esquema novo.

## 3. Contrato mínimo de entrada e normalização

**Entrada humana:** texto/CSV/imagem legitimamente fornecido. Preservar bruto somente quando autorizado e necessário; caso contrário, anotar origem e dados mínimos. A plataforma pode usar `respondidas`, `apresentadas`, `tentativas` ou `questões resolvidas` com significados diferentes.

**Estado `PENDING_MAPPING`:** se não sabemos se `12 respondidas, 3 em branco` representa 12 exibidas ou 15 exibidas, não preencher `total=15` por suposição. Solicitar apenas a convenção necessária ou usar relato agregado com ressalva, **sem emitir evento canônico inválido**.

**Normalização admissível:** se uma fonte válida demonstrar explicitamente que `apresentadas = respondidas + não respondidas`, e corretas/erradas somarem respondidas, converter para o schema técnico, anotando convenção, origem e decisão. Preservar valores ausentes sem inventar novidade, tempo, independência ou assunto.

**Resultado por tópico:** `topic_results.attempted` significa **itens respondidos** no componente atual, não todos os apresentados; erro por tópico é `attempted - correct`. Itens em branco não devem ser debitados artificialmente a tópico quando a fonte não permite essa distribuição. Sem relatório por tema, `topic_results=[]`, e projeção por tema permanece sem tentativa observada.

**Privacidade:** o fato de `validate_events(...,allow_private=True)` aceitar fixtures em memória é **apenas uma capacidade de teste**. `scripts/write_policy.py` exige `personal_results_writes_enabled=false` e rejeita eventos pessoais; não alterar flag, nem gravar resultados reais.

## 4. Correção versus nova tentativa

- **Correção:** reinterpretação ou conserto dos dados **da mesma tentativa**, preservando `corrects_event_id` apontando para o último evento de resultado daquele caderno.
- **Nova tentativa:** resolução adicional com novo conjunto/tempo/condições, ainda que a plataforma mantenha o mesmo caderno externo. Deve ter identidade observacional própria e não substituir o resultado anterior silenciosamente.
- **Histórico de aprendizagem:** a mesma questão repetida em várias tentativas não vira evidência inédita independente. Manter novidade, ajuda e contexto se conhecidos.

O código atual atende o primeiro conceito e rejeita a segunda tentativa como segundo `resultado_recebido` do mesmo `caderno_id`. Isso é **limitação de modelagem**, não autorização para contorná-la rotulando a tentativa nova como `resultado_corrigido`.

## 5. Fixtures sintéticas auditáveis

Arquivo complementar: [FIXTURES_INGESTAO_GP1_2026-11-04.json](FIXTURES_INGESTAO_GP1_2026-11-04.json).

| Grupo | IDs | Expectativa |
|---|---|---|
| Validação canônica atual | IGP-01–IGP-11 | Entradas fictícias com `validate_events` e saídas/erros esperados; **não executadas nesta entrega** |
| Normalização e esquema futuro | IGP-12–IGP-14 | Contratos de decisões ainda pendentes, **não executáveis pelo validador atual sem nova implementação** |

Os 14 IDs **IGP** servem apenas para organizar fixtures vinculadas a **PED, CDO, PRD, FIQ e EFA existentes**; não adicionam 14 novos requisitos independentes ao catálogo de 102.

**Regras de implementação:** executar primeiro os casos atualmente suportados em ambiente isolado, sem persistência, vinculando o resultado ao SHA técnico exato. Separar resultados `PASS/FAIL` das lacunas `BLOCKED/NOT_IMPLEMENTED`. Só depois aprovar schema ou adaptador versionado.

## 6. Encaminhamento, sem interferência no PR #1

1. **ENG-01:** escolher e documentar semântica de `caderno_id`, tentativa, evento, fonte e tempo; validar compatibilidade com `tests/test_harness.py`.
2. **ENG-02:** implementar adaptadores condicionados a arquivos legítimos, verificando convenções antes do evento canônico.
3. **ENG-06/GP-3:** ligar IGP-01–11 aos testes já presentes sem duplicá-los; usar IGP-12–14 como provas de aceitação de capacidade nova.
4. **GP-4:** somente com autorização, segurança, contratos e reprodutibilidade verificados, integrar ciclo real.
5. **GP-5:** piloto real consentido e comparabilidade, sem inferir melhora de aprendizagem a partir de CI.

**Veredito GP-1:** PARCIALMENTE COBERTO POR VALIDAÇÕES EXISTENTES, **PENDENTE** de identidade de tentativa, semântica temporal, adaptador de entrada e transições de caderno. O PR #2 não altera o código.
