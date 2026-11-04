# Reauditoria incremental GP-0/GP-1 — ciclo 3, 04/11/2026

**Escopo:** READ ONLY na frente técnica do PR #1 e leitura de fontes oficiais, com checkpoint exclusivamente documental no PR #2. Não houve implementação, aprovação de gate, escrita pessoal nem merge.

## Identidade congelada e fontes

- Repositório: `Andraus35/UFMS-MEU-ESTUDO`.
- PR técnico **#1**, branch `setup/harness-memory-v0-2`, HEAD `1efce57f77f36a692a534f101def0b263af847ce`, aberto como draft no momento da consulta.
- PR pedagógico **#2**, branch `docs/especificacao-pedagogica-v1-2`, HEAD **anterior** `597185286cd2d88dab0749e8b69adf8aff6046ea`, aberto como draft.
- Edital original UFMS (47 páginas): https://www.ufms.br/wp-content/uploads/2026/10/SEI_6775306_Edital.pdf .
- Página FAPEC do concurso: https://portal.concurso.fundacaofapec.org.br/edital/ver/22 .
- Registros CI no SHA técnico: https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41796845666 e https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41796839200 .

## Atualização factual dos bloqueios GP-1

| Pendência v1.7 | Fato verificado no HEAD do PR #1 | Resultado restrito |
|---|---|---|
| REC-01 — sete contra nove arquivos obrigatórios | `settings.json` e `AGENTS.md` listam nove; `rules/CORE.md` e `docs/OPERACAO.md` agora também exigem nove | **CORRIGIDA NA CANDIDATA**, não na main |
| REC-02 — gates de inicialização | `scripts/bootstrap.py` chama `check_bootstrap` e `check_hook_contract`. `scripts/agent_gates.py` lê bytes, gera hashes SHA-256, confere ordem e procura interfaces `run` por AST | **MITIGADA PARCIALMENTE**; não comprova leitura semântica ou registro automático em todos os agentes |
| REC-03/04 — IDs e tempo | `scripts/core.py` usa `event_id`, `caderno_id` e timestamp com fuso; não expõe `attempt_id` como campo distinto no componente lido | **PENDENTE** contrato de recomendação, tentativa, data de registro e data da resolução |
| REC-05 — normalização TEC/Qconcursos | O validador técnico exige contagens inteiras coerentes com um total canônico | **PENDENTE** adaptador das convenções de relatórios, sem inventar números |
| REC-06/07 — evidência/fila | O `scripts/core.py` lido faz validação e reconstrução; não identifica `E0` ou função `queue` | **NÃO DEMONSTRADA NESSE COMPONENTE**; não afirmar ausência em todo o repositório sem inventário |
| REC-08 — máquina de estados | Tipos técnicos de evento ainda não modelam explicitamente todos os estados pedagógicos de criação, cancelamento e substituição | **PENDENTE** |
| REC-09 — resultados pessoais | `personal_results_writes_enabled=false`; `scripts/write_policy.py` reprova flag alterada ou resultado privado inesperado. `docs/OPERACAO.md` exige autorização, verificação de privacidade e testes | **BLOQUEIO REFORÇADO; escrita continua vedada** |
| REC-13 — CI | Duas execuções `Validar harness` no SHA exato terminaram `completed/success`; dois check-runs `validate` também `success` | **CI do harness comprovada**, sem comprovação da suíte pedagógica de 102 casos |
| REC-15 — integração | PRs #1 e #2 abertos como draft e independentes, ambos com base main | **SEM INTEGRAÇÃO**, nenhum merge autorizado |

**Demais registros REC-xx da matriz histórica não foram reavaliados integralmente neste ciclo.** Não declarar seus estados alterados.

## GP-0: fontes oficiais e limites da verificação

- O PDF primário consultado identifica `EDITAL PROGEP/UFMS Nº 152, DE 29 DE OUTUBRO DE 2026`. Foram visualmente examinadas a primeira página e a do Anexo II (página impressa 13), com inscrições originais de 04/11 a 04/12/2026 e prova em 17/01/2027.
- A página FAPEC ainda apresenta o rótulo `EDITAL PROGEP/UFMS N.º 001/2026 - Edital de Abertura` (30/10/2026).
- A tentativa de seguir o DOWNLOAD da FAPEC redirecionou para objeto S3 com URL temporária não acessível pelo mecanismo consultado. **Não foi lido nem hasheado o PDF da FAPEC**; identidade e alterações são desconhecidas.
- Consultas limitadas em canais públicos não localizaram retificação positiva vinculada de forma inequívoca ao edital. Isso **não prova ausência de retificações**.
- A inconsistência cronológica de recurso em data anterior ao resultado preliminar no Anexo II, já registrada anteriormente, continua sem retificação confirmada.

**GP-0 permanece PENDENTE:** conferir documento da FAPEC, retificações, cronograma e versão vigente do programa. O documento UFMS citado comprova somente sua redação original.

## Veredito, próximos atos e limitações

| Gate | Estado |
|---|---|
| GP-0 | Parcialmente verificado no original; **não homologado** |
| GP-1 | **Pendente**; REC-01 corrigido na candidata, REC-02 mitigado, controles de privacidade reforçados |
| GP-2/GP-3 | Tutor adaptativo e 102 testes executáveis **não demonstrados** |
| GP-4/GP-5 | Fluxo operacional/piloto autorizado **não demonstrados** |

A próxima intervenção técnica deve reconsultar o HEAD do PR #1, confirmar GP-0, reconciliar identidades, datas e adaptadores e executar testes adversariais sobre dados fictícios. Sem escrever no PR #1 a partir desta sessão, sem habilitar resultados pessoais e sem merge.

**Limite:** foram consultados arquivos técnicos por SHA e statuses do GitHub; não houve checkout ou execução local de seus scripts nesta auditoria. O compromisso de commit deste relatório depende de readback remoto do PR #2 após sua publicação.
