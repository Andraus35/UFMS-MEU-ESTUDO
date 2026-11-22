# E17: COR-C, filtros de conteúdo (21/11/2026)

**Natureza:** registro do lote COR-C da fila de auditoria Tutor e Coach (`docs/governanca/FILA_AUDITORIA_TUTOR_COACH_20261121.md`). Nada altera `agents/`, `AGENTS.md`, `PRODUCT.md` nem o esquema de comandos. Todos os filtros são **heurísticos**: reduzem, não eliminam.

Módulo novo: `scripts/content_filters.py` (funções puras, folha de importação, sem ciclo): `tem_url`, `instrucao_embutida`, `mistura_de_scripts`, `desempenho_individual`, `desconfundir`.

| Achado | Correção | Prova |
|---|---|---|
| AT-3 (média) | `tem_url` recusa endereço sem esquema (`google.com.br`), ofuscado (`example[.]com`, `hxxp://`, `h**p://`), `www.` e IPv4; o prompt do Notebook usa o filtro (`URL_PROIBIDA`) | `tests/test_cor_c_filtros_de_conteudo.py` |
| AT-4 (baixa/média) | Instrução embutida com homóglifo cirílico/grego, leet e novos padrões (`act as`, `finja que`, `do anything now`); palavra com letra latina e cirílica/grega juntas é recusada (`CARACTERE_MISTO`); comando de prova em prosa no prompt é recusado (`QUESTAO_INTEGRAL`, via `agent_commands.comando_de_questao`, sem recusar "os incisos (a) e (b)") | idem; `tests/test_prompt_para_comando.py` (corpus legítimo sem falso positivo) |
| AT-5 (baixa) | `enviar_mensagem` recusa URL (`PARAMS_URL`) e instrução embutida (`PARAMS_INSTRUCAO_EMBUTIDA`) no validador e na caixa, como o verificador de entrega já fazia; `test_command_box` deixa de aceitar "IGNORE PREVIOUS INSTRUCTIONS" | idem |
| AT-6 (baixa) | `objetivo` do handoff recusa URL, instrução embutida, homóglifo e resultado pessoal (`TEXTO_COM_URL`, `TEXTO_COM_INSTRUCAO_EMBUTIDA`, `TEXTO_COM_RESULTADO_PESSOAL`); `notebook_prescriber` recusa `objective` com CPF, URL ou instrução | idem |
| AT-7 (baixa) | `platform_read_guard`: os efeitos em inglês (`delete`, `remove`, `update`, `submit`, `logout`, `settings`, `account`, etc.) entram em `SEGMENTOS_COM_EFEITO`; URL de leitura comum segue liberada | idem |

**Limites (declarados):**
- Heurística: um homóglifo fora da tabela, ofuscação nova ou texto de questão parafraseado ainda podem passar; a defesa final é tratar texto como dado (S5-R4) e o verificador de entrega.
- `mistura_de_scripts` só pega homóglifo dentro da mesma palavra; texto todo em cirílico não é recusado por esse filtro.
- O filtro de domínio usa lista de sufixos (`TLDS`); sufixo fora da lista passa.
- A lista de efeitos em inglês é por segmento exato; uma ação escrita de outro jeito (`/del/3`) não é detectada.
- Nada foi testado com serviço real nem com texto real do aluno.
