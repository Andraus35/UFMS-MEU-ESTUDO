# RM-02 — implementação aditiva dos contratos IGP-12/13/14

**Data:** 05/11/2026  
**Base:** `main@725858292ecc1e3e0ad7a85a0ae9a91966d112ee`  
**Escopo:** ENG-01/02, GP-1. Código puro/offline; fixtures sintéticas; sem persistência.

## Contrato implementado

### IGP-12 — normalização explícita
`normalize_external_report(report, answered_convention)` exige convenção explícita do chamador:
- `answered_excludes_unanswered`: respondidas exclui em branco; total = respondidas + em branco.
- `answered_includes_unanswered`: o total reportado inclui em branco; respondidas efetivas = total - em branco.
- convenção ausente/desconhecida retorna `pending_clarification`, sem evento.
- contagens incoerentes, identidades ausentes ou data inválida são rejeitadas. IDs nunca são inventados.

### IGP-13 — identidade de tentativa
- Eventos aditivos `attempt_recorded` e `attempt_corrected`, schema `1.0`.
- `recommendation_id`, `platform_notebook_id` e `attempt_id` são campos distintos.
- Duas tentativas independentes podem compartilhar o mesmo `platform_notebook_id), desde que `attempt_id` seja diferente.
- Correção só substitui a tentativa indicada e deve apontar para seu último `event_id`; não pode alterar a identidade da tentativa.
- Eventos legados `resultado_recebido`/`resultado_corrigido` permanecem no caminho original.

### IGP-14 — tempo
- `recorded_at` é obrigatório e representa recepção/registro.
- `attempt_at` é opcional; `null` permanece desconhecido, nunca inferido do commit ou da mensagem.
- Datas exigem fuso; tentativa posterior ao registro é rejeitada.
- A projeção `last_event_at` usa `recorded_at` nos novos eventos.

## Compatibilidade e privacidade
- `core.validate_events` e `core.rebuild` reconhecem os eventos novos sem reescrever ou rehashar JSONL legado.
- A projeção soma tentativas independentes e substitui somente a tentativa corrigida.
- A recomendação é encerrada quando a tentativa correspondente é registrada.
- Resultados pessoais continuam bloqueados por padrão; `allow_private=True` existe apenas para testes em memória.
- Não houve escrita em `state/CURRENT.json`, `state/events`, `PROGRESS.csv`, nem alteração de `settings.json`.

## Evidência e limites
A suíte nova `tests/test_gp1_ingestion.py` cobre normalização ambígua/confirmada, duas tentativas no mesmo caderno externo, correção isolada, IDs duplicados, correção órfã, identidade, tempo, versão de schema e bloqueio de escrita. As regressões antigas permanecem em `tests/test_harness.py`.

A aprovação desta implementação requer CI completa no SHA exato e revisão do readback. Ainda não prova integração com TEC/Qconcursos, importação real, autorização de dados pessoais ou eficácia pedagógica. GP-1 só poderá ser homologado após evidência externa legítima e revisão independente dos contratos.
