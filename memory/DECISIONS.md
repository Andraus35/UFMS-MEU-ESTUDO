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

Estado: **diretriz de proposta em PR #9, sem merge**. Governança mínima deve proteger privacidade, edital/retificações, integridade de eventos, origem de escrita e retomada da fila; orientação cognitiva comum do Tutor/Coach não necessita aprovação humana por mensagem. Mudanças sensíveis e merge continuam em revisão própria. Reduzir documentos carregados no START, PRs paralelos e gates duplicados conforme `ROADMAP.md#fila-de-simplificação-pessoal--05112026`. ALTA/MEDIA precisam de contraprovas negativas e CI no HEAD; BAIXA pode ficar documentada. Não declarar correção concluída com texto/CI isoladamente.

## ADR-007 — Fluxo serial e uma fonte de estado (05/11/2026)

**Decisão vigente proposta no PR #9:** o desenvolvimento pessoal é sequencial: **uma tarefa → uma branch → um PR → um merge**, sem frentes empilhadas, paralelas ou PRs de auditoria separados. Criar próxima tarefa somente depois de concluir e integrar a anterior. O estado operacional `state/WORKFLOW.json` identifica trabalho ativo e registra PRs históricos pausados com SHAs. O `ROADMAP.md` descreve fila/criticidade e `memory/HANDOFF.md` resume retomada; não duplicar estado editável em três locais. O `state/CURRENT.json` continua exclusivamente como projeção de resultados de estudo. O gate local e a CI remota falham com múltiplos PRs; não garantem impossibilidade administrativa de criação. Exceção transitória: consolidar o saneamento existente no PR #9, depois iniciar SIM-01.
