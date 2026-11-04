# Pré-gate Spec Lean — UFMS

Artefato técnico de **diagnóstico documental, não homologação** do PR #5.

- `VALIDACAO_PRE_GATE_TLC_2026-11-04.md`: achados vinculados ao objeto exato.
- `preflight-result.json`: recibo machine-readable com estados PASS/BLOCKED/WARN/NOT_RUN.
- `tlc_preflight_snapshot.py`: teste estático inspirado na condição literal do upstream, não o validador oficial.
- `tests/test_tlc_preflight.py`: dez testes adversariais do pré-gate.
- `test-run.txt`: saída dos testes.
- `PROMPT_REAUDITORIA_GQD_PR5.md`: orientação ao auditor independente.

Para executar em cópia local com `plan.md`, `checks.md`, `approval-receipt.json` e `composition-manifest.json` correspondentes: `python -m unittest discover -s tests -v` e `python tlc_preflight_snapshot.py --json preflight-result.json`. Não copiar dados pessoais para esse ambiente.
