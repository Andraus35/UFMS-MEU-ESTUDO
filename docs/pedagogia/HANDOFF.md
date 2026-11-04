# Handoff pedagógico — ciclo 8

**Checkpoint:** 04/11/2026, America/Campo_Grande.  
**Natureza:** prova local de referência isolada, não integração com harness nem homologação de GP-1.

## START e identidade

- Repositório `Andraus35/UFMS-MEU-ESTUDO`; PR pedagógico #2 `docs/especificacao-pedagogica-v1-2`, aberto/draft, HEAD anterior `66c218f91548ef4316b024930186036cece5fa49`.
- PR técnico #1 `setup/harness-memory-v0-2`, HEAD confirmado `1079d7aa2cadb97d099d1e478f9e83b36180a624`, aberto/draft; não alterado nesta entrega.
- `scripts/core.py`, `config/topics.csv` e IGP-01–14 preservados nos Git blobs conferidos no recibo.
- SHA do novo commit deste ciclo deve ser apurado por readback remoto.

## Entrega, evidência e limites

- [REFERENCIA_GP1_CICLO8_2026-11-04.md](REFERENCIA_GP1_CICLO8_2026-11-04.md) registra módulo de referência em Python para IGP-12/13/14, **15 testes PASS / 0 FAIL**, além de **11 PASS / 0 FAIL / 3 NOT_IMPLEMENTED** da suíte original de 14 fixtures.
- [RECIBO_REFERENCIA_GP1_CICLO8_2026-11-04.json](RECIBO_REFERENCIA_GP1_CICLO8_2026-11-04.json) registra SHA dos artefatos e fonte. O pacote `ufms_gp1_reference_ciclo8.zip` está disponível como artefato de conversa, não versionado no GitHub, SHA-256 `dc3dc599a8aba4536de89311ffd4fb71725b6d745d92d98339a58aed3c201adb`.
- README e este handoff atualizados no mesmo commit. **Códigos novos não foram commitados no PR #2**, que permanece documental; PR #1 e main intocados.
- O protótipo usa somente fixtures; não lê dados reais, não possui persistência, política efetiva de autenticação ou integração de eventos legados. `source_kind=synthetic_fixture` é guard didático, não segurança operacional.

## Estado e próxima ação

GP-0: edital local original já autorizado para estudo, retificações exigem monitoramento. GP-1: **PENDENTE** de implementação real de IGP-12/13/14 no harness, migração e testes; GP-2 a GP-5 não homologados. São 102 critérios pedagógicos documentados, não executados integralmente.

**Próxima entrega de maior valor:** a sessão técnica, após readback HEAD, deve portar somente as capacidades necessárias para branch técnica autorizada, implantar testes que falham primeiro e validar regressões/CI por commit. Esta sessão pedagógica só prossegue com nova evidência ou decisão de método; não repetir relatórios. Sem merge e sem resultados pessoais.
