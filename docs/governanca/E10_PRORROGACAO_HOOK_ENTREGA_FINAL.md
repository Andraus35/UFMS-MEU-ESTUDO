# E10 — Prorrogação do hook Stop de entrega final (20/11/2026)

**Natureza:** registro de uma decisão do proprietário e da mudança mínima que a cumpre. **Altera `.claude/hooks/entrega_final.py`** (arquivo de contrato, `CODEOWNERS`): o merge do PR é a aprovação expressa dele. **Não** altera `.claude/settings.json`, `AGENTS.md`, `PRODUCT.md`, `agents/` nem flag.

## Decisão

Em 20/11/2026, por escolha em pergunta de fim de rodada, o proprietário decidiu **prorrogar o hook de entrega final até o fim do piloto**. A versão de 18/11/2026 valia só até 20/11/2026 (HOOK2).

## O que muda

| Item | Antes | Depois |
|---|---|---|
| `PRAZO` em `entrega_final.py` | 20/11/2026 | **18/12/2026** |
| Mensagens de contagem regressiva | "para 20/11" | "para 18/12" |
| Testes (`tests/test_hook_entrega_final.py`) | prazo 20/11 | prazo 18/12, e o hook segue ativo depois de 20/11 |

**Por que 18/12/2026 e não "o fim do piloto":** "fim do piloto" não é uma condição que o hook consiga ler sem depender de estado externo. A data de 18/12/2026 é o **vencimento relatado dos tokens** (`zapia_dados` e `zapia token`): sem renovação o piloto não existe depois dela, então a data é um **teto seguro**. Se o piloto fechar antes, o hook segue ativo até esse teto; se for preciso mais tempo, a renovação dos tokens e uma nova prorrogação são **decisões dele**, em PR próprio.

## Limites (S14-R17)

- O hook **falha aberto**: erro interno, comando ausente ou tempo esgotado permitem encerrar. Ele é **lembrete de entrega**, **não controle**; o controle é o CI, a proteção da `main` e o merge dele.
- Só **lê e avisa**: não faz merge, não grava, não usa rede nem credencial.
- **Não prova** a CI do GitHub no head nem a eficácia pedagógica.
- A S14-R17 manda levar a checagem para o CI; **esta prorrogação não substitui isso**, só mantém o lembrete enquanto o piloto não acontece.
