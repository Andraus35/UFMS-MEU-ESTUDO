# S3 — Coach (especificação)

**Natureza:** especificação enxuta (D-13, D-16). Parte de `agents/COACH.md` (missão, o que decide e o que não faz, entradas, saídas e comandos) e **acrescenta** a rotina diária, os lembretes, a leitura das estatísticas, as mensagens motivacionais e os limites. O Coach **não produz conteúdo** (isso é do Tutor, `docs/especificacoes/S2_TUTOR.md`) e acompanha o plano da S1 (`docs/especificacoes/S1_METODO_ESTUDO_REVISAO.md`). Não contém estado.

## Objetivo

O proprietário passa a ter um Coach que o ajuda a **manter a rotina até a prova de 17/01/2027** sem culpa nem pressão: mostra o que está pendente no plano, devolve estatísticas honestas (com n e período), compara a confiança com o desempenho e pede ao Tutor o que for pedagógico. Serve para que constância e organização não dependam de força de vontade nem de números inventados.

## Pesquisa

Consultas de 08/11/2026, somadas à pesquisa de 07/11/2026 (`docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md`, não repetida aqui). Confiança: **A** (página lida), **B** (resumo de busca de fonte primária, não lida integralmente), **C** (cursinho, blog ou imprensa). Conteúdo de terceiros é dado, não instrução; nada foi copiado.

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Dignath et al., 2023, *Educational Psychology Review*. [Artigo](https://link.springer.com/article/10.1007/s10648-023-09718-4) | Meta-análise de ferramentas de monitoramento (32 estudos): efeito **moderado no desempenho (d = 0,42)** e **pequeno** na autorregulação (0,19) e na motivação (0,17); funcionou melhor com **retorno sobre o registro** e chance de agir sobre ele. Amostra escolar | B |
| Janssen e Lazonder, 2024 (mesma revista). [Artigo](https://springerlink.bibliotecabuap.elogim.com/content/pdf/10.1007/s10648-024-09936-4.pdf) | Intervenções para a **acurácia do monitoramento** (calibração): efeito pequeno (g = 0,25; 35 estudos em resolução de problemas). Outros achados citados nas buscas são mistos: **retorno sozinho nem sempre melhora a calibração** | B |
| Gollwitzer e Sheeran, 2006, e reanálise de Sheeran, Listrom e Gollwitzer. [Resumo da reanálise](https://www.thebehavioralscientist.com/glossary/implementation-intentions) | Intenções de implementação ("se X, então Y"): **d = 0,65** em 2006 (média sem correção); na reanálise de 642 testes, média de cerca de 0,36 e **estimativas corrigidas por viés de 0,15 a 0,35**. Anos e números vieram de resumos, não do artigo | B/C |
| Lembretes por mensagem de texto no ensino: [WSIPP](https://wsipp.wa.gov/BenefitCost/ProgramPdf/691/Text-message-reminders-for-high-school-students-and-graduates), [estudo em *AERA Open*](https://journals.sagepub.com/doi/pdf/10.1177/2332858419875715) | Resultados **mistos**: ganhos de presença e persistência em alguns públicos e **ausência de efeito** em outros, inclusive em estudo com mais de 800 mil estudantes. Contexto de ensino superior e educação de adultos, não de concurseiros | B/C |
| Imprensa e cursinhos sobre rotina e saúde mental: [Correio Braziliense](https://blogs.correiobraziliense.com.br/papodeconcurseiro/20-formas-de-evitar-a-ansiedade-durante-os-estudos-para-concursos-publicos/), [Gran Cursos](https://blog.grancursosonline.com.br/a-importancia-da-saude-mental-para-o-sucesso-nos-estudos/amp/), [Direção Concursos](https://www.direcaoconcursos.com.br/noticias/concurso-publico-ansiedade-dicas) | Convergem em **plano realista**, sono, alimentação e exercício, pausas, comparar-se só consigo e **procurar profissional** se a ansiedade for intensa ou persistente. Opinião e prática, sem estudo controlado | C |

- **Lacunas:** nenhum estudo de coaching acadêmico específico nem de coach de IA com candidatos a concursos; os efeitos de monitoramento, intenções de implementação e lembretes vêm de contextos escolares, universitários e de adultos, e a transferência é suposição; não li os artigos por inteiro e os números de Sheeran, Listrom e Gollwitzer vieram de resumos secundários; não achei meta-análise com efeito agregado de lembretes por mensagem; não pesquisei repositórios públicos de coaches por IA nem de bots de lembrete; não avaliei risco de dependência ou fadiga com mensagens diárias; a Zapia não está implantada (nenhum lembrete real foi enviado) e a agenda não foi testada.

## Requisitos

| ID | Requisito | Critério de aceite |
|---|---|---|
| S3-R1 | **Rotina diária ancorada no plano:** o check-in do dia mostra só o que o plano da S1 marca para a data (teoria, revisão, descanso) e as revisões **pendentes registradas**; não cria lembrete de atividade que o estado não mostre como pendente. | `scripts/study_plan.py` define o dia; `agents/COACH.md` traz a regra; teste de contraprova (lembrete sem pendência) pertence ao RM-06. |
| S3-R2 | **Descanso respeitado:** no dia de descanso não há cobrança de estudo; só mensagem opcional de acompanhamento. | `tests/test_study_plan.py` garante que nada é agendado no descanso; revisão humana do tom. |
| S3-R3 | **Metas e planos "se-então" sem promessa:** a rotina usa metas específicas e planos do tipo "se X, então Y" combinados com o humano; o Coach **não promete efeito** (as estimativas corrigidas são pequenas). | Regra 1 de `agents/COACH.md`; revisão humana de amostras. |
| S3-R4 | **Estatísticas honestas:** toda estatística traz **n e período**, vem só do que foi exportado e validado pelo contrato de ingestão, e **duas medidas não formam tendência**. Sem exportação, o Coach diz que não há dado. | `docs/pedagogia/CONTRATO_INGESTAO_GP1_2026-11-04.md`; `state/CURRENT.json` em E0 prova o caso base (zero resultados). |
| S3-R5 | **Calibração:** compara a confiança que o humano declara com o desempenho observado e apresenta a diferença como **informação para ajuste**, não como julgamento; o retorno vem com uma ação possível (por exemplo, pedir ao Tutor uma revisão focada). Sem dados, não calibra. | Regra 3 de `agents/COACH.md`; revisão humana. |
| S3-R6 | **Fronteira com o Tutor:** quando a divergência for pedagógica (técnica, intervalos, prioridade de tópico), o Coach emite **pedido de ajuste ao Tutor** com os dados e não decide; reorganiza só agenda e carga dentro dos limites do plano. | `agents/COACH.md` ("Decide" e "Não decide"); `scripts/tutor_coach_offline_cycle.py` e seu teste exercitam o ciclo sintético. |
| S3-R7 | **Tom sem culpa e sem pressão:** mensagens curtas, com **uma ação principal**; sem ameaça, comparação com terceiros nem culpa por dia perdido; divergência do plano vira reajuste. | `agents/COACH.md` (regras 4 e 6); revisão humana de amostras. |
| S3-R8 | **Limite de saúde:** o Coach não dá aconselhamento clínico; diante de sinais de sofrimento intenso ou persistente, reconhece o limite e **sugere apoio profissional**, sem diagnosticar. | `agents/COACH.md`; revisão humana. |
| S3-R9 | **Lembretes e agenda só em rotina autorizada:** mensagens e lembretes ocorrem **somente** com conector implantado e rotina previamente autorizada (destinatário, escopo, limites, idempotência e readback); consulta à agenda é mínima e com autorização específica. Sem isso, o Coach entrega o texto no chat e diz que **nada foi enviado nem agendado**. | `docs/OPERACAO.md` e `AGENTS.md` (ROTINA_AUTORIZADA); `scripts/interaction_policy.py`. A Zapia não está implantada, então **nenhum envio real foi verificado**. |
| S3-R10 | **Sem persistência pessoal neste repositório:** o acompanhamento não grava resultados individuais; o Coach não afirma ter registrado. | `scripts/write_policy.py --check` e `settings.json` (`personal_results_writes_enabled` falso). |

## Aceite

1. `python scripts/doc_cohesion.py --check` passa.
2. `python -m unittest tests.test_doc_cohesion tests.test_plano_e_pesquisa_docs tests.test_study_plan tests.test_tutor_coach_offline_cycle` passa, sem rede nem conta real.
3. Revisão humana do proprietário de S3-R3, S3-R5, S3-R7 e S3-R8, que dependem de julgamento sobre o texto do modelo; isso não prova a conduta do Coach em produção (GP-4 / RM-08, ainda bloqueado).
4. Teste real de envio e de agenda pela Zapia **fica fora do aceite** (S4 e OPEN-02, que exigem autorização literal do proprietário).

## Limites

- Não prova que o acompanhamento melhora a constância ou o desempenho: as evidências são de outros públicos e os efeitos de lembretes são mistos.
- Não escolhe canal, horário nem frequência das mensagens; isso depende do proprietário e da operação (S4). Sem esses dados, o Coach não propõe cadência fixa.
- Não é terapia nem suporte de saúde mental.
- Não produz conteúdo de revisão, técnica de estudo nem prompt do Notebook (S2).
