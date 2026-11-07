# Registro de decisões arquiteturais

## ADR-001 — Repositório como fonte de verdade

Estado: vigente (adotado na prática desde 04–05/11/2026). As sessões são retomadas pelo histórico de eventos, estado derivado e handoff compacto.

## ADR-002 — Agente único, pedagogia flexível

Estado: vigente (adotado na prática desde 04–05/11/2026). Regras de integridade são determinísticas; seleção de questões, explicações e recuperação são adaptativas.

## ADR-003 — Interação humana com TEC e Qconcursos

Estado: vigente (adotado na prática desde 04–05/11/2026). O estudante usa as plataformas e devolve estatísticas. Não há coleta automatizada presumida.

## ADR-004 — Privacidade anterior a dados reais

Estado: bloqueio inicial. O registro histórico alegava visibilidade privada em 04/11/2026; consulta autenticada de 05/11/2026 confirmou **visibilidade pública**. Portanto não gravar resultados individuais, credenciais ou relatórios brutos; manter a flag de escrita pessoal bloqueada e rever a visibilidade antes de qualquer futura autorização.

## ADR-005 — Mudanças estruturais por PR

Estado: vigente (adotado na prática desde 04–05/11/2026). Sem merge autônomo; sessões ordinárias podem persistir dados autorizados após validar e proteger a privacidade.

## ADR-006 — Simplificação proporcional para uso pessoal (05/11/2026)

Estado: **integrado à main via PR #9 (merge 7942771aea28)**. Governança mínima deve proteger privacidade, edital/retificações, integridade de eventos, origem de escrita e retomada da fila; orientação cognitiva comum do Tutor/Coach não necessita aprovação humana por mensagem. Mudanças sensíveis e merge continuam em revisão própria. Reduzir documentos carregados no START, PRs paralelos e gates duplicados conforme `ROADMAP.md#fila-de-simplificação-pessoal--05112026`. ALTA/MEDIA precisam de contraprovas negativas e CI no HEAD; BAIXA pode ficar documentada. Não declarar correção concluída com texto/CI isoladamente.

## ADR-007 — Fluxo serial e uma fonte de estado (05/11/2026)

**Decisão vigente, integrada pelo PR #9:** o desenvolvimento pessoal é sequencial: **uma tarefa → uma branch → um PR → um merge**, sem frentes empilhadas, paralelas ou PRs de auditoria separados. Criar próxima tarefa somente depois de concluir e integrar a anterior. O estado operacional `state/WORKFLOW.json` identifica trabalho ativo e registra PRs históricos pausados com SHAs. O `ROADMAP.md` descreve fila/criticidade e `memory/HANDOFF.md` resume retomada; não duplicar estado editável em três locais. O `state/CURRENT.json` continua exclusivamente como projeção de resultados de estudo. O gate local e a CI remota falham com múltiplos PRs; não garantem impossibilidade administrativa de criação. Exceção do PR #9 concluída. Frente ativa e próxima tarefa: ver `state/WORKFLOW.json`.

## ADR-008 — Recuperação seletiva de branches legadas (05/11/2026)

Estado: **decisão operacional SIM-01/PR #19, ainda candidata**. Após o merge do PR #9, 13 branches históricas restaram, das quais 12 têm commits exclusivos. Não fazer merge em lote: preferir recuperação seletiva, em um PR e uma capacidade de cada vez, com testes no HEAD atual. Proteger o bloqueio de dados pessoais em repositório público e não instalar infraestrutura não comprovada. Inventário e ordem em `docs/governanca/PLANO_RECUPERACAO_BRANCHES_20261105.md`.

## ADR-009 — API writer em host confiável, não em prompt (SIM-02/PR #20)

Estado: **candidata de integração**. A cadeia histórica #13→#17→#18 tem controles de proposta, readback de bytes e escrita transacional; a versão terminal está sendo recuperada seletivamente no PR #20. A biblioteca de escrita permanece bloqueada por padrão e exige `UFMS_ENABLE_GITHUB_WRITE=1` e `GH_TOKEN` segregado fora do LLM. Mesmo depois de incorporada à `main`, sua implantação e a obrigação de todos os agentes de passarem pelo guard são **gates distintos**. Não alterar a política de resultados individuais em repositório público. Referências: `docs/governanca/CONTRATO_API_PR_ATUAL.md` e `docs/governanca/PLANO_RECUPERACAO_BRANCHES_20261105.md`.

## ADR-010 — Não reintegrar versão obsoleta do broker (SIM-05/PR #22)

Em 05/11/2026, comparação de `main` com branches #11 e #15 confirmou que o broker atual já oferece START 4/5 arquivos, SHA externo confiável, checkout limpo, contexto/hashes e bloqueio de ações externas. A versão histórica usa lista de 10 arquivos, contrato de RM-00..10 e API `AgentBroker` incompatível; testes de composição exigem métodos não existentes na implementação atual. Reintegrá-la por cópia substituiria uma implementação mais recente e reintroduziria carga e gates excessivos. Branches #12/#14 contêm fotografias de estado e handoffs obsoletos (HEAD e PRs antigos), não autoridade operacional. Decisão: manter branches preservadas, não importar código/documentação obsoletos e registrar apenas a reconciliação. A decisão não afirma enforcement universal: o broker continua read-only e não intercepta clientes externos que o ignorem.

## ADR-011 — Não instalar Trusted Governance externa sem E2E e benefício proporcional (SIM-07/PR #24)

A branch histórica #10 propõe GitHub App, host Oracle, token de instalação, chave RSA da App e assinatura humana Ed25519. Não há instalação nem prova E2E real. A própria ADR-P0-APP-001 registra que o check verde pode permanecer válido por até sete dias e que o limite local de 10 minutos não é lease imposta pelo GitHub; não há revogação imediata garantida em indisponibilidade. A alternativa de migrar para organização/merge queue também é proposta sem implementação. Para uso pessoal, não integrar os scripts/workflows/segredos. Manter proteção `validate`, CI e fluxo serial, sem alegar enforcement universal. Reavaliar apenas se necessidade multiusuário concreta justificar o custo e se testes E2E demonstrarem comportamento durante outage/revogação.

## ADR-012 — Adiar ponte Oracle/Telegram/Calendar (#3) até decisão de interface e E2E (SIM-08/PR #25)

A branch #3 oferece MVP isolado com dois bots Telegram, SQLite, Google Calendar secundário e adaptador LLM opt-in, mas declara não estar implantada, não ter bots/OAuth reais e não integrar ao Tutor/Coach. A auditoria disponível é interna e os testes são offline. RATE-01 (quotas/retention), OPS-01 (infra/OAuth/backup/secrets) e PED-01 (estado/fontes reais) permanecem bloqueados. Para o harness pessoal, não integrar aplicação nem workflow agora; preservar a branch. Reavaliar após escolha explícita de interface, necessidade 24/7 e E2E de consentimento, revogação, idempotência, retenção, backup e operação sem credenciais. Não assumir que testes unitários comprovam serviço em produção.

## ADR-013 — Persistência privada de resultados pessoais: desenho (07/11/2026)

Estado: **decisão de desenho; implementação e habilitação não autorizadas.** Resultados pessoais, quando habilitados, vão para um **repositório GitHub privado separado**; este repositório público permanece sem dados pessoais e `personal_results_writes_enabled=false`. A habilitação exige PR próprio, aprovação humana e os controles P1–P9 (visibilidade `private=true` verificada a cada escrita, destino fixo, consentimento versionado, token fora do LLM, idempotência/CAS, readback, replay e revogação). O histórico Git é permanente, então a minimização prevalece sobre a revogação. O app Claude não recebe acesso ao repositório privado nesta etapa. **Decisões do proprietário (07/11/2026):** repositório `Andraus35/ufms-meu-estudo-dados` (privado, ainda não criado); escritor = a Zapia, como executora por comando do Tutor, pela API REST do GitHub com credencial própria (revisado em 07/11/2026; substitui a decisão anterior de gravação manual pelo proprietário), condicionado a P1–P9 e a OPEN-01/OPEN-02 do `PRODUCT.md`; retenção até a prova (17/01/2027) mais 30 dias, e revogação efetiva = apagar o repositório privado; texto de consentimento **v2** aprovado em 07/11/2026 (inclui Zapia e Google; substitui o v1). Em aberto: criação do repositório pelo proprietário e registro formal do consentimento (P3) antes do primeiro evento. Detalhes: `docs/governanca/ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md`.

## ADR-014 — PRODUCT.md como documento do produto e leitura obrigatória de engenharia (07/11/2026)

Estado: **decisão do proprietário.** A ideia e o passo a passo do produto (Tutor e Coach como agentes que decidem com base no harness, Zapia como interface e executora restrita ao harness e aos comandos deles, harness no GitHub como fonte de verdade, Gemini Notebook como ambiente de revisão) não podem se perder entre sessões ou modelos construtores, como ocorreu na transição entre modelos. `PRODUCT.md` (raiz) passa a ser o **3º arquivo** do START de engenharia (`AGENTS.md`, `ROADMAP.md`, `PRODUCT.md`, `memory/HANDOFF.md`, `state/CURRENT.json`, `state/WORKFLOW.json`); o START de estudo não muda. **Não contém estado** (fila, PR, SHA), para não criar segunda fonte editável. Precedência: `AGENTS.md` > `PRODUCT.md` > `ROADMAP.md`. Validado por `scripts/product_gate.py --check` (seções, IDs, aceite por requisito, referências cruzadas, ausência de estado) dentro do bootstrap de engenharia. Substitui `docs/pedagogia/PROMPT_TRANSFERENCIA_TECNICA_v1.8.md` como porta de entrada de construção; o prompt permanece como histórico.
