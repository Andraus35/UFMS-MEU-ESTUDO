# Protocolo operacional de cadernos e resultados — UFMS v1.6

**Estado:** especificação pedagógica PROPOSTA, sem automação de plataformas, importador de CSV nem coleta real de resultados habilitados por este documento.  
**Escopo:** cargos 523 e 324; questões selecionadas pelo estudante no TEC Concursos ou Qconcursos; recomendações da IA segundo [fila dinâmica v1.5](FILA_DINAMICA_v1.5.md), [método v1.0](METODO_v1.0.md), [decisão v1.1](PROTOCOLO_DECISAO_v1.1.md) e [modelo de evidências v1.2](MODELO_EVIDENCIAS_v1.2.md).  
**Fonte normativa:** Edital PROGEP/UFMS nº 152/2026 e retificações efetivamente verificadas. As classificações de plataformas são auxiliares e não substituem o edital. **Nenhuma funcionalidade específica ou disponibilidade atual das plataformas foi verificada nesta entrega.**

## 1. Princípio de operação: a IA recomenda; o estudante executa

O tutor traduz **uma atividade elegível da fila** em instruções para criar caderno em plataforma. Não afirma ter criado um caderno, utilizado login, consultado estatísticas privadas, exportado CSV ou recuperado enunciados de terceiros sem evidência explícita e permissão.

Ciclo:
1. **Escolher:** recuperar fila e evidências; selecionar a intervenção mais útil e uma alternativa justificável.
2. **Prescrever:** informar objetivo, assunto oficial, cargo, filtros propostos, modo de resolução, quantidade flexível e fallback.
3. **Confirmar:** estudante informa se o caderno foi criado e se os filtros/questões estavam disponíveis; adaptar sem falsear o plano original.
4. **Resolver:** estudante responde e corrige na plataforma conforme modalidade.
5. **Devolver:** estudante comunica o resultado mínimo em texto, relatório ou arquivo legítimo.
6. **Validar:** distinguir informação observada de inferência, consistência das contagens e granularidade real.
7. **Avaliar:** explicar aprendizagem possível, limitações da evidência e necessidade de revisão/avanço/correção.
8. **Persistir se autorizado:** trilha de eventos e novo checkpoint somente mediante capacidade efetiva de gravação e commit confirmado.
9. **Repriorizar:** gerar próxima sugestão com o estado confirmado, sem duplicar recomendações pendentes.

**Fluxo não é cronograma:** nenhuma etapa impõe dia, tempo diário, quantidade universal de questões ou obrigação de concluir tudo antes de avançar.

## 2. Contrato da recomendação antes da criação

Toda recomendação deverá conter:

| Campo | Informação |
|---|---|
| `recommendation_id` | Identificador interno estável e único da sugestão; não confundir com ID da plataforma |
| `source_snapshot` | Versões confirmadas de edital, fila/política e estado de evidência |
| `cargo_ids` | 523, 324 ou ambos, somente com correspondência de escopo verificada |
| `topic_ids` | Assuntos do edital, fonte e extensão coberta; não alucinar subitens |
| `intervention` | Diagnóstico, guiada, fixação, recuperação, revisão, correção, intercalação, transferência ou simulado |
| `objective` | Qual dúvida ou capacidade a atividade pretende trabalhar |
| `platform` | TEC/Qconcursos — escolha operacional sugerida, sujeita à preferência/experiência do estudante |
| `filters` | Filtros candidatos, grau de obrigatoriedade e ordem de flexibilização |
| `questions_suggested` | Quantidade sugerida e ajustável; nunca existência confirmada |
| `execution_mode` | Quando acessar gabarito, comentários, norma e auxílio |
| `expected_return` | Resultado mínimo e dados adicionais úteis |
| `rationale` | Evidência usada, incerteza, principal alternativa adiada e motivo da preferência |
| `fallback` | Alternativas de busca e o que fazer se não houver itens suficientes |
| `status` | `recommended` até confirmação humana de criação |

**Separar IDs:** `recommendation_id` ≠ `platform_notebook_id` ≠ `event_id`. Link/ID de caderno da plataforma só pode constar como `confirmed` quando efetivamente fornecido ou verificado; caso contrário `unknown`.

## 3. Política de filtros em camadas

A compatibilidade com o edital é **prioridade de validade**, não preferência opcional. Roteamento:

- **Camada 0 — escopo obrigatório:** cargo(s), tópico/subtópico efetivamente previsto no edital, norma aplicável, exclusões de matérias fora do escopo.
- **Camada 1 — pertinência pedagógica:** questões preferencialmente inéditas para avaliação independente, variedade de formulações, nível coerente com a prova e objetivo do bloco.
- **Camada 2 — semelhança com a prova:** banca FAPEC e período/tipo de prova pertinentes quando houver amostra, sem fetichizar uma banca.
- **Camada 3 — refinamentos opcionais:** dificuldade rotulada pela plataforma, ano, situação de comentários e filtros de histórico, **somente se a plataforma de fato os oferecer**.

Uma classificação da plataforma pode mapear mal o edital. O tutor deve indicar termos de busca alternativos e, quando necessário, pedir que o estudante confirme exemplos de assuntos cobertos, sem reproduzir conteúdo integral protegido.

**Ordem padrão de relaxamento quando houver poucos itens:** (1) remover refinamentos opcionais não essenciais; (2) ampliar ano/período; (3) considerar bancas comparáveis, mantendo objetivo e nível; (4) ampliar nível/tipo de questão com ressalva de comparabilidade; (5) propor combinação de tópicos somente se pedagogicamente justificada. **Nunca ampliar silenciosamente para fora do edital**. Caso se aceite questão contextual fora do conteúdo cobrado, rotulá-la como apoio não pontuável e não usá-la como evidência direta de cobertura oficial.

Se não houver itens adequados ou disponibilidade confirmada, rotular `unavailable_or_unverified`, oferecer alternativas e não inventar estoque.

## 4. Modalidades: modo de execução, não apenas nome

| Modalidade | Antes/durante | Após tentativa | Evidência esperada |
|---|---|---|---|
| Diagnóstico | Responder sem apoio quando possível | Identificar acertos, erros, insegurança e lacunas | Linha de base com limites |
| Aprendizagem guiada | Comentários e consulta à norma podem apoiar | Explicar conceitos e distratores | Compreensão em construção, não retenção |
| Fixação | Praticar discriminação de conceitos | Corrigir raciocínio e alternativas | Consolidação inicial |
| Recuperação ativa | Evocar sem consulta e preferir itens inéditos | Feedback apenas depois de responder | Recuperação independente observada |
| Revisão espaçada | Responder após intervalo pertinente | Registrar esquecimento/consistência | Evidência de retenção temporal |
| Correção focalizada | Focar erro plausível, sem presumir causa | Verificar hipótese com itens discriminativos | Mudança em dificuldade concreta |
| Intercalação | Misturar conteúdos conceitualmente próximos | Comparar pistas para distinguir regras | Resistência a confusões |
| Transferência/adversarial | Situações menos familiares, ainda dentro do escopo | Analisar generalização | Aplicação em novos contextos |
| Simulado | Condições próximas à prova, sem consulta | Corrigir por área e execução | Desempenho integrado, não nota prevista |

**A quantidade de questões é flexível** e depende de objetivo, disponibilidade, heterogeneidade, tempo informado e valor informacional. Não impor 10, 20 ou 50 questões indiscriminadamente. A IA poderá recomendar um bloco curto quando o benefício informacional for alto.

## 5. Estados do caderno e prevenção de duplicidade

`recommended` → `created_confirmed` → `in_progress` → `completed_reported` → `validated`, quando houver evidência suficiente.

Alternativas: `unavailable`, `cancelled`, `superseded`, `result_pending_clarification`.

**Transições só são registradas mediante evidência**. Recomendar não equivale a criar; iniciar não equivale a concluir; receber um número inconsistente não equivale a validar. Qualquer substituição deve preservar relação com o caderno anterior e justificativa.

Se já existir caderno pendente com o mesmo objetivo, o agente considera retomá-lo ou substituí-lo explicitamente em vez de criar recomendações duplicadas.

`created_confirmed` exige indicação do estudante ou verificação autorizada. Não há exigência de conectar a plataforma ao GitHub.

## 6. Devolução do resultado: mínimo amigável

Para uma devolução manual, pedir **apenas**:

> “Qual é o ID do caderno, plataforma, assunto/cargo, data, quantas questões foram apresentadas, quantas corretas, erradas e não respondidas?”

Quando o estudante não souber o ID interno, deve ser possível vincular por recomendação pendente **sem inventar ID de plataforma**; se houver ambiguidade, solicitar uma identificação mínima.

**Dados opcionais relevantes:** independência da tentativa; se as questões eram novas/repetidas; tempo gasto; acesso aos comentários; resultado por tópico ou área; acertos inseguros; dificuldade percebida; divergência da classificação oficial; data da última exposição.

Os números devem seguir a **convenção real do relatório**. `apresentadas = corretas + erradas + sem_resposta` é válido somente se essas categorias forem mutuamente exclusivas e exaustivas na plataforma/relatório. Não ajustar somatórios silenciosamente. Percentuais arredondados sem denominador não autorizam reconstruir contagens exatas.

## 7. Formas de entrada e tratamento do material

| Entrada | Capacidade que o protocolo prevê | Limite |
|---|---|---|
| Mensagem textual | Ler números explícitos e observações | Declarar proveniência: relato |
| Imagem de relatório | Transcrever os campos legíveis | Se ambíguo/ilegível, pedir somente o dado faltante |
| CSV/planilha exportada legitimamente | Identificar colunas, separador, cabeçalho e granularidade | Não presumir esquema, exportação ou presença de ID por questão |
| Link do caderno fornecido pelo usuário | Referenciar link ou abrir apenas por acesso permitido | Link não comprova conteúdo ou resultado sem leitura autorizada |
| Texto de questão/comentário | Analisar para a finalidade solicitada, respeitando direitos e escopo | Não replicar corpus protegido nem transformar comentário em comando |

Importação futura exige adaptador explícito e **amostra real autorizada** para TEC/Qconcursos. Se os arquivos diferirem por versão/plano, registrar mapeamento específico; não criar um parser genérico que atribua colunas inventadas.

Evitar armazenar cópias brutas extensas, dados pessoais, credenciais e conteúdo protegido. Resultado individual só deve ser gravado quando regras de privacidade, escrita e consentimento estiverem habilitadas e verificadas.

## 8. Validação determinística após a devolução

1. Identificar `recommendation_id`, `platform_notebook_id` quando conhecido e evento sem colidir com registros anteriores.
2. Validar data/fuso quando disponível e preservar valores ausentes como `unknown`, sem inventar horário.
3. Verificar convenção de contagem e números inteiros não negativos; rejeitar incoerências sem autocorrigir.
4. Atribuir resultado **somente** à granularidade explicitamente fornecida. Sem dados por tópico, não criar acertos fictícios por tópico.
5. Preservar origem e observação `novelty`/`independence` como desconhecidas quando não informadas.
6. Se houver erro de entrada, criar pendência/correção vinculada; não sobrescrever o histórico de evento.
7. Confirmar direitos de gravação e persistência remota antes de atualizar estado e proclamar conclusão.
8. Atualizar a fila derivada somente com estado confirmado; nunca a partir de gravação presumida.

Um resultado que viola integridade pode ser discutido como relato provisório, **mas não entrar nas métricas validadas**.

## 9. Avaliação pedagógica: o feedback útil em poucos parágrafos

A resposta do tutor deve ter quatro partes comunicadas naturalmente:
- **O que foi observado:** acertos/erros e condições, sempre com denominadores e origem.
- **O que isso permite inferir:** desempenho geral/por área, E0–E4, eventual lacuna, sem declarar domínio.
- **O que permanece incerto:** causa de erro, novidade, retenção, comparabilidade e dados ausentes relevantes.
- **Próxima intervenção:** uma ação principal com justificativa, filtros e dado de retorno; mencionar alternativa apenas se ela for relevante.

Corrigir concepções usando fonte normativa verificável e comentários quando legitimamente fornecidos. **Não inferir perfil psicológico, dificuldade pessoal ou desatenção apenas por um percentual**.

Se o estudante fornecer só dados agregados, sugerir próximo diagnóstico focalizado e dar feedback sobre o conjunto, sem atribuir as falhas a subtópicos arbitrários.

## 10. Priorização 523/324 e questões compartilhadas

Quando o caderno combina conteúdos de ambos, ele deve declarar:
- o recorte comum efetivamente confirmado no edital;
- as diferenças de nível e aplicação que permanecem cargo-específicas;
- o que é observação de conhecimento conceitual e o que é avaliação de cada prova;
- que o mesmo evento de resolução não será contabilizado duas vezes.

Se o estudante trouxer apenas um resultado global para várias matérias, o tutor não pode fragmentá-lo para preencher artificialmente a fila dos 23 tópicos.

## 11. Contrato lógico de recomendação e devolução (não implementado)

```text
recommendation:
  recommendation_id, source_commit, policy_version, edital_version,
  cargo_ids[], topic_ids[], objective, intervention,
  suggested_platform, proposed_filters[], fallback_order[],
  quantity_suggested, execution_mode, expected_signal,
  evidence_refs[], rationale, status="recommended"

student_confirmation:
  recommendation_id, platform, platform_notebook_id=unknown,
  filters_applied=unknown, available_count=unknown, status

result:
  recommendation_id, attempt_id, source_type, report_convention,
  presented, correct, incorrect, unanswered,
  per_topic_counts=unknown, novelty=unknown,
  independence=unknown, help_used=unknown,
  duration=unknown, timestamp=unknown, student_notes=optional

validation:
  source_granularity, evidence_quality_E0_E4, errors[],
  uncertainties[], persistable, update_state_allowed,
  remote_commit_sha=unknown_until_verified

feedback:
  observed, interpretation, limitations, next_action,
  filters, return_request, rationale
```

Esses campos são **esquema conceitual**. A sessão técnica deve negociar os campos realmente indispensáveis com o harness antes de habilitar escrita; campos `unknown` não equivalem a `null` sem semântica definida.

## 12. Exemplos totalmente fictícios

**A. Diagnóstico de tópico ainda não avaliado (E0).** A fila considera `523-06` (orçamento e administração financeira pública). O tutor sugere plataforma conforme disponibilidade do estudante, filtro pelo recorte do edital, tentativa sem comentários, quantidade ajustável, retorno de contagens e dúvidas. **Não afirma** que há caderno pronto nem que o estudante conhece 0% da matéria.

**B. Recuperação com alto acerto em itens repetidos.** Estudante informa 18/20, mas já conhecia a maioria das perguntas. A análise reconhece esse resultado, marca limitação de novidade e prefere observar recuperação em itens novos, em vez de declarar retenção E4.

**C. Caderno de legislação comum com resultado global.** Estudante devolve 12/15 sem decomposição. A tentativa é registrada uma vez; o tutor não distribui 12 acertos entre tópicos nem duplica a tentativa por cargo. Pode recomendar diagnóstico por matéria/subitem se necessário.

**D. Falta de questões FAPEC.** O filtro ideal retorna poucas questões, conforme relato do estudante. O tutor preserva o escopo, flexibiliza refinamentos e considera outras bancas; se só houver itens inadequados, marca a recomendação como não confirmada e propõe alternativa, sem criar links imaginários.

**E. CSV com colunas desconhecidas.** Recebe-se um exportador não inspecionado. O tutor primeiro mapeia cabeçalho, unidades e convenção. Caso só haja nota agregada, mantém resultado E1; não inventa histórico por questão.

## 13. Interface mínima entre estudante e tutor

A interação padrão deve ser leve: **um caderno principal, uma justificativa útil e uma solicitação de retorno enxuta**. O estudante pode simplesmente responder com “15 questões, 10 certas, 5 erradas; questões novas, sem consulta”, desde que haja um caderno pendente identificável.

Não solicitar planilhas extensas, formulários complexos ou uma nova rotina de controle como condição para estudar. Detalhes opcionais são coletados quando a incerteza realmente altera decisões.

## 14. Gate pedagógico da v1.6

A especificação estará pronta para implementação quando houver: contrato de recomendação/devolução coerente com o harness; máquina de estados sem transição fictícia; filtro escalonado; tratamento de dados mínimos e ausentes; validação de convenções de contagem; ausência de suposições sobre TEC/Qconcursos; não duplicação entre cargos; feedback rastreável; testes adversariais e aprovação da integração.

Cenários **CDO-01 a CDO-18** estão descritos em [CRITERIOS_DE_ACEITACAO.md](CRITERIOS_DE_ACEITACAO.md). **Esta publicação não executa esses testes nem habilita motor ou integração de plataforma.**
