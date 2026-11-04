# Matriz de reconciliação entre pedagogia v1.0–v1.6 e harness — v1.7

**Objeto:** inconsistências, diferenças de camada e decisões pendentes identificadas na leitura dos documentos pedagógicos do PR #2 e dos arquivos técnicos do PR #1.  
**Amostra técnica efetivamente consultada:** SHA 18a81bacd6163e6d510e58c00f2a55e77051b3ca do PR #1 em 04/11/2026. **Reconsultar antes de executar correções.**  
**Estado:** parecer documental de integração; não altera código, fonte do edital, configuração de permissões ou políticas do PR #1.

Legenda: **D** = divergência documental; **I** = contrato de integração não implementado; **B** = bloqueio de segurança/prontidão; **V** = verificação externa pendente.

| ID | Tipo | Evidência observada | Disposição proposta | Gate |
|---|---|---|---|---|
| REC-01 | D | docs/OPERACAO.md e rules/CORE.md mencionam *sete* arquivos; settings.json e AGENTS.md listam *nove* obrigatórios. | Adotar a lista efetiva de settings.json como referência de bootstrap do harness atual; sincronizar menções antigas e testar consistência de arquivos após revisão técnica. | GP-1 |
| REC-02 | I | scripts/bootstrap.py valida presença de arquivos e devolve resumo, mas não prova que um agente leu semanticamente todos eles; hooks exigem registro. | Distinguir verificação de presença, readback e leitura efetiva; adicionar gate verificável onde possível e não alegar execução automática só pela existência do script. | GP-1 |
| REC-03 | I | v1.6 distingue recommendation_id, platform_notebook_id, attempt_id e event_id; scripts/core.py exige caderno_id, event_id, type e timestamp. | Especificar mapeamento e ciclo de vida compatível; eventos legados não devem mudar de significado silenciosamente. | GP-1 |
| REC-04 | I | v1.6 admite tentativas com data real desconhecida; validador atual exige timestamp ISO com fuso para cada evento. | Manter timestamp de **registro** comprovável no evento técnico; data da tentativa só se fornecida. Nunca fabricar attempt_at. | GP-1 |
| REC-05 | I | Protocolo admite convenções distintas de apresentadas/respondidas; validate_events exige corretas + erros + em branco = total. | Ingestão deve normalizar contagens conhecidas **antes** do evento validado; se não for possível, manter pendência sem transformar porcentagens arredondadas em contagens exatas. | GP-1 |
| REC-06 | I | v1.2 propõe E0–E4; state/CURRENT.json e PROGRESS.csv no harness consolidam eventos e precisão, não demonstram cálculo desses níveis. | Criar projeção derivada explícita com proveniência e lacunas; não tratar E0–E4 como domínio. | GP-2 |
| REC-07 | I | v1.5 propõe fila, status, as_of, comparador multicritério; scripts/core.py faz validação/reconstrução, não possui ranqueador pedagógico. | Implementar componente separado e testável com snapshot explícito, idempotência e justificativa de mudança. | GP-2/3 |
| REC-08 | I | v1.6 prevê criado, pendente, indisponível, cancelado e substituído; VALID_TYPES no core só contém caderno_recomendado, resultado_recebido/corrigido, revisão e decisão. | Definir máquina de estados e migração/novos eventos por aprovação técnica; não simular confirmação de criação por evento de recomendação. | GP-1/2 |
| REC-09 | B | settings.json mantém personal_results_writes_enabled = false; repositório privado é condição declarada, mas não autoriza escrita por si só. | Preservar bloqueio até confirmar visibilidade, consentimento, privacidade, minimização de dados, testes e autorização específica. | GP-1/4/5 |
| REC-10 | V | config/concursos.json declara retificacoes_verificadas = false; a pedagogia usa pesos e regras de corte como dados a conferir. | Confirmar edição normativa e retificações relevantes antes de usar cortes eliminatórios, equivalência de simulado ou afirmar regras atuais. | GP-0 |
| REC-11 | I | v1.3 identifica possíveis sobreposições de específicos; config/topics.csv contém rótulos/aliases, não prova identidade integral. | Comparar subitens literais do edital e manter duas trilhas de desempenho até equivalência confirmada. | GP-0/2 |
| REC-12 | V | v1.6 descreve opções de filtros e exportação como condicionais; não se confirmou formato de CSV nem estoque de itens em TEC/Qconcursos. | Validar amostra legítima de relatórios e capacidades disponíveis; sem acesso automatizado nem URLs de caderno inventadas. | GP-1/4 |
| REC-13 | I | O arquivo de aceitação contém 86 cenários textuais; a CI técnica atual testa os controles existentes, não o motor adaptativo proposto. | Converter cenários relevantes em fixtures positivas/negativas, com resultados verificáveis; não declarar testes pedagógicos aprovados antes de executá-los. | GP-3 |
| REC-14 | I | v1.4 requer sinal esperado *antes* da intervenção e avaliação posterior; hoje o estado técnico não assegura ambos os vínculos. | Definir evento/registro de decisão auditável, com comparação de evidências e classificação inconclusiva quando necessário. | GP-2/3 |
| REC-15 | D | O PR #2 foi criado a partir de main antes de integrar o harness do PR #1; as duas branches evoluem de forma independente. | Planejar integração revisada após base estável; não rebasear, mesclar ou alterar PR #1 automaticamente. Reexecutar gates sobre HEAD integrado quando autorizado. | GP-1/3 |
| REC-16 | I | A IA pode selecionar intervenções probabilísticas no contrato, mas não há módulo de sorteio/reprodução identificado no core observado. | Usar seleção qualitativa justificada até haver implementação e testes com política/pesos/seed versionados; não fingir probabilidade calibrada. | GP-2/3 |

## Decisões de reconciliação do escopo pedagógico

- **Sem mudança retroativa nas versões anteriores:** a v1.7 estabelece o contrato unificado e registra os pontos de integração. As especificações v1.0–v1.6 permanecem históricas e rastreáveis. Nenhuma divergência foi corrigida no código do PR #1 por esta entrega.
- **Compatibilidade primeiro:** não permitir que a conveniência da estrutura JSONL atual elimine requisitos pedagógicos importantes; tampouco relaxar validador seguro para aceitar entrada malformada.
- **Informação ausente:** usar estado desconhecido ou pendente, sempre distinguindo dados **não observados** de dados **observados com resultado zero**.
- **Fronteira de autoria:** a sessão pedagógica especifica e audita comportamento. A sessão técnica implementa, testa e propõe alterações de governança mediante autorização adequada.
- **Prioridade de validação:** REC-09 e REC-10 são bloqueadores de prontidão; REC-03/04/05/08 são contratos de ingestão; REC-06/07/14/16 definem motor; REC-01/02/15 protegem continuidade e integração.

## Próximas verificações

1. Reconsultar HEAD e hashes do PR #1; esta matriz só é válida como fotografia técnica do SHA citado.
2. Verificar o edital primário e possíveis retificações antes de afirmar regras de prova em produção.
3. Obter amostra legítima de arquivo TEC/Qconcursos, somente se o estudante a oferecer.
4. Especificar schemas de migração e testar entradas desconhecidas, correções e duplicações no harness técnico.
5. Construir motor sob testes de cenário e avaliar decisões humanas/operacionais, sem alegar eficácia causal.

**Conclusão:** a especificação pedagógica pode ser entregue à engenharia como contrato, mas os gates de prontidão GP-0 a GP-5 **não foram aprovados** nesta revisão documental.
