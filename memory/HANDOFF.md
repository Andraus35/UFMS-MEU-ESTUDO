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

Não atualizar este documento com estados não confirmados nem copiar conversas inteiras. A nova sessão deve conferir o SHA atual da branch/PR antes de agir.
