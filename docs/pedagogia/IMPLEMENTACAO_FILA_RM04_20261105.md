# RM-04 — fila adaptativa determinística

**Data:** 05/11/2026  
**Base:** `main@e03c086bcd6b60e5bd60273cf2d50979775a4775`  
**Tarefa:** ENG-04 / GP-2  
**Natureza:** ranking informacional de candidatos, não cronograma ou previsão de aprovação.

## Contrato

`rank_candidates(candidates, as_of, source_commit, edital_version, policy)` recebe:
- snapshot temporal explícito com fuso;
- SHA Git de 40 caracteres e versão documental;
- candidatos com IDs, tópicos, cargos, estado de elegibilidade, justificativa e fatores explícitos;
- política versionada com pesos inteiros configuráveis.

## Regras determinísticas

- `blocked`, `pending_confirmation`, `temporarily_deferred` e `completed_observation` são excluídos do ranking, com motivo preservado.
- `eligible` e `needs_evidence` podem ser ranqueados; viabilidade zero exclui.
- Fatores desconhecidos são `null`, contribuem zero e aparecem em `unknown_factors`; não são inferidos.
- Pesos default são escolhas provisórias de engenharia, não parâmetros científicos. Podem ser alterados apenas por política com versão explícita e testes.
- Desempate é por `candidate_id`; não há sorteio por padrão.
- Um candidato compartilhado entre 523 e 324 é uma única linha com ambos os cargos, não duas observações.
- Snapshot SHA-256 deriva do payload canônico: `as_of`, commit, edital, política, ranking e exclusões.
- Resultado inclui score breakdown, justificativa, alternativa adiada, selecionado e até três alternativas.
- Nenhuma probabilidade de aprendizagem, retenção ou aprovação é emitida.

## Limites

A função não inventa fatores a partir de ausência de resultados. A camada que constrói candidatos precisa provar cada valor por edital, eventos e disponibilidade. Os pesos não foram calibrados com dados reais. O ranking não executa cadernos, não consulta TEC/Qconcursos e não persiste decisões. A seleção final deve continuar condicionada à validação humana das fontes e da viabilidade.
