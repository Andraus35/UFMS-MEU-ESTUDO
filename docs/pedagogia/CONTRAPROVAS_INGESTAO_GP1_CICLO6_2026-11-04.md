# Contraprovas de ingestão IGP-12–14 — GP-1, ciclo 6

**Data:** 04/11/2026, America/Campo_Grande.  
**Modalidade:** confrontação estática do código e dos contratos existentes com entradas **inteiramente fictícias**. **Nenhum caso IGP-12–14 foi executado como teste automatizado nesta entrega.**  
**Repositório:** `Andraus35/UFMS-MEU-ESTUDO`.  
**Objeto técnico efetivamente consultado:** PR [#1](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/1), branch `setup/harness-memory-v0-2`, HEAD exato `b312a1f9f2110d3d75810e45b414b85c8e775445`, aberto/draft e não mesclado.  
**Especificação:** PR [#2](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/2), HEAD antes da entrega `85fc0ef98eb866058ee75297a5818c7525248f7c`.  
**Evidência de CI técnica:** [Validar harness, run 41828336395](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41828336395), `completed/success` no SHA técnico exato. A CI **não valida** essas três capacidades ainda ausentes.

## 1. Escopo e diferença para o ciclo 5

O [ciclo 5](EXECUCAO_FIXTURES_GP1_2026-11-04.md) executou 11/11 fixtures compatíveis com o módulo antigo. Os casos [IGP-12–IGP-14](FIXTURES_INGESTAO_GP1_2026-11-04.json) foram classificados corretamente como `NOT_IMPLEMENTED`.

A leitura atual do PR #1 mostra que o **Git blob do `scripts/core.py` permanece `28649e5b649c239cb03d748ab5822c352ddfe1db`**, o mesmo testado no ciclo 5. `tests/test_harness.py` mantém blob `00288b757073e87b47c4ce7223704a168843b389`. O HEAD da branch técnica mudou por outras entregas, mas **não há alteração nesses dois objetos**. Não reexecutar os mesmos 11 testes sem motivo; concentrar as próximas contraprovas nas três lacunas.

As conclusões abaixo são sustentadas **por inspeção do código**, não por execução de entradas nessa rodada.

## 2. IGP-12 — normalização de relatório ambíguo

**Entrada fictícia:** o relatório diz “12 respondidas, 3 não respondidas”, mas não define se `respondidas` já inclui ou exclui as em branco; `reported_total` está ausente.

**Evidência no código:** `validate_events` chama `count_integer(event.get("total"), ...)` e exige `acertos + erros + nao_respondidas == total`. Não há adaptador que descubra a semântica da coluna externa ou registre a proveniência da transformação.

**Resposta exigida do futuro adaptador:** `pending_clarification`; não gerar `resultado_recebido` com um `total` inventado. O usuário informa apenas a convenção necessária. Se a fonte comprovar que foram **15 apresentadas**, **12 respondidas** (por exemplo 8 corretas e 4 incorretas) e **3 em branco**, o adaptador poderá produzir o evento canônico correspondente, identificando a transformação e sua fonte.

**Negativa obrigatória:** um percentual arredondado sozinho não pode virar contagem exata; não usar a validação aritmética do evento como se ela provasse a interpretação da coluna do TEC/Qconcursos.

**Critérios existentes:** CDO-09/10/11, PRD-05. **Não criar caso novo.**

## 3. IGP-13 — uma plataforma, duas tentativas legítimas

**Entrada fictícia:** recomendação interna `R-FICT-1`, caderno externo `EXT-FICT-44`, tentativas independentes `TRY-FICT-A` e `TRY-FICT-B`. Nenhum desses IDs é real.

**Evidência no código:** `validate_events` armazena a última identidade em `results[caderno_id]`; um segundo evento `resultado_recebido` com mesmo `caderno_id` é rejeitado como duplicado. `rebuild` agrega por chave `caderno_id`, substituindo o resultado anterior. A simples inclusão de `attempt_id` como atributo extra não altera essa chave nem prova a semântica de tentativa.

**Comportamento esperado da engenharia:** definir política versionada que distingue `recommendation_id`, `platform_notebook_id`, `attempt_id` e `event_id`; aceitar duas tentativas **realmente independentes** com identidades distintas, preservar seus históricos e permitir corrigir somente a tentativa explicitamente indicada. Rejeitar tentativa repetida com o mesmo identificador e correção órfã. O caso legado de “um resultado corrente por caderno interno” deve continuar reconstruível sem rehashar eventos anteriores.

**Negativa obrigatória:** não lançar a segunda tentativa como `resultado_corrigido` apenas para contornar o validador; isso apagaria a distinção entre nova observação e conserto da mesma observação.

**Critérios existentes:** CDO-02/14, PED-14, PRD-03. **Não criar caso novo.**

## 4. IGP-14 — tempo de registro versus tempo de resolução

**Entrada fictícia:** `recorded_at="2026-11-04T10:05:00-04:00"` representa recepção; `attempt_at=unknown` porque a pessoa não informou quando resolveu as questões.

**Evidência no código:** `validate_events` exige apenas `timestamp` ISO com fuso; não verifica um campo `attempt_at` distinto. `rebuild` atualiza `last_event_at` a partir do `timestamp` de evento. A presença de um `attempt_at` adicional no objeto atual não significa que seu significado tenha sido verificado ou persistido de maneira recuperável.

**Comportamento esperado:** definir `recorded_at` ancorado na recepção/registro e `attempt_at` separado, com origem e fuso quando conhecido; se desconhecido, manter desconhecido. Não interpretar automaticamente `last_event_at` como data de aprendizagem. Retenção espaçada somente pode usar intervalos baseados em datas de tentativa suficientemente verificadas.

**Negativa obrigatória:** horário do commit ou da mensagem não prova quando a pessoa respondeu ao caderno.

**Critérios existentes:** CDO-09, PRD-04. **Não criar caso novo.**

## 5. Ordem de implementação, regressão e provas de aceite

| Ordem | Pacote | Entrada de teste | Saída exigida | Gate |
|---|---|---|---|---|
| 1 | ENG-01 — identidades/versionamento | Duas tentativas ligadas ao mesmo caderno externo e uma correção da segunda | Duas tentativas preservadas; somente a segunda corrigida; replay estável | GP-1 |
| 2 | ENG-01 — temporalidade | Registro com timestamp conhecido e tentativa sem data | `attempt_at` desconhecido, `recorded_at` verificável; nenhuma retenção inventada | GP-1 |
| 3 | ENG-02 — adaptador | Relatório com semântica de `respondidas` desconhecida e outro com convenção confirmada | Primeiro pendente; segundo evento normalizado, rastreado e validado | GP-1 |
| 4 | ENG-06 — regressões | Todos IGP-01–14 e `tests/test_harness.py`, inclusive correção duplicada, ID colidido e data inválida | PASS/FAIL/BLOCKED por SHA e reexecução em CI independente do produtor | GP-3 |

**Definition of Done mínimo:** especificar entrada/saída, origem de cada campo, migração e compatibilidade do legado; executar testes com dados fictícios; salvar stdout/relatório com SHA e CI; não liberar `personal_results_writes_enabled`; readback remoto do commit candidato; revisão independente quando exigida. O caso que não tem implementação permanece `BLOCKED` ou `NOT_IMPLEMENTED`, nunca `PASS`.

## 6. Estado ao fim do ciclo 6

- **IGP-01–11:** execução isolada anterior PASS, com proveniência e limites documentados no ciclo 5. Este ciclo não os executou novamente.
- **IGP-12–14:** lacunas de capacidade confirmadas por inspeção do `core.py` no SHA citado; **sem teste executado nesta rodada**.
- **GP-0:** permanece pendente de cotejo atualizado de retificações e equivalência de documentos FAPEC/UFMS; não foi reavaliado neste ciclo.
- **GP-1:** **PENDENTE**; os três contratos ainda requerem implementação e testes na frente técnica.
- **GP-2 a GP-5:** não homologados. CI técnica verde não certifica tutor adaptativo.
- **Fronteira:** sem edição do PR #1, regras, hooks, `settings.json`, estado pessoal ou fonte normativa. Sem merge.

**Próxima ação realmente produtiva:** executar ENG-01/02 na sessão de engenharia, usando este relatório e as fixtures existentes; evitar gerar novos documentos pedagógicos se não surgirem novas contraprovas ou decisões de método.
