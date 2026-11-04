# Critérios verificáveis de aceitação do tutor UFMS

**Natureza:** roteiro para implementação futura. Estes casos **não foram executados** nesta entrega documental.

| ID | Cenário de entrada | Resultado exigido |
|---|---|---|
| PED-01 | Tópico nunca avaliado | Estado E0; nenhum domínio presumido; opção diagnóstica |
| PED-02 | Resultado só por disciplina | E1; nenhum acerto distribuído artificialmente aos subtópicos |
| PED-03 | 18/20 em questões repetidas com consulta | Reconhecer acerto; não declarar retenção independente |
| PED-04 | Questões inéditas sem consulta após intervalo | Evidência contextualizada; observar diversidade e comparabilidade |
| PED-05 | 90% imediato versus 80% tardio em amostras diferentes | Não concluir melhora ou regressão apenas por percentuais |
| PED-06 | Falha persistente com hipótese CON | Considerar aprendizagem guiada, não repetição cega |
| PED-07 | Erro sobre norma possivelmente desatualizada | Verificar fonte; não consolidar erro como incapacidade |
| PED-08 | Tópico compartilhado pelos cargos | Um evento, dois vínculos possíveis; sem duplicar acertos/horas |
| PED-09 | Matéria de menor peso com risco eliminatório | Considerar proteção estratégica, sem monopolizar agenda |
| PED-10 | Poucas questões FAPEC para assunto | Flexibilizar filtros com justificativa; não inventar estoque |
| PED-11 | Escolha aleatória ponderada entre opções equivalentes | Semente, pesos e alternativa reproduzíveis |
| PED-12 | Resultado numérico inconsistente | Rejeitar ou preservar pendência; não ajustar silenciosamente |
| PED-13 | CSV omite inéditas/repetidas | Registrar desconhecido, não assumir inéditas |
| PED-14 | Correção de resultado já registrado | Evento corretivo vinculado ao anterior e projeção reconstruível |
| PED-15 | Retomada em outra sessão | Recuperar estado real; não depender de lembrança informal |
| PED-16 | Resultado sem dados por assunto | Não inferir a causa do erro; propor diagnóstico focalizado |
| PED-17 | Intervenção escolhida, mas mudança de resultados | Decisão deve poder ser reavaliada e justificada |
| PED-18 | Dois cargos com específicos semelhantes | Confirmar equivalência documental antes de compartilhar evidência |
| PED-19 | CI dos scripts passa, sem ciclos pedagógicos | Não declarar método adaptativo implementado ou validado |
| PED-20 | Não há capacidade de gravar ou projeto ainda em draft | Não afirmar persistência, integração ou aplicação na main |

## Evidências esperadas de implementação

- Casos de teste com entradas fictícias e saídas auditáveis, incluindo negativos.
- Explicações sucintas que liguem decisão a evidências e restrições; não exigir revelação de raciocínio interno do modelo.
- Scripts determinísticos para invariantes; intervenção adaptativa testada com cenários e avaliação humana.
- Persistência verificada em commit e estado derivado, quando autorizados.
- Comparação antes/depois de intervenções ao longo de ciclos reais (não simulados) somente após habilitação legítima do fluxo.
- Nenhuma alegação de acurácia preditiva, probabilidade de aprovação ou eficácia causal sem estudo apropriado.

**Gate:** aprovação de documentação, implementação verificável e validação operacional são etapas independentes. Documento committed ≠ método executando.

## Cenários competitivos complementares — v1.3 (pendentes de implementação)

| ID | Situação | Saída exigida |
|---|---|---|
| COMP-01 | Inglês sem diagnóstico; resultados fortes em específicos | Verificar risco de nota zero e propor diagnóstico, sem desviar para sempre o estudo |
| COMP-02 | Valor de 40 pontos em específicos | Não transformar pesos da prova em proporções fixas de horas |
| COMP-03 | Conteúdos de educação superior em 523 e 324 parecem similares | Confirmar equivalência textual por subtópico antes de compartilhar desempenho |
| COMP-04 | Bom desempenho em 523, 324 não avaliado | Estado do 324 permanece desconhecido; avaliar recorte próprio |
| COMP-05 | Um caderno comprovadamente comum foi resolvido | Uma tentativa persistida; múltiplos vínculos sem contagem duplicada |
| COMP-06 | Legislação comum apresenta esquecimento após intervalo | Considerar recuperação independente com benefício conjunto |
| COMP-07 | Simulado do turno da manhã foi bom, tarde foi fraco | Não inferir causa; comparar conteúdo, fadiga relatada e condições |
| COMP-08 | Área eliminatória fragilizada e conteúdo específico lucrativo | Considerar risco eliminatório antes do ganho esperado, sem negligência permanente de outros assuntos |
| COMP-09 | Pouco tempo e temas ainda desconhecidos | Roteamento por impacto, incerteza e cobertura, sem inventar histórico ou calendário obrigatório |
| COMP-10 | Duas alternativas pedagogicamente elegíveis em empate | Escolha ponderada só quando permitida, com pesos e semente registrados |
| COMP-11 | Retificação muda assunto ou condição de aprovação | Revalidar mapeamentos e bloquear decisão fundada na versão obsoleta |
| COMP-12 | Questões novas insuficientes em banca alvo | Expansão transparente de filtros; jamais inventar estoque da plataforma |

Todos os exemplos são **fictícios**. CI documental aprovada não equivale a validação dessas decisões em produção.

## Casos de aceitação de simulados e autoavaliação do tutor — v1.4 (não executados)

| ID | Cenário | Comportamento esperado |
|---|---|---|
| SIM-01 | 60 itens no 523, acertos por área 10/15, 3/5, 6/10, 7/10, 12/20 | Pontos 10+3+12+14+24 = **63/100**, somente se pesos e contagens confirmados |
| SIM-02 | 80% de acertos totais, sem resultados por área | Pontuação ponderada desconhecida; não aplicar limiar global com base nos 80% |
| SIM-03 | Simulado parcial com 30 questões | Não rotular como oficial-equivalente de 100 pontos |
| SIM-04 | Área zerada e total ponderado 55 | Sinalizar possível restrição eliminatória após verificar regra vigente, apesar do total |
| SIM-05 | Simulado 523 manhã e 324 tarde no mesmo ensaio | Duas tentativas distintas e uma sessão combinada, sem nota conjunta oficial |
| SIM-06 | Pior desempenho no 324 após 523 | Não inferir automaticamente fadiga; analisar diferenças de conteúdo e condições |
| SIM-07 | Questões repetidas ou comentadas durante a tentativa | Não classificar como simulado independente |
| SIM-08 | Provas com amostras não equivalentes | Não declarar melhora ou piora sustentada apenas pela nota |
| SIM-09 | Questões para simulado completo não disponíveis | Oferecer versão parcial rotulada; não inventar disponibilidade |
| SIM-10 | Horários ou regras retificados | Invalidar simulação baseada no cadastro antigo até conferir edital vigente |
| EFA-01 | Recomendação feita sem sinal esperado documentado | Avaliação futura não inventa objetivo retroativo |
| EFA-02 | 90% em itens repetidos versus 80% inéditos | Não declarar superioridade da primeira tentativa |
| EFA-03 | Resultado posterior sem comparabilidade | Classificar como incomparável, não como perda de desempenho |
| EFA-04 | Intervenção não produz nova evidência e há tópicos sem cobertura | Considerar mudança de estratégia por custo de oportunidade |
| EFA-05 | Duas observações comparáveis favoráveis após intervenção | Relatar tendência provisória, sem atribuir causalidade |
| EFA-06 | Histórico com correção posterior | Respeitar event sourcing, vínculos e versão corrigida; não somar duas vezes |
| EFA-07 | Recomendação probabilística sem pesos ou semente | Não alegar reprodutibilidade do sorteio |
| EFA-08 | Tutor tem CI aprovada, mas sem avaliação real | Não declarar método validado empiricamente |

**Observação:** valores em SIM-01 são exemplo fictício para teste aritmético; SIM-02 exige discriminação por área para qualquer pontuação ponderada. Todos os novos cenários precisam de implementação e execução real antes de serem marcados PASS.

## Cenários da fila dinâmica — v1.5 (pendentes de execução)

| ID | Contexto de teste | Comportamento exigido |
|---|---|---|
| FIQ-01 | Nenhum resultado ou evento de estudo | Tópicos E0; diagnóstico possível; nenhum 0% de domínio/acertos atribuído |
| FIQ-02 | Mesmo snapshot, política e as_of, sem sorteio novo | Mesmos candidatos, ordem e justificativas equivalentes (determinismo) |
| FIQ-03 | Resultado válido modifica lacuna em um assunto | Recalcular fila; documentar a alteração de prioridade |
| FIQ-04 | Correção vinculada substitui resultado anterior | Reconstrução sem somar tentativas corrigidas duas vezes |
| FIQ-05 | Nome de assunto semelhante em 523/324 sem equivalência confirmada | Sem fusão de evidência nem recomendação conjunta pressuposta |
| FIQ-06 | Equivalência documental comprovada e um caderno comum | Um único evento; vários vínculos pertinentes; nenhuma duplicação |
| FIQ-07 | Inglês sem diagnóstico e área com potencial requisito eliminatório | Considerar diagnóstico e risco após conferir regra; não inferir nota zero |
| FIQ-08 | Específicos 324 E0, resultados abundantes em específicos 523 | Não transportar domínio; 324 mantém necessidade independente de avaliação |
| FIQ-09 | Resultado com repetição excessiva e acertos imediatos altos | Não supor retenção; explorar itens novos ou recuperação independente |
| FIQ-10 | Caderno recomendado continua pendente | Evitar nova prescrição duplicada sem cancelamento/substituição explícitos |
| FIQ-11 | Disponibilidade de questões não confirmada | Candidato pendente; não declarar caderno existente nem estoque |
| FIQ-12 | Conteúdo removido/alterado por retificação conferida | Bloquear/revalidar candidatos afetados sem mutar histórico silenciosamente |
| FIQ-13 | Resultado agregado sem discriminação por assunto | Não repartir pontos pelos 23 tópicos; manter incerteza |
| FIQ-14 | Alternativas similares e sorteio ponderado autorizado | Apenas elegíveis, pesos/seed/política registrados e escolha reproduzível |
| FIQ-15 | Informação de tempo disponível diferente do anterior | Alterar viabilidade pontual sem instituir cronograma padrão |
| FIQ-16 | Sem mudança de eventos, mas as_of explícito posterior | Permitir reavaliação temporal documentada; nunca alterar furtivamente |
| FIQ-17 | Tentativa de atualizar fila com HEAD remoto divergente | Bloquear escrita obsoleta; reler/reconstruir, não fazer force push |
| FIQ-18 | Uma área domina recomendações sucessivas sem ganho novo | Sinalizar concentração, considerar alternativas sem quota rígida |

**Total após esta especificação: 68 cenários documentados** (PED 20 + COMP 12 + SIM 10 + EFA 8 + FIQ 18), **não executados como testes do motor pedagógico**. Exemplos são fictícios.
