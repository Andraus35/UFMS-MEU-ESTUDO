# Auditoria RM-01 — fontes oficiais e monitoramento

**Data:** 05/11/2026  
**Base:** `main@1ab0c25a8b0084034fb1987097bfcb6b38ccea44`  
**Tarefa:** RM-01 / ENG-00 / GP-0  
**Modo:** leitura e contraprovas; sem alteração do PDF canônico ou incorporação normativa.

## Evidências confirmadas

1. O registro canônico identifica o Edital PROGEP/UFMS nº 152/2026, 47 páginas, com SHA-256 e Git blob registrados. A fonte é explicitamente classificada como original e não incorpora retificações.
2. A política de retificações mantém `auto_apply=false`, preserva a fonte original e exige emissor oficial, URL de publicação, data, título, bytes com SHA-256 verificado, alvo/itens afetados e revisão humana antes de adoção normativa.
3. O monitor FAPEC é somente leitura. Consulta uma página específica, limita a resposta a 1 MiB, valida HTTP/HTML e identidade do concurso. Não baixa nem aplica PDFs, não grava arquivos e classifica resultados como `no_change_observed_on_single_page`, `needs_manual_review` ou `unverifiable`.
4. O workflow `.github/workflows/monitor-fapec.yml` declara cron `17 12 * * *` e `workflow_dispatch`, permissão `contents: read`, `persist-credentials: false` e trata candidato/inconclusivo como falha que exige revisão.

## Não conformidades / limites ainda abertos

- **RM01-NC-01 — execução agendada: RESOLVIDA em 07/11/2026.** Em 05/11/2026 a consulta não encontrou runs com `event=schedule`. Em 07/11/2026 a consulta autenticada encontrou dois: run `42279755785` (06/11/2026, `main@7df4b8f`) e run `42397876811` (07/11/2026, `main@937f3c7`), ambos `event=schedule`, job `check` `success`; o JSON no log de cada um traz `status=no_change_observed_on_single_page`, `publication_candidate=false`, `writes=false`, `normative_revision_verified=false`. O horário real (≈19:27 e ≈17:45 UTC) difere do cron `17 12 * * *` por atraso de agendamento do GitHub; a execução agendada ocorreu. Estado: `VERIFIED` apenas para o agendamento; **não** prova ausência de retificações (ver NC-03).
- **RM01-NC-02 — bytes remotos não verificados:** o PDF listado pela FAPEC e o PDF institucional UFMS permanecem com SHA-256 remoto ausente e equivalência `unverified`. Não afirmar que os bytes remotos correspondem ao PDF canônico.
- **RM01-NC-03 — cobertura parcial:** a sonda cobre uma página da FAPEC, não todas as fontes oficiais, boletins ou publicações posteriores. Resultado sem mudança não prova ausência geral de retificação.
- **RM01-NC-04 — alerta cronológico aberto:** `ALERTA-DOC-01`, Anexo II, p. 13, continua `unresolved_source_inconsistency`: o período de recurso (11 e 12/01/2027) antecede a data indicada para divulgação do resultado (10/02/2027). Não corrigir por inferência.

## Parecer

**RM-01 permanece `implementado_nao_homologado`.** Os controles offline, a preservação da fonte e a arquitetura read-only estão documentados e cobertos por contraprovas, e o monitor agendado foi observado em execução real (NC-01). Continuam impedindo a homologação: os bytes oficiais remotos não foram obtidos/hash-verificados (NC-02), a cobertura é de uma única página (NC-03) e o alerta cronológico segue aberto (NC-04).

## Critério para fechar a pendência

1. ~~Obter pelo menos um run GitHub Actions com `event=schedule`, concluído e com log/result JSON legível.~~ **Cumprido em 07/11/2026** (dois runs, ver NC-01).
2. Se o resultado for `unverifiable` ou `needs_manual_review`, manter a pendência e registrar a causa; não converter falha em estabilidade.
3. Para declarar equivalência documental, obter os bytes da publicação oficial, calcular SHA-256 independentemente e comparar com a versão arquivada sem sobrescrever a fonte original.
4. Só resolver `ALERTA-DOC-01` mediante ato oficial verificável e revisão humana documentada.
