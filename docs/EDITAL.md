# Recorte operacional do edital UFMS — referência inicial

Edital PROGEP/UFMS nº 152 de 29/10/2026. Banca FAPEC. Prova objetiva 17/01/2027.

| Código | Cargo | Lotação | Vagas | Escolaridade |
|---|---|---|---:|---|
| 523 | Analista em Educação / Administração e Informação / Gestão Pública | Campo Grande | 29 | Duas alternativas de formação, incluindo graduações listadas ou graduação em qualquer área com especialização em Gestão Pública, segundo condições integrais da p. 15 |
| 324 | Técnico em Educação / Processos Educacionais / Assuntos Estudantis | Campo Grande | 18 | Ensino médio completo |

- Matutino: superior (fechamento dos portões às 8h). Vespertino: médio (fechamento às 14h). Horário de MS.
- Em cada prova: Português 15 questões/15 pontos; Inglês 5/5; Legislação 10/20; Raciocínio Lógico 10/20; Específicos 20/40. Total 60 questões/100 pontos e 4 horas.
- Aprovação: mínimo 50 pontos e nota não zero em nenhuma das cinco áreas; homologação limitada conforme o edital.
- Inscrições para um cargo de cada turno são permitidas. Município de prova é escolhido no ato da inscrição e não precisa ser a localidade de lotação.

**Escopo:** `config/topics.csv` usa os blocos de assuntos do Anexo V. O cadastro de subtópicos poderá ser detalhado depois, sem suprimir os blocos originais. A estrutura de um assunto no TEC/Qconcursos pode diferir da classificação do edital.

**Pendente:** verificar retificações em fonte oficial antes da operacionalização dos cadernos.

## Busca do edital

O índice derivado `edital/vagas_index.json` localiza as linhas exatas dos cargos 523 e 324 no quadro do Anexo III, com evidências de cada campo e coordenadas de inspeção no PDF. Consultar `python scripts/search_edital.py --vagas-cargo 523 --full` ou `--vagas-cargo 324 --full`; não tratar a classificação derivada como texto normativo. O índice derivado `edital/topic_index.json` conecta os 23 tópicos da configuração aos trechos literais do edital com offsets por página. Consulte `edital/INDEX.md` para roteamento por cargo, assunto, seção e página. Títulos e aliases são metadados derivados; não alteram a redação oficial. O validador `scripts/index_edital.py --check` integra o gate de CI e `scripts/benchmark_edital.py` executa consultas versionadas. A qualidade da transcrição de tabelas deve ser verificada no PDF original quando houver ambiguidade.

Atribuições do **Anexo IV**: `edital/atribuicoes_index.json` registra recortes literais do 523 (p. 23) e 324 (p. 28), com offsets e SHA-256 de cada trecho. Para consultar: `python scripts/search_edital.py --atribuicoes-cargo 523 --full` ou `--atribuicoes-cargo 324 --full`. O índice só localiza texto do edital, não cria obrigações ou qualificação adicionais. `scripts/index_atribuicoes.py --check` integra a CI.

## Distinção entre fontes do concurso

- **Anexo III:** vagas, escolaridade e demais condições de ingresso (p. 15 para o 523, p. 18 para o 324).
- **Anexo IV:** tarefas e atribuições do exercício do cargo (p. 23 para 523, p. 28 para 324).
- **Anexo V:** o que está listado no programa de prova, compreendendo quatro blocos gerais compartilhados e dez específicos do 523 ou nove específicos do 324. **Não** inferir exigência de ingresso ou conteúdo programático a partir da descrição de atribuições.
- **Comando:** `python scripts/search_edital.py --anexo III|IV|V --cargo 523` (substituir `III|IV|V` pelo anexo pretendido); para o conteúdo integral do 324: `python scripts/search_edital.py --anexo V --cargo 324 --full`. Sem `--full`, o inventário do Anexo V é compacto.
- **Integridade de rotas:** `tests/fixtures/annex_cases.json` e `scripts/benchmark_anexos.py` controlam 21 contraprovas no workflow. Consulta que mistura anexos deve ser separada por tipo documental, não resumida como se fossem equivalentes.

Fonte integral na raiz: `EDITAL_UFMS_152_2026.md`. Índice de recuperação: `edital/INDEX.md`. Chunks: `edital/chunks/`. Manifest com página/offsets: `edital/manifest.json`. Consultar fragmentos relevantes e ampliar o contexto antes de concluir. Retificações exigem verificação própria.
