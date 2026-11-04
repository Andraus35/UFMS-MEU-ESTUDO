# Avaliação da eficácia das recomendações da IA — v1.4

**Estado:** ESPECIFICAÇÃO PEDAGÓGICA PROPOSTA; não há avaliação real de eficácia implementada. Vinculada a [evidências v1.2](MODELO_EVIDENCIAS_v1.2.md), [decisão v1.1](PROTOCOLO_DECISAO_v1.1.md) e [simulados v1.4](PROTOCOLO_SIMULADOS_v1.4.md).

## 1. Problema

Uma IA pode recomendar atividades convincentes e ainda assim ter pouco impacto na aprendizagem. O tutor precisa verificar **se suas intervenções parecem gerar melhores resultados sustentáveis**, sem confundir associação com prova causal.

Não julgar a IA pelo número de cadernos recomendados, questões resolvidas ou pela satisfação imediata. Avaliar principalmente qualidade da evidência, retenção, transferência e cobertura relevante.

## 2. Antes da recomendação: hipótese e sinal de sucesso

Cada decisão deverá registrar antecipadamente:
- `decision_id`, data/fuso e versão da política;
- evidências e qualidade E0–E4; cargo e tópico;
- **necessidade visada** (lacuna, retenção, cobertura, execução, transferência ou redução de incerteza);
- intervenção escolhida, alternativas relevantes e justificativa;
- **sinal observável esperado** (ex.: redução do mesmo erro em questões inéditas sem ajuda; recuperação posterior de um conteúdo; avaliação de área até então desconhecida);
- quando e com que evidência o sinal poderá ser verificado; condições de comparabilidade;
- possíveis fatores de confusão e dados ausentes.

A recomendação não pode mudar retroativamente sua definição de sucesso para parecer eficaz. É permitido revisá-la explicitamente, preservando versões.

## 3. Depois da atividade: quatro resultados distintos

| Categoria | Interpretação autorizada |
|---|---|
| **Sinal observado favorável** | Houve mudança congruente com objetivo em evidência suficientemente comparável; não se afirma causalidade |
| **Sinal observado desfavorável** | Resultado em condições pertinentes sugere necessidade de rever intervenção; investigar outras causas |
| **Inconclusivo** | Evidência fraca, amostra insuficiente, ausência de tentativa independente ou dados incompletos |
| **Incomparável** | Diferenças de conteúdo, dificuldade, novidade, ajuda ou medida impedem conclusão de evolução |

Nenhum caso pode ser convertido automaticamente em `probabilidade de eficácia` nem em avaliação moral do estudante.

## 4. Indicadores separados, não um índice mágico

**Indicadores diretos:** acertos por área/cargo quando disponíveis, pontos ponderados de simulados equivalentes, número de questões novas resolvidas independentemente, padrões de erro e respostas em branco.

**Indicadores de aprendizagem:** recuperação posterior independente, diversidade de formulações, melhora em dificuldades específicas, transferência para itens novos e redução de acertos inseguros — somente quando observados.

**Indicadores estratégicos:** áreas do edital cobertas com evidência, assuntos não avaliados, riscos eliminatórios diagnosticados, equilíbrio entre cargos e valor informacional do próximo caderno.

**Indicadores de funcionamento do tutor:** decisões com proveniência, pedidos de informação mínima, correções transparentes, disponibilidade confirmada das questões, registros de incerteza e consistência da persistência.

Não agregar esses indicadores em um suposto `dominio_total` nem declarar uma porcentagem de preparo sem definição e validação.

## 5. Comparação justa (mesmo aluno, condições relevantes)

Antes de comparar `antes` e `depois`, verificar:
- mesmo tópico/competência ou equivalência documentada;
- ajuda/consulta, tempo e grau de independência;
- questões inéditas, já vistas ou mistas;
- quantidade, dificuldade e diversidade da amostra;
- intervalo, condições de resolução e origem;
- repetição de itens entre as avaliações;
- contexto de prova/cargo, quando específico.

Relatar mudanças descritivas com denominadores claros (`8/12`, `9/13`) em vez de divulgar somente percentuais arredondados. Amostras pequenas não sustentam generalizações confiantes.

## 6. Validação com itens não usados na intervenção

Quando a plataforma permitir seleção suficiente:
1. Usar questões de aprendizagem/prática adequadas para a intervenção.
2. Reservar, na medida do possível, itens **inéditos** e independentes para verificações posteriores, evitando reapresentação das mesmas respostas.
3. Variar formulação, contexto e, quando cabível, banca ou nível para observar transferência; manter aderência ao edital.
4. Registrar se houve sobreposição com o conjunto de treino ou impossibilidade de controlar isso.

Isso não obriga um protocolo experimental rígido nem garante efeito causal; reduz o risco de confundir memorização de itens com aprendizagem.

## 7. Teste de retenção e custo de oportunidade

O tutor deverá investigar se o ganho se mantém após intervalo pertinente à decisão. Nenhum intervalo fixo universal é exigido.

Além da melhora aparente, observar o **custo de oportunidade**:
- a mesma intervenção está se repetindo sem nova evidência útil?
- conteúdos relevantes continuam sem diagnóstico?
- o desempenho melhora apenas em questões conhecidas?
- revisão está consumindo esforço sem ganhos de recuperação observáveis?
- concentrar-se em um cargo está negligenciando lacunas do outro?

Se a resposta indicar baixo retorno, considerar outra atividade e registrar o motivo. Não afirmar superioridade estatística de uma estratégia com base em um único resultado.

## 8. Critérios para manter, modificar ou suspender uma estratégia

**Manter provisoriamente:** há evidências favoráveis e limitações aceitáveis, sem custo excessivo ou riscos mais urgentes.

**Ajustar:** surgem falhas recorrentes, evidências contraditórias, baixa diversidade, dependência de comentários, repetição excessiva ou mudança de prioridades.

**Investigar antes de decidir:** dados incompletos, tentativas incomparáveis, resultado atípico isolado, origem questionável ou causa de erro não identificada.

**Suspender uma recomendação:** ela depende de item fora do edital, norma não conferida, fonte incompatível, dados inventados, acesso indevido ou condições inadequadas informadas pelo estudante.

Não programar sequências compulsórias por dificuldade nem penalizar pausas, fadiga ou indisponibilidade de tempo. O estudante determina limites de execução.

## 9. Controle determinístico + liberdade probabilística

A avaliação da IA será **determinística em fatos e invariantes**: identidades, convenções de pontuação, proveniência, unicidade, comparabilidade explicitada e registros consistentes.

A IA poderá ser **adaptativa** na interpretação das necessidades e comparação das intervenções, mas deverá documentar hipóteses e incertezas.

Sorteio ponderado de intervenções permanece opcional conforme v1.1: pesos, alternativas elegíveis, semente e decisão reproduzível. Sem atribuir chances fictícias de aprovação ou retenção.

## 10. Log mínimo da avaliação

Campos lógicos propostos, sem promessa de implementação:
- `evaluation_id`, `decision_id`, `related_caderno_ids`, `cargo_ids`, `topic_ids`;
- `baseline_evidence_refs`, `followup_evidence_refs`, `comparability`, `novelty`, `independence`, `interval`;
- `expected_signal`, `observed_signal`, `evaluation_class`, `limitations`;
- `next_decision_options`, `recommendation_change_reason`, `source_commit` quando persistido.

A avaliação só considera dados realmente recebidos, e eventos corrigidos preservam rastreabilidade. Não inferir resultados de subtópicos a partir de uma nota agregada.

## 11. Exemplo hipotético de auditabilidade

- **Antes:** assunto de Legislação com erros recorrentes e hipótese de confusão entre normas (proveniência e acertos previamente registrados).
- **Decisão registrada:** caderno intercalado para diferenciar normas; sinal esperado é melhor discriminação em itens novos sem ajuda.
- **Depois A:** 9/12 em questões repetidas com comentários → **inconclusivo** para o sinal pretendido.
- **Depois B:** 10/12 em questões inéditas sem consulta após intervalo, com dificuldade compatível → sinal **possivelmente favorável**, sujeito a amostra, comparabilidade e variação natural.
- **Próxima ação:** decidir entre ampliar cobertura e nova recuperação com base nas lacunas e custo de oportunidade, sem proclamar efeito causal.

Os números são fictícios. Não há dados reais de estudante neste documento.

## 12. Critérios de aceitação

1. Cada recomendação documenta previamente hipótese e sinal verificável.
2. A avaliação não muda retroativamente o critério de sucesso.
3. Diferencia favorável, desfavorável, inconclusivo e incomparável.
4. Não chama acerto repetido de retenção comprovada.
5. Distingue variação observada de efeito causado pela IA.
6. Mostra tamanho de amostra, proveniência e limitações.
7. Protege histórico de tentativas corrigidas, não duplica eventos ou cargos.
8. Não utiliza probabilidades não calibradas nem métricas globais sem definição.
9. Reconsidera estratégia com base em resultados e custo de oportunidade.
10. Usa apenas dados legítimos fornecidos ou consultados com permissão.

**Gate:** um documento de avaliação e uma CI de integridade não provam que a recomendação melhora aprendizagem. Isso exige validação operacional e acompanhamento de evidências reais, com limitações explicitadas.
