# Registro de decisões arquiteturais

<!-- governance-current:start -->
**Situação vigente (readback autenticado):** main 676dd5d3259c66ba97c3e7e3338451cfc4e5cd68; PRs mesclados: #1, #2, #6, #7, #8; fechados sem merge: #3, #4, #10. O texto original a seguir é histórico quando mencionar PRs antigos; rever o estado atual antes de cada operação. Registros ADR anteriores não são apagados nem automaticamente revogados por este script. Consultar [docs/governanca/STATUS_VIGENTE.md](../docs/governanca/STATUS_VIGENTE.md).
<!-- governance-current:end -->

## ADR-001 — Repositório como fonte de verdade

Estado: proposto. As sessões são retomadas pelo histórico de eventos, estado derivado e handoff compacto.

## ADR-002 — Agente único, pedagogia flexível

Estado: proposto. Regras de integridade são determinísticas; seleção de questões, explicações e recuperação são adaptativas.

## ADR-003 — Interação humana com TEC e Qconcursos

Estado: proposto. O estudante usa as plataformas e devolve estatísticas. Não há coleta automatizada presumida.

## ADR-004 — Privacidade anterior a dados reais

Estado: bloqueio inicial. O repositório foi observado como privado em 2026-11-04; revalidar visibilidade antes de dados pessoais e não persistir credenciais ou relatórios brutos.

## ADR-005 — Mudanças estruturais por PR

Estado: proposto. Sem merge autônomo; sessões ordinárias podem persistir dados autorizados após validar e proteger a privacidade.
