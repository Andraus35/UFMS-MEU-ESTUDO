# E14: gates G-MOT verificáveis e derivado paginado do Manual (GAP-E, 21/11/2026)

**Natureza:** registro do lote GAP-E (GE-1 e GE-2 da fila de gaps). **Proposta**; nada aqui altera `agents/`, `AGENTS.md` ou `PRODUCT.md`.

## GE-1: derivado paginado do Manual (`scripts/manual_pages.py`)
- O repositório PÚBLICO guarda só um **manifesto** por página (número, SHA-256 do texto normalizado, contagem de palavras). **Nenhum texto do livro** entra (direito autoral; decisão do proprietário de 21/11/2026).
- `montar_manifesto` roda **onde o texto está** (ambiente privado do proprietário); só o manifesto sai de lá.
- `prova_de_leitura`: página só conta como lida se o texto aberto bate com o hash (a truncada, como a das p. 148 a 153, aparece como `divergente`).
- `conferir_citacao`: 2 a 25 palavras, literal na página aberta, página conferida pelo hash. `afirmar_leitura`: só se afirma ter lido o que foi aberto. `suspeitas_de_truncamento`: sequência de páginas quase vazias.
- **Não feito (ato do proprietário):** gerar o derivado paginado e o manifesto reais na pasta privada e rodar a prova de leitura nas p. 148 a 153. O código foi testado só com dados sintéticos; a S18-R14 segue com "prova de leitura pendente".

## GE-2: gates G-MOT (`scripts/gates_mot.py`)
| Classe | Gates | Como verifica |
|---|---|---|
| Estruturais (10) | 01, 02, 03, 06, 07, 13, 14, 17, 18, 19 | campos do registro de intervenção (formato fechado PROPOSTO): evidência e incerteza, dimensões separadas, alvo e indicador, base da eficácia, encaminhamentos, consentimento, revisão |
| Lexicais (10) | 04, 05, 08, 09, 10, 11, 12, 15, 16, 21 | frase proibida na mensagem ao candidato; **heurística** (negação na mesma oração não dispara) |
| Não gateáveis (2) | 20, 22 | dependem de juízo; ficam para a auditoria por amostra (S14-R14) |

Estruturais provam presença e coerência dos campos, não a verdade do registro. Os gates **não homologam** o harness.

## Texto PROPOSTO para o perfil do Coach (NÃO aplicado)
> Antes de enviar mensagem de acompanhamento ou registrar uma intervenção de IMC, o Coach passa o texto e o registro pelos gates G-MOT verificáveis (`scripts/gates_mot.py`). Falha em gate exige correção, coleta adicional ou abstenção. Os gates G-MOT-20 e G-MOT-22 dependem de juízo e seguem sob auditoria por amostra.

**Aplicar esse texto em `agents/COACH.md` exige a aprovação expressa do texto e do merge do proprietário, em PR próprio.**
