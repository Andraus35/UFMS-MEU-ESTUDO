# Protocolo de decisão pedagógica — v1.1

**Estado:** PROPOSTA PEDAGÓGICA. Não há motor implementado por este arquivo.

## Problema que o tutor deve resolver

A cada decisão, identificar (1) qual assunto ou necessidade merece atenção, (2) qual intervenção deve vir a seguir, (3) como equilibrar os cargos 523/324 e (4) o que observar no resultado para adaptar a estratégia.

### Unidade de decisão

O menor assunto com evidência confiável e referência ao edital: ID, disciplina, cargos aplicáveis, relações de sobreposição, histórico, cobertura, resultados, qualidade da evidência, grau de incerteza e alternativas de intervenção. Se só existir resultado agregado, a unidade continua agregada: **não repartir acertos hipotéticos entre subtópicos**.

## Camada determinística (invariantes)

Antes de recomendar:

1. Conferir estado persistido, versão do edital e referências aplicáveis.
2. Verificar se o assunto consta do escopo e se os cargos atribuídos são corretos.
3. Conferir consistência aritmética e proveniência dos resultados; não duplicar eventos.
4. Distinguir itens inéditos/repetidos e com/sem ajuda quando a informação estiver disponível; senão registrar desconhecido.
5. Verificar requisitos eliminatórios da versão válida do edital, sem inferir chance de aprovação.
6. Não confundir acerto recente com retenção; não declarar domínio em função de limiar universal.
7. Não repetir resultado compartilhado entre cargos como duas observações independentes.
8. Impedir afirmações sem evidência e decisões incompatíveis com dados contraditórios.
9. Preservar histórico de eventos e justificativa; confirmar gravação antes de alegá-la.
10. Se faltar informação decisiva, preferir diagnóstico, sinalizar pendência ou pedir complemento mínimo.

A camada determinística garante coerência, **não escolhe sozinha uma sequência rígida**.

## Camada adaptativa (comparação de alternativas)

Considerar conjuntamente:

| Dimensão | Efeito possível |
|---|---|
| Cobertura | Favorecer exploração de área ainda pouco trabalhada |
| Lacuna observada | Favorecer intervenção corretiva ou aprendizagem |
| Retenção | Favorecer recuperação após intervalo pertinente |
| Peso da matéria | Influenciar oportunidade estratégica por prova |
| Risco eliminatório | Evitar deixar áreas sem diagnóstico ou com dificuldade persistente |
| Sobreposição real | Considerar ganhos para ambos os cargos |
| Prazo até a prova | Ajustar exploração, consolidação, recuperação e simulação |
| Disponibilidade/diversidade | Evitar cadernos inviáveis ou saturados de itens repetidos |
| Esforço e condições relatadas | Ajustar carga e modalidade |
| Valor informacional | Preferir diagnóstico quando a incerteza impede boa decisão |

Nenhuma variável isolada deve dominar permanentemente. Prioridade não é sinônimo de probabilidade de dominar a matéria; não gerar probabilidades numéricas de aprovação ou esquecimento sem calibração adequada.

## Dois cargos, duas leituras da evidência

- **Conceitual:** quando o conteúdo é realmente compartilhado, uma atividade pode informar aprendizagem útil aos dois cargos.
- **Por prova:** preservar diferenças de recorte, nível, peso, desempenho e questões usadas; não transportar automaticamente conclusões entre específicos.
- Registrar cada tentativa uma vez e associar múltiplos objetivos a ela sem somar duas vezes questões, acertos ou horas.

## Risco eliminatório

Conferir nota mínima global e proibição de nota zero nas áreas, conforme versão vigente do edital. Área sem evidência pede diagnóstico quando estrategicamente necessário; dificuldade recorrente pode merecer correção mesmo com baixo peso. Reavaliar após novos dados: a proteção eliminatória não deve prender o estudante indefinidamente na mesma área.

## Decisão entre modalidades

- Evidência insuficiente → considerar diagnóstico.
- Conceito desconhecido ou mal compreendido → aprendizagem guiada.
- Conhecimento recente e instável → fixação.
- Bom desempenho imediato, retenção não observada → recuperação posterior.
- Confusão entre regras próximas → intercalação.
- Acerto em itens familiares → transferência para itens novos.
- Esquecimento observado → recuperação ou correção adaptada.
- Cobertura e desempenho integrados precisam ser observados → simulação.
- Conhecimento estável, baixa cobertura em outras áreas → explorar conteúdo novo.

Essas relações são hipóteses orientadoras; o agente compara alternativas e registra a motivação. Uma intervenção pode combinar modalidades quando justificado.

## Aleatoriedade controlada e reprodutível

A seleção probabilística é **opcional** e destinada à exploração entre alternativas já validadas como adequadas. Antes de qualquer sorteio: filtrar restrições, calcular critérios transparentes, excluir opções inadequadas. Quando uma alternativa for claramente superior, preferi-la diretamente. Se houver empate aproximado, permitir pesos configurados e uma semente registrada para reproduzir a escolha. Não ignorar risco grave por sorteio. Probabilidade de escolher um caderno **não equivale** a probabilidade de aprendizagem.

## Volume de questões e critérios de avanço

Quantidade depende do objetivo, heterogeneidade, dificuldade, evidência, diversidade disponível e tempo/energia informado pelo estudante. Não impor número fixo.

Avanço não exige 70%, 80% ou 90% universais: ocorre quando outra intervenção tende a oferecer mais benefício. Acerto alto em questão repetida pode justificar transferência; dificuldade persistente pode justificar reconstrução conceitual; domínio aparente em uma área não cancela recuperação futura.

## Exploração versus consolidação

O tutor não deve nem explorar superficialmente todo o edital nem perpetuar repetição de assuntos confortáveis. Comparar valor de novos tópicos e valor de recuperar/aprofundar os antigos; ajustar a distribuição sem planograma impositivo.

## Registro de decisão

Persistir apenas resumo auditável: versão do estado, assunto, evidências utilizadas, incerteza, riscos, alternativas plausíveis, intervenção escolhida, filtros/quantidade sugerida, justificativa e dados esperados para próxima decisão. Não registrar raciocínio interno extensivo nem afirmar persistência sem SHA.

## Verificação mínima

Testar mudança de preferência entre alternativas quando muda a evidência, proteção de área eliminatória, uso da sobreposição sem duplicação, distinção entre itens repetidos/inéditos, seleção probabilística reproduzível, zero evidência, dados agregados e ausência de questões FAPEC. Ver [critérios de aceitação](CRITERIOS_DE_ACEITACAO.md).
