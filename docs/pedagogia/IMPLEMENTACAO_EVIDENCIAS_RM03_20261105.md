# RM-03 — projeção determinística E0–E4

**Data:** 05/11/2026  
**Base:** `main@4052a06d530b269410f0300a8ae503e822672caa`  
**Tarefa:** ENG-03 / GP-2  
**Escopo:** projeção informacional, sem inferir domínio ou probabilidade de aprovação.

## Regra de classificação

| Nível | Condição implementada | Limite |
|---|---|---|
| E0 | Nenhuma tentativa/resultado | Sem avaliação; não equivale a nota zero |
| E1 | Resultado agregado sem discriminação por tópico | Desempenho geral observado |
| E2 | Resultado com `topic_results` | Desempenho localizado; não comprova independência |
| E3 | Tentativa com `attempt_at` e dimensões conhecidas: independência, familiaridade, diversidade, proveniência e confiança | Diagnóstico contextualizado; uma observação não prova retenção |
| E4 | Pelo menos duas tentativas sem consulta, inéditas, variadas, com `item_set_id` distintos e datas de tentativa distintas | Evidência mais informativa; ainda não é domínio absoluto |

## Implementação

- `scripts/evidence_projection.py` deriva E0–E4 e explicita dimensões/uncertainties.
- `scripts/gp1_ingestion.py` aceita dimensões opcionais validadas; ausência vira `unknown`. `item_set_id` nunca é gerado.
- `scripts/core.py` inclui a projeção em `rebuild`, tanto no caminho legado quanto no schema aditivo de tentativas.
- `state/CURRENT.json` foi reconstruído para estado vazio: E0, sem resultados, `knowledge_status=unknown_until_evidence`.
- Correções substituem a observação da tentativa, sem multiplicar evidência; tentativas independentes permanecem separadas.
- E4 exige datas distintas e conjuntos distintos. Consulta, repetição ou mesma data não promovem para E4.

## Incertezas preservadas

A projeção reporta `aggregate_only_no_topic_breakdown`, `attempt_time_unknown`, `independence_unknown`, `familiarity_unknown`, `diversity_unknown`, `provenance_unknown`, `confidence_unknown` e/ou `insufficient_independent_recoveries_on_distinct_dates_and_item_sets`, conforme os campos observados. Nenhum campo desconhecido é inferido de horário de commit, mensagem ou score agregado.

## Testes

`tests/test_evidence_projection.py` cobre E0–E4, ausência de contexto, tentativa repetida, mesma data, consulta e integração de E3 ao `core.rebuild`. Os testes usam exclusivamente IDs e resultados sintéticos. A CI deve confirmar a projeção no SHA exato.

## Limites

- Nenhum dado pessoal foi lido ou gravado; `CURRENT.json` continua sem eventos e E0.
- A implementação não estima domínio, retenção, esquecimento ou chance de aprovação.
- E4 depende da veracidade da proveniência/contexto fornecidos; não existe verificação automática da plataforma.
- Não habilita escrita pessoal, scraping ou API privada do TEC/Qconcursos.
