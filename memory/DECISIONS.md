# Registro de decisões arquiteturais

## ADR-001 — Repositório como fonte de verdade

Estado: proposto. As sessões são retomadas pelo histórico de eventos, estado derivado e handoff compacto.

## ADR-002 — Agente único, pedagogia flexível

Estado: proposto. Regras de integridade são determinísticas; seleção de questões, explicações e recuperação são adaptativas.

## ADR-003 — Interação humana com TEC e Qconcursos

Estado: proposto. O estudante usa as plataformas e devolve estatísticas. Não há coleta automatizada presumida.

## ADR-004 — Privacidade anterior a dados reais

Estado: bloqueio inicial. O registro histórico alegava visibilidade privada em 04/11/2026; consulta autenticada de 05/11/2026 confirmou **visibilidade pública**. Portanto não gravar resultados individuais, credenciais ou relatórios brutos; manter a flag de escrita pessoal bloqueada e rever a visibilidade antes de qualquer futura autorização.

## ADR-005 — Mudanças estruturais por PR

Estado: proposto. Sem merge autônomo; sessões ordinárias podem persistir dados autorizados após validar e proteger a privacidade.

## ADR-006 — Simplificação proporcional para uso pessoal (05/11/2026)

Estado: **integrado à main via PR #9 (merge 7942771aea28)**. Governança mínima deve proteger privacidade, edital/retificações, integridade de eventos, origem de escrita e retomada da fila; orientação cognitiva comum do Tutor/Coach não necessita aprovação humana por mensagem. Mudanças sensíveis e merge continuam em revisão própria. Reduzir documentos carregados no START, PRs paralelos e gates duplicados conforme `ROADMAP.md#fila-de-simplificação-pessoal--05112026`. ALTA/MEDIA precisam de contraprovas negativas e CI no HEAD; BAIXA pode ficar documentada. Não declarar correção concluída com texto/CI isoladamente.

## ADR-007 — Fluxo serial e uma fonte de estado (05/11/2026)

**Decisão vigente, integrada pelo PR #9:** o desenvolvimento pessoal é sequencial: **uma tarefa → uma branch → um PR → um merge**, sem frentes empilhadas, paralelas ou PRs de auditoria separados. Criar próxima tarefa somente depois de concluir e integrar a anterior. O estado operacional `state/WORKFLOW.json` identifica trabalho ativo e registra PRs históricos pausados com SHAs. O `ROADMAP.md` descreve fila/criticidade e `memory/HANDOFF.md` resume retomada; não duplicar estado editável em três locais. O `state/CURRENT.json` continua exclusivamente como projeção de resultados de estudo. O gate local e a CI remota falham com múltiplos PRs; não garantem impossibilidade administrativa de criação. Exceção do PR #9 concluída. A única frente atual é SIM-01/PR #19; próximo ciclo SIM-02 após merge comprovado.

## ADR-008 — Recuperação seletiva de branches legadas (05/11/2026)

Estado: **decisão operacional SIM-01/PR #19, ainda candidata**. Após o merge do PR #9, 13 branches históricas restaram, das quais 12 têm commits exclusivos. Não fazer merge em lote: preferir recuperação seletiva, em um PR e uma capacidade de cada vez, com testes no HEAD atual. Proteger o bloqueio de dados pessoais em repositório público e não instalar infraestrutura não comprovada. Inventário e ordem em `docs/governanca/PLANO_RECUPERACAO_BRANCHES_20261105.md`.

## ADR-009 — API writer em host confiável, não em prompt (SIM-02/PR #20)

Estado: **candidata de integração**. A cadeia histórica #13→#17→#18 tem controles de proposta, readback de bytes e escrita transacional; a versão terminal está sendo recuperada seletivamente no PR #20. A biblioteca de escrita permanece bloqueada por padrão e exige `UFMS_ENABLE_GITHUB_WRITE=1` e `GH_TOKEN` segregado fora do LLM. Mesmo depois de incorporada à `main`, sua implantação e a obrigação de todos os agentes de passarem pelo guard são **gates distintos**. Não alterar a política de resultados individuais em repositório público. Referências: `docs/governanca/CONTRATO_API_PR_ATUAL.md` e `docs/governanca/PLANO_RECUPERACAO_BRANCHES_20261105.md`.

## ADR-010 — Não reintegrar versão obsoleta do broker (SIM-05/PR #22)

Em 05/11/2026, comparação de `main` com branches #11 e #15 confirmou que o broker atual já oferece START 4/5 arquivos, SHA externo confiável, checkout limpo, contexto/hashes e bloqueio de ações externas. A versão histórica usa lista de 10 arquivos, contrato de RM-00..10 e API `AgentBroker` incompatível; testes de composição exigem métodos não existentes na implementação atual. Reintegrá-la por cópia substituiria uma implementação mais recente e reintroduziria carga e gates excessivos. Branches #12/#14 contêm fotografias de estado e handoffs obsoletos (HEAD e PRs antigos), não autoridade operacional. Decisão: manter branches preservadas, não importar código/documentação obsoletos e registrar apenas a reconciliação. A decisão não afirma enforcement universal: o broker continua read-only e não intercepta clientes externos que o ignorem.

## ADR-011 — Não instalar Trusted Governance externa sem E2E e benefício proporcional (SIM-07/PR #24)

A branch histórica #10 propõe GitHub App, host Oracle, token de instalação, chave RSA da App e assinatura humana Ed25519. Não há instalação nem prova E2E real. A própria ADR-P0-APP-001 registra que o check verde pode permanecer válido por até sete dias e que o limite local de 10 minutos não é lease imposta pelo GitHub; não há revogação imediata garantida em indisponibilidade. A alternativa de migrar para organização/merge queue também é proposta sem implementação. Para uso pessoal, não integrar os scripts/workflows/segredos. Manter proteção `validate`, CI e fluxo serial, sem alegar enforcement universal. Reavaliar apenas se necessidade multiusuário concreta justificar o custo e se testes E2E demonstrarem comportamento durante outage/revogação.
