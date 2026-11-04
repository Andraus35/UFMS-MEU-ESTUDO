# Handoff pedagógico — ciclo 7

**Checkpoint:** 04/11/2026, America/Campo_Grande. PR #2 `docs/especificacao-pedagogica-v1-2`, HEAD anterior `e1e9248ea4f6c8b5a32de3dc46f47c4027aa4104`, aberto/draft e sem merge. A nova identidade de commit requer readback remoto.

## Evidência obtida e publicada

- [Execução negativa IGP-12–14](EXECUCAO_NEGATIVA_GP1_CICLO7_2026-11-04.md): **3 GAP_REPRODUCED, 0 UNEXPECTED**, com eventos fictícios em memória, SHA Git dos insumos e observações efetivas.
- [Recibo estruturado](RESULTADOS_NEGATIVOS_GP1_CICLO7_2026-11-04.json), `README.md` e este `HANDOFF.md` sincronizados no commit.
- Executor Python local possui Git blob `28db1cdd26515697fa8c87feedba00a15e4338a2`; **não foi commitado**. O JSON remoto é resumo, não recibo local byte-idêntico.
- Os 102 critérios de aceitação e 14 fixtures anteriores continuam preservados; 11 PASS do ciclo 5 e 3 lacunas reproduzidas no ciclo 7 **não equivalem** a aceitação do GP-1.

## Mudança concorrente

O PR #1 avançou de `b312a1f9f2110d3d75810e45b414b85c8e775445` para `1079d7aa2cadb97d099d1e478f9e83b36180a624`; `core.py`, `topics.csv` e `test_harness.py` permanecem em seus blobs exatos conferidos. Nenhum arquivo do PR #1 foi editado por esta sessão.

O handoff técnico do novo HEAD confirma que o edital local 152/2026 (47 páginas, SHA-256 `c758bb421ad848bf76757f6ece7a7b786e80e45123b80c3e01a13d0985f09675`) é utilizável para **iniciar estudos imediatamente**. A falta de outra cópia remota não impede o uso da versão original; monitorar retificações separadamente.

## Próxima ação e bloqueios

A **engenharia** deve implementar ENG-01/ENG-02/ENG-06 com testes de tentativa independente, datas distintas e adaptador de relatórios, por SHA, sem habilitar gravação pessoal. GP-1 permanece pendente; GP-2–GP-5 não homologados. Não repetir análises de lacunas sem novas implementações. Não realizar merge ou escrever dados do estudante. Confirmar HEAD do PR #2, README, handoff e CI antes de qualquer próximo ciclo.
