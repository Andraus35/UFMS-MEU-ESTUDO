# Protocolo de simulados e preparação para duas provas — v1.4

**Estado:** ESPECIFICAÇÃO PEDAGÓGICA PROPOSTA, sem implementação nem simulado real confirmado.
**Cargos:** 523 (manhã, nível superior) e 324 (tarde, nível médio).
**Dependências:** [método v1.0](METODO_v1.0.md), [decisão v1.1](PROTOCOLO_DECISAO_v1.1.md), [evidências v1.2](MODELO_EVIDENCIAS_v1.2.md), [estratégia v1.3](ESTRATEGIA_COMPETITIVA_v1.3.md).

## 1. Função do simulado

O simulado avalia **execução integrada**: recuperação independente, combinação de áreas, velocidade, decisões sob tempo, atenção e manejo de uma prova completa. Não é apenas mais um caderno de questões, não substitui diagnóstico conceitual focalizado e **não prevê classificação**.

O estudante deve saber se o objetivo é:
- **Diagnóstico de prova:** obter evidência sobre distribuição de erros, tempo e áreas ainda frágeis;
- **Treino de execução:** praticar condições semelhantes à prova, com controle de consultas e intervalo;
- **Verificação de progresso:** comparar tentativas pertinentes e suficientemente semelhantes;
- **Ensaio do dia com duas provas:** observar a sequência manhã → tarde quando viável e desejada.

O agente pode recomendar um simulado por cargo sem obrigar o estudante a fazer dois no mesmo dia.

## 2. Parametrização documental e legitimidade

A configuração do PR #1 consultada em 04/11/2026 indica, **para cada prova**, 60 questões, 100 pontos, 240 minutos e a seguinte distribuição:

| Área | Questões | Valor por questão | Total |
|---|---:|---:|---:|
| Português | 15 | 1 | 15 |
| Inglês | 5 | 1 | 5 |
| Legislação | 10 | 2 | 20 |
| Raciocínio Lógico | 10 | 2 | 20 |
| Específicos do cargo respectivo | 20 | 2 | 40 |
| **Total** | **60** | — | **100** |

**Gate obrigatório:** antes de usar a composição como simulado oficial-equivalente, conferir `EDITAL_UFMS_152_2026.md`, anexos pertinentes e eventuais retificações oficiais. Não converter valores de cadastro em regra atual sem conferência.

Pontuação ponderada **somente** quando as contagens corretas por área forem conhecidas, houver correspondência válida entre item e área e a regra de pontuação estiver verificada:
`P = 1·(PORT_acertos + ING_acertos) + 2·(LEG_acertos + RLM_acertos + ESP_acertos)`.
Sem discriminação por área, **não computar** `P` a partir de percentual agregado; registrar `pontuacao_ponderada = desconhecida`.
Se houver formato reduzido, provas antigas, substituição de matérias ou itens não correspondentes, identificar `simulado_parcial` e não rotular sua pontuação como oficial-equivalente.

O cadastro inicial informa mínimo global de 50 pontos e nota não zero por área; aplicar como condições de corte **apenas após confrontar versão válida do edital**, inclusive disposições sobre eliminação/classificação. Um simulado isolado não determina aprovação.

## 3. Modalidades e independência

| Modalidade | Proposta | Regra de interpretação |
|---|---|---|
| Parcial focado | Seleção de áreas ou partes da prova | Não comparável diretamente a 100 pontos |
| Completo 523 | Composição específica do cargo 523 | Desempenho do 523, não transferido ao 324 |
| Completo 324 | Composição específica do cargo 324 | Desempenho do 324, não transferido ao 523 |
| Ensaio combinado | Realizar 523 de manhã e 324 de tarde, se viável | Dois relatórios e avaliação complementar de execução |
| Reavaliação | Outra amostra equivalente e predominantemente inédita | Comparar com limitações documentadas |

Recomendar não consultar comentários, gabarito, ajuda externa ou materiais **durante** um simulado independente; analisar depois da conclusão. Se houver consulta, rotular como `guiado`, não como equivalente a um teste independente.
Não afirmar disponibilidade de exatamente 60 questões com filtros desejados no TEC/Qconcursos sem confirmação.

## 4. Ensaio combinado em dois turnos

O ensaio integral é **opcional** e depende do objetivo, disponibilidade e condições do estudante. Cada prova possui avaliação separada; registrar também o intervalo entre elas, alimentação/pausas apenas se informado, sensação subjetiva de fadiga e possível efeito de ordem.

A IA não define horários oficiais de portões por suposição. Deve consultar a versão atual do edital, e o estudante deve reproduzir condições reais apenas quando apropriadas e seguras. A duração de 240 minutos por prova vem do cadastro; não significa que se deva insistir em estudar oito horas sem avaliação das condições.

Uma queda no segundo simulado **não comprova fadiga**; pode refletir dificuldade diferente da prova, lacunas específicas, condições de amostragem ou execução.

## 5. Registro mínimo por tentativa

`simulation_id` único, `cargo_id`, `source_edital_version`, `date_time_tz`, `platform`, `format`, `independent_or_guided`, `question_novelty`, `official_equivalence_status`, `provenance`, `per_area_counts` (se disponíveis), `duration_observed` (se disponível), `reported_confidence` (opcional), `missing_fields`.

Por área: `n_apresentadas`, `n_acertos`, `n_erros`, `n_sem_resposta`, tempo quando houver, e convenção de contagem. Os totais devem corresponder à convenção da fonte; não calcular subconjuntos ausentes.

Ao registrar dois simulados combinados, utilizar **dois identificadores únicos** e um `combined_session_id` que os vincule, sem agregar os acertos como se formassem uma única prova oficial.

## 6. Diagnóstico após o simulado

O tutor deverá separar:
1. **Execução:** conclusão da prova, tempo, questões sem resposta, mudança de ritmo e sinais de fadiga apenas relatados.
2. **Resultado por área:** pontos observados, se calculáveis, e alertas de áreas fragilizadas.
3. **Aprendizagem:** conteúdo não conhecido, interpretação, procedimento, retenção, transferência ou causas ainda indeterminadas.
4. **Qualidade da avaliação:** amostra inédita/repetida, independência, diversidade e equivalência com o edital.
5. **Próxima intervenção:** uma ação principal justificada e alternativas, usando v1.1.

Um resultado global alto com uma área zerada requer análise das condições eliminatórias, mesmo que o total seja expressivo. Por outro lado, baixa pontuação global não deve ser traduzida em déficit por subtópico sem discriminação.

## 7. Comparação temporal e inferência

Comparações entre simulados exigem cautela com: composição, número de itens, incidência de assunto, nível, banco de questões, novidade, independência, tempo e intervalo entre provas.

- **Comparável:** mudanças observadas podem ser relatadas como tendências provisórias, com amostra e limitações.
- **Parcialmente comparável:** relatar métricas por área e dimensões equivalentes, evitando afirmações globais.
- **Não comparável:** preservar resultados em separado, sem classificar evolução ou regressão sustentada.

Não transformar a diferença entre dois percentuais em causalidade pedagógica. Repetições e aprendizado com um mesmo conjunto de questões podem inflar a pontuação sem melhorar o desempenho em questões inéditas.

## 8. Decisão de quando recomendar

Não estabelecer simulado semanal, quinzenal ou quota obrigatória. A escolha depende de:
- cobertura e qualidade das evidências;
- necessidade de verificar desempenho integrado e ritmo;
- incerteza que um simulado pode reduzir;
- custo em tempo/energia diante de outras alternativas;
- proximidade das provas;
- equilíbrio entre ambos os cargos.

Se não há dados suficientes para oferecer simulado oficial-equivalente, recomendar versão diagnóstica com rótulo correto ou caderno focalizado, nunca simulação ficticiamente completa.

## 9. Saída obrigatória da análise de simulado

A análise deverá informar:
- contexto e proveniência da tentativa;
- composição efetivamente observada;
- pontuação ponderada **somente se calculável**;
- áreas críticas e incertezas;
- comparação condicional com avaliações anteriores;
- limitações da inferência e ausência de previsão de aprovação;
- intervenção recomendada e motivo;
- dados desejáveis para a próxima verificação;
- persistência remota apenas quando confirmada.

## 10. Gate de implementação

Aprovado apenas quando houver testes de pontuação e somatórios por área, rejeição de dados inconsistentes, diferenciação entre dois cargos, simulado parcial e completo, tratamento de área zerada, independência, repetição, comparabilidade e ensaio combinado. O documento especifica, mas não executa tais testes.
