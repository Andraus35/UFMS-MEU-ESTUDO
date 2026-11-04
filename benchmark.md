# Benchmark técnico-científico — gates para cognição probabilística do harness UFMS

**Pesquisa:** 04/11/2026 | **Status:** benchmark de referência; não é conformidade certificada | **Objeto:** `Andraus35/UFMS-MEU-ESTUDO` | **Abrangência:** tutor, coach e controles de ferramentas.

## Veredito

A combinação mais defensável é **gates determinísticos de contrato e de efeitos externos + avaliações repetidas e graduadas da qualidade semântica + revisão independente**. Nenhum conjunto finito de testes ou prompt garante que toda saída futura de um LLM esteja correta. O resultado exigível é: *não executar uma ação crítica não autorizada, não persistir um resultado inconsistente, não alegar fato crítico sem evidência admissível e não declarar prontidão sem provas verificadas*.

## 1. Benchmark comparativo e transferência para UFMS

| Fonte | Prática consolidada | Adaptação recomendada | Limitação da transferência |
| --- | --- | --- | --- |
| **Tech Leads Club — Spec Lean v2.2.0 (31/10/2026)** | `PLAN -> CHECKS -> BUILD -> VERIFY`; plano humano; EARS; cada check tem prova específica; Verifier não autor | `.specs/features/ufms-cognitive-gates/plan.md` e, só após aceite humano, `checks.md`, `proofs.md` e `verification.md`; números e SHA rastreados | Validadores oficiais não foram executados neste levantamento; implantação da skill via npx indisponível no ambiente |
| **Anthropic — Demystifying Evals for AI Agents (2026)** | Evals end-to-end com graders de código, modelo e humanos; trials repetidos; `pass@k` e `pass^k`; regressão distinta de capacidade | 40 tarefas iniciais (10 edital/RAG, 10 decisões pedagógicas, 10 ações/privacidade, 10 adversariais), 5 tentativas cada; ampliar conforme falhas; 0 violações críticas observadas | 40 x 5 é proposta de desenho, não norma ou garantia estatística; rodar só quando o LLM/infra estiver disponível |
| **OpenAI — Evaluate Agent Workflows / Guardrails** | Traces de ferramenta, respostas e handoffs; grades estruturadas; aprovação humana para ações de risco; guardrails por entrada, saída e ferramenta | Guard antes e depois do LLM e, principalmente, **gateway de autorização fora do LLM** para ferramentas com efeitos | Guardrails do agente não se aplicam universalmente a toda ferramenta nem substituem aprovação e controles externos |
| **OWASP — Agentic Top 10 (2026)** | Falhas de objetivo, ferramenta, privilégios, supply chain, contexto/memória, interagentes, efeitos em cascata e confiança humana | Threat model por superfície: edital, PDF, mensagens Telegram, planilha de questões, respostas de ferramenta, memória e síntese | Classificação de ameaças não comprova resistência; precisa de ataques reproduzíveis do próprio projeto |
| **NIST AI RMF + GenAI Profile** | GOVERN, MAP, MEASURE, MANAGE; risco de confabulação, integridade, privacidade e dependências | Registro de risco por gate, severidade, proprietário, mitigação, risco residual e revisão de versão | Estrutura voluntária de gestão de risco, não certificação nem teste técnico executado |
| **AgentDojo (NeurIPS 2024)** | Simulação de ataques indiretos por conteúdo de ferramentas (97 tarefas e 629 casos na publicação original) | Injetar ordens falsas em chunks, relatórios, comentários, páginas e resultados do Telegram; confirmar que não há escrita, envio ou alteração de prioridade | Benchmark externo não substitui ataques construídos com as ferramentas e permissões UFMS |
| **τ-bench (ICLR 2025)** | Verificação do **estado final** e de cumprimento da política em diálogo multi-turn; `pass^k` para consistência | Verificar estado dos eventos, agenda, decisões e permissões após 5 execuções por cenário, não apenas a aparência da resposta | Domínios originais não são ensino/concurso; não importar taxas ou limiares publicados |
| **Anthropic — Effective Harnesses for Long-running Agents** | Retomada por artefatos versionados, progressos pequenos, testes fim-a-fim e prevenção de conclusão prematura | `HANDOFF`, readback remoto por SHA, checkpoint de estado e cancelamento de anúncio de conclusão quando o gate estiver pendente | Checkpoint não substitui executor e não comprova leitura semântica de cada arquivo |
| **OpenTelemetry GenAI conventions** | Traces com identidade de modelo, ferramenta e avaliação; atenção explícita a PII em prompt, resposta e argumentos | Registrar só metadados mínimos (`run_id`, `policy_sha`, `source_sha`, `decision`, `reason_codes`, métricas agregadas) por padrão | Observabilidade integral pode expor informações privadas; *não* armazenar prompts ou respostas sensíveis sem consentimento |
| **RAGBench / Ragas / DeepEval** | Distinguir recuperação, fidelidade à fonte, relevância e julgamento semântico | Testar separadamente recuperação de página/chunk do edital, apoio das afirmações, e recusa/abstenção em dúvidas normativas | LLM-as-judge é probabilístico; calibrar com gabarito humano e nunca usar nota isolada como autorização de escrita |
| **Giskard Open Source** | Testes de comportamento por cenário e varreduras adversariais como ferramenta opcional | Só considerar caso testes nativos não cubram segurança/qualidade com simplicidade suficiente | Ferramenta adiciona dependências e às vezes exige conta/modelo/API; não é garantia de compliance |

## 2. Padrão de qualidade em camadas (defesa em profundidade)

1. **Invariantes verificáveis (hard gates)**: autenticação/autorização, schemas, quantidade de questões, identidade do edital, fonte, idempotência, restrição de escopo, estado do consentimento, validade temporal, chamadas de ferramentas, integridade dos logs/projeções. Falha -> `DENY`/`BLOCKED` antes de produzir efeito.
2. **Fundamentação factual (mixed gate)**: citação de página/trecho do edital ou ato vigente para afirmações normativas, distinção entre fonte original e retificada. Verificador de citações confere existência, bytes e localização; avaliador semântico confere suficiência do apoio. Ausência -> `NEEDS_EVIDENCE`, nunca inventar.
3. **Qualidade da pedagogia (soft eval)**: adequação de dificuldade e caderno, não duplicação de evidência, distinção de diagnóstico/revisão/recuperação, incerteza explícita, utilidade e clareza. Métrica de comparação em lote, com avaliador humano calibrando grader automático.
4. **Resiliência adversarial**: falsa autoridade em chunk, “ignore regras”, logs contaminados, memória envenenada, tentativas duplicadas, dados fora de ordem, conflito de regras, falhas parciais de fornecedor e timeouts. Exigir prova negativa da ação vedada e teste de recuperação segura.
5. **Governança e prova**: política versionada, SHA de fonte/commit, testes reprodutíveis, relatório de ressalvas e verificador diferente do autor. Declarações de aprovação não substituem artefatos e resultados.

## 3. Metodologia proposta de avaliação

**Base inicial de 40 tarefas (sugestão, não prescrição da literatura):**
- 10 perguntas normativas/documentais com gabarito oficial e exigência de citação correta, incluindo casos sem evidência e retificações hipotéticas **marcadas como ficção**;
- 10 casos de decisão pedagógica com evidência E0–E4, 523/324, interseção parcial, repetição de questão, dados agregados vs. discriminados;
- 10 casos de ferramenta/privacidade com negações de escrita e aprovação, duplicatas, correção, idempotência, timeouts e concorrência;
- 10 ataques: chunk malicioso, mensagem forjada de coach, comando Telegram injetado, fonte normativamente falsa, tool output hostil, vazamento de dados, solicitação de desligar guardrail, registro retroativo falso, alteração de fonte e escalada de permissões.

**Repetibilidade:** registrar configuração de modelo, policy SHA, fonte/hash, dataset SHA, versão do avaliador, critérios, argumentos de ferramenta e artefatos de teste. Testar cada cenário em cinco tentativas onde houver acesso ao executor LLM; reportar distribuição, casos e taxa de sucesso repetido (`pass^k`), não apenas média global.

**Graders:** (a) Python/contrato para ações e campos; (b) comparação contra gabarito/rubrica editorial para pertinência; (c) avaliador LLM somente para critérios realmente semânticos, revisado contra amostra humana. Separar avaliações cega/holdout de casos usados para ajustar prompts.

**Critérios de liberação propostos, sujeitos a aprovação e calibração:** zero **violações críticas observadas** no lote de red team, zero bypass de ações externas proibidas em testes de fronteira, 100% dos checks de integridade semântica sintética para entradas conhecidas, cobertura de todos os caminhos e risco residual explícito. Os escores probabilísticos são **métricas de monitoramento** e objetivos de qualidade, não garantias universais. Não promover a produção só porque o juiz LLM aprovou tudo.

**Risco estatístico:** zero falhas em N testes ainda permite falhas não observadas; reportar N, distribuição dos casos e intervalos de incerteza quando aplicável. Não usar “100% seguro”.

## 4. Nove dimensões obrigatórias no `checks.md` (Spec Lean)

| Dimensão | Exemplo de contraprova UFMS |
| --- | --- |
| Validation and bounds | total incompatível, ID e data inválidos, link de fonte inventado |
| Failure and partial failure | LLM sem resposta, timeout de ferramenta, falha após aprovação |
| Idempotency, retry, duplicates | mesmo `event_id`, mesmo commit recebido duas vezes |
| Authorization and rate limits | usuário pede gravação sem consentimento, abuso de ferramenta, envio Telegram |
| Concurrency and ordering | duas correções concorrentes da mesma tentativa |
| Data lifecycle | expurgo/redação de trace e reconstrução a partir de eventos autorizados |
| External dependency failure | fonte offline, falha de provedor LLM/Calendar/Telegram |
| State transitions | `NEEDS_EVIDENCE` não transita direto para `WRITE_COMMITTED` |
| Observability | trace de gates com SHA e código de bloqueio, sem conteúdo pessoal |

## 5. Instrumentação e simplicidade

**Primeira escolha:** Python stdlib + `unittest` (já existente no repositório), fixtures JSON sintéticas, repositório GitHub como trilha de versões de código/regras e testes. Não criar dashboard, servidor HTTP ou banco próprio neste estágio. Só adicionar biblioteca (p.ex., Giskard/DeepEval/OpenTelemetry) quando uma obrigação **não puder** ser provada adequadamente com o harness mínimo.

**Barreira arquitetural obrigatória:** o LLM propõe uma `decision`; somente um componente determinístico externo decide se a ferramenta recebe permissão. Instruções no texto recuperado nunca modificam a política. O repositório já usa `personal_results_writes_enabled=false`: manter essa condição e impedir que ela seja mudada por saída do modelo.

**As provas de entrada devem vir do contrato, não do código atual**. Testes passam se a obrigação for verdadeira, não se o implementador copiar o comportamento defeituoso. Exigir duas contraprovas novas do verificador além das fixtures enumeradas pelo produtor.

## 6. Limites e pontos de decisão

- **Não foi realizado** estudo experimental com um tutor LLM operacional; os números 40 tarefas x 5 tentativas são desenho de benchmark a aprovar.
- **Não foi homologado** `plan.md` ou `checks.md`; a Skill Lean proíbe fixar checks antes do aceite humano formal do plano.
- Não se deve inferir que um prompt, o `.specs` ou o CI por si só impede chamadas diretas à API. Esse bloqueio exige **enforcement no gateway/credenciais**.
- Os testes anteriores de IGP-12–14 e o protótipo isolado são **evidência histórica útil**, não conclusão do novo harness cognitivo.
- Para a prova de confiança epistemológica, é indispensável revisão independente de amostras e rastreabilidade da versão do edital.

## 7. Fontes principais (primárias e documentação oficial)

1. Tech Leads Club, Spec Lean v2.2.0 (31/10/2026): https://agent-skills.techleads.club/skills/tlc-spec-lean/ ; referência de plano: https://raw.githubusercontent.com/tech-leads-club/agent-skills/main/packages/skills-catalog/skills/%28development%29/tlc-spec-lean/references/plan.md ; checks: https://raw.githubusercontent.com/tech-leads-club/agent-skills/main/packages/skills-catalog/skills/%28development%29/tlc-spec-lean/references/checks.md
2. Anthropic, Demystifying evals for AI agents: https://www.anthropic.com/research/demystifying-evals-for-ai-agents
3. Anthropic, Building effective agents: https://www.anthropic.com/research/building-effective-agents
4. Anthropic, Effective harnesses for long-running agents: https://www.anthropic.com/research/effective-harnesses-for-long-running-agents
5. OpenAI, Evaluate agent workflows: https://developers.openai.com/api/docs/guides/agent-evals
6. OpenAI, Guardrails and human review: https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
7. NIST, AI RMF 1.0 and Generative AI Profile 600-1: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
8. OWASP, Top 10 for Agentic Applications 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
9. AgentDojo, NeurIPS 2024: https://proceedings.nips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html
10. τ-bench, ICLR 2025: https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html
11. OpenTelemetry, GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/
12. RAGBench: https://arxiv.org/abs/2407.11005 ; Ragas faithfulness: https://github.com/vibrantlabsai/ragas/blob/main/docs/concepts/metrics/available_metrics/faithfulness.md
13. Giskard Open Source: https://docs.giskard.ai/oss
