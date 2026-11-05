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
