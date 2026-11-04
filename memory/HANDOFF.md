# Handoff — harness e checkpoints verificáveis

- **Estado verificado em 2026-11-04:** harness v0.2 publicado em branch de proposta `setup/harness-memory-v0-2`, por meio do PR draft [#1](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/1). **Não está mesclado à main.**
- **Prova alvo:** 17/01/2027; cargos UFMS 523 (manhã) e 324 (tarde).
- **Último caderno recomendado:** nenhum.
- **Último resultado confirmado:** nenhum.
- **Estado quantitativo:** zero eventos e zero cadernos concluídos; conferir `state/CURRENT.json` no HEAD da branch.
- **Project:** [Andraus35/2](https://github.com/users/Andraus35/projects/2), vínculo informado pelo estudante, registrado em `config/project.json`. Não há confirmação técnica de leitura/edição ou sincronização de itens no Projects.
- **Próxima ação:** confirmar CI e aprovação humana da configuração; somente depois do merge autorizado iniciar operações de estudo em `main`.
- **Pendências:** verificar retificações do edital; obter amostra de CSV TEC e relatório Qconcursos antes de automatizar importação; definir integração autorizada ao GitHub Projects se necessária.
- **Persistência:** o PR e seu commit são verificáveis no GitHub. Uma falha de sincronização com o Projects não altera o histórico persistente.

## Checkpoint de engenharia documental — 04/11/2026

- **Escopo:** recuperação econômica e verificável do Edital PROGEP/UFMS 152/2026. Nenhum planejamento pedagógico ou dado de estudo foi alterado.
- **PR:** #1, branch `setup/harness-memory-v0-2`, ainda em draft e sem merge. Reconferir HEAD e estado antes de retomar.
- **Fonte:** `EDITAL_UFMS_152_2026.md` (Git blob SHA `a4129cceabd20fc119625d71b1c1599b3ce644e1`) e 81 chunks em 47 páginas. O `source_pdf_sha256` está declarado no manifesto, mas a correspondência visual de tabelas com o PDF original **não foi revalidada** nesta entrega. Retificações não verificadas.
- **Índice derivado:** `edital/topic_index.json` localiza 23 tópicos de `config/topics.csv` em 24 intervalos literais nos chunks, com páginas e offsets. Gerar e conferir usando `scripts/index_edital.py --write/--check`.
- **Busca:** `scripts/search_edital.py` roteia por item literal (`3.6`, `10.2`), ID do tópico, título/alias, e finalmente BM25; isola conteúdos específicos quando `--cargo` e `--area especificos` são usados. Expansão sob demanda por `--neighbors` e `--page`. Aliases são metadados derivados, nunca texto normativo.
- **Evidência remota verificada:** GitHub Actions [run 41787447862](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41787447862), commit `d7081e4581f6c42c4b5b533c70cc90ad776f83dd`: **32 testes aprovados**, 47 páginas/81 chunks íntegros, 23 tópicos indexados, **Hit@1 27/27, Hit@3 27/27, negativos 2/2**, média 0,005171 do documento integral em caracteres por consulta no conjunto de 29 casos. Métricas de conjunto diagnóstico, não garantia universal.
- **Verificações integradas:** `scripts/validate.py` bloqueia índice incompatível; `.github/workflows/validate.yml` executa o benchmark e testes a cada commit. Alterações posteriores ao SHA da evidência devem ter CI própria confirmada.
- **Pendências técnicas:** cotejo humano das tabelas com o PDF de origem; confirmar retificações oficiais em versão separada; incluir perguntas independentes do conjunto de aliases para aferir generalização e monitorar falsos positivos de números de normas externas.
- **Próxima retomada restrita a esta frente:** reconfirmar HEAD/CI do PR #1; executar revisão adversarial de consultas não usadas na construção dos aliases; verificar PDF, se disponível, sem modificar texto canônico silenciosamente. **Proibido merge sem autorização expressa.**

## Checkpoint — auditoria adversarial e cotejo do PDF (04/11/2026)

- **Base de retomada:** PR #1 draft, branch `setup/harness-memory-v0-2`; HEAD antes da atualização de handoff `9d2852fde2a1fcdb22352bc5389ea3867a42a6f2`. Revalidar HEAD atual em toda sessão. **Não executar merge.**
- **Origem do PDF comprovada:** arquivo original disponibilizado pelo estudante encontrado e examinado (47 páginas), SHA-256 **recalculado** `c758bb421ad848bf76757f6ece7a7b786e80e45123b80c3e01a13d0985f09675`, igual ao SHA do `edital/manifest.json`.
- **Cotejo visual amostral:** p. 12 (remuneração, benefícios), p. 15 (523/29 vagas/Campo Grande), p. 18 (324/18 vagas/Campo Grande/ensino médio), p. 29 (conhecimentos gerais), pp. 35–36 (limites do conteúdo 523) e p. 45 (conteúdo 324). Achados e limites documentados em `docs/AUDIT_RECUPERACAO_EDITAL_2026-11-04.md`.
- **ALERTA-DOC-01:** no **PDF original**, Anexo II p. 13 indica resultado preliminar em `10/02/2027` e prazo de recurso em `11 e 12/01/2027`; datas cronologicamente inconsistentes. **Não corrigir** por inferência e verificar retificações/atos oficiais. A consulta pontual à página da FAPEC (`https://portal.concurso.fundacaofapec.org.br/edital/ver/22`) não comprovou retificação para este edital; ausência não está garantida.
- **Aprimoramentos:** `scripts/search_edital.py` agora restringe Anexo V ao `--cargo` mesmo sem `--area`, exige duas correspondências para BM25 em consultas longas e detecta contradições explícitas entre cargo informado e filtro. Mantidos os 81 chunks sem alterações normativas.
- **Evidência GitHub CI:** runs [41788773512](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41788773512) e [41788768486](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41788768486), ambos `success` no HEAD `9d2852fde2a1fcdb22352bc5389ea3867a42a6f2`. Total **34 testes**, fonte 47 páginas/81 chunks íntegros, índice 23 tópicos, benchmark original 27/27 Hit@1 e 2/2 negativos. Benchmark adversarial adicional **17/17**: 9/9 positivos Hit@1, 3/3 isolamentos, 2/2 negativos, 1/1 conflito e 2/2 normas externas não tratadas como itens. Conjunto criado por esta frente, **não auditoria externa cega**.
- **Revalidação reforçada:** [run 41789110667](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41789110667), SHA `e6d35913d1485200285ba129e03bb0ebb0b05ef2`, `success`: 34/34 testes; conjunto adversarial 9/9 no primeiro resultado **com rota BM25 e trecho literal correspondente**, 3/3 isolamentos, 2/2 negativos, 1/1 conflito e 2/2 normas externas não confundidas com itens; conjunto curado 27/27 Hit@1. [Run 41789035123](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41789035123) reprovou antes por expectativa textual incorreta de fixture; corrigida sem mudar a consulta. Evidências registradas em `docs/AUDIT_RECUPERACAO_EDITAL_2026-11-04.md`.
- **Pendências:** (1) confirmar retificação oficial da anomalia p. 13; (2) verificar o restante das tabelas visuais e, se preciso, indexar linhas de vagas/requisitos p. 14–18; (3) ampliar perguntas não usadas na seleção de aliases; (4) rever limites de fragmentos quando a regra ultrapassa 450 caracteres; (5) exigir leitura visual da linha de tabela antes de afirmar requisitos.
- **Limites de governança:** nenhum plano de estudos, cronograma pedagógico ou seleção de questões foi alterado; `main` e PR permanecem sem merge autorizado; consulta externa não altera automaticamente o edital canônico.

Não atualizar este documento com estados não confirmados nem copiar conversas inteiras. A nova sessão deve conferir o SHA atual da branch/PR antes de agir.
