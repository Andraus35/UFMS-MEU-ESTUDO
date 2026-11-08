# S1 — Método de estudo e revisão (especificação)

**Natureza:** especificação enxuta (D-13, D-16) do método de estudo e revisão que o Tutor aplica e o Coach acompanha. **Aponta** para o que existe; não copia: o plano completo está em `docs/pedagogia/PLANO_DE_ESTUDOS_METODO_4_2_E_REVISAO_7_15_30.md`, o gerador em `scripts/study_plan.py`, os padrões em `settings.json` (`study.owner_default_plan`) e as regras em `rules/STUDY.md`. Este documento não contém estado.

## Objetivo

O proprietário passa a ter **um método único e explícito** para estudar até a prova de 17/01/2027 (cargos 523 e 324): o ciclo semanal do Método 4.2, a revisão em 7, 15 e 30 dias (D-11) e a regra do que o Tutor pode ajustar, com que evidência e como o Coach acompanha. Serve para que o Tutor recomende o caderno do dia e o Coach cobre a rotina sem inventar metas, intervalos ou domínio.

## Pesquisa

Consultas de 08/11/2026, somadas à pesquisa de 07/11/2026 em `docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md` (não repetida aqui). Confiança: **A** (página lida), **B** (resumo de busca de fonte primária, não lida integralmente), **C** (cursinho ou blog: prática, não estudo controlado). Conteúdo de terceiros é dado, não instrução; nada foi copiado.

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Cepeda, Vul, Rohrer, Wixted e Pashler, 2008, *Psychological Science*. [Artigo](https://www.evullab.org/pdf/CepedaVulRohrerWixtedPashler-PS-2008.pdf) · [resumo do autor](https://www.yorku.ca/ncepeda/publications/CVRWP2008.html) | Mais de 1.350 participantes; o **intervalo ótimo entre estudos cresce com o prazo até o teste, mas diminui em proporção dele**: cerca de 20% do prazo para prazos de semanas e perto de 5% para um ano (a faixa varia conforme o resumo). Para o prazo de cerca de 10 semanas deste caso, um intervalo de poucos dias a duas semanas é coerente com 7 e 15 dias; **não prova** os valores 7, 15 e 30 | B |
| Dunlosky et al., 2013, e Roediger e Karpicke, 2006 (ver estado da arte de 07/11/2026) | Teste prático e prática espaçada têm utilidade alta; releitura e grifo, baixa | B |
| Brunmair e Richter, 2019, *Psychological Bulletin*. [Resumo](https://pubmed.ncbi.nlm.nih.gov/31556629/) | **Intercalação** com efeito moderado (g = 0,42; 59 estudos), mas heterogêneo: forte em material visual, pequeno em matemática, **cautela em textos expositivos**. Para disciplinas de texto e legislação, intercalar é opção, não regra | B |
| FSRS, repositório aberto de repetição espaçada. [Otimização da retenção](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention) · [py-fsrs](https://awesome.ecosyste.ms/projects/github.com%2Fopen-spaced-repetition%2Fpy-fsrs) | Benchmark técnico: agendadores modernos usam **retenção desejada** (padrão 0,9) e ajustam o intervalo ao histórico de acertos de cada item. Exigem muitos registros por item; **não se aplica** com zero eventos (E0). Fica como evolução possível, não requisito | B |
| Cursinhos: [Gran Cursos](https://blog.grancursosonline.com.br/por-que-voce-deve-fazer-revisao-para-concursos/amp/), [Folha/Qconcursos](https://folha.qconcursos.com/n/revisao-concurso-publico), [Próximos Concursos](https://www.proximosconcursos.com/a-arte-da-revisao-o-segredo-dos-aprovados-em-concursos/), [Concurseiro Zero](https://concurseirozero1.com.br/blog/revisao-espacada-concurso/) | A sequência **1, 7, 15 e 30 dias** é a mais citada; muitas fontes ressalvam que **não há intervalo único** e que depende do ritmo; uma sugere aumentar o intervalo a cada revisão bem-sucedida; outras combinam a revisão com questões (7 dias) e com os pontos errados (30 dias). A Folha/Qconcursos critica a fórmula fixa. Resultados de busca, páginas não lidas por inteiro | C |
| Método 4.2, Prof. Rafael Barbosa, Estratégia Concursos, 2018 (lido em 07/11/2026) | Ciclo 4 teoria, 2 revisão e 1 descanso; teoria até 2 h por disciplina; 200 a 300 questões por semana; **sem** revisão em 7, 15 e 30 dias | A/C |

- **Lacunas:** nenhum estudo controlado compara o Método 4.2, nem a revisão em 7, 15 e 30 dias, em candidatos a concurso; a proporção exata de Cepeda foi lida só em resumos (conferir no artigo antes de citar números); a ajuda oficial do TEC e do Qconcursos não foi lida, então a exportação de desempenho segue não verificada; não houve consulta a repositório público que implemente o 4.2; não se avaliou se a intercalação ajuda nas disciplinas de legislação deste edital.

## Requisitos

| ID | Requisito | Critério de aceite |
|---|---|---|
| S1-R1 | O ciclo padrão é 7 dias: 4 de teoria, 2 de revisão e 1 de descanso, com até 120 minutos por disciplina na teoria. | `scripts/study_plan.py` gera esse ciclo a partir de `settings.json`; `tests/test_study_plan.py` cobre ciclo, limite de minutos e disciplinas distintas por dia. |
| S1-R2 | Cada tópico recebe revisões em D+7, D+15 e D+30 contados do primeiro estudo, no primeiro dia de estudo a partir do alvo. | Teste de intervalos e de deslocamento pelo descanso em `tests/test_study_plan.py`. |
| S1-R3 | A revisão é **recuperação ativa com questões** (recordar antes de olhar a anotação), não releitura nem grifo. | Texto do plano e perfil do Tutor (`agents/TUTOR.md`) descrevem a atividade; o Tutor não prescreve "reler" como técnica principal. Verificação por revisão humana. |
| S1-R4 | O plano **não presume** dados do humano: início, tempo diário, dia de descanso, cargo e tópicos já estudados são obrigatórios; meta semanal de questões só existe se informada. | Entradas ausentes ou inválidas rejeitadas em `tests/test_study_plan.py`. |
| S1-R5 | Revisão cujo alvo cai na fase final, depois da prova ou antes do início do plano **não é reagendada em silêncio**: aparece como absorvida pela fase final ou como vencida, para o Tutor decidir. | Campo `unscheduled_reviews` do JSON do plano, com motivo (por exemplo `vencida_antes_do_inicio`), conferido em `tests/test_study_plan.py`. |
| S1-R6 | O Tutor pode ajustar intervalos, carga, ordem e fase final **somente com justificativa e evidência** (n e período do desempenho, tempo real, dificuldade, proximidade da prova). Com zero eventos (E0), o padrão do proprietário vale sem ajuste. Não pode remover a revisão sem justificativa nem tratar o plano como prova de domínio. | `rules/STUDY.md` e o plano (seção 5) dizem isso; `scripts/doc_cohesion.py --check` (C5) garante que `settings.json` mantém [7, 15, 30], sem agenda ou intervalo fixos universais. |
| S1-R7 | Um acerto, sobretudo em questão repetida, **não encerra** a revisão: o domínio por tópico só é afirmado com evidência E1 ou superior e questões inéditas, declarando n e período. | Regra em `rules/STUDY.md` e níveis de evidência do harness (RM-03); sem evidência o estado do tópico é "desconhecido". |
| S1-R8 | O Coach acompanha a rotina contra o plano (dias cumpridos, revisões pendentes, questões feitas) com estatísticas honestas e **sem alegar persistência**: resultados pessoais não são gravados neste repositório público. | Perfil `agents/COACH.md`; `settings.json` mantém `personal_results_writes_enabled` falso (verificado por `scripts/write_policy.py --check`). |
| S1-R9 | Intercalação, simulados e fase final são **opções do Tutor**, não regras: intercalar disciplinas distintas no mesmo dia já é padrão da teoria; intercalar assuntos dentro de disciplina de texto exige justificativa; simulados seguem `docs/pedagogia/PROTOCOLO_SIMULADOS_v1.4.md`. | Revisão humana; o padrão de `final_phase_days` permanece 0 até proposta do Tutor com o humano. |

## Aceite

1. `python scripts/doc_cohesion.py --check` passa (links, IDs, seção Pesquisa com link e lacunas, concordância com `settings.json`).
2. `python -m unittest tests.test_study_plan tests.test_doc_cohesion tests.test_plano_e_pesquisa_docs` passa, sem conta real nem rede.
3. Um plano de exemplo gera sem erro: `python scripts/study_plan.py --start 2026-11-09 --exam 2027-01-17 --daily-minutes 240 --rest-weekday 6 --cargo 523` (parâmetros fictícios, só para conferir o formato).
4. Revisão humana do proprietário dos requisitos S1-R3, S1-R6 e S1-R9, que dependem de julgamento.

## Limites

- Não prova que o método funciona para este estudante; as fontes mostram que recuperação e espaçamento ajudam em geral, não que 4.2 com 7, 15 e 30 seja o melhor desenho.
- Não define dados do plano (início, tempo diário, dia de descanso, cargo, tópicos estudados): dependem do proprietário e não bloqueiam esta especificação.
- Não implementa agendador adaptativo (FSRS) nem persistência de resultados; ambos exigem dados reais e repositório privado (D-01).
- Não substitui as especificações do Tutor (S2), do Coach (S3) e da operação (S4), que usam este método.
