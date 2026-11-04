# UFMS — candidata documental v0.3-r3 (NÃO APROVADA)

Material de preparação corretiva decorrente da **reauditoria independente GQ-D REPROVADA** no objeto PR #5 SHA `652634b70a411ed4641cb7a202b0ae2f9a19ed1b`.

- `plan.md`: revisão **proposta** de TC-05, AC14, AC20, AC21, AC26, e da matriz Observable; conserva 27 critérios numerados.
- `checks-preview.md`: versão não aprovada correspondente; nenhum teste funcional executado.
- `APPROVAL_PRECEDENCE.md`: resolve precedência temporal do estado sem adulterar os bytes do PLAN r2 aprovado.
- `composition-lock.json`: composição por SHAs e árvores; main atual já inclui os PRs #1 e #2 mesclados, mas **sem prova de execução integrada**.
- `tools/verify_receipt_and_composition.py`: verificador fail-closed do recibo r2 e manifesto, com identidades imutáveis independentes do recibo (não substitui auditoria externa).
- `tests/test_receipt_and_proposal.py`: testes negativos de M-NEW-01/02/03 e condições adicionais.
- `NC_MATRIX.md`: rastreabilidade dos 9 achados originais e novos achados.

Não alterar ou reclassificar aprovado-r2. A próxima decisão é aprovação humana **específica** para o PLAN r3, precedida da leitura. Até nova aprovação: GQ-D REPROVADA, GQ-C NOT_RUN, GQ-O BLOCKED. Nenhum merge/deploy/credencial/escrita pessoal.
