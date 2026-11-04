# Plano de transferência à engenharia — UFMS v1.8

**Status:** plano de implementação proposto. Não é código executado, abertura de PR técnico, parecer de aprovação de gates ou instrução para merge.
**Data:** 04/11/2026, fuso America/Campo_Grande.
**Projeto:** `Andraus35/UFMS-MEU-ESTUDO`; [PR pedagógico #2](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/2), sem merge.
**Base de especificação:** v1.0–v1.7 de `docs/pedagogia/` e [matriz de reconciliação](MATRIZ_RECONCILIACAO_v1.7.md).
**Objeto técnico:** tutor assistido por IA para os cargos UFMS 523 e 324, por questões e evidências; sem planograma rígido.

## 1. Premissas não negociáveis

- **Não implementar nada no PR #2:** ele preserva a especificação de origem. Engenharia prepara sua própria proposta técnica, sujeita à governança e à autorização do responsável. Não alterar, rebasear ou mesclar o PR #1 sem aprovação expressa.
- **Revalidar a fonte técnica:** durante esta entrega, o PR #1 foi observado em `4317103ab91fae43c7e07cf5527d6ecbcc5681d7`; isso pode mudar. A matriz v1.7 foi produzida sobre SHA técnico **anterior** `18a81bacd6163e6d510e58c00f2a55e77051b3ca`, de modo que suas conclusões são hipóteses a reconfirmar.
- **Não habilitar `personal_results_writes_enabled` por dedução.** Visibilidade privada, consentimento, necessidade, autorização, testes e gate de persistência devem ser comprovados separadamente.
- **O edital vigente prevalece.** Nenhuma regra de corte, equivalência entre específicos ou atualização normativa é considerada verificada apenas porque está num JSON, índice ou resumo.
- **TEC/Qconcursos:** a IA prescreve filtros, o estudante executa e devolve resultados legítimos. Sem scraping, API não confirmada, IDs inventados ou cópias integrais de questões.
- **Sem merge automatizado.** CI verde de integridade não significa aptidão do tutor nem qualidade pedagógica comprovada.

## 2. Work packages e dependências

| Pacote | Prioridade | Gate | Trabalho técnico a produzir | Dependência para iniciar | Saída e aceite mínimos |
|---|---|---|---|---|---|
| ENG-00 | P0 | GP-0 | Conferir edital primário, versão, retificações e recortes 523/324 | Ler documentos da branch técnica atual | Mapa de fontes/versionamento; pontos não verificáveis permanecem pendentes |
| ENG-01 | P0 | GP-1 | Reconciliar START/DELIVERY, política de leitura, IDs de eventos/cadernos/tentativas e modelo de datas | HEAD técnico readback + especificação v1.7 | Contratos explicitados; migração compatível, sem perda histórica |
| ENG-02 | P0 | GP-1 | Adaptador seguro de resultados com convenções diferentes e estados de caderno | ENG-01 e amostra legítima quando necessária | Dados incertos não viram contagens falsas; eventos inválidos não entram no histórico |
| ENG-03 | P1 | GP-2 | Derivação de evidências E0–E4 e classificação de incertezas | ENG-01/02; dados fictícios | Projeção reconstruível, E0–E4 não tratados como nota de domínio |
| ENG-04 | P1 | GP-2 | Fila dinâmica, elegibilidade, comparador contextual e critérios de reavaliação | ENG-00 + ENG-03 | Mesma entrada/versão/as_of dá saída reproduzível; explicação auditável |
| ENG-05 | P1 | GP-2 | Prescritor de cadernos e feedback mínimo ao estudante | ENG-04 e modelo de plataforma sem APIs presumidas | Um caderno principal viável; filtros e fallback; estados honestos |
| ENG-06 | P1 | GP-3 | Testes adversariais e fixtures para contratos e decisões | ENG-01–05 em incrementos | Rastreio de cenários, PASS/FAIL por SHA, casos negativos e regressões |
| ENG-07 | P2 | GP-4 | Ciclo integrado controlado: recomendação → confirmação → resultado → validação → reconstrução → nova recomendação | GP-0/1/2/3 satisfatórios | Readback de eventos autorizados em ambiente controlado e recuperação correta entre sessões |
| ENG-08 | P2 | GP-5 | Piloto consentido e avaliação de utilidade da aprendizagem | GP-4 + consentimento, minimização e proteção de dados | Observações transparentes, sem causalidade ou probabilidades não calibradas |

**Sobreposição permitida:** ENG-06 deve gerar fixtures e testes **junto com** cada ENG-01–05, não somente ao final. GP-0 pode avançar em paralelo às definições de GP-1, mas requisitos normativos não verificados bloqueiam decisões afetadas.

**Mecanismos probabilísticos:** a seleção ponderada é **opcional**. Implementar somente após a fila determinística funcionar; registrar alternativas elegíveis, pesos configuráveis, semente, política e amostra de teste. Não estimar probabilidade de aprender/aprovar sem calibração e dados.

## 3. Contratos de integração que exigem resposta explícita

| Decisão de engenharia | Não aceitar como substituto | Resultado esperado |
|---|---|---|
| Fonte de verdade de eventos | “O chat lembrou” | Evento único, correção vinculada, projeções reconstruíveis |
| Identidade de caderno | Um `caderno_id` ambíguo para todos os conceitos | Mapeamento documentado entre recomendação, plataforma, tentativa e evento |
| Temporalidade | Data da tentativa preenchida com hora de commit | `recorded_at` com origem real; `attempt_at` desconhecido até informado |
| Números do TEC/Qconcursos | Somar campos incompatíveis ou completar via porcentagem | Adaptador por convenção, com pendência em caso de ambiguidade |
| Evidência por subtópico | Ratear resultado global | Só valores discriminados; E0/desconhecido quando não observado |
| Sobreposição 523/324 | Igualar títulos de disciplinas | Equivalência documental explícita e uma só tentativa contabilizada |
| Escolha pedagógica | `accuracy` isolada ou metas universais | Comparador multicritério com regras de bloqueio e justificativa |
| Confirmação de caderno | Recomendação = criação | Estados separados; link da plataforma só com origem comprovada |
| Aprendizagem retida | 90% em repetidas = domínio | Histórico posterior independente; incerteza declarada |
| Persistência | “Salvo” antes de readback | SHA/evento verificado; caso contrário, atualização pendente |
| CI/parecer | Contagem de testes existentes | Evidência do comportamento específico no SHA da candidata |

## 4. Entrega técnica por pacote: Definition of Done

Cada pacote deverá conter:
1. Escopo e arquivos alterados, compromisso de não interferir em frentes paralelas.
2. SHA base e SHA candidato, com comparabilidade e objeto congelável.
3. Contrato de entrada e saída, casos válidos e inválidos, migração quando houver.
4. Casos positivos, negativos, adversariais, concorrência/idempotência e replay quando relevantes.
5. Resultado real de testes locais/CI no SHA candidato, não mero comando esperado.
6. Readback do GitHub e resumo de alterações no handoff técnico.
7. Pendências, limitações, riscos e decisões humanas não resolvidas.
8. PR próprio, sem merge antes de autorização explícita.

**Stop-the-line:** resultados pessoais escritos sem autorização; perda ou rehash silencioso de histórico; violação de contrato de fonte/edital; inflação de acertos por duplicação; simulado pontuado sem dados suficientes; alegação de sincronização sem commit; bloqueio não detectado em decisão. Esses casos impedem homologação do pacote afetado.

## 5. Encadeamento recomendado por gates

```text
Reconferir HEAD PR #1 + fontes → ENG-00/ENG-01
                                  ↘ ENG-02 (ingestão e estados)
                                  ↘ ENG-03 (projeção de evidências)
                                  ↘ ENG-04 (fila determinística)
                                  ↘ ENG-05 (cadernos e feedback)
                    ENG-06 testa cada incremento e regressões
GP-0/GP-1/GP-2/GP-3 satisfeitos → ENG-07 (ciclo controlado)
Segurança + autorização + GP-4 → ENG-08 (piloto)
```

Não transformar este fluxo técnico em cronograma de estudo. A fila do estudante permanece adaptativa.

## 6. Acompanhamento de progresso da implementação

Registrar por pacote: `package_id`, `gate`, `candidate_sha`, `tests_ref`, `test_result`, `audit_status`, `blocked_reasons`, `next_action`, `approved_by` quando efetivamente autorizado.

Estados recomendados: **not_started**, **in_progress**, **blocked**, **implemented_unverified**, **tests_passed**, **independent_review_pending**, **approved_for_next_gate**. Não converter “testes passaram” em “aprovado para merge”.

A auditoria pedagógica deve responder se as decisões são coerentes com os casos de teste. A auditoria técnica deve responder se o código faz o que afirma sob entradas adversariais. Um resultado não substitui o outro.

## 7. Referências mínimas para a engenharia

- [Contrato consolidado v1.7](CONTRATO_PRONTIDAO_v1.7.md) e [reconciliação v1.7](MATRIZ_RECONCILIACAO_v1.7.md).
- [Fila v1.5](FILA_DINAMICA_v1.5.md), [protocolo de cadernos v1.6](CADERNOS_RESULTADOS_v1.6.md) e [modelo de evidências v1.2](MODELO_EVIDENCIAS_v1.2.md).
- [102 critérios de aceitação](CRITERIOS_DE_ACEITACAO.md) e [matriz de vinculação aos gates](RASTREABILIDADE_GATES_v1.8.md).
- [Prompt de transferência técnica v1.8](PROMPT_TRANSFERENCIA_TECNICA_v1.8.md) para iniciar outra sessão sem copiar longos históricos.

**Conclusão:** pacote pronto como material de handoff, não como implementação certificada. A sessão pedagógica não altera os scripts/harness nem abre merge.
