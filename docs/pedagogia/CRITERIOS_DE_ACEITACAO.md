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
