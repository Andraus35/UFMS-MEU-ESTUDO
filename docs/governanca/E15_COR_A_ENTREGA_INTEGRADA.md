# E15: COR-A, entrega integrada (21/11/2026)

**Natureza:** registro do lote COR-A da fila de auditoria Tutor e Coach (`docs/governanca/FILA_AUDITORIA_TUTOR_COACH_20261121.md`). Nada altera `agents/`, `AGENTS.md`, `PRODUCT.md` nem o esquema de comandos.

| Achado | Correção em `scripts/delivery_gate.py` | Prova |
|---|---|---|
| AT-1 (alta) | COMANDO `enviar_prompt_notebook` passa por `notebook_prompt_validator.conferir_parametros` (hash, forma canônica, filtros); recusa `comando_prompt_notebook_invalido` | `tests/test_cor_a_entrega_integrada.py` (o gate recusa tudo o que o validador recusa) |
| AT-2 | **Formato único** do que a Zapia recebe: `{prompt, prompt_sha256}` (`FORMATO_PROMPT`); o envelope `PROMPT_NOTEBOOK` com o rascunho de 5 campos é recusado (`prompt_notebook_forma_nao_canonica`): o rascunho é forma de AUTORIA, passa por `preparar` | idem |
| AC-1 (alta) | Idade da projeção na entrega (S15-R5): LEMBRETE e COMANDO `criar_lembrete` usam 24 h com instante (`projecao_velha_para_prazo`, `projecao_sem_instante_para_prazo`); as demais entregas avisam acima de 72 h (`projecao_defasada`); projeção no futuro recusa; **limites 24 h e 72 h confirmados pelo proprietário** | idem |
| AC-2 | `lembretes_verificados` agora é `{hash: {corpo, atividade_ids}}`: o hash é recalculado e os ids do COMANDO têm de ser exatamente os do lembrete (`comando_vinculo_hash_nao_confere`, `comando_lembrete_ids_diferentes_do_lembrete`); a forma antiga, só com hashes, recusa (`comando_vinculo_sem_ids_verificados`); o resultado do LEMBRETE traz `lembrete_atividade_ids` | idem |

**Efeito em fixtures:** `PROJ` e `PROJECAO` passam a ter `gerado_em` com instante UTC; o prompt válido dos testes e do `delivery_eval` é o canônico (`preparar`); `delivery_eval` ganhou os casos KL3 a KL6, KP1, KP2 e KI1.

**Limites:** o verificador confere a forma e a coerência; não prova que a Zapia o use nem que o runtime chame `verificar_entrega` com o contexto certo (`lembretes_verificados` e `projecao` vêm de quem chama).
