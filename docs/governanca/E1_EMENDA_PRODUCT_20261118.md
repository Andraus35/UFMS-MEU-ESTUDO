# E1 — Emenda do PRODUCT.md (18/11/2026)

**Natureza:** registro da emenda do `PRODUCT.md`, tarefa E1 da fila de engenharia. **Situação: proposta aguardando a aprovação do proprietário**, que revê o diff no próprio PR; o `PRODUCT.md` é contrato (`.github/CODEOWNERS`) e **só vale depois do merge, que exige pedido explícito dele**. Este registro **não contém estado do ciclo** (PR, SHA, tarefa ativa): isso vive em `state/WORKFLOW.json`.

## O que muda no PRODUCT.md

| Onde | Antes | Depois | Origem |
|---|---|---|---|
| D-02 | A Zapia grava os resultados por comando do Tutor, pela API REST, com credencial própria | Marcada **emendada pela D-25** (o texto original fica, pela convenção de emendas do documento) | S6-R3, decisão de 17/11/2026 |
| D-18 | Tutor e Coach rodam no computador do proprietário, com chaves locais | Marcada **superada pela D-25** | S6-R1 |
| D-12 | "O Tutor deve acessar o NotebookLM diretamente; a Zapia só faz a ponte se isso não for possível" | Marcada **acesso ao Notebook emendado pela D-26** | decisão de 18/11/2026 |
| **D-25** (nova) | — | Execução em sessões do app Claude na nuvem, sem chave no modelo, **origem do comando não provada**; a Zapia entrega na fila de `entrada`, o fluxo de Actions é o **único escritor** de `dados`; aviso de rejeição no app e por e-mail; flag segue `false` | S6, aprovação de 17/11/2026 |
| **D-26** (nova) | — | O Tutor usa o Notebook **só pela Zapia, como ponte**; resolve o OPEN-10 | S10, resposta de 18/11/2026 |
| **D-27** (nova) | — | O proprietário **liberou a Zapia** (redação de 21/11/2026) a acessar livremente TEC, Qconcursos e Gemini Notebook, sem condição prévia; S9-R5 e S9-R6 valem por si | resposta de 18/11/2026 |
| F6, §4, PR-003, PR-012 | Escrita pela Zapia; caminho direto ao Notebook como prioridade | Alinhados à D-25 e à D-26 (a Zapia entrega, o fluxo grava; Notebook pela Zapia) | consistência |
| OPEN-09, OPEN-10 | Agentes no computador do proprietário; acesso direto não decidido | OPEN-09 reescrito para a nuvem com origem não provada; **OPEN-10 resolvido** pela D-26, ficam abertas a prova do caminho e a retenção do Google | consistência |

**Nada foi apagado:** os IDs D-xx, PR-xxx, OPEN-xx e E-xx continuam definidos (o gate e a coesão exigem), e o texto de D-02, D-12 e D-18 permanece.

## Redução de bytes (arquivamento sob demanda)

O `PRODUCT.md` tinha 40.886 bytes, a **74 bytes do limite de 40 KiB** do gate (40.960). Para caber a emenda, o texto integral das evidências E-01 a E-12 foi **movido sem alteração** para `docs/governanca/ARQUIVO_PRODUCT_EVIDENCIAS_E01_E12_20261118.md`; o `PRODUCT.md` mantém **um resumo de uma linha por evidência**, os IDs e o ponteiro. Resultado: 38.084 bytes, **cerca de 2,8 KiB de folga**. O orçamento fica fixado em teste (`tests/test_e1_emenda_product.py`: no máximo 38 KiB).

## O que a E1 NÃO inclui

- **Não altera** `AGENTS.md`, `agents/`, `settings.json`, `scripts/tool_gateway.py`, a S5 nem a S4-R2 (a S6 previu emendas à S5 e à S4-R2; ficam **fora** desta tarefa e são pendência declarada).
- **Não aprova** a ordem de caminhos proposta na S9 (exportação do TEC primeiro; Qconcursos só manual): essa decisão **segue sem resposta** do proprietário; a D-27 registra só o que ele respondeu.
- **Não registra** o consentimento v4 (outra tarefa) nem habilita a flag de escrita (C6).
- **Não prova** nada em conta real, na nuvem nem na Zapia.

## Limites

- A emenda é **texto de contrato**: o gate confere estrutura e bytes, **não** o sentido; a revisão do diff é humana.
- Fixar o orçamento só do `PRODUCT.md`: HANDOFF, ROADMAP e `AGENTS.md` **não** têm teto (o HANDOFF é muito maior) e ficam como lacuna.
- A D-25 **descreve** o desenho aprovado; sua eficácia depende das tarefas C3, C5 e C6 (provas reais, atos do proprietário).
