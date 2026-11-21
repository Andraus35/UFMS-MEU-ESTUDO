# E11 — Alinhamento do hook de perguntas à regra de lote (21/11/2026)

**Natureza:** registro de uma decisão do proprietário e da mudança mínima que a cumpre. **Altera `.claude/hooks/perguntas_boas_praticas.py`** (arquivo de contrato, `CODEOWNERS`): o merge do PR é a aprovação expressa dele. **Não** altera `.claude/settings.json`, `AGENTS.md`, `PRODUCT.md`, `agents/` nem flag.

## Decisão

Em 21/11/2026 o proprietário decidiu que o merge ocorre **após um lote de entrega**, com micro tarefas coesas da mesma frente, e que outra frente exige mesclar antes (regra já formalizada no `AGENTS.md`, PR #145). Em pergunta de fim de rodada ele pediu alinhar o hook de perguntas, que ainda mandava "Uma tarefa por vez".

## O que muda

| Item | Antes | Depois |
|---|---|---|
| Texto de bloqueio do hook | "Uma tarefa por vez." | "Um lote por vez: micro tarefas coesas da mesma frente no mesmo PR; se o próximo trabalho for de outra frente, o merge vem antes (AGENTS.md)." |
| `tests/test_hook_perguntas.py` | sem checagem do trecho | confere o texto de lote e a ausência da frase antiga |

## Limites

- O hook **falha aberto** e só **lembra**: não faz merge, não grava, não usa rede nem credencial. A ordem da sequência (pendências, roadmap, fila) e o gatilho de entrega **não mudam**.
- O texto não substitui o `AGENTS.md`: em conflito, vale o contrato.
