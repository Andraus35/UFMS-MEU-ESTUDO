# Matriz de correções — reauditoria adversarial r2 (objeto congelado)

**Objeto reprovado:** PR #5 `652634b70a411ed4641cb7a202b0ae2f9a19ed1b`.
**Nova proposta:** v0.3-r3 (não aprovada). **Nenhuma NC será encerrada por autoauditoria.**

| NC | Parecer recebido | Ação nesta proposta | Prova auxiliar (não GQ-D) | Encerramento independente |
|---|---|---|---|---|
| GQD-02 / R2-11 | 3/3 mutantes do recibo sobreviveram | Âncoras externas + auditor de recibo/lock; rejeitar M-NEW-01/02/03 | testes negativos em `tests/test_receipt_and_proposal.py` | PENDENTE |
| GQD-03 | Manifesto antigo de composição | `composition-lock.json` fixa PR5 auditado, main já integrada e commits/árvores PR1/PR2 históricos, com digest | integridade/identidade de componentes; **checkout composto NOT_RUN** | PENDENTE |
| GQD-06 / R2-12 | AC14 inválido misturado ao 202 | PLAN r3 e CHECKS-preview r3 distinguem `202 NEEDS_APPROVAL` ausente de `403 DENY:AUTH_MISMATCH` inválido | testes de correspondência texto/matriz | PENDENTE |
| GQD-07 / R2-10 | Estado de aprovação contraditório | `APPROVAL_PRECEDENCE.md` + `CURRENT.md` apontando r2 aprovada/r3 não aprovada; preservação do PLAN r2 | fonte/hashes/escopo; proibir status sem âncora | PENDENTE |
| GQD-08 / R2-13 | Renderer sem revogação/concorrência | TC-05 e AC26 r3: emissor, epoch, revogação, consumo atômico e UNCONFIRMED | oráculos S-NEW-03/04; **execução real NOT_RUN** | PENDENTE |
| GQD-01, 04, 05, 09 | Encerradas documentalmente pelo auditor | Preservadas na versão r2 aprovada, sem reabrir nem alegar operação | C1–C27 continuam 0 provas funcionais | Reavaliar no HEAD futuro |

**Validação formal:** PLAN/CHECKS r2 passaram TLC com warnings. A r3 **não** tem aprovação humana, portanto o validador de CHECKS exigirá aprovação. Nenhum CI verde da r2 homologa a r3.
