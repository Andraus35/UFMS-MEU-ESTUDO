# Execução adversarial IGP-12–14 — ciclo 7 (04/11/2026)

**Status:** contraprovas executadas com dados sintéticos no `scripts/core.py` do PR técnico. **Não** é homologação GP-1 nem implementação dos três contratos ausentes.

## Identidade congelada e reconciliação de concorrência

O PR técnico #1 estava no SHA `b312a1f9f2110d3d75810e45b414b85c8e775445` quando o experimento ocorreu. Durante a preparação da entrega, o HEAD passou a `1079d7aa2cadb97d099d1e478f9e83b36180a624`. O readback comparou os Git blobs e confirmou que **não mudaram**:
- `scripts/core.py` — `28649e5b649c239cb03d748ab5822c352ddfe1db`.
- `config/topics.csv` — `d733ec5af292934fa4efa0e892470c27603065f6`.
- `tests/test_harness.py` — `00288b757073e87b47c4ce7223704a168843b389`.

O PR pedagógico #2, branch `docs/especificacao-pedagogica-v1-2`, tinha HEAD inicial `e1e9248ea4f6c8b5a32de3dc46f47c4027aa4104`, draft e sem merge.

## Método reproduzido

Um script Python local `probe_igp_12_14.py`, blob Git `28db1cdd26515697fa8c87feedba00a15e4338a2`, checou **hashes Git dos dois insumos** antes de importar o módulo, carregou `config/topics.csv`, executou `validate_events` e `rebuild` em memória com exemplos fictícios e gravou recibo local JSON. SHA-256 desse recibo local: `0d3ba65dd9bb8f1f18d04dd6c63f6df8892f5c198b56c84ab8fedb4e71a2e9c9`. O [recibo resumido](RESULTADOS_NEGATIVOS_GP1_CICLO7_2026-11-04.json) não se declara uma cópia idêntica dos bytes originais. Não foram executados hooks, ações remotas do estudante ou gravações pessoais. O script executor está disponível como artefato local desta sessão, **não foi commitado no PR #2**.

## Evidência obtida

| Caso | Estímulo | Observação exata e significado |
|---|---|---|
| IGP-12 | Entrada externa com 12 respondidas, 3 em branco, convenção desconhecida e `total` canônico ausente | `ValueError: total out-fict-12 deve ser inteiro não negativo`. `core.py` rejeita a entrada bruta, mas isso não prova ausência de adaptadores em outros arquivos |
| IGP-13 | Duas tentativas com `attempt_id` diferente e o mesmo `caderno_id` | `ValueError: Resultado duplicado para caderno NOTEBOOK-FICT-01; use correção`. O validador não modela uma segunda tentativa independente com a mesma identidade de caderno |
| IGP-14 | `timestamp` válido, mas `attempt_at="nao-e-uma-data"` | Evento aceito; `rebuild` só projeta `last_event_at` pelo timestamp do evento, sem `last_attempt_at`. A data da resolução não é validada separadamente |

**Resultado observado: 3 GAP_REPRODUCED, 0 UNEXPECTED.** São confirmações negativas de lacunas, e **não** três PASS do contrato desejado. Os resultados anteriores das 11 fixtures executadas continuam documentados separadamente; o catálogo de 102 critérios não é aumentado.

## Nova informação do PR técnico

No novo HEAD `1079d7a...`, `memory/HANDOFF.md` registra decisão expressa do responsável: o **PDF local original** UFMS nº 152/2026, 47 páginas, SHA-256 `c758bb421ad848bf76757f6ece7a7b786e80e45123b80c3e01a13d0985f09675`, é **fonte primária suficiente para estudar agora**. Download de outra cópia remota não é pré-condição para consulta do edital original. Continuam necessários monitoramento de retificações, separação de versões e tratamento da inconsistência cronológica da página 13 para atos afetados. Portanto, **não usar GP-0 para bloquear o início dos estudos**.

## Saída exigida da implementação técnica

- **IGP-13 / ENG-01:** coexistência de tentativas independentes para um mesmo caderno externo e correções vinculadas à tentativa correta, preservando eventos legados.
- **IGP-14 / ENG-01:** `recorded_at` separado de `attempt_at`, com validação quando a data de tentativa for informada e valor desconhecido quando não for.
- **IGP-12 / ENG-02:** normalizador explícito e rastreável de relatórios externos, com estado pendente se a convenção não for verificável, sem inventar contagens.
- **ENG-06:** executar os testes do **novo comportamento desejado**, não só reproduzir a falha de capacidade. Evidenciar SHA de código, resultados e CI, com readback e revisão.

**Veredito:** GP-1 segue PENDENTE; GP-2 a GP-5 não homologados. Sem alteração do PR #1, `settings.json`, fonte canônica, `main` ou resultados pessoais; nenhum merge.
