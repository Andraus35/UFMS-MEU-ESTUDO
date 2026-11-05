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

## Evidência da primeira execução isolada C2/C3 — 04/11/2026

- **HEAD testado:** `dffc56625c92e7a563f81806ac07a91c920b3174`; merge sintético `8caec3a975221e613aaa015a6caf60b8db923141`; main `676dd5d3259c66ba97c3e7e3338451cfc4e5cd68`.
- **CI composta:** [41941588161](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41941588161): `success`, **12/12 testes isolados C2/C3**, **8/8 testes de composição** e **171/171 testes da suíte técnica**. Recibo e logs do teste estão no artifact do workflow.
- **Outras CIs do mesmo HEAD:** [harness 41941588160](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41941588160), [r2 formal 41941588156](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41941588156), [r3 documental 41941588174](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41941588174), [r2 push 41941579138](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41941579138), todas `success`.
- **Alcance:** duas obrigações C2/C3 verificadas **somente no componente isolado de resolução exata**, não na integração Tutor/Coach. As 27 provas funcionais de ponta a ponta continuam `NOT_RUN`; C25/apoio semântico, gateway, renderer e Zapia não foram executados.
- **Limite de segurança:** o gate prende a fonte a blob conhecido e preserva `semantic_support=NOT_CHECKED` / `publication_authorized=false`. A independência da avaliação e a presença no executor real continuam pendentes. Não declarar GQ-D/GQ-C/GQ-O aprovadas.
- **Checkpoint documental:** a publicação deste registro gerará novo HEAD, que exigirá nova CI e readback; não herdar automaticamente o resultado desta execução.

