# E18: COR-D, G-MOT na entrega, fail-closed e léxico de desempenho (22/11/2026)

**Natureza:** registro do lote COR-D da fila de auditoria Tutor e Coach (`docs/governanca/FILA_AUDITORIA_TUTOR_COACH_20261121.md`). Nada altera `agents/`, `AGENTS.md`, `PRODUCT.md` nem o esquema de comandos; o texto da IMC em `agents/COACH.md` segue exigindo aprovação expressa. Tudo continua **heurístico**.

| Achado | Correção | Prova |
|---|---|---|
| AC-5 (média) | `delivery_gate._corpo` chama `gates_mot.verificar_mensagem` (`frase_proibida_gmot`, também no texto livre do COMANDO); paráfrases novas (`Garanto que você passa`, `Aprovação garantida`, `Você tem TDAH`, `Pare a medicação`, `Você é um preguiçoso`); a janela de negação passa de 15 para 40 caracteres e aceita `ninguém`, `nenhum`, `sem` (`Ninguém pode garantir aprovação`, `Não quero que você durma menos` deixam de disparar) | `tests/test_cor_d_gmot_e_desempenho.py`; casos KG1 e KG2 em `scripts/delivery_eval.py` |
| AC-6 (média/baixa) | `verificar_intervencao` falha fechado em tipo não booleano (`SOFRIMENTO_CAMPO_NAO_BOOLEANO`, `EFICACIA_DECLARADA_NAO_BOOLEANA`, `APOIO_SOCIAL_CAMPO_NAO_BOOLEANO`); `comportamento_alvo` e `indicador` passam pelos gates lexicais e pelos filtros de URL e instrução (`ALVO_OU_INDICADOR_COM_CONTEUDO_PROIBIDO`) | idem |
| AC-7 (baixa) | Desempenho: `40٪`, `por cento`, `taxa de 0.4`, `12 de 20 acertos` e fração `12/20` (o segundo número passa de 12, para não pegar data); disponibilidade: `Há cadernos prontos`, `existem questões suficientes`; `enviar_mensagem` no COMANDO limitada a 500 caracteres (`mensagem_acima_do_limite`) | idem |

**Efeito em outros arquivos:** `scripts/delivery_eval.py` ganhou KG1 e KG2 (todo código do portão precisa de caso); o teste de imports offline do `delivery_gate` passa a listar `gates_mot`.

**Limites (declarados):**
- Paráfrase fora dos padrões ainda passa; a negação por janela pode deixar passar uma frase proibida depois de "não" na mesma oração (trade-off assumido).
- A fração `10/10` ou `5/12` escapa porque se confunde com data; `12/20` sem contexto pode ser data inválida e é recusada.
- O AC-7 sobre `ORIENTACAO` com `12 de 20 acertos` não foi reproduzido na sessão principal (já era recusado); a correção cobre as formas do relato.
- Os gates G-MOT-20 e G-MOT-22 seguem não gateáveis (auditoria por amostra). Nada foi testado com serviço real nem com texto real do aluno.
