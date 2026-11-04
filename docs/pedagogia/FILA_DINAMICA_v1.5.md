# Fila dinâmica de aprendizagem — UFMS v1.5

**Estado:** ESPECIFICAÇÃO PEDAGÓGICA PROPOSTA — não há mecanismo de ranqueamento implementado, nem execução de questões, nem resultados pessoais persistidos por esta entrega.  
**Escopo:** cargos 523 e 324 do Edital PROGEP/UFMS nº 152/2026, condicionado a retificações verificadas.  
**Dependências:** [método v1.0](METODO_v1.0.md), [decisão v1.1](PROTOCOLO_DECISAO_v1.1.md), [evidências v1.2](MODELO_EVIDENCIAS_v1.2.md), [estratégia v1.3](ESTRATEGIA_COMPETITIVA_v1.3.md), [simulados v1.4](PROTOCOLO_SIMULADOS_v1.4.md) e [eficácia v1.4](AVALIACAO_EFICACIA_v1.4.md).  
**Fonte normativa:** edital e retificações verificadas; índices/aliases e `config/topics.csv` são metadados derivados, não novas regras de prova.

## 1. Propósito: uma fila de oportunidades, não um planograma

A fila é uma **visão dinâmica e reconstruível de candidatos à próxima ação**. Não estabelece dias, horários, carga semanal, número de questões ou ciclos fixos. A IA recomenda **uma intervenção principal viável** e pode apresentar alternativas justificadas.

As decisões respondem: o que gera mais aprendizagem ou informação agora, por quê, que risco não podemos ignorar e em qual evidência precisamos reavaliar a prioridade?

**Não confundir:**
- Prioridade na fila ≠ domínio, probabilidade de aprovação, nota prevista ou obrigação de estudo.
- Revisão pendente ≠ atraso moral ou incapacidade.
- Ausência de caderno concluído ≠ 0% de acertos.
- Posição mais baixa ≠ exclusão do edital.

## 2. Modelo lógico das unidades e atividades

**Unidade curricular:** um tópico do edital, com `topic_id`, `source_ref`, `cargo_ids`, `area`, `subtopic_ref` opcional e `overlap_status` (confirmada/parcial/não confirmada). A granularidade não pode exceder a precisão da evidência disponível.

**Candidato a intervenção:** combinação de `topic_ids`, `cargo_ids`, modalidade de caderno, objetivo pedagógico, condições mínimas para executar, evidências que o sustentam e critério de reavaliação. Uma mesma unidade pode gerar candidatos distintos (diagnóstico, correção, recuperação, transferência), **sem multiplicar resultados históricos**.

**Evento observado:** resultado validado, correção do resultado, nova informação de contexto, autorização de tempo, disponibilidade confirmada de questões, retificação do edital ou decisão pedagógica registrada.

**Snapshot de fila:** projeção datada, ligada à versão do edital e a um `source_commit`, com candidatos, estado da avaliação, restrições, justificativas e identidade do algoritmo/política. É derivada, não a fonte de verdade; não persistir como se fosse histórico autoritativo independente.

## 3. Estados de elegibilidade

| Estado de candidato | Significado |
|---|---|
| `eligible` | Pode ser recomendado com as informações atuais |
| `needs_evidence` | Falta informação relevante; pode gerar diagnóstico ou pedido mínimo |
| `pending_confirmation` | Depende de disponibilidade de questões, recorte do edital ou condição comunicada pelo estudante |
| `temporarily_deferred` | Viável, mas outra necessidade demonstrada é mais útil no momento; registrar motivo e condição de retorno |
| `blocked` | Contradiz regra ou dado indispensável, usa fonte inválida, duplica atividade incompatível ou está fora do escopo |
| `completed_observation` | Intervenção executada e resultado associado; futuras ações requerem nova avaliação |

`temporarily_deferred` nunca significa abandono permanente. `needs_evidence` não implica que o estudante desconhece o conteúdo. Um candidato só muda para `completed_observation` quando houver evidência real de execução, não apenas recomendação.

Não criar fila artificial infinita: calcular opções relevantes sob demanda, priorizando a próxima decisão e um conjunto pequeno de alternativas auditáveis.

## 4. Geração de candidatos

A partir dos tópicos válidos, projeções verificáveis e relatórios de desempenho:

1. **Diagnóstico** para conteúdo sem evidência suficiente ou área estratégica ainda não avaliada.
2. **Aprendizagem guiada/correção** para lacuna conceitual, confusão, procedimento ou interpretação sustentados por evidência.
3. **Recuperação independente/espacial** para testar retenção após intervalo; o prazo depende da história, não de regra universal.
4. **Intercalação/transferência** para distinguir normas semelhantes ou verificar desempenho em formulações inéditas.
5. **Exploração** para reduzir cobertura insuficiente de tópicos pertinentes ao cargo.
6. **Simulado parcial/completo** para avaliar integração e execução quando houver objetivo pedagógico claro e itens apropriados.

Não gerar uma nova recomendação idêntica quando existe caderno pendente adequado ao mesmo objetivo e ainda não executado, salvo replanejamento explícito. Um caderno pendente pode ser cancelado/substituído mantendo seu histórico; não registrar resultado fictício.

## 5. Gate determinístico antes da priorização

São invariantes:
- Assunto compatível com edital vigente e cargo informado; retificação com efeito relevante exige revalidação.
- Integridade e identidade dos eventos: sem duplicação, sem resultado inventado, sem repartição de agregado por subtópicos.
- Evidência E0–E4 avalia **qualidade informacional**, não domínio.
- Sobreposição entre específicos 523/324 somente após comparação documental; um evento não é contado duas vezes.
- Restrições eliminatórias são verificadas na versão válida antes de afirmar risco normativo.
- Disponibilidade de caderno, filtros, questões e acesso a plataforma não pode ser presumida.
- O estudante não deve receber recomendação inviável pelo tempo, capacidade ou condições **quando tais limites forem conhecidos**; limites desconhecidos não são adivinhados.
- Candidato fora de escopo ou com fonte contraditória é bloqueado ou submetido à conferência, não tratado como prioridade baixa.
- Dados insuficientes levam a diagnóstico, ressalva ou pedido mínimo, não a precisão inventada.

**Política de falha:** inconsistência em evento, mapeamento ou retificação suspende apenas as decisões afetadas; manter o restante utilizável quando isso for seguro e verificável. Em caso de integridade global comprometida, não recomendar com estado supostamente confiável.

## 6. Vetor de prioridade explicável

Para cada opção elegível, registrar uma avaliação **multicritério** (não uma única pontuação mágica):

| Critério | Pergunta | Fonte mínima |
|---|---|---|
| `exam_impact` | Qual área/cargo e qual valor de prova? | Edital vigente |
| `elimination_risk` | Existe risco relevante ou área sem diagnóstico? | Regra verificada + evidência |
| `coverage_gap` | O conteúdo permanece pouco observado? | Tópicos do edital + eventos |
| `learning_need` | Erros ou hipóteses sustentam correção? | Resultados e contexto |
| `retention_signal` | Há esquecimento observado ou recuperação a verificar? | Histórico e intervalos reais |
| `uncertainty_reduction` | O caderno resolveria dúvida decisiva? | Lacunas de evidência E0–E4 |
| `cross_cargo_benefit` | Há vantagem comprovada para 523 e 324? | Sobreposição documental |
| `freshness_diversity` | Haverá questões suficientemente variadas? | Plataforma/relato, se disponível |
| `feasibility` | A intervenção é exequível neste momento? | Limites informados + itens confirmados |
| `opportunity_cost` | Que outra necessidade seria adiada? | Fila e estado atual |
| `deadline_context` | O prazo altera o custo de testar, recuperar ou explorar? | Data da prova verificada |

**Sem pesos numéricos universais.** Se a implementação optar por escalas ou ponderações, seus valores são escolhas explícitas de engenharia, versionadas e avaliadas em cenários adversariais; não são estimativas científicas de aprendizagem. Não produzir probabilidades de domínio ou aprovação.

## 7. Ordem de resolução e desempate

**Etapa A — filtro de validade:** eliminar candidatos `blocked`, preservar motivos e referências.

**Etapa B — necessidades críticas:** conferir restrições eliminatórias e falhas de integridade/escopo. Risco normativo confirmado pode prevalecer sobre conveniência. Não transformar toda área E0 em emergência permanente.

**Etapa C — oportunidades de aprendizagem:** comparar cobertura, lacuna, retenção, transferência, custo e benefício para os dois cargos. Privilegiar valor esperado *pedagógico e informacional* qualitativo, não “chance de passar”.

**Etapa D — auditoria de equilíbrio:** verificar se a mesma área ou cargo está dominando sucessivas decisões sem justificativa. Ausência de evidência do outro cargo pode motivar exploração, não quotas rígidas.

**Etapa E — escolha e explicação:** selecionar uma atividade principal, registrar pelo menos a principal alternativa adiada (quando houver), explicitar incerteza, condição de revisão e filtros do caderno.

**Empate:** primeiro, critério desempate determinístico documentado (ex.: menor incerteza de disponibilidade ou maior ganho informacional) ou escolha humana. Sorteio ponderado é **opcional**, restrito a candidatas válidas, com semente, pesos e versão da política registrados. Reproduzir o sorteio não comprova que foi pedagogicamente superior.

## 8. Recalcular quando houver evento relevante

A fila deve ser **derivada novamente** após:
- resultado novo **validado**;
- correção vinculada a evento anterior;
- revisão concluída ou evidência de esquecimento;
- mudança de escopo por retificação conferida;
- indicação do estudante sobre disponibilidade, objetivos ou limites;
- confirmação de falta de questões ou novos filtros possíveis;
- decisão de cancelar, substituir ou adiar caderno com motivo.

Sem novo evento ou mudança verificada da fonte, repetir a consulta ao mesmo estado e à mesma versão da política deve produzir **mesmo conjunto ordenado e justificativas equivalentes**, exceto quando a escolha aleatória estiver explicitamente solicitada com nova semente. A mera passagem de tempo pode afetar intervalos e prazo de prova, mas precisa entrar no snapshot como `as_of` explícito; não mudar decisões furtivamente com relógio implícito.

**Correção:** reconstruir a partir do log canônico, não acrescentar acertos antigos e novos cumulativamente. Se o commit lido divergir durante atualização, não publicar uma fila baseada em estado desatualizado; recomputar sobre o HEAD confirmado.

## 9. Regras antiengessamento e antifixação

- Não impor ordem fixa “gerais → específicos → revisão → simulado”.
- Não reservar quotas arbitrárias de minutos ou porcentagens de estudo por cargo/área.
- Não insistir em repetição de itens já conhecidos por elevar artificialmente acertos.
- Não penalizar interrupções e pausas; fila não gera “atrasos” fictícios.
- Não arquivar um tópico como “dominado para sempre”; retenção pode precisar de nova observação.
- Não abandonar permanentemente matérias de menor peso diante de requisito eliminatório.
- Não escolher sempre o conteúdo mais fácil, mais disponível ou mais confortável.
- Não gerar cronograma individual sem solicitação expressa.
- Não considerar o ranking uma obrigação de execução: o estudante pode selecionar outra atividade; registrar a divergência sem apagar evidências.

## 10. Projeção mínima de recomendação

Campos lógicos sugeridos; **não** é um schema implementado:

```text
queue_snapshot_id, as_of, source_commit, edital_version, policy_version,
candidate_id, cargo_ids, topic_ids, intervention, eligibility_status,
priority_reasons[], evidence_refs[], evidence_quality, uncertainties[],
risk_flags[], overlap_status, feasibility, pending_caderno_refs[],
alternatives_considered[], deferred_reason, reentry_condition,
selection_mode, random_seed_if_applicable,
expected_signal, reassessment_condition, persistence_status
```

Não armazenar texto integral de questões de plataforma; metadados apenas quando legitimamente disponíveis. Identificadores de candidatos devem ser estáveis para o mesmo conjunto de entrada, mas não colidir com `event_id` ou `caderno_id`. Não inventar IDs existentes.

## 11. Pseudoprocesso de referência (não código em produção)

```text
build_queue(snapshot, policy, as_of):
    verify_versions_and_event_integrity(snapshot, policy)
    topics = resolve_applicable_topics(snapshot.edital)
    options = generate_relevant_interventions(topics, snapshot.evidence)
    options = validate_or_mark_pending(options, snapshot.constraints)
    eligible = options.filter(status == eligible)
    assessments = assess_qualitatively(eligible, exam, risks, uncertainty,
                                        retention, coverage, cross_cargo, feasibility)
    ordered = resolve_critical_needs_then_compare(assessments)
    flag_fairness_and_repetition_patterns(ordered, snapshot.history)
    return shortlist_with_reasons(ordered, deferred, blocked, as_of, policy.version)

after_result(valid_event):
    append_once_and_rebuild_projections(valid_event)
    recompute_queue_from_confirmed_state()
```

A função de política deve trabalhar sobre **snapshot explícito**. A validação de conteúdo do edital e a persistência são responsabilidades do harness técnico e dependem de autorização. O pseudoprocesso não executa código, não habilita escrita nem controla as plataformas.

## 12. Exemplos fictícios de movimentação da fila

| Evento ou contexto | Antes | Depois — interpretação esperada |
|---|---|---|
| Inglês E0, específicos 523 bem observados | Inglês desconhecido | Diagnóstico de Inglês ganha relevância; não recebe 0% fictício |
| Chega resultado de legislação comum com falhas de recuperação | Uma exploração de 324 era preferida | Recuperação de Legislação pode superar exploração, se risco e custo sustentarem |
| 523-07 e 324-09 compartilham nome, mas não houve confronto de ementas | Candidato de caderno “comum” | Compartilhamento fica pendente; duas unidades permanecem separadas |
| Resultado corrigido substitui total anterior | Projeção baseada em evento antigo | Recomputar sem duplicar; justificar possível mudança de posição |
| Nenhuma mudança de dados, versão ou `as_of` | Ranking A | Ranking A novamente; nenhuma oscilação aleatória escondida |
| Muitas questões repetidas e alta precisão imediata | Revisão fácil parece prioritária | Exploração ou recuperação inédita pode ganhar relevância |
| Faltam questões FAPEC na plataforma | Caderno inviável | Marcar `pending_confirmation` e sugerir expansão controlada de filtros |
| Estudante informa pouco tempo disponível hoje | Simulado completo candidato | Reavaliar viabilidade; sugerir caderno focalizado sem transformar limite em rotina permanente |

**Não há dados reais de desempenho nestes exemplos.**

## 13. Critérios de aceitação

A implementação deve superar testes para: edição de fila após evento, estabilidade/idempotência, relevância de risco eliminatório, ausência de nota fictícia, não duplicação 523/324, respeito a disponibilidade, correção de resultados, mudança de versão do edital, bloqueios, empate, sorteio com semente, controle de repetição, interrupções, `as_of` explícito, dados incompletos e justificativa da escolha. Casos FIQ-01 a FIQ-18 estão detalhados em [critérios de aceitação](CRITERIOS_DE_ACEITACAO.md).

**Gate:** v1.5 é uma regra escrita para futura implementação. Ainda é necessário provar coerência com testes executáveis e validar a utilidade das recomendações em acompanhamento real; o commit documental não comprova isso.
