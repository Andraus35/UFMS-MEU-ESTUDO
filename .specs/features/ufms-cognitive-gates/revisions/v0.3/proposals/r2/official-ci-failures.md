# Evidências de validação oficial TLC — HEAD 677d91e

**Data:** 04/11/2026. **Objeto:** PR #5 commit `677d91e7c06f50ca9f3a96f0348454ad8de00896`.

Fontes primárias dos resultados: [run push 41867793245](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41867793245) e [run PR 41867808884](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41867808884). Os dois jobs usaram os scripts oficiais `validate_plan.py`/`validate_checks.py` pinados ao commit TLC `1da2195067c14ae5d44dc615b31cb26f50ebeb91` e tiveram falha real na etapa de validação. Download dos scripts e verificação do hash, assim como a integridade do PLAN e CHECKS aprovados, **PASS**.

| Artefato | Código | Erros | Warnings | Resultado |
|---|---:|---:|---:|---|
| PLAN v0.3-r1 canônico | 1 | 2 | 13 | FAIL |
| CHECKS v0.3-r1 canônico | 1 | 2 | 31 | FAIL |
| PLAN na cópia efêmera com aprovação | 1 | 2 | 13 | FAIL |
| CHECKS na cópia efêmera com aprovação | 1 | 1 | 31 | FAIL |

**Falhas oficiais específicas:**

1. PLAN, `Shape` L27: parser identifica nome de módulo não desenhado a partir de backticks de `(exists)` adjacentes. Resolver a notação e conferir o diagrama; não alterar o fluxo.
2. PLAN, `Surface` linha `evaluate-fixture <case-id>`: `Who` restringe o executor ao CI/local, mas seus `Status` não incluem código de negação para outros callers. Como o runner é uma CLI sintética sem endpoint remoto, a r2 propõe descrevê-lo como disponível a qualquer processo com acesso ao ambiente local isolado, sem inventar autenticação ou um quarto exit code.
3. CHECKS, Coverage `Matriz Surface (16)`: célula declara 16 membros mas não vincula nenhum Cn individual; deve listar os 16 com os respectivos checks.
4. CHECKS canônico: `plan.md` não contém `**Approved**:`; recibo externo de aprovação foi deliberadamente preservado e validado. A cópia efêmera com marcador removeu somente este erro de compatibilidade, não os demais.

**Warnings**: 13 no PLAN (principalmente labels dos nós do diagrama) e 31 no CHECKS (seletor unittest não reconhecido pela heurística TLC e linhas de prova que são revisão humana futura). Não foram convertidos em PASS nem automaticamente apagados.

**Atenção:** a validação formal executada **não equivale a homologação independente GQ-D**. Novas edições normativas exigem aprovação humana. A proposta r2 é *não aprovada*; CHECKS são preview. GQ-D REPROVADA, GQ-C NOT_RUN e GQ-O BLOCKED.
