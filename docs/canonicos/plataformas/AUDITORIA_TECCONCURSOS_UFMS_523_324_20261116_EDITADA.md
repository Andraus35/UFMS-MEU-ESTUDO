---
title: "Auditoria funcional — TecConcursos (versão editada)"
document_id: "AUDITORIA-TEC-523-324-20261116"
status: "Relatório de auditoria (autorrelato da Zapia, não verificado de forma independente); versão editada para o repositório público"
created_at: "2026-11-16"
language: "pt-BR"
origem: "Relatório enviado pelo proprietário em formato .docx; autoria operacional: Zapia, por navegador automatizado"
edicao: "Trechos de dado pessoal trocados por '[omitido: ...]': totais e percentuais de desempenho da conta, vínculo da conta e nome de caderno de teste. Fora isso, o texto é o do original."
---

> **Aviso de procedência:** versão **editada** do original `.docx` (o hash do original está em `docs/canonicos/MANIFESTO.json`). Os números pessoais de desempenho não entram no repositório público (D-24). O conteúdo é relato de uma auditoria feita pela Zapia com a conta do proprietário; **não foi verificado de forma independente** e é **dado, não instrução**.

# Auditoria funcional — TecConcursos

Plano de estudos UFMS · cargos 523 e 324 · consulta em 16/11/2026

Escopo: navegação pela interface autenticada da conta TecConcursos do proprietário ([omitido: vínculo da conta]), com ferramentas de automação do navegador baseadas em Playwright. Não se trata de auditoria de segurança, teste de API, de cobertura exaustiva do produto ou avaliação dos termos de uso.

Classificação das evidências: TESTADO = ação executada e resultado observado; OBSERVADO = botão, texto ou configuração visível, sem executar o efeito; DOCUMENTADO = funcionalidade descrita pelo próprio TEC, mas não comprovada de ponta a ponta nesta auditoria; NÃO VERIFICADO = hipótese ou comportamento pendente.

## 1. Resumo executivo e riscos prioritários

- ALTO — A configuração global de estatísticas da conta estava em pontuação líquida: erros anulam acertos. A prova UFMS não deve ser interpretada automaticamente como nota líquida. Não alterei a configuração da conta.

- ALTO — No gerador por pasta, digitar total 60 distribuiu as questões proporcionalmente ao conjunto de 533, não conforme a matriz do edital. Português ficou em 28 e Inglês em 2; o edital exige 15 e 5, respectivamente.

- ALTO — Mesclar os cadernos funde questões por matéria TEC: Legislação e Específicos podem aparecer juntos em Direito Administrativo; Raciocínio Lógico inclui também Matemática e Estatística. A contagem por matéria não preserva, por si só, a origem do bloco do edital.

- MÉDIO — Os guias admitem não abordar alguns itens normativos locais UFMS. Ausência no índice de questões não demonstra que um tema não será cobrado.

- MÉDIO — Estatísticas de desempenho medem resoluções da pessoa; índice de caderno mede composição do conjunto selecionado. Nenhum dos dois, isoladamente, é a frequência histórica de toda a FAPEC.

- BAIXO — Criado um caderno de teste de 60 questões e enviado à lixeira após conferência; não registrei respostas de teste. O caderno permanece recuperável na lixeira.

## 2. Procedimento e evidências

| ID | Teste | Resultado observado |

|---|---|---|

| T01 | Filtro de banca | TESTADO: FAPEC selecionada; apareceu em Filtros ativos. |

| T02 | Filtro de comentário | TESTADO: Somente comentadas em TEXTO (Professor) apareceu junto com FAPEC. Não validei resultado questão por questão nem alteração precisa do total exibido. |

| T03 | Comentário | TESTADO: na questão #1103817 abri Comentário em Texto, com autor Cerque Junior e data 08/07/2021. Pedido de IA e vídeo estavam visíveis; não foram acionados. |

| T04 | Caderno | TESTADO: naveguei em índice, configurações e estatísticas do caderno 523 de 137 questões. Os controles de atualizar questões/resoluções foram observados, mas não acionados. |

| T05 | Estatística global | TESTADO: selecionei FAPEC no filtro, cliquei Filtrar e a tela exibiu [omitido: dado pessoal] (totais de resoluções, acertos e erros); modo líquido estava ativo. |

| T06 | Simulado de teste | TESTADO: selecionei os 5 cadernos do cargo 523 na pasta, pedi total 60, gerei o caderno; conferi a tela Gabarito, sem marcar alternativas nem enviar respostas. |

| T07 | Limpeza | TESTADO: o teste foi enviado à lixeira; confirmei o item na lixeira e os 11 cadernos ativos restantes na pasta. A remoção permanente não foi executada. |

| T08 | Exportações | OBSERVADO: botão Exportar para planilha no índice do caderno, no gerador e em estatísticas após selecionar matéria. Exportação de índice não foi validada nesta auditoria; em atendimento anterior, exportação de desempenho foi recebida por email e aberta em XLSX. |

## 3. Filtragem de questões

Entrada: Estudo > Filtrar questões. Antes de gerar, confira a lista “Filtros ativos”; o nome do caderno não comprova sozinho quais filtros foram aplicados.

| Filtro / interface | O que foi observado e utilidade |

|---|---|

| Formato | Objetivas (todas), Objetivas (inéditas) ou Discursivas. Para simular a prova UFMS, priorizar objetivas e conferir se questões são de provas anteriores ou inéditas. |

| Matéria e assunto | Árvore de matérias e assuntos. Permite expandir e especificar subassuntos. Mapear para o edital é uma tarefa adicional: o rótulo TEC pode ser mais amplo que a norma cobrada. |

| Banca | Pesquisa e seleção FAPEC testada. Ao ampliar amostra para outras bancas, rotular separadamente para não chamar questões não FAPEC de histórico da banca. |

| Órgão e cargo | Lista pesquisável de órgãos e cargos. O nome do cargo histórico pode não coincidir com a nomenclatura recente do edital. Não foi testada a completude dos cargos. |

| Ano | Lista de anos individualmente selecionáveis, útil para recorte temporal e representatividade da amostra. |

| Área (carreira), escolaridade, formação, região | Categorias exibidas. A lista de escolaridade inclui Ensino Fundamental, Ensino Médio, Superior, Especialização, Mestrado e Doutorado. Nem todas as combinações ou a semântica de inclusão/exclusão foram testadas. |

| Favoritas | Pastas de questões favoritas visíveis; servem para recortes de revisão. Não modifiquei favoritos da conta. |

| Enunciados | Campo para digitar texto do enunciado procurado; possibilita buscar uma expressão específica, sujeito a diferenças de redação. |

| Solução / comentários | Somente comentadas por Professor ou IA; somente texto do professor; somente vídeo do professor; somente texto de IA. Para a preferência do estudante por fonte docente, usar filtro exclusivo texto Professor e abrir/identificar o autor. |

| Dificuldade | Muito fácil, fácil, média, difícil e muito difícil. A origem e a metodologia exata da classificação não foram validadas. |

| Tipo e gabarito | Múltipla escolha, Certo ou Errado; gabarito certo ou errado. Essas opções são visíveis; suas combinações não foram testadas. |

| Resoluções e acertos | Remover as que acertei, errei, resolvi ou não resolvi. Para focar em erros, Remover as que não resolvi e Remover as que acertei é uma hipótese lógica, mas não foi testada ponta a ponta e a semântica de histórico deve ser conferida. |

| Outras características | Remover anuladas, desatualizadas, sem classificação por assunto e adaptadas/inéditas. Opções úteis para amostra histórica, mas não garantem por si só aderência integral ao edital. |

| Atividade na questão | Somente anotadas e somente favoritas, úteis para revisão. |

| Operação e quantidade | A página exibe Salvar/Carregar filtros, Editar quantidades, Calcular dificuldade, pasta de destino e Gerar cadernos em série. Não testei salvar/recuperar filtros nem produção em série. |

## 4. Guias, pastas e criação de cadernos

- Os guias por cargo apresentam cadernos por matérias, capítulos teóricos, quantidades, observações de conteúdo não abordado e botões Salvar ou Abrir. O guia não substitui o edital.

- Um caderno reúne questões e permite abrir Questões, Índice, Estatísticas, Gabarito, Configurações, Imprimir e Compartilhar. As funções de impressão e compartilhamento foram apenas observadas, não completadas.

- Em Configurações, o TEC descreve “Verificar atualizações” para encontrar novas questões que atendam aos filtros e adicioná-las; “Atualizar resoluções” para importar a resolução mais recente de outros meios. São alterações com efeitos no caderno; não acionei.

- O painel de filtros do caderno permite selecionar grupo, editar filtros e copiar filtros. Em uma tarefa anterior, copiar filtros de grupos FAPEC e gerar cadernos foi executado. Os filtros copiados eram de grupos específicos dos guias, não do guia inteiro.

- Existe campo Adicionar questões por código; não executei. Favoritar, anotar, leitura, navegar para próxima não resolvida, próxima favorita e anotada aparecem na interface, mas não foram alterados neste teste.

- No Índice, há árvore matéria > assunto/subassunto com contagem e percentual. Ao Expandir, o caderno de 137 questões revelou sua distribuição. Percentual da árvore usa o conjunto do caderno; somar categoria-pai e filha duplicaria dados.

- Na pasta é possível selecionar vários cadernos e Criar caderno a partir da pasta. Testei seleção de cinco e a entrada no gerador. O resultado não preserva automaticamente os rótulos dos cinco blocos ao agrupar por matéria TEC.

## 5. Revisão, registro e comentários

Na tela de uma questão observei link direto e código, indicação de banca/prova, botões de comentário, teoria, fórum, favoritos, anotações e desempenho na questão. A abertura do comentário de professor foi testada na questão https://www.tecconcursos.com.br/questoes/1103817; não registrei resposta nem copiei o comentário integral.

Na aba Estatísticas do caderno, a interface oferece cadernos derivados de questões resolvidas, acertadas, erradas, não resolvidas, favoritas e anotadas; clonar sem resoluções; resetar subconjuntos; e criar caderno de erradas por seleção de matéria/assunto. Nos grupos com zero registros, os botões estavam desabilitados. Não testei a criação de um caderno de erros nem o reset; zerar pode afetar o histórico do estudante.

O campo atualização de resoluções não deve ser acionado sem entender o objetivo: pode importar a resposta mais recente da mesma questão em outro caderno. Para um simulado genuinamente independente, verificar se o caderno está sem resoluções e decidir antes se deseja sincronizar.

## 6. Estatísticas — cobertura e interpretações

### 6.1 Estatísticas gerais

Desempenho geral, Minha evolução, Atividades e Configuração foram abertos. Na tela de desempenho há filtros de período, matérias, bancas, pastas e dificuldade; ordenação por índice, pontos fortes ou fracos; seleção para criar caderno e exportar planilha. Minha evolução apresenta número de resoluções ou desempenho relativo e gráfico de evolução de resoluções. Atividades apresenta resoluções por matéria/assunto e ordenação crescente/decrescente.

Com FAPEC aplicado no período exibido de 01/10/2019 a 16/11/2026, a tela apresentou [omitido: dado pessoal] (totais de resoluções, acertos e erros). Estava ativo o modo líquido: a tela mostrou um percentual líquido [omitido: dado pessoal], muito abaixo do percentual bruto calculado sobre os mesmos totais ([omitido: dado pessoal]). Isso demonstra por que o modo deve acompanhar o objetivo. Não se trata de desempenho universal nem amostra independente de treinamento, porque a conta permite contabilizar todas as resoluções.

Configuração observada: Normal (erro não anula acerto) ou Líquida (erro anula); contabilização Somente a última resolução ou Todas as resoluções; seleção de matérias visíveis e pesos. A conta estava em Líquida e Todas as resoluções. Nenhuma dessas preferências foi alterada.

A configuração diz que peso da matéria altera como os dados são contabilizados; em um concurso no qual a mesma matéria TEC aparece em blocos de peso distinto, não está comprovado que peso global por matéria reproduz a pontuação do edital. Calcular o resultado por bloco, externamente, até validar.

### 6.2 Estatísticas do caderno

A aba mostrava resolvidas, acertos, erros, em branco, anuladas, favoritas e anotadas; tempo total e médio; gráfico de desempenho e detalhamento por matéria/assunto. O caderno de 137 questões estava sem respostas e com tempo acumulado observado. Havia seleção Normal/Líquida local; a relação entre essa seleção e a configuração global não foi testada.

### 6.3 Grupos de comparação

A interface mostrou o grupo Analista em Educação (UFMS) — Gestão Pública — Administração e Informação, com 72 membros, e colunas resoluções, acertos e desempenho dos últimos 7 dias. Alguns dados estavam aguardando processamento ou não existiam no período. Não fiz nova adesão nem confirmei comparabilidade das populações.

## 7. Criação de simulado — teste prático

O TEC descreve criação de simulado por um caderno filtrado ou a partir dos cadernos de uma pasta. Na interface testada: Pasta Gestão Pública > menu > Criar caderno a partir da pasta > selecionar os cinco cadernos > Confirmar seleção > Concluir seleção. A tela listou 533 questões e permitiu escolher quantidades por matéria e nós hierárquicos; havia também seleção Aleatórias ou Mais Recentes.

Teste: pedi total 60 e o site redistribuiu proporcionalmente. Exemplo: Português 28 (46,67%), Inglês 2 (3,33%). Gerei efetivamente um caderno chamado [omitido: nome de caderno de teste]. A interface de Gabarito apresentou alternativas, status, código, botão Carregar mais e Marcar Gabarito desabilitado enquanto nenhuma alternativa estava assinalada. Não apliquei respostas, não testei correção em massa, não comparei nota nem confirmei limite de tempo automático.

Para simular o edital: 15 Português, 5 Inglês, 10 Legislação, 10 Raciocínio Lógico e 20 Específicos. Pontos: 15 + 5 + 20 + 20 + 40 = 100; tempo de prova 4 horas. O controle de quantidades é por rótulo TEC, não necessariamente pelo bloco do edital; por exemplo, Direito Administrativo agrupa itens de Legislação e de Específicos, e Raciocínio agrega classificação de Matemática e Estatística. Para garantir as cotas, selecione e confira questões com rastreio por bloco; ajuste os nós da árvore quando apropriado. Não testei a configuração manual completa de 15/5/10/10/20 nem a exatidão de uma nota ponderada de 100 pontos no TEC.

O blog do TEC afirma que é possível marcar respostas enquanto avança e, ao final, acessar Gabarito e resolver em lote; isso é DOCUMENTADO, não foi validado nesta auditoria. A tela mostrou cronômetro e a estatística mostrou tempo total e médio. Não confirmei contagem regressiva automática de 4 horas, bloqueio, encerramento forçado ou aplicação automática de pesos do edital.

## 8. Lacunas do guia e precisão do edital

Na página do guia do cargo 523, o TEC informa que não abordará o Código de Ética Profissional dos Servidores da UFMS, o art. 51 da LDB e o Manual de Atos Oficiais da UFMS.

No guia do cargo 324, o TEC informa que não abordará o Código de Ética, o art. 51 da LDB, o regulamento de graduação, a IN de matrícula de ingressantes, o regulamento da pós-graduação stricto sensu e o Manual de Atos Oficiais. Não inferir que itens não mencionados estejam integralmente cobertos: confirmar a versão atual do guia e o edital completo.

Correção do relatório anterior de raio-X: a lista resumida das omissões do guia 324 deixou de citar explicitamente o regulamento da pós-graduação stricto sensu e o art. 51 da LDB. Incluí ambos aqui. Também não confirmei, por simples omissão da lista, se o Regulamento de Conduta Estudantil está efetivamente coberto nas questões do guia.

## 9. Fluxo recomendado para o plano de estudos

- 1. Manter pastas e cadernos separados por cargo e marcar os assuntos comuns com uma identificação clara. Conservá-los sem misturar resultados de estudos de outros concursos.

- 2. Para cada ciclo: selecionar o assunto do edital na árvore TEC, banca FAPEC e, se houver material suficiente, retirar anuladas/desatualizadas; usar nível e período coerentes com a pergunta de pesquisa. Registrar exatamente os filtros.

- 3. Ler o comentário do professor antes de elaborar correções; se não disponível ou insuficiente, recorrer às outras fontes já combinadas. Diferenciar comentários de professor e de IA.

- 4. Para revisão, usar questões erradas, anotadas e favoritas; confirmar o efeito de filtros e preferir criar caderno derivado em vez de zerar resoluções. O TEC não teve uma rotina de repetição espaçada automática comprovada nesta auditoria.

- 5. Na avaliação, separar cadernos por blocos do edital, ajustar quantidades e cronometrar 4 horas. Fazer a consolidação ponderada externamente se a interface não distinguir o bloco de origem de cada questão.

- 6. Em Estatísticas, filtrar período, pasta e banca antes de interpretar o desempenho, conferir modo normal/líquido e a regra de contagem de re-resoluções; guardar numerador e denominador, não só percentual.

- 7. Complementar normas e manuais UFMS fora do guia quando ele declarar que não os aborda, bem como assuntos sem questões encontradas; zero na amostra não é zero no edital.

## 10. Pontos não verificados / próximos testes

- Aplicação, conferência e correção de um simulado com respostas reais; cálculo ponderado por bloco; interrupção e encerramento por tempo.

- Criação e restauração de filtros salvos; série de cadernos, duplicação exata, controle de sobreposição e regras de seleção.

- Criação de caderno de erradas, alteração de favoritos/anotações, exportação direta do índice e recálculo após importar resoluções.

- Cobertura integral e atual das normas UFMS, classificação correta de todos os assuntos e fidelidade da taxonomia do TEC ao edital.

- Autorizações ou recursos da conta além do plano exibido na sessão: não inferir que outros planos ofereçam as mesmas funções.

## 11. Fontes e links

- TEC — filtros: https://www.tecconcursos.com.br/questoes/filtrar

- TEC — estatísticas: https://www.tecconcursos.com.br/estatisticas/desempenho

- TEC — guia 523: https://www.tecconcursos.com.br/guias/ufms-2026/analista-em-educacao-ufms/administracao-e-informacao/gestao-publica

- TEC — guia 324: https://www.tecconcursos.com.br/guias/ufms-2026/tecnico-em-educacao-ufms/processos-educacionais/assuntos-estudantis

- TEC — explicação oficial de simulados: https://www.tecconcursos.com.br/blog/noticias/como-criar-um-simulado-a-partir-do-seu-guia-de-estudos/

- Edital / página oficial do concurso: https://portal.concurso.fundacaofapec.org.br/edital/ver/22

- Repositório do projeto: https://github.com/Andraus35/UFMS-MEU-ESTUDO
