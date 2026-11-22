# E19: COR-E, endurecimento menor (22/11/2026)

**Natureza:** registro do lote COR-E, último da fila de correção da auditoria Tutor e Coach (`docs/governanca/FILA_AUDITORIA_TUTOR_COACH_20261121.md`). Aberto depois que o proprietário liberou a COR-E em 22/11/2026, em paralelo à espera da prova real da Zapia (ZAPIA-F1 segue pendente e à frente na fila). Nada altera `agents/`, `AGENTS.md`, `PRODUCT.md` nem o esquema de comandos.

| Achado | Correção | Prova |
|---|---|---|
| AT-8 (info) | Lista de permissão para `ler_arquivo_repositorio` em `command_params_schema.py`: prefixos `edital/`, `docs/`, `config/`, `rules/`, `agents/` e os arquivos `AGENTS.md`, `ROADMAP.md`, `PRODUCT.md`, `README.md`, `memory/HANDOFF.md`; `state/CURRENT.json` e o resto (`state/`, `scripts/`, `.github/`, `tests/`, `settings.json`, `comandos/`) são recusados (`PARAMS_CAMINHO_FORA_DA_LISTA`); travessia e oculto seguem recusados antes (`PARAMS_CAMINHO_INVALIDO`) | `tests/test_cor_e_endurecimento_menor.py` |
| AC-9 (baixa), citação | `manual_pages.conferir_citacao` exige sequência contígua de **palavras inteiras** da página (fragmento no meio de palavra não casa; pontuação não conta) | idem |
| AC-9 (baixa), hash | `hash_pagina(texto, pagina)` leva o **número da página** no hash: páginas de texto idêntico não compartilham hash. **Muda o formato do manifesto**; o manifesto real do Manual ainda não existe (pendente do proprietário), então nenhum manifesto gerado fica inválido | idem |
| AC-9 (baixa), idade | `session_read_guard.conferir_idade` com data sem hora em orientação usa a idade **máxima** (desde 00:00 UTC): `2026-11-18` em 21/11 12:00 dá 84 h e avisa; prazo continua recusando data sem hora | idem |

**Proposta a confirmar pelo proprietário:** a lista de permissão acima (AT-8 é decisão de política; a lista é a mais restrita que ainda atende ao que Tutor e Coach precisam ler).

**Limites:** a lista de permissão vale na validação de params, não prova que o leitor use só esses caminhos; a citação por palavra ignora pontuação e caixa de pontuação, não a de letras; o formato novo do manifesto exige que o proprietário gere o manifesto real com este código.
