# UFMS — PLAN → CHECKS → VERIFY sem BUILD obrigatório

**Resultado:** PASS apenas da estrutura documental (27/27 mapeamentos, 9 dimensões, 10/10 mutantes). **GQ-D final, GQ-C e GQ-O não homologados**.

O PLAN v0.2 aprovado e o CHECKS original foram **preservados byte a byte**, sem mudança de obrigações. A adaptação de fases está em `.specs/STATE.md` (AD-006), à luz da decisão do usuário de manter VERIFY e adiar BUILD de software tradicional.

## Arquivos

- `.specs/features/ufms-cognitive-gates/plan.md` — original aprovado, SHA-256 fixado.
- `.specs/features/ufms-cognitive-gates/checks.md` — 27 obrigações derivadas, provas funcionais ainda pendentes.
- `.specs/features/ufms-cognitive-gates/verification-gqd.md` — auditoria documental, achados, limites e veredito.
- `.specs/features/ufms-cognitive-gates/verify-c-protocol.md` — protocolo de avaliação do Tutor/Coach ainda não executado.
- `audits/verify-d-structure.json` — recibo da execução local.
- `audits/matriz-27-criterios.csv` — rastreabilidade individual das 27 obrigações por nível de prova.
- `fixtures/verify-c-scenarios.json` — 14 cenários adversariais sintéticos, marcados NOT_RUN.
- `tools/verify_spec.py` e `tests/test_verify_spec.py` — **auditor estrutural auxiliar**, não substitui o verificador oficial da skill nem um auditor independente.

## Como repetir

```sh
python -m unittest discover -s tests -v
python tools/verify_spec.py --root . --output audits/verify-d-structure.json
```

O script não faz requisições de rede, alterações de repositório remoto nem chamadas a LLM.

## Critério honesto de conclusão

- Auditor estrutural executado: **PASS**.
- Validador oficial TLC: **NOT_RUN**; instalador npm indisponível neste ambiente.
- Verifier verdadeiramente independente: **NOT_RUN**.
- Evals de modelo: **NOT_RUN**.
- Enforcement operacional: **BLOCKED**.

Não realizar merge nem gravar dados pessoais. Não declarar o projeto concluído.
