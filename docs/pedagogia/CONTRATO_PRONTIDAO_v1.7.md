# Contrato integrado de prontidão pedagógica — UFMS v1.7

**Natureza:** especificação consolidada e decisão de encaminhamento, **não** implementação ou homologação de tutor autônomo.  
**Fonte:** propostas pedagógicas v1.0–v1.6 desta pasta e diagnóstico de compatibilidade realizado em 04/11/2026.  
**Cargos:** UFMS 523 (Gestão Pública) e 324 (Assuntos Estudantis).  
**Limites:** não alterar o PR #1, não criar dados do estudante, não habilitar gravação de resultados, não fazer merge.

## 1. Contrato de hierarquia e rastreabilidade

A implementação deverá distinguir fontes e escopos:

1. **Edital e retificações oficiais verificadas:** regras de prova, conteúdo, exigências, pontuação e alcance temporal.
2. **Contrato do harness efetivamente aprovado:** AGENTS.md, settings.json, regras, guardrails e validadores no HEAD aplicável.
3. **Especificação pedagógica proposta:** v1.0–v1.7, como requisitos e hipóteses de intervenção; não modifica automaticamente o harness.
4. **Dados e relatórios legitimamente obtidos:** observações, com proveniência e granularidade preservadas.
5. **Inferências da IA:** hipóteses diagnósticas e recomendações condicionais, nunca fatos presumidos.

Quando houver conflito entre as camadas, não escolher silenciosamente uma redação. Registrar dependência, validar com a fonte competente e bloquear apenas as decisões afetadas, quando possível. A [matriz de reconciliação](MATRIZ_RECONCILIACAO_v1.7.md) organiza as pendências identificadas.

**Escopo desta revisão:** a avaliação de compatibilidade técnica foi feita sobre o HEAD do PR #1 observado durante a entrega: 18a81bacd6163e6d510e58c00f2a55e77051b3ca. Esse SHA é um ponto de observação, **não** uma base congelada para implementação; reconfirmar antes de trabalhar nele.

## 2. Objetivo único do tutor

Em cada oportunidade de estudo, escolher uma **intervenção pedagógica principal e viável**, considerando:
- validade e abrangência do edital;
- resultados, confiança, independência, novidade e qualidade de evidência E0–E4;
- necessidade de cobertura, correção, recuperação, transferência ou simulado;
- risco eliminatório e valor das áreas em cada prova, sem converter pesos em horas;
- correspondência documental entre conteúdos 523/324, sem dupla contagem;
- tempo e condições informados pelo estudante;
- custo de oportunidade e valor diagnóstico.

A escolha deve declarar evidências, incertezas, principais alternativas e o gatilho de reavaliação. Nenhum cronograma universal, percentual mágico de domínio ou probabilidade de aprovação é autorizado.

## 3. Fronteiras entre objetos, identidades e estados

**Identidades lógicas distintas:**
- *decision_id*: escolha do tutor e seus critérios;
- *recommendation_id*: prescrição interna do caderno;
- *platform_notebook_id*: ID real de TEC/Qconcursos, quando confirmado;
- *attempt_id*: uma tentativa relatada ou comprovada;
- *event_id*: evento persistido único, se a gravação for autorizada;
- *topic_id*: identificador de tópico oficial mapeado;
- *source_commit*: commit em que o estado foi lido ou persistido; não confundir com o estado de plataformas externas.

O harness atual utiliza o campo *caderno_id* nos eventos, o que **não demonstra suporte separado** a todas as identidades acima. A implementação técnica deve definir um mapeamento explícito, sem quebra de eventos antigos. Um mesmo caderno pode ter várias tentativas apenas quando a política validar sua identidade, origem e semântica; não somar tentativas repetidas como se fossem independentes.

**Estados lógicos de recomendação/caderno:** recomendado, criação confirmada, em andamento, concluído relatado, validado, indisponível, cancelado, substituído ou pendente de esclarecimento. O motor atual pode representar somente parte disso. Estados propostos não equivalem a transições já implementadas.

**Estados lógicos de evidência E0–E4** representam precisão informacional, não uma escala de domínio. Falta de dados produz *desconhecido*, não nota zero.

## 4. Contrato mínimo da decisão (pré-intervenção)

Registrar, antes do caderno:
- versão do edital e estado de verificação de retificações;
- identidade do snapshot, HEAD e instante de avaliação *as_of* explícito;
- lista de alternativas elegíveis e restrições/bloqueios;
- tópico(s), cargo(s), área e interseção documental comprovada;
- sinais de aprendizagem observados e evidência que falta;
- modalidade e propósito da intervenção;
- filtros propostos e ordem de flexibilização (sem presumir suporte TEC/Qconcursos);
- quantidade sugerida, não obrigatória;
- sinal observável esperado e condição para reavaliar;
- justificativa breve, sem fingir certeza;
- quando houver sorteio permitido: política, pesos, semente e escolha, para reprodução.

Decisões sem mudanças de entradas, política e *as_of* devem ser estáveis. Não usar o relógio implicitamente para mover prioridades de forma inexplicável.

## 5. Contrato mínimo de devolução (pós-intervenção)

Receber ao menos uma identificação inequívoca do caderno pendente e o resultado efetivamente disponível. Quando houver contagens exatas: registrar total, corretas, incorretas, não respondidas e convenção usada pela plataforma.

Dados opcionais: data real da resolução, ajuda, comentários, questões inéditas/repetidas, tempo, tentativas, resultado por assunto, dúvidas e confiança. Ausência preservada como desconhecido. A data e hora de **registro do evento** podem ser diferentes da data da **tentativa**; não inventar a segunda a partir da primeira.

O usuário pode devolver um relatório simples. O processo de ingestão deve mapear cabeçalhos, definições e convenções antes de produzir o evento esperado pelo validador. Se o resultado não puder ser normalizado com segurança, manter pendência e dar feedback pedagógico limitado — não relaxar o validador para produzir coerência artificial.

Não imputar acertos de caderno agregado a subtópicos, nem computar pontuação ponderada de simulado quando faltarem resultados por área.

## 6. Pipeline único: separação de responsabilidades

| Etapa | Regra ou responsabilidade | Prova de aceite esperada |
|---|---|---|
| START | Recuperar versão do repositório e fontes obrigatórias | Conferência de SHA e arquivos reais |
| Escopo | Identificar assunto no edital e alterações verificadas | Página/trecho e versão |
| Estado | Reconstruir eventos e evidências, validar unicidade | Projeção reproduzível, sem duplicação |
| Fila | Gerar opções válidas e marcar pendências/bloqueios | Candidatos reprodutíveis no mesmo snapshot |
| Decisão | Comparar necessidades e escolher intervenção | Justificativa, alternativas e sinais esperados |
| Prescrição | Sugerir caderno com filtros e fallback | Contrato sem caderno externo inventado |
| Execução humana | Confirmar criação e resultado quando informado | Evidência da plataforma/estudante |
| Ingestão | Normalizar observação para schema técnico | Validações sem fabricação de campos |
| Análise | Classificar qualidade e limites de evidência | E0–E4 sem confundir com domínio |
| Persistência | Registrar somente se autorizado e confirmado | Commit SHA ou estado explicitamente pendente |
| Reavaliação | Reconstruir fila após novo evento verificado | Decisão adaptada e historicamente explicável |
| Eficácia | Comparar sinal esperado e observado quando comparável | Favorável/desfavorável/inconclusivo/incomparável |

Este pipeline é um **contrato arquitetural**, não descrição de software executável hoje.

## 7. Invariantes que devem tornar-se testes determinísticos

- Sem duplicação de eventos, tentativas corrigidas ou benefício cruzado 523/324.
- Sem resultado inventado a partir de percentual arredondado ou dados agregados.
- Sem atribuição de desempenho a subtópico cuja contagem não foi informada.
- Sem score ponderado de simulado com áreas faltantes.
- Sem IDs/links de cadernos não confirmados.
- Sem afirmação de retenção por acerto imediato em item repetido.
- Sem escolha de candidato bloqueado; filtro fora do edital requer rejeição ou validação.
- Sem mutação remota quando falta autorização; sem sucesso declarado antes do readback.
- Sem diferença de decisão sob mesmo snapshot, política, semente e *as_of*, exceto mudanças explicitamente justificadas na parte probabilística.
- Sem usar qualidade de evidência E0–E4 como probabilidade de domínio.

A interpretação pedagógica entre candidatos válidos pode permanecer qualitativa e adaptativa, desde que o resultado seja coerente com essas restrições.

## 8. Gates de prontidão separados

| Gate | Exigência para ser satisfeito | Situação desta entrega |
|---|---|---|
| GP-0 — Fonte | Escopo, regras de prova e retificações confrontados com fonte primária vigente | **Pendente de retificações e verificações aplicáveis** |
| GP-1 — Contratos | Reconciliação de campos, IDs, estados, datas, erros e permissões | **Pendente de implementação técnica e revisão** |
| GP-2 — Motor | Fila, seleção, evidências e decisões integradas a componentes executáveis | **Não implementado** |
| GP-3 — Testes | Cenários pedagógicos transformados em casos reproduzíveis; negativos e adversariais passando | **Não demonstrado** |
| GP-4 — Ciclo completo | Recomendação → caderno real → devolução → validação → persistência → nova decisão | **Não demonstrado** |
| GP-5 — Piloto consentido | Uso com dados reais autorizados e avaliação de eficácia sem inferência causal indevida | **Não iniciado** |

Os gates são independentes. Documentação revisada não constitui homologação de software; CI verde de integridade não demonstra utilidade pedagógica.

**Ordem sugerida de construção:** GP-0 e GP-1 antes de habilitar dados reais; GP-2 + GP-3 com fixtures fictícias; GP-4 em ambiente controlado; GP-5 somente depois de proteção de dados, autorização e validação. Mudanças de governança, permissões e merge exigem decisão humana apropriada.

## 9. Mapa dos testes documentados

Antes desta versão há **86 cenários de aceitação documentados**, ainda não executados como testes do tutor: PED-01–20; COMP-01–12; SIM-01–10; EFA-01–08; FIQ-01–18; CDO-01–18.

A v1.7 acrescenta **PRD-01–16** para reconciliação, controle de versões, contratos, gates e autorização; total: **102 cenários documentados**. Esses números representam cobertura de especificação, não taxa de aprovação de testes.

Cada cenário deverá futuramente apontar entrada, estado/configuração, saída permitida, saída proibida, evidência de execução e gate. Testes por fixtures são diferentes de piloto real. Não inventar métricas de desempenho pedagógico.

## 10. Definição de entrega pronta e próximo passo

**Especificação pronta para implementação:** os documentos já definem o comportamento esperado de ponta a ponta, e pendências de integração estão explícitas na matriz. A v1.7 não resolve automaticamente pendências técnicas do PR #1.

**Próxima frente recomendada:** fornecer à sessão técnica um pacote de implementação por gates e contratos, com priorização dos riscos GP-0/GP-1, preservando separação entre PRs. Esta sessão pode continuar revisando estratégia e aceitação, mas a execução dos scripts, hooks, importadores e piloto deve ocorrer na frente técnica autorizada.

**Sem merge. Sem resultados pessoais inventados. Sem declarar tutor operacional.**
