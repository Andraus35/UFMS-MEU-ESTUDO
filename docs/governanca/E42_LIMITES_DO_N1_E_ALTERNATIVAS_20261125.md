# E42: limites do N1 e alternativas implementadas (lote VOLTA-N1, 25/11/2026)

**Natureza:** registro e roteiro, não contrato. Decisões do proprietário de 25/11/2026 ("Resolver limites com alternativas"). Não altera `agents/`, `AGENTS.md`, `PRODUCT.md`, o esquema de comandos nem a caixa (que continua **recusando** `signature`, S6-R7).

| Limite | Alternativa escolhida | O que foi entregue | O que continua NÃO provado |
|---|---|---|---|
| 1. A volta Tutor→Coach dependia da sessão | Orquestrador offline | `scripts/volta_n1.py`: confere as respostas da Zapia (`notebook_response_check`), gera `relatorio_tutor` (**sem** o texto do Notebook), `entrada_coach` (só contagens) e passa a proposta do Coach pela caixa, recusando eco do Notebook e qualquer coisa que não seja `enviar_mensagem` do Coach | Quem **dispara** a execução segue sendo uma sessão; o Tutor e o Coach (LLM) continuam subagents chamados à mão |
| 2. Gabarito sem conferência | Conferir contra a fonte colada | Campo `ancora_gabarito` (trecho da fonte que sustenta o gabarito, registrado pelo Tutor em `config/propostas_tutor_n1.json`, verificado como parte da fonte); `conferir(..., ancora_gabarito=)` recusa citação que não a contenha (`CITACAO_NAO_SUSTENTA_GABARITO`) | Prova que o Notebook **citou a passagem certa**, não que a resposta dele acertou; só serve a fonte curta |
| 3. Origem `tutor` só declarada | Aprovação destacada por chave fora do modelo | `scripts/aprovacao_comando.py` (Ed25519 sobre o `hash_corpo`, domínio próprio, guarda da chave de `agent_keys`) e `scripts/termux/aprova_n1.sh` (`chave` e `aprovar`: mostra o prompt, frase **APROVO N1**, grava `comandos/aprovacoes/`). `volta_n1.py --aprovacoes --publica` marca `aprovada_pelo_proprietario` ou derruba o veredito | Prova que **a chave dele** aprovou **aquele hash**, **não** que o Tutor escreveu o texto; a verificação é posterior (o hook da Zapia não executa Ed25519); o **ato** de gerar a chave e aprovar é dele |
| 4. Notebook trava; resposta é autorrelato | Segunda via: captura dele | `volta_n1.py --captura` aceita `{relogio_visivel: true, descricao}`; sem ela a confiança é `B`, com ela `B+captura` | A captura é ato dele e o código **só a registra**; não verifica a imagem |

## Roteiro do proprietário (depois do run)

1. `bash scripts/termux/aprova_n1.sh chave` (uma vez) e guardar a chave **pública** impressa. 2. `bash scripts/termux/aprova_n1.sh aprovar`, ler os prompts e digitar `APROVO N1`. 3. Trazer a chave pública e, se quiser, o JSON da captura. 4. A sessão roda `python scripts/volta_n1.py --entrada <clone> --meta <meta.json> --fonte <fonte> --aprovacoes <pasta> --publica <hex> [--captura c.json]`.

## Testes

`tests/test_volta_n1.py` (13), `tests/test_aprovacao_comando.py` (9), `tests/test_termux_aprova_n1.py` (7) e as novas em `tests/test_zapia_n1.py`; mutações do código novo mortas (as duas vivas em `aprova_n1.sh` são equivalentes: a guarda da chave e o `O_EXCL` da geração já recusam).

## Limites que seguem

Autorrelato da Zapia (B); uma execução; qualidade pedagógica por revisão humana; o aluno está em E0 (nenhum dado do aluno entra nesta cadeia).
