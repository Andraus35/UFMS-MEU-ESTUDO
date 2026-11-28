# E54 — Prova do despertar por rotina (28/11/2026)

**Natureza:** entrega do item `ENG-DESPERTAR` da fila. **Registro de prova, não contrato.** O detalhe está no E49 (item 24) e no E50 (plano); aqui ficam o resultado e os limites. (Não confundir com `E54_EMENDA_S6R6_ISSUES_20261128.md`, que é a emenda do token.)

- **Caminho D:** a Zapia grava a resposta e abre a issue `RESP eng-NNNN` (token com Issues, emenda E54) → uma **rotina com gatilho GitHub "Issue: Aberto"** no `entrada` (ambiente Default, sem conectores, prompt de `config/rotina_despertar_prompt.txt`, SHA-256 `666d66c7…dda7`) acorda uma **sessão nova** em cerca de 2 a 3 minutos → confere por código e grava `registro/`.
- **Provado (confiança B, quatro execuções, `eng-0012` a `eng-0015`):** a rotina acorda, roda o START, confere e grava só em `registro/` (`--auditar rotina` com `fora: []`). Ela grava em **branch `claude/adoring-turing-*`**, não na `main` (padrão do produto; decisão do proprietário: **manter**).
- **P8 (28/11/2026):** o `entrada` **voltou ao Claude GitHub App** por decisão do proprietário, para este despertar; isso supera a P8 "feita" de 19/11/2026 enquanto o despertar durar. A revogação do anexo e do App é ato dele.
- **Não provado:** o filtro de autor da rotina (a tela de detalhes não o mostra), o consumo do cursor `leitura/orquestrador.json`, o despertar do Tutor e do Coach além do registro, a estabilidade em muitas ativações e o consumo do limite diário de execuções.
- **Pendências dele:** conferir o filtro de autor; revisar o pedido de permissões pendente do App ("Review request") antes de aceitar; excluir pelo navegador os branches `claude/adoring-turing-*` (a exclusão por este ambiente foi recusada).
