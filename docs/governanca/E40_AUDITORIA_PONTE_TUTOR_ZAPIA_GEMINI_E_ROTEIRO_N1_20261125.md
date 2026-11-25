# E40: auditoria da ponte Tutor, Zapia e Gemini Notebook e roteiro do teste N1 (25/11/2026)

**Natureza:** registro de auditoria documental e **roteiro de teste**. Nada foi executado no Notebook, na Zapia nem no `entrada`. Pedido do proprietário de 25/11/2026.

## Cadeia decidida

Tutor (prompt em 5 campos, validado) -> comando `enviar_prompt_notebook` -> caixa de comandos -> fluxo promove (flag falsa hoje) -> Zapia abre o Notebook com a sessão do proprietário -> devolve texto literal e uma citação aberta -> Tutor verifica contra edital ou norma (S10-R7) -> só então entrega ao estudante.

## Decisões que valem (fonte)

D-26 (ponte só pela Zapia) e D-23 (Tutor escreve e verifica, Notebook gera rascunho, Zapia transporta): `PRODUCT.md`, `docs/especificacoes/S10_NOTEBOOK_TUTOR.md`. D-27 (Zapia liberada no Notebook), D-31 e E26 (sem `AUTORIZO` por mensagem; login e captcha da plataforma seguem). E15 e E17 (gate de entrega e filtros do prompt). E25, item 5a (o Tutor pode reformular questões como referência). E37 e E38 (enunciado e gabarito permitidos na entrega da Zapia ao Tutor; campos separados). E35 (harness: `enviar_prompt_notebook` do Tutor passa, o do Coach é recusado).

## Achados

1. `agents/TUTOR.md` (item 8 das práticas) ainda diz "o caminho direto tem prioridade; a Zapia entra só se o direto não existir (D-12)": contradiz a D-26 e a S10-R1. Arquivo de contrato: só muda com aprovação expressa.
2. Conflito aberto (E25, 5a): o validador recusa texto de questão no prompt; o proprietário permitiu reformular. O E25 remete a "S21", que não existe (a numeração está reservada ao ciclo de revisão). O C1 não resolve (vale para a entrega da Zapia ao Tutor).
3. O caminho de volta não tinha forma definida nem código: nada consumia ou verificava a resposta do Notebook (AT, S10-R6 e R7). Este lote entrega a **conferência offline** (`scripts/notebook_response_check.py`); o evento de retorno pela fila segue **proposta**.
4. N1 (teste real) nunca virou item de fila; falta o notebook descartável (a Lei 8.112 não existe em notebook, S10-R4).
5. A rotina de entrega da Zapia no código (`scripts/zapia_entrega.py`) **só executa `enviar_mensagem`**; `enviar_prompt_notebook` cai em `OPERACAO_NAO_SUPORTADA`. A execução no Notebook depende da instrução à Zapia (modelo), não de código.
6. O fluxo não promove (flag falsa): o fim a fim só na janela do piloto; hoje só o par sintético manual (`SINTETICO_MANUAL`).
7. Privacidade do Notebook (retenção, exclusão, revisão humana em conta pessoal) não verificada (S10-R8). Relatório de plataforma de 16/11 (autorrelato da Zapia, confiança C): a citação do chat aponta a fonte mas não certifica; houve paráfrase e extrapolação.

## O que este lote entrega (offline)

- `scripts/zapia_n1_prep.py`: dois comandos sintéticos do Tutor (pergunta que a fonte responde e **contraprova** que a fonte não traz), recibos `SINTETICO_MANUAL`, fonte pública (caput do art. 37 da CF) e o texto de instrução à Zapia; passam pelo validador do prompt e pela caixa.
- `scripts/notebook_response_check.py`: confere a resposta devolvida (forma fechada, vínculo com o comando, conteúdo perigoso, citação literal na fonte com até 2 frases; contraprova exige "não consta nas fontes" e nenhuma citação). Devolve só um código.
- `tests/test_zapia_n1.py`: 17 testes, mutações detectadas (4 de 5; a quinta, a repetição do filtro de instrução, é coberta pelo filtro geral).

## Roteiro N1 (ato do proprietário; a sessão não executa)

1. No clone atualizado: `python scripts/zapia_n1_prep.py --saida ~/n1` (gera os arquivos e `instrucao-zapia.txt`).
2. Colocar em `entrada`, à mão e com a **sua** sessão do `gh`: `n1-fonte.json` e `n1-contraprova.json` em `comandos/validados/`, os `*.recibo.json` em `comandos/recibos/` (com o nome do comando, sem `.recibo`).
3. Colar `~/n1/instrucao-zapia.txt` na conversa da Zapia (ela cria o notebook descartável com `fonte-n1.txt` como única fonte e grava `comandos/respostas/<nome>`).
4. Baixar as respostas e conferir: `python -c` com `notebook_response_check.conferir(...)` (o comando de conferência fica no PR de roteiro; a regra: `None` = pode seguir ao Tutor).
5. Tutor verifica a afirmação contra a fonte (S10-R7b) e relata. Apagar os arquivos de teste do `entrada` e o notebook descartável.

**Script do Termux (PR #202, 25/11/2026):** `bash scripts/termux/prova_n1.sh preparar` (passo 1, offline), `colocar` (passo 2: frase `COLOCAR N1`, recusa sobrescrever, leitura de volta byte a byte, só `comandos/`, nunca a fila) e `conferir` (passo 4, só leitura, não imprime o texto da resposta; resposta pendente ou `PARADO` não é sucesso). Usa a **sua** sessão do `gh`; nenhum token em argumento. `tests/test_termux_prova_n1.py` (14 testes, `gh` falso) e 8 de 8 mutações mortas. **A sessão não o executou**; o N1 real segue ato do proprietário.

**Kit com os campos C1 (PR #204, 25/11/2026):** o kit passa a gerar **três** comandos: além de `n1-fonte.json` e `n1-contraprova.json`, `n1-questao.json`, com o prompt proposto pelo subagent Tutor (art. 37 da CF, campos `enunciado_reformulado`, `alternativas` e `gabarito` C), aceito pelo validador e pela caixa. A conferência da resposta exige citação aberta da fonte; **não confere o gabarito** (a fidelidade do Notebook segue sem medida). `prova_n1.sh` coloca 6 arquivos e confere 3 respostas. Lacuna do Tutor: tópico e lacuna são **inferência** (estado E0).

## Limites

Sintético, um disparo, autorrelato da Zapia; não prova fidelidade para direito administrativo, nem a promoção pelo fluxo, nem várias execuções. A conferência da citação prova só que o trecho existe na fonte dada. Nenhum arquivo de contrato (`agents/`, esquema, gates) foi alterado.
