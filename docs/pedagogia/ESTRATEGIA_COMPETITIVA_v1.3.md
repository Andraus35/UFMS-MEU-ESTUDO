# Estratégia competitiva integrada — cargos UFMS 523 e 324 | v1.3

**Estado:** ESPECIFICAÇÃO PEDAGÓGICA PROPOSTA — não é motor implantado nem demonstração de resultados.  
**Referências:** [método v1.0](METODO_v1.0.md), [decisor v1.1](PROTOCOLO_DECISAO_v1.1.md), [evidências v1.2](MODELO_EVIDENCIAS_v1.2.md).  
**Recorte do edital:** PROGEP/UFMS nº 152/2026, sujeito à conferência de retificações. Dados abaixo decorrem de `config/concursos.json` e `config/topics.csv` na branch de engenharia do PR #1, consultados em 04/11/2026; **não são retificações verificadas**.

## 1. Objetivo competitivo sem promessas de aprovação

Preparar **duas provas diferentes** com aproveitamento de aprendizado compartilhável, respeitando:
- Cargo **523**: Analista em Educação / Administração e Informação / Gestão Pública — prova de nível superior, turno da manhã.
- Cargo **324**: Técnico em Educação / Processos Educacionais / Assuntos Estudantis — prova de nível médio, turno da tarde.
- Mesma data prevista na configuração: **17/01/2027**, banca FAPEC, provas de **60 questões**, **100 pontos**, **4 horas** cada.
- O cadastro atual indica mínimo global de **50 pontos** e **nota não zero em nenhuma das cinco áreas**. Tratar como condição normativa **a confirmar no edital vigente antes de simular cortes ou afirmar elegibilidade**.

Não produzir probabilidade numérica de classificação, estimativa de nota final, de aprovação ou de esquecimento sem dados apropriados e validação. Não atribuir competência por idade, formação ou impressão subjetiva.

## 2. Matriz normativa de pontuação e atenção

| Área | Questões em cada prova | Pontos por prova | Aplicação |
|---|---:|---:|---|
| Língua Portuguesa | 15 | 15 | Conteúdos gerais; verificar recorte por cargo |
| Língua Inglesa | 5 | 5 | Conteúdos gerais; não ignorar risco de nota zero |
| Legislação | 10 | 20 | Conteúdos gerais; checar normas vigentes e alterações |
| Raciocínio Lógico | 10 | 20 | Conteúdos gerais |
| Conhecimentos Específicos | 20 | 40 | Programas separados 523 e 324 |
| **Total** | **60** | **100** | **Cada prova** |

Esta tabela não justifica dedicar 40% do tempo aos específicos, nem 5% ao Inglês. Pontos são **valor de prova**, não proporção automática de estudo, probabilidade de cobrança de subtópico ou domínio. O agente pondera pontos, risco eliminatório, lacuna, incerteza e custo de oportunidade.

## 3. Fonte de verdade e fronteiras entre cargos

A representação atual possui **4 blocos gerais** aplicáveis a ambos os cargos, **10 blocos específicos 523** e **9 blocos específicos 324**.

Aproveitamento entre cargos exige duas camadas:
1. **Conceitual:** um conteúdo idêntico pode ser aprendido uma vez e servir aos dois objetivos.
2. **Prova/cargo:** dificuldade, contexto, formulação e capacidade de resolver itens de cada prova permanecem **evidências distintas**.

Exemplos de **sobreposições a verificar por subtópico**, não equivalências aprovadas:
- `523-04` ↔ `324-01`: organização/funcionamento da educação superior.
- `523-07` ↔ `324-09`: recursos materiais e patrimoniais.
- `523-09` ↔ `324-05`: informação, documentação e comunicação oficial.
- `523-10` ↔ `324-08`: atendimento ao público.
- `523-01` ↔ `324-07`: noções de administração e organização do trabalho.

O rótulo semelhante é uma **hipótese de ganho conjunto**, não autorização para fundir todas as exigências. O agente deve comparar os trechos oficiais dos dois programas e classificar a interseção: confirmada / parcial / não confirmada. Registrar a evidência documental; quando incompleta, preservar planos e resultados separados.

## 4. Prioridade como decisão multicritério, não cronograma

Para cada candidato a próxima atividade, avaliar separadamente:
- **Valor de prova:** área, peso e requisito eliminatório aplicável ao cargo.
- **Necessidade observada:** dificuldade conceitual, erro recorrente, retenção, transferência, cobertura.
- **Qualidade da evidência:** E0–E4, independência, novidade, comparabilidade e incerteza.
- **Ganhos de escopo:** avanço em um ou dois cargos, sem contagem dupla de questões.
- **Custo e viabilidade:** tempo/energia disponíveis **informados**, quantidade/diversidade de questões confirmadas.
- **Proximidade temporal:** demanda por simulações, recuperação e cobertura antes da data de prova.
- **Oportunidade diagnóstica:** o que uma atividade nova esclareceria quando o sistema sabe pouco.

O avaliador deve produzir uma **comparação documentada entre alternativas**, não uma nota pseudoexata escondida. Peso relativo de critérios pode ser configurado, versionado e revisto, mas não se pode afirmar calibração científica onde ela não existe.

### Ordem de proteção

1. **Bloqueios:** fonte inválida, atribuição errada de assunto a cargo, resultado incoerente, caderno impossível, recomendação baseada em dados inventados.
2. **Riscos prioritários:** área sem diagnóstico ou com desempenho muito fragilizado frente a requisitos eliminatórios; corrigir com avaliação proporcional, não aprisionar o estudo.
3. **Necessidades de aprendizagem:** exploração de conteúdo relevante, correção de lacuna, recuperação, transferência ou simulação.
4. **Preferência adaptativa:** comparar benefícios e custos; a escolha aleatória ponderada, quando usada, acontece apenas entre opções elegíveis e com semente e pesos registrados.

Um risco eliminatório conhecido pode superar uma oportunidade de pontuação elevada em outra área. Isso não implica negligenciar indefinidamente os conhecimentos específicos.

## 5. Como decidir entre conteúdos compartilhados e específicos

**Compartilhado é candidato forte** quando: há correspondência documental, benefício para os dois cargos, aprendizagem insuficiente e inexistência de risco mais urgente em específicos.

**Específico 523 é candidato forte** quando: há lacuna substantiva nos seus 10 blocos, peso relevante e pouca evidência de transferência para provas de nível superior.

**Específico 324 é candidato forte** quando: procedimentos acadêmicos/estudantis ou regras próprias permanecem sem cobertura, apesar de boas notas em conteúdos administrativos gerais.

**Recuperação supera exploração** quando: o histórico aponta esquecimento relevante que provavelmente comprometerá conhecimentos já estudados.

**Exploração supera repetição** quando: se acumulam acertos em itens familiares, mas ainda há muitos blocos sem avaliação e pouca evidência de ganho marginal da repetição.

Nenhuma dessas situações cria uma cota fixa de tempo ou de questões. O tutor reavalia depois de cada devolução significativa.

## 6. Sequência de decisão sem planograma

Em cada oportunidade de estudo:
1. Carregar o checkpoint e as evidências relevantes; validar integridade.
2. Identificar cargos e áreas ainda sem diagnóstico e verificar riscos normativos, sem inventar nota futura.
3. Listar candidatos: comum, específico 523, específico 324, correção, recuperação ou simulação.
4. Qualificar a incerteza e retirar candidatos sem suporte ou fora do escopo.
5. Comparar o benefício informacional/pedagógico e o custo de oportunidade.
6. Escolher **uma atividade principal viável**, com alternativas se faltarem questões; justificar também por que as principais opções concorrentes foram adiadas.
7. Prescrever filtros e forma de execução; esperar o resultado real.
8. Atualizar estado apenas quando houver autorização, validação e commit confirmado; recalcular prioridades.

O estudante pode indicar tempo disponível, preferência por disciplina ou necessidade de descanso; isso altera a recomendação de maneira transparente. A IA nunca deve inventar disponibilidade diária ou impor um calendário.

## 7. Estratégia de simulados: duas provas no mesmo dia

Planejar avaliações distintas:
- **Simulado do 523:** conteúdo e nível do cargo 523, composição prevista no edital, restrições e modalidade independente.
- **Simulado do 324:** conteúdo e nível do cargo 324, com sua própria composição e relatório.
- **Simulação combinada do dia:** quando viável e consentida, reproduzir a sequência **manhã → intervalo → tarde**, observando atenção, ritmo e fadiga, sem impor duração/intervalo inventados ou substituir as regras oficiais dos turnos.

Registrar por cargo: pontos, respostas em branco, desempenho por área, tempo, grau de ajuda, dúvidas, erros de execução e comparação com simulados **equivalentes**. O tutor não deve inferir que fazer uma boa prova de manhã garanta a da tarde.

Uma simulação completa informa mais sobre execução integrada do que sobre a causa de cada erro: para intervenção focalizada, recuperar questões e dados por área quando disponíveis. Não confundir simulado isolado com previsão de nota real.

## 8. Mudança da estratégia com a proximidade das provas

Não converter o prazo em percentuais fixos ou fases por semanas. O tempo restante altera o custo de oportunidade:
- Com muita cobertura pendente, favorecer amostragem diagnóstica e aprendizagem de conteúdos relevantes sem abandonar recuperações comprovadamente necessárias.
- Quando o avanço conceitual existir mas retenção for incerta, valorizar recuperações sem ajuda e itens novos.
- Quando a prova se aproximar e a cobertura estiver razoavelmente documentada, ampliar simulados, intercalação e execução sob tempo **se houver benefício evidenciado**.
- Nos últimos dias, não presumir que exaustão, privação de sono ou volume máximo de questões aumentem o resultado. Ajustar a carga às condições relatadas.

Essa adaptação decorre de estados observados, não de calendário obrigatório.

## 9. Regras contra estratégias aparentemente boas e ineficientes

**É proibido inferir:**
- “Conhecimentos específicos valem 40 pontos, então devem receber 40% das horas.”
- “O assunto X tem 0% de acertos” quando ainda não houve avaliação.
- “Acertou questões do 523, portanto já domina o 324” sem equivalência verificada.
- “Matéria vale só 5 pontos, então pode ser ignorada” apesar da restrição eliminatória.
- “Uma sequência de acertos em questões repetidas prova retenção.”
- “Uma amostra pequena, sem comparabilidade, demonstra melhora de nota.”
- “Temos 29 vagas e 18 vagas, logo as chances individuais de aprovação são estimáveis.”

**O agente deve explicitar** evidência, incerteza, trade-off, intervenção, próxima condição de reavaliação e origem do conteúdo do edital.

## 10. Registro estruturado de cada recomendação

Campos sugeridos (modelo lógico, ainda não schema de produção):
- `decision_id`, `timestamp`, `source_commit`, `edital_version`, `retifications_checked`.
- `target_cargo_ids`, `topic_ids`, `overlap_status`, `scope_evidence`.
- `evidence_refs`, `evidence_quality_E0_E4`, `uncertainties`, `risk_flags`.
- `considered_options`, `selected_intervention`, `selection_mode` (comparação ou sorteio), `weights` e `seed` quando usados.
- `expected_learning_signal`, `caderno_filters`, `suggested_quantity`, `fallback_filters`, `rationale`, `next_reassessment_condition`.
- `persistence_status` e `remote_commit_sha` somente após confirmação.

Sem medição real, os campos de desempenho e progresso permanecem vazios/desconhecidos. Registros de decisão devem ser concisos, sem armazenar texto protegido de plataformas.

## 11. Cenários ilustrativos de avaliação (não são dados do estudante)

| Cenário | Resposta esperada do tutor |
|---|---|
| Inglês sem diagnóstico; específicos 523 com resultados bons | Considerar diagnóstico de Inglês pela exigência de não zerar, sem impor estudo diário |
| Legislação comum com esquecimento posterior | Favorecer recuperação independente útil a ambos |
| Documentação oficial 523 e comunicação oficial 324 com nomes parecidos | Conferir o recorte de cada um antes de compartilhar uma mesma evidência |
| Específicos 324 sem avaliação e muitos cadernos 523 resolvidos | Considerar diagnóstico de 324 em vez de extrapolar preparo |
| Acertos altos em Português com questões repetidas | Buscar itens inéditos e recuperação, não declarar domínio |
| Simulado 523 adequado; simulado 324 fraco após o intervalo | Investigar causas e condições da segunda prova, sem reduzir a análise a fadiga |
| Prazo mais curto e amplo conteúdo inexplorado | Priorizar por relevância, risco e informação; não inventar percentuais de cobertura |
| Assunto compartilhado bem comprovado e assunto exclusivo crítico | Escolher o exclusivo quando o ganho marginal e risco o justificarem |

## 12. Condições de aprovação pedagógica da v1.3

1. Há **duas provas-alvo** e um histórico de eventos que não duplica tentativas.
2. A pontuação por área é lida como fonte normativa, não convertida automaticamente em horas de estudo.
3. Risco eliminatório é considerado mesmo em áreas de menor peso, com reavaliação após evidência.
4. Conteúdo compartilhado é somente o que o edital confirma; sem fusão por nomes parecidos.
5. Resultados de um cargo não viram nota do outro.
6. Cenários com dados ausentes geram incerteza explícita ou diagnóstico.
7. Simulações por turno e combinadas são avaliadas separadamente.
8. O tutor justifica prioridades e custos de oportunidade sem impor um cronograma.
9. Aleatoriedade jamais supera bloqueios determinísticos; sorteio reproduzível só quando elegível.
10. Mudança nas evidências ou no escopo do edital pode mudar a decisão, com justificativa.

**Gate:** esta entrega documenta estratégia e critérios, não habilita tutor adaptativo, acesso a plataformas ou escrita de desempenho. Implementação, integração ao PR #1, testes e aprovação humana são posteriores e independentes.
