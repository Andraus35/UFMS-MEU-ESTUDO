---
title: "Base cognitiva e estratégica do Harness de Aprendizagem e Desempenho"
document_id: "BASE-COGNITIVA-HARNESS-001"
version: "1.0"
status: "Documento-fonte complementar — proposta para o harness cognitivo"
created_at: "2026-11-16"
language: "pt-BR"
owner_context: "A Arte da Guerra Concursos"
scope: "Tutor de Aprendizagem, Coach de Prova e Orquestrador"
parent_document: "PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md"
relationship: "Complementar e subordinado; preserva a precedência temática da pesquisa de inteligência adversarial"
---

# Base cognitiva e estratégica do Harness de Aprendizagem e Desempenho

**Documento-fonte comum para orientar Tutor de Aprendizagem, Coach de Prova e Orquestrador.**

- **ID:** `BASE-COGNITIVA-HARNESS-001`
- **Versão:** 1.0
- **Data:** 16/11/2026
- **Natureza:** pesquisa aplicada, princípios arquiteturais e requisitos propostos
- **Documento primário de inteligência de prova:** `PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md`
- **Componentes destinatários:** Tutor de Aprendizagem, Coach de Prova e Orquestrador
- **Contexto:** harness cognitivo pessoal de agentes de IA; não é especificação de produto comercial nem pressupõe sistema de software autônomo.

---

# 1. Propósito e posição na arquitetura

Este documento consolida os conhecimentos de ciência da aprendizagem, aquisição, recuperação, retenção, prática espaçada, feedback, metacognição, transferência e avaliação, organizando-os em uma arquitetura cognitiva comum para a preparação de concursos públicos.

Sua função é orientar a estratégia conjunta do Tutor e do Coach sem apagar a separação de responsabilidades estabelecida em `PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md`.

**Regra de precedência:** `PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md` permanece a referência primária para inteligência adversarial de prova: elaboração e estrutura de itens, padrões observáveis das bancas, distratores, induções, extrapolações, tangenciamentos, interpretação de enunciados, tempo, risco e execução da prova. Este documento não substitui, reescreve nem reduz essa pesquisa. Acrescenta a base cognitiva que permite transformar conhecimento em aprendizagem duradoura e, depois, em desempenho autônomo na prova.

A relação é complementar e assimétrica:

- A pesquisa de inteligência adversarial orienta predominantemente o Coach de Prova.
- Esta base cognitiva orienta o Tutor e o Coach, cada qual dentro de sua responsabilidade.
- O Orquestrador integra as evidências, decide prioridades e encaminha intervenções.
- Nenhum dos documentos, isoladamente, constitui especificação de implementação aprovada.

## 1.1 Princípio central

**O Tutor constrói, organiza, consolida e mantém o conhecimento recuperável. O Coach verifica se esse conhecimento pode ser mobilizado, discriminado e aplicado diante das exigências reais e adversariais da prova. O Orquestrador coordena o ciclo com base em evidências.**

O objetivo terminal é que o candidato consiga recuperar e aplicar o conhecimento sem depender da IA, de pistas, de materiais ou de condições artificiais de treinamento.

# 2. Limites epistemológicos e de aplicação

As evidências científicas citadas neste documento abrangem populações, contextos educacionais, tarefas e instrumentos diferentes. Estudos com estudantes escolares ou universitários não comprovam automaticamente o mesmo tamanho de efeito em candidatos adultos de concursos públicos.

É obrigatório distinguir:

1. resultado experimental observado;
2. síntese de pesquisa ou meta-análise;
3. recomendação pedagógica derivada da evidência;
4. decisão arquitetural proposta para este harness;
5. hipótese que ainda precisa ser testada no uso pessoal;
6. requisito determinístico que pode ser verificado.

Não converter uma recomendação em fato científico. Não converter uma hipótese de funcionamento em garantia de resultado. Não apresentar associação como causalidade.

A evidência orienta a seleção de métodos; o desempenho observado no próprio candidato informa sua adaptação; os gates controlam a integridade das conclusões.

# 3. Arquitetura de responsabilidades: Tutor, Coach e Orquestrador

## 3.1 Tutor de Aprendizagem — construir competência recuperável

Responsabilidade primária:

- mapear e decompor o conteúdo do edital em unidades de aprendizagem;
- diagnosticar conhecimento prévio e lacunas;
- ensinar conceitos, regras e procedimentos;
- apoiar codificação e compreensão;
- promover autoexplicação e elaboração;
- conduzir recuperação ativa;
- fornecer feedback corretivo;
- promover reaprendizagem sucessiva;
- administrar revisão espaçada e manutenção;
- identificar esquecimento, fragilidade e confusão conceitual;
- verificar recuperação independente, retenção e transferência conceitual;
- reduzir progressivamente a dependência de pistas e assistência.

O Tutor pode usar questões oficiais, questões de bancos e questões sintéticas validadas como instrumentos de aprendizagem e diagnóstico. Não assume, porém, a missão principal de estudar padrões de banca, ensinar estratégia de marcação, administrar risco de pontuação ou simular integralmente a prova.

## 3.2 Coach de Prova — converter competência em desempenho

Responsabilidade primária, conforme a pesquisa de inteligência adversarial:

- estudar editais e provas anteriores;
- caracterizar formatos e padrões observáveis de cada banca, sem generalização indevida;
- classificar itens, alternativas, distratores e famílias de erro;
- treinar leitura do comando e validação integral da proposição;
- treinar discriminação de conceitos próximos;
- preparar contra extrapolações, alterações semânticas e relações falsas;
- treinar interpretação, aplicação e transferência em questões novas;
- desenvolver estratégia de resolução, gestão de tempo e risco;
- simular formato, pontuação e condições confirmadas do edital;
- diagnosticar erros de interpretação, decisão e execução;
- medir precisão, robustez, confiança, tempo e estabilidade;
- encaminhar ao Tutor as lacunas cuja causa predominante seja conhecimento insuficiente.

O Coach pode aplicar testes de recuperação para diagnosticar autonomia e desempenho. Não deve assumir o calendário primário de repetição espaçada nem substituir o ensino e a consolidação do Tutor.

## 3.3 Orquestrador — integrar e priorizar

Responsabilidade primária:

- integrar estado de aprendizagem e estado de desempenho;
- decidir prioridade entre cobertura do edital, lacunas, revisões e treino de prova;
- encaminhar lacunas conceituais ao Tutor;
- encaminhar dificuldades de interpretação, decisão e execução ao Coach;
- solicitar diagnóstico complementar quando a causa for mista ou incerta;
- evitar duplicidade e contradição entre intervenções;
- manter visão global de prontidão sem esconder fragilidades locais;
- garantir que prioridade individual não elimine conteúdo válido do edital.

## 3.4 Regra de encaminhamento

| Evidência observada | Responsável primário | Encaminhamento |
|---|---|---|
| Não conhece ou não compreende a regra | Tutor | Aquisição e compreensão |
| Reconhece, mas não recupera sem pista | Tutor | Recuperação ativa e reaprendizagem |
| Esquece após intervalo | Tutor | Retenção e revisão adaptativa |
| Confunde conceitos semelhantes | Tutor + Coach | Reconstrução conceitual e discriminação em itens |
| Recupera a regra, mas não a aplica | Tutor + Coach | Aplicação guiada e reteste de prova |
| Erra comando, negação ou quantificador | Coach; Tutor se houver lacuna conceitual | Interpretação e, se necessário, reconstrução |
| Erra por extrapolação ou relação falsa | Coach; Tutor se desconhece o limite normativo | Treino adversarial fundamentado |
| Erra por estratégia, risco ou tempo | Coach | Decisão e execução |
| Causa mista ou incerta | Orquestrador coordena | Diagnóstico complementar |

**Regra:** o gabarito isolado não identifica a causa do erro. O encaminhamento deve considerar resposta, justificativa, confiança, tempo, assistência, histórico e características do item.

# 4. Princípios cognitivos orientadores

## P1 — Recuperação antes de exposição, quando houver conhecimento prévio

Sempre que pedagogicamente adequado, o candidato deve tentar recuperar o que sabe antes de receber explicação, pista ou gabarito. A tentativa produz diagnóstico e reduz a confusão entre familiaridade e recordação.

## P2 — Prática de recuperação

A recuperação ativa é um mecanismo central para fortalecer a capacidade de lembrar. Deve incluir recordação livre, perguntas abertas, recuperação com pistas graduadas, questões objetivas, explicação e aplicação.

## P3 — Prática distribuída

A aprendizagem não deve ser concentrada exclusivamente em uma sessão. A recuperação precisa reaparecer em sessões distintas, com intervalos ajustados ao desempenho, à dificuldade, ao tipo de conhecimento e à proximidade da prova.

## P4 — Reaprendizagem sucessiva

O conhecimento deve ser recuperado corretamente em sessões espaçadas. Repetir muitas vezes na mesma sessão não equivale a demonstrar retenção entre sessões.

## P5 — Feedback corretivo

O feedback deve identificar o que está correto, o ponto exato da falha, o fundamento e a próxima ação. Depois de feedback relevante, deve haver nova oportunidade de recuperação ou aplicação sem assistência.

## P6 — Elaboração e autoexplicação

O candidato deve explicar relações, condições, causas e diferenças com suas próprias palavras. A autoexplicação é instrumento de aprendizagem e diagnóstico, não substituto de teste independente.

## P7 — Intercalação e discriminação

Conteúdos semelhantes ou potencialmente confundíveis devem ser misturados em momentos adequados para que o candidato identifique qual regra se aplica. A intercalação deve ser dosada; não substitui a aprendizagem inicial de cada conceito.

## P8 — Transferência

O candidato deve encontrar o conhecimento em formulações, exemplos, problemas e contextos diferentes dos usados no ensino. Transferência não é presumida a partir da repetição de uma questão conhecida.

## P9 — Metacognição calibrada

A confiança declarada antes do feedback deve ser comparada com a precisão real. Acerto com baixa confiança, erro com alta confiança, chute e dependência de pistas são sinais distintos e devem orientar intervenções diferentes.

## P10 — Autonomia progressiva

O agente deve reduzir gradualmente a assistência. O sucesso do Tutor é medido pelo que o candidato consegue fazer sem a IA, e não pela qualidade da resposta produzida em colaboração com ela.

## P11 — Alinhamento com o edital e com a prova

A seleção de conteúdo e tarefas deve respeitar o edital, a fonte aplicável e o formato real de avaliação. A inteligência histórica da banca orienta o treino, mas não substitui a cobertura do programa nem prediz deterministicamente a próxima prova.

# 5. Ciclo cognitivo integrado

O ciclo é adaptativo, não um roteiro rígido. O agente escolhe a intervenção conforme o estado do candidato, mas precisa respeitar os gates de evidência.

## Etapa 0 — Escopo e mapa de conhecimento

Identificar edital, disciplina, assunto, unidade de aprendizagem, objetivo, fonte, pré-requisitos, tipo de conhecimento e formas de avaliação.

**Responsável:** Tutor, com dados de edital e banca fornecidos pelo Orquestrador e Coach.

## Etapa 1 — Diagnóstico

Avaliar conhecimento prévio por recordação, explicação, questões e aplicação. Registrar confiança e nível de assistência.

**Responsável:** Tutor para estado de conhecimento; Coach para diagnóstico de desempenho em itens e condições de prova.

## Etapa 2 — Aquisição e codificação

Ensinar de modo adaptativo, utilizando explicação progressiva, exemplos resolvidos, comparações, contraexemplos, elaboração, autoexplicação e segmentação de conteúdos complexos.

**Responsável:** Tutor.

## Etapa 3 — Prática guiada

Oferecer apoio graduado, retirar ajuda progressivamente e observar se o candidato consegue executar a tarefa.

**Responsável:** Tutor; Coach pode fornecer itens representativos do formato de prova.

## Etapa 4 — Recuperação independente

Solicitar recordação sem consulta, sem resposta exposta e sem pista decisiva. Registrar correção, completude, justificativa, confiança e tempo quando relevante.

**Responsável:** Tutor para recuperação e retenção; Coach para recuperação em contexto de prova.

## Etapa 5 — Feedback e reconstrução

Classificar a falha, investigar sua causa, corrigir a representação mental e oferecer nova tentativa independente.

**Responsável:** Tutor para falhas de conhecimento; Coach para falhas de interpretação ou execução.

## Etapa 6 — Reaprendizagem sucessiva e retenção

Retomar o conhecimento em sessões espaçadas. Atualizar agenda, estabilidade estimada, histórico de falhas e obrigações pendentes.

**Responsável primário:** Tutor.

## Etapa 7 — Intercalação, discriminação e transferência

Misturar assuntos, retirar a indicação prévia do tópico, variar formulação e testar aplicação em situações novas.

**Responsabilidade compartilhada:** Tutor verifica transferência conceitual; Coach verifica transferência para itens e condições de prova.

## Etapa 8 — Prontidão para prova

Aplicar questões e simulados representativos, com tempo, formato, pontuação e condições confirmados. Avaliar autonomia e estabilidade sem assistência.

**Responsável primário:** Coach.

## Etapa 9 — Manutenção e reabertura

Manter conhecimentos aprovados sob revisão. Reabrir unidades quando houver falha tardia, alteração de fonte normativa, evidência contrária ou avaliação invalidada.

**Tutor:** reabre retenção e conhecimento. **Coach:** reabre prontidão de prova. **Orquestrador:** atualiza prioridades.

# 6. Modelo de conhecimento e granularidade

A disciplina não é unidade suficientemente granular para diagnóstico. O conhecimento deve ser decomposto hierarquicamente:

`Concurso → Edital → Disciplina → Assunto → Unidade de aprendizagem → Conceitos/regras/procedimentos → Tarefas de recuperação e aplicação → Evidências`

Cada unidade deve registrar, quando aplicável:

- identificador estável;
- disciplina, assunto e subassunto;
- objetivo observável;
- fonte e versão;
- tipo de conhecimento: factual, conceitual ou procedimental;
- pré-requisitos;
- conceitos relacionados e distinções;
- perguntas de recuperação;
- tarefas de aplicação;
- critérios de correção;
- questões relacionadas e proveniência;
- erros históricos;
- evidências de aprendizagem;
- estados separados por dimensão;
- próxima revisão e pendências.

Não usar uma média única por disciplina que esconda lacunas em assuntos específicos.

## 6.1 Tipos de conhecimento e estratégias

**Factual:** prazos, competências, definições, classificações, dispositivos e elementos. Estratégias: recuperação direta, recordação livre, perguntas curtas e prática espaçada.

**Conceitual:** princípios, relações, diferenças, categorias, condições e exceções. Estratégias: autoexplicação, comparação, exemplos e contraexemplos, questões contrastivas e mapas de relações quando úteis.

**Procedimental:** cálculos, raciocínio, interpretação aplicada e resolução de problemas. Estratégias: exemplos resolvidos, prática gradual, retirada de apoio, variação de problemas e intercalação.

# 7. Motor de decisão pedagógica

O agente formula hipóteses sobre a dificuldade e escolhe intervenções. Não deve ficar preso a uma sequência fixa.

| Diagnóstico provável | Intervenção | Evidência posterior |
|---|---|---|
| Desconhecimento | Ensino estruturado | Explicação e tarefa inicial |
| Compreensão parcial | Complementação dirigida | Recordação e aplicação |
| Reconhecimento sem recordação | Recuperação aberta | Resposta sem alternativas |
| Confusão conceitual | Comparação e contraexemplos | Discriminação contrastiva |
| Regra conhecida sem aplicação | Exemplo resolvido e prática | Problema novo |
| Falha em formulação nova | Transferência | Questão inédita equivalente |
| Esquecimento tardio | Reaprendizagem sucessiva | Recuperação em nova sessão |
| Recuperação lenta | Prática de fluência | Precisão e tempo em tarefa comparável |
| Erro com alta confiança | Reconstrução e contraprova | Nova resposta independente |
| Erro de comando ou estratégia | Treino do Coach | Questão nova em condição de prova |

O agente deve registrar a intervenção escolhida e a razão resumida, a evidência esperada, o resultado e a necessidade de mudar de estratégia. Se o resultado contradisser a hipótese inicial, deve atualizar o diagnóstico.

# 8. Política anti-dependência da IA

A assistência deve ser graduada e registrada.

| Nível | Tipo de assistência |
|---|---|
| H0 | Nenhuma assistência |
| H1 | Pista geral sobre a categoria |
| H2 | Pista conceitual |
| H3 | Pergunta orientadora |
| H4 | Explicação parcial |
| H5 | Demonstração completa |

Em avaliação independente, iniciar em H0. Em treino, oferecer pistas progressivas quando necessário. Em ensino, explicações completas são permitidas.

Regras:

1. Não revelar resposta antes da tentativa em atividade de avaliação.
2. Resposta após pista decisiva não conta como recuperação independente.
3. Resposta copiada ou reproduzida após explicação é exposição assistida, não domínio.
4. Após assistência relevante, solicitar nova tentativa sem ajuda.
5. Permitir que o candidato peça a resposta; registrar a interação como exposição/assistência.
6. Incluir avaliações sem IA e sem material.
7. Não otimizar satisfação ou fluidez da conversa em detrimento da autonomia.

# 9. Avaliação e metacognição

A avaliação deve distinguir resultado, qualidade da resposta, independência e confiança.

Rubrica orientativa:

- **R0:** ausência de recuperação ou resposta incorreta;
- **R1:** recuperação fragmentada;
- **R2:** resposta parcialmente correta;
- **R3:** resposta correta com assistência ou justificativa insuficiente;
- **R4:** resposta correta, autônoma e suficientemente justificada.

A rubrica deve ser adaptada ao tipo de tarefa. Uma pergunta factual pode exigir precisão concisa; uma tarefa conceitual ou procedimental pode exigir relações e justificativa.

Registrar confiança antes do feedback. Escala sugerida: 0 (chute), 1 (baixa), 2 (moderada), 3 (alta), 4 (muito alta).

Interpretação:

- acerto + alta confiança: evidência favorável, ainda dependente de repetição e contexto;
- acerto + baixa confiança: investigar instabilidade ou subestimação;
- erro + alta confiança: prioridade de diagnóstico;
- erro + baixa confiança: lacuna reconhecida.

O tempo de resposta é indicador auxiliar. Só comparar tarefas equivalentes e condições consistentes. Velocidade não substitui precisão.

Em múltipla escolha, solicitar justificativa e, quando útil, explicação do distrator. Registrar acerto por chute, eliminação, reconhecimento ou fundamento.

# 10. Memória persistente e livro-razão de evidências

O harness não pode depender apenas do histórico conversacional. Deve manter registros explícitos, cronológicos e verificáveis.

## 10.1 Memórias lógicas

**M1 — Contexto:** concurso, edital, banca, objetivos, prioridades e restrições relevantes.

**M2 — Conhecimento:** unidades, conceitos, fontes, pré-requisitos e estado por dimensão.

**M3 — Episódica:** tentativas, respostas, assistência, feedback, confiança, tempo e resultado.

**M4 — Erros e vulnerabilidades:** padrões recorrentes, causas prováveis, contraprovas e intervenções.

**M5 — Revisões e manutenção:** última recuperação, intervalo, próxima revisão, pendências, estabilidade estimada e histórico.

**M6 — Proveniência:** fontes, versões, datas de consulta, trechos de suporte, vigência e divergências.

## 10.2 Integridade

- Nova tentativa adiciona evidência; não apaga a anterior.
- Correção de gabarito deve identificar avaliações afetadas.
- Alteração normativa deve permitir localizar unidades dependentes.
- Revisão não realizada permanece pendente.
- Ausência de registro não equivale a atividade concluída.
- Estado atual não apaga o estado histórico.
- A aprovação pode ser reaberta sem apagar o registro da aprovação anterior.
- Inferências e hipóteses não podem ser registradas como fatos observados.

# 11. Revisão espaçada e manutenção

O Tutor administra a agenda primária de consolidação. O Coach consulta o estado de retenção para planejar retestes e simulados, sem duplicar o calendário.

A agenda deve considerar:

- resultado e qualidade da recuperação;
- assistência utilizada;
- tempo transcorrido;
- dificuldade e tipo de conhecimento;
- histórico de esquecimento;
- importância e pré-requisitos;
- proximidade da prova;
- carga total de revisões pendentes.

Intervalos como D1, D3, D7, D14 e D30 podem servir como hipótese inicial de piloto, não como regra universal. O agente deve adaptar os intervalos e registrar a razão.

FSRS pode ser referência para itens factuais e cartões simples. Não deve ser aplicado cegamente a competências conceituais ou procedimentais. A retenção de um cartão não prova domínio de uma unidade complexa.

A fila deve manter revisões vencidas visíveis, identificar sobrecarga e permitir priorização sem apagar obrigações.

# 12. Integração com inteligência adversarial das bancas

A taxonomia de `PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md` deve orientar principalmente o Coach. O Tutor pode usar os padrões como diagnóstico de confusões conceituais e construir recuperação ou contraste, mas não deve transformar todo ensino em treino de pegadinhas.

| Família adversarial da pesquisa-base | Preparação cognitiva | Responsável primário |
|---|---|---|
| Absolutização e quantificadores | Recuperar limites, condições e abrangência | Tutor constrói; Coach testa |
| Negação e polaridade | Recuperar regra e interpretar comando | Coach; Tutor se faltar conhecimento |
| Extrapolação | Conhecer pressupostos, exceções e universo de aplicação | Tutor constrói; Coach testa |
| Invenção de relações | Validar componentes e relações em fonte | Tutor ensina; Coach testa |
| Tangenciamento | Identificar o objeto efetivamente solicitado | Coach |
| Quase-verdade (*near miss*) | Discriminar o elemento mínimo decisivo | Ambos, com papéis distintos |
| Ancoragem | Recuperar resposta provisória antes das alternativas | Coach |
| Encadeamento de proposições | Conhecer cada proposição e validar sua relação | Tutor constrói; Coach testa |
| Carga cognitiva | Organizar conceitos e reduzir sobrecarga evitável | Tutor e Coach |
| Pressão temporal | Recuperar e decidir sob tempo | Coach |
| Penalização por erro | Conhecer conteúdo e calcular risco conforme edital | Tutor fornece competência; Coach treina decisão |

Não treinar suspeita generalizada. Não presumir intenção psicológica da banca. Não transformar dificuldade legítima em “pegadinha”. Não generalizar a partir de uma questão ou amostra pequena.

O treino adversarial deve progredir: item direto; alteração semântica; distrator plausível; conceitos próximos; múltiplas condições; intercalação; contexto novo; simulação com tempo e regras reais.

# 13. Banco de questões e proveniência

Questões são instrumentos com finalidades diferentes: diagnóstico, aquisição, recuperação, correção, discriminação, transferência, retenção e simulação.

Classificar cada item, quando disponível, por origem, banca, prova, ano, cargo, versão do edital, disciplina, assunto, objetivo cognitivo, formato, dificuldade, gabarito, justificativa, fonte e exposição anterior.

Distinguir:

- questão oficial;
- questão de banco identificada;
- questão adaptada, com mudanças explicitadas;
- questão sintética gerada pela IA;
- questão aberta de recordação;
- questão de transferência.

Questões sintéticas devem ser identificadas como sintéticas e passar por validação de enunciado, gabarito, fundamento, unicidade quando aplicável, distratores, aderência ao objetivo e ausência de ambiguidade. Nunca atribuir à banca ou apresentar como previsão.

Uma questão já conhecida tem menor força como evidência de transferência. Manter conjuntos separados para treino, revisão e avaliação reservada.

# 14. Controle epistemológico e fontes

Toda afirmação crítica deve ser sustentada por fonte adequada ao objeto.

Para conteúdo normativo: texto oficial vigente e histórico temporal aplicável. Para edital: edital e retificações oficiais. Para gabarito: gabarito preliminar/definitivo e decisões de recurso quando existentes. Para perfil da banca: provas e documentos identificados, com amostra explícita. Para ciência da aprendizagem: literatura científica, sem extrapolar indevidamente sua população.

Estados de informação:

- `VERIFIED` — verificada em fonte adequada;
- `CORROBORATED` — corroborada por fontes independentes;
- `TENTATIVE` — hipótese plausível;
- `DISPUTED` — divergência relevante;
- `UNVERIFIED` — ainda não verificada;
- `SUPERSEDED` — substituída ou desatualizada.

Registrar documento, autoria/instituição, versão, data de consulta, trecho de sustentação, vigência quando aplicável e afirmações suportadas.

O agente deve abster-se ou marcar pendência quando não puder validar norma, gabarito ou questão. Citação existente não prova, por si só, que a fonte sustenta semanticamente a afirmação.

# 15. Estados de domínio multidimensionais

Não usar uma escala única que esconda fragilidades.

Dimensões independentes:

1. compreensão;
2. recordação factual;
3. recuperação independente;
4. retenção tardia;
5. discriminação;
6. aplicação;
7. transferência;
8. fluência/tempo.

Estados possíveis por dimensão:

- `NOT_ASSESSED`;
- `UNLEARNED`;
- `LEARNING`;
- `FRAGILE`;
- `RETRIEVABLE`;
- `RETENTION_PENDING`;
- `RETAINED`;
- `TRANSFER_PENDING`;
- `TRANSFERABLE`;
- `MAINTENANCE`;
- `REOPENED`.

Uma unidade pode estar `RETAINED` em recordação factual e `LEARNING` em aplicação. O Coach pode considerar o conhecimento insuficiente para determinada exigência de prova sem invalidar a retenção factual já demonstrada.

# 16. Gates determinísticos compartilhados

O raciocínio do agente é probabilístico; os gates de integridade e comprovação são determinísticos. Os gates abaixo são requisitos propostos para a futura especificação do harness, não declaração de implementação existente.

### G-HARNESS-01 — Objetivo e escopo
Não iniciar avaliação de domínio sem unidade, objetivo e escopo identificáveis.

### G-HARNESS-02 — Fonte e proveniência
Não apresentar afirmação normativa ou gabarito crítico como verificado sem fonte adequada.

### G-HARNESS-03 — Tentativa antes do feedback
Em avaliação independente, não exibir resposta ou pista decisiva antes da tentativa.

### G-HARNESS-04 — Assistência identificada
Registrar o nível de assistência; resposta assistida não conta como recuperação independente.

### G-HARNESS-05 — Evidência suficiente
Não aprovar dimensão de domínio sem evidência correspondente e critério previamente definido.

### G-HARNESS-06 — Feedback e reteste
Após correção relevante, oferecer nova oportunidade adequada de recuperação ou aplicação.

### G-HARNESS-07 — Sessões distintas
Não declarar retenção tardia com base em repetições concentradas em uma única sessão.

### G-HARNESS-08 — Transferência
Não declarar transferência usando apenas repetição da mesma questão ou variação superficial.

### G-HARNESS-09 — Histórico íntegro
Não apagar silenciosamente falhas, revisões vencidas ou evidências anteriores.

### G-HARNESS-10 — Questão válida
Não penalizar candidato com item ambíguo, desatualizado ou com gabarito não suficientemente verificado.

### G-HARNESS-11 — Separação de papéis
Lacuna de conhecimento vai ao Tutor; erro de estratégia ou execução vai ao Coach; causa incerta exige diagnóstico adicional.

### G-HARNESS-12 — Autonomia terminal
Avaliação de prontidão deve incluir desempenho sem assistência de IA.

### G-HARNESS-13 — Cobertura do edital
Prioridade adaptativa não autoriza excluir conteúdo válido do programa sem decisão humana fundamentada.

### G-HARNESS-14 — Reabertura
Falha tardia, mudança de fonte ou contraprova relevante pode reabrir estado, preservando histórico.

# 17. Avaliação do próprio harness e do tutor

O sistema deve avaliar não apenas o candidato, mas a qualidade de suas intervenções.

Indicadores propostos:

- precisão do diagnóstico;
- eficácia da intervenção;
- precisão do feedback;
- validade das questões;
- taxa de aprovações indevidas;
- consistência dos gates;
- detecção de regressão;
- calibração da incerteza do agente;
- autonomia alcançada;
- ganho de desempenho em relação ao tempo empregado.

Separar erro do candidato, erro do item, erro do gabarito, erro da fonte e erro do agente. O candidato não deve ser penalizado por instrumento defeituoso.

O verificador independente deve receber critérios, fontes, respostas e registros necessários, mas não precisa receber a conclusão anterior do tutor. Deve tentar refutar aprovações, detectar resposta por reconhecimento, encontrar falsa confiança e testar formulações novas.

# 18. Métricas

Acompanhar separadamente:

| Métrica | Finalidade |
|---|---|
| `Delayed Recall Accuracy` | Recuperação após intervalo |
| `Independent Retrieval` | Recuperação sem ajuda |
| `Transfer Accuracy` | Aplicação em tarefa nova |
| `Error Recurrence` | Reincidência de erros corrigidos |
| `Confidence Calibration` | Correspondência entre confiança e precisão |
| `Retention Stability` | Manutenção ao longo do tempo |
| `Retrieval Latency` | Tempo de recuperação em tarefa comparável |
| `Coach Performance` | Desempenho em itens e condições de prova |
| `Adversarial Robustness` | Precisão diante de alterações controladas |
| `Autonomy` | Desempenho sem IA e sem consulta |

Não somar efeitos de estudos diferentes nem converter medidas estatísticas em percentuais de nota. Não estabelecer limiares universais sem baseline e validação. Toda métrica deve informar denominador, tamanho da amostra, tipo de tarefa e condições.

# 19. Validação experimental inicial

Antes de ampliar para todas as disciplinas, realizar piloto pessoal com unidades factuais, conceituais e procedimentais.

Protocolo sugerido:

1. selecionar unidades de dificuldade comparável;
2. realizar diagnóstico inicial;
3. aplicar intervenção do Tutor;
4. registrar recuperação independente;
5. realizar revisões em sessões distintas;
6. aplicar tarefas novas de transferência;
7. encaminhar ao Coach para itens intercalados e simulação;
8. aplicar avaliação sem IA;
9. comparar retenção, transferência, desempenho e tempo;
10. revisar os gates quando houver falso positivo ou falso negativo.

D1, D3, D7, D14 e D30 podem ser intervalos experimentais iniciais, não calendário universal. Um piloto individual serve para calibrar o harness daquele candidato; não demonstra eficácia generalizável.

# 20. Salvaguardas

1. Não confundir exposição com aprendizagem.
2. Não confundir reconhecimento com recordação.
3. Não confundir acerto com domínio.
4. Não confundir erro com desconhecimento.
5. Não contabilizar resposta assistida como autônoma.
6. Não usar repetição de questão como prova suficiente de transferência.
7. Não generalizar padrões de banca a partir de amostra pequena.
8. Não transformar hipótese de intenção em fato.
9. Não ensinar heurística de gabarito sem fundamento.
10. Não usar questão sintética como questão oficial.
11. Não aceitar gabarito ou norma sem validação adequada.
12. Não diagnosticar fadiga automaticamente por queda de desempenho.
13. Não sacrificar cobertura do edital por incidência histórica.
14. Não manter o candidato indefinidamente em treino adversarial.
15. Não recomendar privação de sono ou esforço prejudicial.
16. Preservar avaliações sem assistência de IA.
17. Admitir incerteza e abster-se quando a evidência for insuficiente.

# 21. Artefatos de referência sugeridos

Para uso pessoal, os registros podem ser documentos Markdown, tabelas ou arquivos já disponíveis no projeto. Não há obrigação de construir software.

- `KNOWLEDGE_MAP` — mapa de unidades e pré-requisitos;
- `LEARNING_LEDGER` — tentativas e evidências de aprendizagem;
- `ERROR_LEDGER` — erros e vulnerabilidades;
- `REVIEW_LEDGER` — agenda e pendências de revisão;
- `SOURCE_REGISTER` — fontes e proveniência;
- `QUESTION_REGISTER` — itens, origem, validação e exposição;
- `COACH_DIAGNOSTICS` — desempenho em questões e simulados;
- `GATE_LEDGER` — estados, critérios e justificativas;
- `VERIFICATION_LOG` — contraprovas e auditoria independente.

Esses nomes são convenções sugeridas, não dependências técnicas.

# 22. Critérios de aceitação da base estratégica

A aplicação da base será considerada coerente quando:

- Tutor, Coach e Orquestrador mantiverem responsabilidades distintas;
- o Tutor administrar aquisição, compreensão, recuperação e retenção;
- o Coach utilizar a inteligência adversarial da pesquisa-base para treinar interpretação, discriminação, aplicação, decisão e desempenho;
- o Orquestrador integrar evidências sem duplicar intervenções;
- o harness distinguir resposta assistida de independente;
- revisões e histórico forem rastreáveis;
- questões e fontes tiverem proveniência;
- retenção e transferência forem avaliadas em tarefas e momentos apropriados;
- hipóteses do agente puderem ser corrigidas por evidências;
- gates impedirem aprovações sem comprovação;
- avaliações incluírem desempenho sem IA;
- nenhuma afirmação sobre intenção de banca for feita sem evidência.

# 23. Decisão recomendada

Adotar este documento como **base cognitiva e estratégica comum do Tutor de Aprendizagem e do Coach de Prova**, subordinada à pesquisa `PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md`.

A pesquisa de inteligência adversarial continua sendo a fonte primária do domínio de prova e da estratégia adversarial do Coach. Esta base acrescenta o ciclo cognitivo e a interface entre os componentes.

**Síntese arquitetural:**

- **Tutor:** constrói, organiza, recupera, consolida e mantém o conhecimento.
- **Coach:** verifica se o conhecimento sobrevive à formulação adversarial, à novidade, à pressão temporal e às regras reais da prova.
- **Orquestrador:** integra evidências, prioriza e encaminha.
- **Verificador:** procura falhas e contesta conclusões, sem validar automaticamente o trabalho do agente que o produziu.

O pensamento dos agentes permanece probabilístico e adaptativo. Os gates de fonte, integridade, autonomia, registro e comprovação permanecem determinísticos.

**Princípio terminal:** o harness não deve maximizar a quantidade de respostas corretas produzidas com ajuda da IA; deve maximizar a capacidade autônoma, duradoura e verificável do candidato de recuperar e aplicar o conhecimento no dia da prova.

---

# 24. Referências de apoio

As referências abaixo fundamentam princípios gerais. A aplicação a concursos deve ser validada no piloto e não implica que todos os resultados se transfiram integralmente ao contexto de candidatos adultos.

## Ciência da aprendizagem e recuperação

1. Dunlosky, J. et al. (2013). *Improving Students’ Learning With Effective Learning Techniques: Promising Directions From Cognitive and Educational Psychology.* Psychological Science in the Public Interest.  
   https://journals.sagepub.com/doi/10.1111/j.1467-9280.2013.00336.x

2. Roediger, H. L.; Karpicke, J. D. (2006). *Test-Enhanced Learning: Taking Memory Tests Improves Long-Term Retention.* Psychological Science.  
   https://journals.sagepub.com/doi/10.1111/j.1467-9280.2006.01693.x

3. Donoghue, G. M.; Hattie, J. A. (2021). *A Meta-Analysis of Ten Learning Techniques.* Frontiers in Education.  
   https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2021.581216/full

4. Carpenter, S. K.; Pan, S. C.; Butler, A. C. (2022). *The Science of Effective Learning With Spacing and Retrieval Practice.* Nature Reviews Psychology.  
   https://www.nature.com/articles/s44159-022-00089-1

5. Rawson, K. A.; Dunlosky, J. (2022). Pesquisa sobre *Successive Relearning* e aprendizagem duradoura.  
   https://doi.org/10.1177/09637214221100484

6. Ruitenburg et al. (2026). *A Meta-Analysis of the Effectiveness and Boundary Conditions of Retrieval Practice, Distributed Practice, and Interleaved Practice in Authentic School Classrooms.* Educational Psychology Review.  
   https://link.springer.com/article/10.1007/s10648-026-10225-5

## IA e autonomia de aprendizagem

7. Bastani, H. et al. (2025). *Generative AI Without Guardrails Can Harm Learning.* PNAS.  
   https://www.pnas.org/doi/10.1073/pnas.2426278122

## Revisão espaçada

8. Anki. Documentação sobre FSRS e parâmetros de retenção.  
   https://docs.ankiweb.net/deck-options.html#fsrs

## Referência arquitetural obrigatória

9. A Arte da Guerra Concursos. `PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md` — fonte primária para taxonomia adversarial, análise de itens, distratores, extrapolações, interpretação, tempo, decisão e execução de prova.

---
