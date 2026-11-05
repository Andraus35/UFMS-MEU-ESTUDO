# Monitor FAPEC — rotina integrada, somente leitura

## Estado atual (05/11/2026)

- O PR #21 integrou o workflow `.github/workflows/monitor-fapec.yml` à `main`.
- O workflow declara agendamento diário `17 12 * * *` UTC e acionamento manual por `workflow_dispatch`.
- O workflow usa `contents: read`, checkout com `persist-credentials: false`, não usa secrets e não executa em push/PR.
- A existência do cron no YAML e os testes estáticos de CI **não provam** que um evento agendado foi executado. Até ser observado um run do GitHub Actions com `event=schedule`, o estado é **NOT_VERIFIED**.
- O último registro de observação no inventário oficial é de 04/11/2026. Não afirmar que o portal foi consultado hoje sem um run correspondente.

## Escopo e códigos

A sonda consulta somente uma página pública da FAPEC:
https://portal.concurso.fundacaofapec.org.br/edital/ver/22

- **Código 0 — `no_change_observed_on_single_page`:** a listagem observada não apresentou mudança detectável. Não prova ausência de retificações em outras fontes.
- **Código 2 — `needs_manual_review`:** possível publicação, mudança de listagem ou marcador de retificação; job falha e exige conferência humana.
- **Código 3 — `unverifiable`:** falha de acesso, resposta inesperada ou identidade do concurso não confirmada; job falha. Nunca interpretar como estabilidade.
- Qualquer outro código inesperado também falha.

O monitor não baixa automaticamente PDFs, não verifica exaustivamente o boletim UFMS/DOU, não altera o registro de fontes e não incorpora retificações ao edital canônico.

## Prova automatizada

O PR #29 acrescenta teste CLI ponta a ponta usando `--fixture` e subprocesso local, sem rede:

- valida código 0 para página estável;
- valida código 2 para publicação candidata;
- valida código 3 para página não verificável;
- confere `writes=false`, `normative_revision_verified=false` e escopo de página única;
- compara hashes dos arquivos canônicos antes/depois da execução para detectar mutação do edital, manifesto ou registro de fontes.

Esses testes provam o contrato da execução CLI com fixtures, não a execução real do cron nem a cobertura de outras fontes.

## Como comprovar o cron real

1. Abrir **Actions** no repositório.
2. Selecionar **Monitorar retificações FAPEC (sonda)**.
3. Identificar uma execução cujo evento seja `schedule` e cuja branch seja `main`.
4. Conferir o SHA do commit, o resultado JSON e o log do job.
5. Registrar o run ID e o SHA observado no handoff.

Um acionamento manual `workflow_dispatch` comprova somente a execução manual; não substitui um run com `event=schedule`. Até essa evidência existir, manter SIM-03 em andamento.

## Preservação e segurança

- PDF original UFMS 152/2026: imutável; identidade e hash permanecem sob os validadores `validate_fontes_oficiais.py` e `chunk_edital.py`.
- Alerta `ALERTA-DOC-01`: Anexo II, p. 13, datas conflitantes preservadas. Não corrigir por inferência.
- Qualquer publicação candidata requer obtenção dos bytes oficiais, SHA-256, verificação da origem e revisão humana em etapa separada.
- Nenhum resultado pessoal, token, secret, mensagem Zapia/Telegram ou escrita externa é utilizado.
- A CI central é offline; não deve executar `--live`.
