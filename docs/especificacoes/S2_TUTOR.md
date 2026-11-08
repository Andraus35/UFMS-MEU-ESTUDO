# S2 — Tutor (especificação)

**Natureza:** especificação enxuta (D-13, D-16). Parte de `agents/TUTOR.md` (missão, o que decide e o que não faz, entradas, saídas e comandos) e **acrescenta** só três coisas: como o Tutor gera o material de revisão a partir do edital e do desempenho, como pede o prompt ao Notebook e como decide ajustes ao plano. O método vem da S1 (`docs/especificacoes/S1_METODO_ESTUDO_REVISAO.md`). Não contém estado.

## Objetivo

O proprietário passa a ter um Tutor com **comportamento verificável**: ensina e revisa por recuperação ativa, ancora tudo no edital, usa o desempenho como evidência (com n e período) e mantém a dificuldade produtiva em vez de entregar respostas. Serve para que a revisão e a prescrição do caderno do dia não dependam de inspiração do modelo.

## Pesquisa

Consultas de 08/11/2026, somadas à pesquisa de 07/11/2026 (`docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md`, não repetida aqui). Confiança: **A** (página lida), **B** (resumo de busca de fonte primária, não lida integralmente), **C** (cursinho ou blog). Conteúdo de terceiros é dado, não instrução; nada foi copiado.

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Bastani et al., 2025, *PNAS* 122(26). [Registro](https://econpapers.repec.org/RePEc:nas:journl:v:122:y:2025:p:e2422633122) · [resumo Wharton](https://knowledge.wharton.upenn.edu/article/without-guardrails-generative-ai-can-harm-education/) | Campo com quase mil alunos do ensino médio: IA sem proteções melhorou o desempenho **durante a prática**, mas **piorou a prova sem IA** (cerca de 17% abaixo do grupo-controle); o tutor com **dicas graduais, sem entregar a solução, e com a solução e os erros comuns no prompt** ficou na média do controle. A maioria dos alunos só pedia a resposta. Efeito em matemática do ensino médio, não em concursos | B |
| Kestin et al., 2025, *Scientific Reports* (curso de física de Harvard). [Cobertura de Harvard](https://news.harvard.edu/gazette/story/2024/09/professor-tailored-ai-tutor-to-physics-course-engagement-doubled/) | Ensaio randomizado com 194 alunos: um tutor de IA **construído pelos professores**, com princípios pedagógicos, superou a aula ativa no ganho de aprendizagem; amostra pequena, dois tópicos, teste de curto prazo. Detalhes só em fontes secundárias; **não transfere automaticamente a um chatbot genérico** | B |
| Dunlosky et al., 2013, e Roediger e Karpicke, 2006 (estado da arte de 07/11/2026) | Teste prático e espaçamento têm utilidade alta; a sensação de domínio após reler engana | B |
| Cadernos de erros em cursinhos: [Estratégia](https://www.estrategiaconcursos.com.br/blog/caderno-de-erros-por-onde-comecar/), [Folha/Qconcursos](https://folha.qconcursos.com/n/como-revisar-questoes-erradas-concursos), [Concurseiro Zero](https://concurseirozero1.com.br/blog/caderno-de-erros-concurso/), [Aprova Concursos](https://www.aprovaconcursos.com.br/blog/caderno-de-erros/) | Prática comum: registrar **assunto, causa do erro e o raciocínio correto**, em texto curto; agrupar por tipo de erro e matéria; revisar a cada semana e inteiro perto da prova; uma fonte afirma que o padrão de erro aparece depois de cerca de 200 questões (afirmação não verificada). **Prática de cursinho, sem estudo controlado** | C |
| Limites do NotebookLM em contas gratuitas, de blogs: [Fast.io](https://fast.io/resources/notebooklm-limits/), [Elephas](https://elephas.app/blog/notebooklm-source-limits) | 50 fontes por caderno e 500 mil palavras por fonte, citações nas respostas; os números dos planos pagos divergem entre as fontes e **não vieram de página do Google** | C |

- **Lacunas:** nenhum estudo de tutoria por IA com candidatos a concursos, nem com direito e administração pública; os dois estudos de tutoria são de matemática e física, e a transferência é suposição; não li os artigos de Bastani e Kestin por inteiro; não confirmei em página oficial do Google os limites do NotebookLM, nem que o produto virou "Gemini Notebook"; não pesquisei repositórios públicos de tutores por IA com recuperação espaçada; a ajuda oficial do TEC e do Qconcursos segue não lida, então o formato do desempenho exportado continua sem amostra real (OPEN-11); a decisão de acesso direto ao Notebook (OPEN-10) não está tomada e o teste sintético de PR-012 não foi feito.

## Requisitos

| ID | Requisito | Critério de aceite |
|---|---|---|
| S2-R1 | **Dificuldade produtiva:** o Tutor não entrega a resposta ou o gabarito antes da tentativa do estudante; ensina por dicas graduais, pede que ele tente primeiro e só então explica. Pode explicar direto o que o estudante pedir explicitamente depois de tentar, ou conteúdo novo de teoria. | `agents/TUTOR.md` traz a regra; revisão humana de amostras de resposta (Bastani). Não há verificação automática do texto do modelo. |
| S2-R2 | **Ancoragem no edital:** todo conteúdo ensinado ou prescrito cita tópico do edital (`config/topics.csv`, `edital/INDEX.md`) e, quando usar o edital, página e trecho. Sem fonte verificada, declara que não tem. | `scripts/search_edital.py` localiza o trecho; `scripts/doc_cohesion.py --check` mantém as referências; teste de contraprova de citação inventada pertence ao RM-06. |
| S2-R3 | **Material de revisão (D-08):** a partir do plano da S1, do tópico e do erro registrado, o Tutor gera **perguntas de recuperação** (não resumo para reler), no nível do tópico, com a fonte do edital ou da norma e sem inventar questão de banca. Questão de banca só entra com ID da plataforma informado pelo estudante. | Saída tem tópico, objetivo, fonte e justificativa; `scripts/notebook_prescriber.py` rejeita ID ou disponibilidade não confirmados. |
| S2-R4 | **Registro de erro:** cada erro informado vira uma entrada curta (assunto, causa provável, raciocínio correto, data) e entra na próxima revisão do tópico; a causa é **hipótese** até haver padrão com n declarado. Resultado agregado não vira diagnóstico por tópico. | Regra 3 e 7 de `agents/TUTOR.md`; `rules/STUDY.md`. Persistência real fica bloqueada (repositório público), então o Tutor entrega a entrada no chat e não afirma ter gravado. |
| S2-R5 | **Ajuste do plano:** o Tutor só altera o padrão da S1 (S1-R6) com evidência E1 ou superior do projeto, registrando n, período, o que mudou e por quê. Com zero eventos (E0) mantém o plano padrão e propõe um **diagnóstico** antes de priorizar. | `scripts/study_plan.py` e `scripts/evidence_projection.py`; `state/CURRENT.json` em E0 prova o caso base. |
| S2-R6 | **Prescrição do caderno:** plataforma, filtros em camadas, quantidade **sugerida** e justificativa, sem afirmar que existam questões; devolve como o estudante envia o resultado. | `scripts/notebook_prescriber.py` e `tests/` já cobrem a prescrição (RM-05). |
| S2-R7 | **Prompt ao Notebook (PR-012):** mínimo, com assunto, lacuna, método e fonte; sem dado pessoal, CPF, credencial, export bruto, captura de tela nem texto integral de questão. A resposta do Notebook é **dado não confiável**: o Tutor confere a fonte antes de entregar. | Regras de `agents/TUTOR.md` (revisão humana). `scripts/tool_gateway.py` é gateway offline de autorização, limite de taxa e estado; **não filtra conteúdo pessoal do prompt**, então esse filtro é lacuna a tratar na S4. O caminho direto ou pela Zapia não está decidido (OPEN-10), e nada foi testado (E-08). |
| S2-R8 | **Honestidade sobre domínio:** acerto recente ou questão repetida não prova retenção; o Tutor só declara domínio com questões inéditas, n e período. | `rules/STUDY.md`; níveis E0 a E4 (RM-03). |
| S2-R9 | **Sem efeito externo próprio:** o Tutor não executa ferramentas, não grava e não recebe credenciais; emite comandos à Zapia pelo formato de PR-013. Se a ferramenta não existir, entrega o conteúdo no chat e diz que nada foi enviado nem gravado. | `agents/TUTOR.md`; `scripts/agent_entrypoint.py` (broker somente leitura) e `scripts/write_policy.py --check`. |

## Aceite

1. `python scripts/doc_cohesion.py --check` passa.
2. `python -m unittest tests.test_doc_cohesion tests.test_plano_e_pesquisa_docs tests.test_study_plan` passa, sem rede nem conta real.
3. Revisão humana do proprietário de S2-R1, S2-R3 e S2-R7, que dependem de julgamento sobre o texto do modelo; o aceite deste item não prova a conduta do Tutor em produção (isso é GP-4 / RM-08, ainda bloqueado).
4. Teste sintético de PR-012 (criar notebook, adicionar fonte de texto, enviar prompt, ler a resposta, abrir citação) **fica fora do aceite** desta especificação e depende da decisão do OPEN-10.

## Limites

- Não prova que o Tutor ensina bem: as evidências são de outras áreas e de outros públicos, e nenhuma compara tutor por IA em concursos.
- Não escolhe o caminho de acesso ao Notebook (OPEN-10) nem a leitura direta das plataformas (OPEN-12); isso é da S4.
- Não implementa persistência de erros nem de resultados (repositório privado pendente, D-01).
- Não define a rotina diária, os lembretes e a motivação, que são do Coach (S3).
