# GP-3 — recorte mínimo para uso pessoal (8 cenários)

**Data:** 05/11/2026  
**Base:** `main@e5560d452e2cf3ddb1c4e8cc8d6594a4c1cb96f2`  
**Finalidade:** definir um recorte de testes sintéticos útil ao harness pessoal, sem exigir implementação comercial ou cobertura artificial de todos os 102 critérios.

## Decisão de escopo

O catálogo original de 102 cenários permanece íntegro e rastreável. Para o primeiro uso pessoal, oito cenários prioritários formam o **GP-3-MVP8**. Os outros 94 continuam no backlog, sem obrigação de implementação imediata.

Este recorte é uma etapa de engenharia proporcional. **Não equivale à homologação integral de GP-3, GP-4, GP-5, GQ-D ou do Tutor/Coach em operação.**

## Os oito cenários essenciais

| # | Cenário | Teste canônico já existente | O que comprova |
|---:|---|---|---|
| 1 | PED-01 — tópico sem avaliação | `tests/test_evidence_projection.py::EvidenceProjectionTests.test_e0_without_results` | Ausência de evidência fica E0; não inventa domínio. |
| 2 | PED-02 — resultado apenas agregado | `tests/test_evidence_projection.py::EvidenceProjectionTests.test_e1_aggregate_only` | Resultado agregado não é distribuído artificialmente por tópico. |
| 3 | PED-12 — contagens inconsistentes | `tests/test_gp1_ingestion.py::GP1IngestionTests.test_igp12_rejects_incoherent_count_instead_of_guessing` | Dados contraditórios são rejeitados, sem correção silenciosa. |
| 4 | PED-14 — correção de tentativa | `tests/test_gp1_ingestion.py::GP1IngestionTests.test_igp13_correction_replaces_only_selected_attempt` | Correção substitui somente a tentativa vinculada na projeção. |
| 5 | FIQ-02 — fila reproduzível | `tests/test_decision_queue.py::DeterministicQueueTests.test_mesma_entrada_politica_e_as_of_reproduz_snapshot` | Mesmos dados, política e instante produzem o mesmo snapshot. |
| 6 | CDO-08 — normalização explícita | `tests/test_gp1_ingestion.py::GP1IngestionTests.test_igp12_explicit_excludes_convention_derives_total_15` | Convenção declarada permite normalizar 12 respondidas + 3 em branco sem adivinhação. |
| 7 | CDO-17 — escrita pessoal bloqueada | `tests/test_gp1_ingestion.py::GP1IngestionTests.test_attempt_results_remain_blocked_for_personal_persistence` | Resultado individual não é persistido enquanto a escrita estiver desabilitada. |
| 8 | PRD-09 — flag não basta | `tests/test_write_policy.py::WritePolicyTests.test_alteracao_da_flag_nao_autoriza_resultados` | Alterar apenas a flag não remove as demais condições de privacidade. |

## Execução

Os oito testes canônicos já fazem parte da suíte `python -m unittest discover -s tests -v`, executada pelo workflow `validate`. Não criamos cópias dos testes nem um segundo framework.

Para uma conferência isolada, a execução pode ser feita por referência de teste com `python -m unittest <modulo>.<classe>.<metodo> -v`; o relatório da CI completa continua sendo a evidência oficial do commit.

## Critério de aceite do MVP

- Os oito testes acima executam na CI do HEAD do PR e no commit pós-merge.
- Nenhum teste usa dados pessoais reais; fixtures são sintéticas.
- Nenhum resultado pessoal é gravado; `state/CURRENT.json` e eventos permanecem intocados.
- Falha em qualquer teste reprova o MVP8.
- Teste unitário aprovado não é chamado de cenário pedagógico E2E nem prova eficácia de aprendizagem.

## O que fica fora deste primeiro recorte

Os outros 94 IDs do catálogo, avaliação humana/adversarial de qualidade pedagógica, fontes normativas reais adicionais, integração Zapia/TEC/Qconcursos, persistência de resultados individuais e piloto consentido permanecem pendentes ou bloqueados conforme o gate aplicável.

**Estado honesto:** GP-3-MVP8 pode ser aceito como cobertura técnica mínima sintética após CI verde. GP-3 integral continua parcial; GP-4 real permanece bloqueado até haver um ciclo operacional autorizado e readback verificável. GP-5 exige avaliação consentida e não é substituído por fixtures.

**Aceite (07/11/2026):** o proprietário aceitou o GP-3-MVP8 como cobertura técnica mínima sintética, após CI verde. Não promove GP-3 integral, GP-4 nem eficácia pedagógica.

**Atualização 07/11/2026:** a rastreabilidade das oito referências é verificada por `tests/test_gp3_mvp8_rastreabilidade.py`. O restante do backlog (agora 46 cenários sem teste canônico na matriz, após SIM-01 a 10, CDO-14, FIQ-10, PRD-01 e PED-15) e o que impede cada frente estão em `MAPA_DESBLOQUEIO_FRENTES_20261107.md`.
