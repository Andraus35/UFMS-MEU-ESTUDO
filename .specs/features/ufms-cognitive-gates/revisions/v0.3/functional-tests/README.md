# Testes funcionais isolados — Cognitive Gates C2/C3

**Escopo:** resolver fonte normativa conhecida e conferir trecho literal por `source_sha`, página e intervalo de caracteres `[start,end)`, na transcrição canônica do Edital UFMS 152/2026.

- `source_gate.py`: verificador determinístico sem rede, tokens, escrita ou publicação. Pina o Git blob `a4129cceabd20fc119625d71b1c1599b3ce644e1` da fonte original, regenera os 81 chunks pelo validador existente e retorna os IDs dos chunks que cobrem o intervalo exato.
- `test_source_gate.py`: testes com bytes reais do edital e contraprovas de fonte inexistente, SHA errado, página trocada, citação inventada, limites, mudança do original, manifesto e chunk alterados.
- O resultado `EVIDENCE_RESOLVED` **não é** `ALLOW` de publicação. `semantic_support=NOT_CHECKED` e `publication_authorized=false` permanecem mesmo quando a referência existe. O gate AC25/C25 ainda precisa verificar se o trecho prova a proposição.
- `NEEDS_EVIDENCE:SOURCE_NOT_FOUND` significa referência indisponível/incompatível; `DENY:BOOTSTRAP_INVALID` significa corrupção do registro canônico.
- O componente é executado na **árvore sintética do PR #5 com a main**, pois a branch histórica do PR #5 não contém isoladamente o harness técnico. A CI não efetua merge.
- Estes testes fornecem evidência **funcional isolada de resolução C2/C3**, não a prova completa no fluxo de Tutor/Coach. Os 27 checks de ponta a ponta, GQ-C, GQ-O e a GQ-D independente permanecem pendentes. PLAN r2 e proposta r3 não foram alterados.

Comando na árvore composta:

```sh
python -m unittest discover -s .specs/features/ufms-cognitive-gates/revisions/v0.3/functional-tests -p 'test_*.py' -v
```
