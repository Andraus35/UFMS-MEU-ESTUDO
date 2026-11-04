# Modelo de evidências de aprendizagem — v1.2

**Estado:** PROPOSTA PEDAGÓGICA. Objetivo: distinguir pontuação observada de conhecimento, retenção e transferência, com mínimo esforço do estudante.

## Princípio de evidência mínima suficiente

Aceitar relatórios simples (texto, CSV, imagem legível ou anotação manual) e manter campos não disponíveis como **desconhecidos**. Informações mais ricas melhoram o diagnóstico, mas não são requisito para continuar a preparação. Não estimar contagens a partir de porcentagens arredondadas sem confirmação.

## Registro mínimo e contexto opcional

| Grupo | Informações | Regra |
|---|---|---|
| Identificação | ID do caderno, plataforma, cargo(s), área/assunto, data da tentativa e origem | Vínculo verificável, sem inventar IDs |
| Resultado | Total apresentado, acertos, erros, não respondidas, convenção de contagem | Validar total de acordo com a plataforma |
| Contexto | Tempo, ajuda/consulta, inéditas/repetidas, confiança, dificuldade, comentários, decomposição por tópico | Opcional; ausentes ficam desconhecidos |
| Proveniência | Informado pelo estudante, extraído de arquivo, confirmação oficial quando aplicável | Diferenciar relato e verificação |

O TEC e o Qconcursos podem definir “respondidas”, “apresentadas” ou “resolvidas” diferentemente. Registrar a convenção sem impor soma que não corresponda ao relatório. Nenhum scraping nem API privada presumida.

## Dimensões da força da evidência

| Dimensão | Valores descritivos |
|---|---|
| Independência | Sem consulta / com consulta / misto / desconhecido |
| Familiaridade | Inéditas / repetidas / mistas / desconhecido |
| Temporalidade | Imediata / intervalo conhecido / intervalo desconhecido |
| Granularidade | Questão / tópico / disciplina / agregado |
| Diversidade | Variada / homogênea / desconhecida |
| Proveniência | Arquivo / relato manual / origem incerta |
| Confiança | Segura / insegura / desconhecida |

A qualidade da evidência não se confunde com percentual de acertos.

## Níveis E0–E4 — informacional, não de domínio

- **E0:** sem avaliação — conhecimento não avaliado.
- **E1:** resultado apenas agregado — desempenho geral observado.
- **E2:** discriminação por assunto — desempenho localizado.
- **E3:** condições de independência, novidade e contexto identificáveis — diagnóstico contextualizado.
- **E4:** recuperações independentes em momentos diferentes e itens variados — evidência mais informativa sobre retenção e generalização.

Os níveis não são uma pontuação do estudante e não devem ser convertidos automaticamente em percentuais de domínio. Mesmo E4 não prova domínio absoluto; E1 não indica baixa capacidade.

## Quatro incertezas fundamentais

1. **Desempenho:** números incompletos, definições divergentes ou inconsistências.
2. **Causa:** erro conhecido, mas explicação não identificada.
3. **Retenção:** ausência de recuperação independente posterior.
4. **Transferência/escopo:** pouca diversidade ou impossibilidade de atribuir resultado a subtópicos.

Quando a incerteza for decisiva, preferir intervenção informativa. Não apresentar probabilidade numérica de esquecimento/domínio sem validação e calibração.

## Hipóteses de dificuldade

| Código | Hipótese |
|---|---|
| CON | Lacuna conceitual |
| INT | Interpretação do enunciado |
| DIS | Confusão entre conceitos ou alternativas |
| PRO | Dificuldade de procedimento |
| RET | Esquecimento/recuperação |
| TEM | Tempo de resolução |
| INS | Acerto inseguro |
| NOR | Norma ou questão possivelmente desatualizada |
| IND | Causa indeterminada |

**Hipótese não é diagnóstico definitivo.** Atribuir código apenas com justificativa e grau de incerteza; revisar à luz de novas evidências.

## Comparabilidade de tentativas

Antes de declarar progresso ou regressão, verificar conteúdo equivalente, condições de consulta, familiaridade, intervalo, quantidade e variedade, dificuldade e proveniência. Se as tentativas não forem comparáveis, registrar variação observada **sem afirmar melhoria sustentada**. Uma tentativa de 90% em questões repetidas imediatamente após estudar não comprova retenção superior à tentativa de 80% em itens inéditos após intervalo; diferenças de dificuldade e amostra também importam.

## Retenção e revisão

Observar recuperação independente após intervalos, consistência e diversidade. Uma avaliação imediata mede outra coisa. Recomendar revisões adaptativas, sem calendário universal. Falha posterior pode justificar nova recuperação ou correção segundo a causa provável.

## Evidência compartilhada entre cargos

Registrar um evento por tentativa; associar aos objetivos compatíveis dos dois cargos sem duplicar acertos, horas ou contagens. Preservar nível de dificuldade e recorte do conteúdo; não extrapolar para específicos diferentes.

## Integridade, correção e privacidade

- Identificador único por evento, origem, data/fuso, caderno, matéria e correção explícita quando aplicável.
- Dados contraditórios não viram resultado válido até resolução ou registro de pendência.
- Correção preserva o original, vinculando o novo evento ao anterior.
- Resultados agregados não criam métricas por subtópico inexistentes.
- Projeções devem ser reconstruíveis; gravação no GitHub só é confirmada por retorno verificável.
- Repositório privado é condição necessária, mas não suficiente: consentimento, mínimos dados e permissões precisam ser avaliados. Não guardar credenciais nem enunciados protegidos.

## Retorno para decisão do agente

Cada evidência útil informa: assunto e cargos afetados, métricas verificadas, contexto, qualidade (E0–E4), incertezas, hipóteses de dificuldade e limite de inferência; o próximo caderno é decidido pelo protocolo v1.1. Se o dado for insuficiente, pedir complemento pequeno ou selecionar diagnóstico.

## Critérios mínimos

Aceitar caderno simples; detectar inconsistências; preservar desconhecidos; não equiparar guiado a independente; distinguir novidade quando informada; não inventar subtópicos; não afirmar retenção sem recuperação posterior; comparar com cautela; não duplicar eventos entre cargos; produzir decisão rastreável.
