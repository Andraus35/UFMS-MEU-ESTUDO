# RM-07 — reauditoria independente das 9 NCs e 27 checks

**Data:** 05/11/2026  
**Objeto atual:** `main@8fda9754846b4fba65cd88244260653cbb606720`  
**Objeto legado:** PR #5, fechado sem merge, head `9f1b347e755c82f15089470749d9d33524167c1f`, base original `c020f78ba07ebb4e2949021b45a7f9b8f2c26d42`.  
**Comparação:** PR5 branch 22 commits ahead e 587 behind a main atual. Proibido merge em lote.

## Resultado executivo

- **9 NCs reavaliadas; 0 encerradas na main.**
- **3 abertas sem mitigação suficiente na main.**
- **6 com mitigação parcial em branch candidata, não integrada.**
- **27 checks funcionais end-to-end: 0 PASS / 27 NOT_RUN.**
- GP-3 permanece bloqueado. RM-07 não homologa GQ-D, GQ-C ou GQ-O.

## Reauditoria por NC

| NC | Severidade | Estado | Conclusão |
|---|---|---|---|
| GQD-01 | P0 | OPEN | A main possui política de interação e bloqueio de escrita, mas não gateway confiável com aprovação autenticada e vínculo de ferramenta, destino e parâmetros; falta prova de zero efeitos. |
| GQD-02 | P1 | OPEN | Há gates estruturais, não quatro mutantes semânticos independentes com oráculos humanos auditados. |
| GQD-03 | P1 | PARTIAL — NOT IN MAIN | PR5 contém manifesto e CI de composição sintética bem-sucedida (run 41952566820), mas o manifesto declara NOT_RUN_FOR_COMPOSITION e a branch está 587 commits atrás. |
| GQD-04 | P1 | PARTIAL — NOT IN MAIN | PR5 contém source_gate/fact_gate para spans e fatos curados; não é verificador semântico geral. Não integrado à main. |
| GQD-05 | P1 | OPEN | Não existe gateway externo com rate limit atômico, prova concorrente e zero chamadas após DENY. |
| GQD-06 | P1 | PARTIAL — NOT IN MAIN | safe_renderer da PR5 cobre prévia local e alguns estados; não demonstra os cinco estados de execução, quatro exits, falha de dependência pré-execução e política de retry integrada. |
| GQD-07 | P1 | PARTIAL — NOT IN MAIN | Há recibo/testes do snapshot r2 na PR5, mas a própria matriz mantém o vínculo da aprovação original como NÃO VERIFICADO. Alterações r3 exigem novo aceite. |
| GQD-08 | P1 | PARTIAL — NOT IN MAIN | Token do renderer candidato vincula estado/fonte/canal/destinatário, porém só em local_preview; não há gateway/rota externa na main nem prova de bypass/zero publicação. |
| GQD-09 | P2 | PARTIAL — NOT IN MAIN | Validadores Spec Lean e CI documental passaram no HEAD candidato (run 41952566886), mas não estão integrados à main e a reauditoria independente final segue pendente. |

A matriz JSON registra os detalhes, os artefatos candidatos e as referências dos 27 seletores. Evidência em branch candidata não é correção na main.

## 27 checks funcionais

O arquivo CHECKS r2 da PR5 declara explicitamente **0 PASS / 27 NOT_RUN** para a feature. Os runs de composição, validação documental e testes unitários isolados não alteram esse estado:
- run 41952566820: composição sintética read-only, success;
- run 41952566886: validação documental Spec Lean, success;
- run 41952566861: harness, success.

C2/C3, C25 e C26 têm evidência isolada no candidato, mas não integração end-to-end Tutor/Coach, gateway, Zapia ou efeitos externos. A matriz conserva os 27 como NOT_RUN_END_TO_END.

## Decisão

Não mesclar PR5 nem cherry-pick em massa. Sua divergência de 587 commits exige extração por arquivo/contrato, revisão de dependências e novos testes na main. NCs P0/P1 que exigem gateway, isolamento de segredo, nonce, rate limit e autorização não podem ser fechadas por documentação ou mocks.

Próximos gates:
1. Novo plano/aceite humano antes de alterar obrigações normativas r3.
2. Implementar gateway confiável e renderer integrado antes de autorizar efeitos.
3. Executar os 27 checks end-to-end no SHA exato, com mutantes e zero-effect assertions.
4. Auditor independente reexecuta GQ-D; GQ-C e GQ-O continuam NOT_RUN/BLOCKED até evidência.

Nenhum resultado pessoal foi acessado ou gravado; nenhum efeito externo foi executado.
