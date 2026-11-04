# ROADMAP — UFMS MEU ESTUDO

**Versão:** 1.0 · **Referência:** 04/11/2026 · **Repositório:** `Andraus35/UFMS-MEU-ESTUDO`  
**Objetivo:** orientar o harness de estudos por questões dos cargos UFMS 523 (Gestão Pública) e 324 (Assuntos Estudantis). Documento de planejamento; não aprova software, PRs, gates ou escrita pessoal.

## Governança e leitura obrigatória

1. **Antes de qualquer trabalho operacional**, todo agente participante (Tutor, Coach, engenheiro documental, pedagógico, auditor ou integrador) deve recuperar e interpretar `AGENTS.md` e **`ROADMAP.md`** do HEAD atual, nessa ordem, e consultar os demais arquivos obrigatórios em `settings.json`.
2. Em checkout local, executar `python scripts/bootstrap.py` e `python scripts/roadmap_gate.py --check` no START; verificar hash SHA-256 e identificar o item RM e eventuais bloqueadores. Sem checkout, ler os arquivos via GitHub autenticado e registrar HEAD e SHA de cada fonte. Se faltar leitura, integridade ou contexto, **não executar decisões nem mutações**.
3. Na entrega, atualizar este roadmap se houver alteração relevante de estado, dependência ou prioridade; registrar evidência do commit no `memory/HANDOFF.md`. Nenhum status será promovido apenas porque um documento ou teste de infraestrutura existe.
4. **Proteção administrativa aplicada:** o proprietário informou execução com `--check` retornando OK via Termux. Consulta GitHub autenticada verificou `main.protected=true` e status obrigatório `validate` aplicável a todos em 04/11/2026. O endpoint detalhado de proteção retornou 403 à integração, portanto estes detalhes adicionais dependem do check administrativo do proprietário. `scripts/protect_main.py` deve ser usado para **verificar**; não reaplicar PUT sem motivo e revisão. `.github/copilot-instructions.md` amplia instruções ao Copilot consultivo, sem constituir gate nativo universal. `.github/copilot-instructions.md` amplia as instruções para o Copilot consultivo, sem criar uma barreira universal.
5. **Limite verificável:** o bootstrap lê bytes, confere UTF-8, presença, ordem, fila RM e integridade local; isso não prova compreensão semântica por LLM. A proteção da `main` impõe check de CI na integração, **mas não impede agentes externos de ignorarem bootstrap ou alterarem código e workflow no mesmo PR**. Um verificador de fonte confiável e gates nos orquestradores de Tutor/Coach permanecem pendentes.
6. Não publicar resultados pessoais enquanto o repositório for público nem habilitar flag por simples alteração. Nenhum merge/deploy sem autorização humana. O PR #3 de ponte Oracle/Telegram está encerrado fora de escopo, sem autorização para retomada.

## Estado observado

Fotografia em `main`, commit **`676dd5d3259c66ba97c3e7e3338451cfc4e5cd68`** (revalidar no START). CI do commit: **160 testes técnicos aprovados**, não homologação do motor pedagógico.

| Frente | Evidência | Maturidade e pendência |
|---|---|---|
| Fonte do edital | PDF original local de 47 páginas, transcrição e 81 chunks | Integrada/testada; retificações e alerta cronológico p. 13 precisam de acompanhamento |
| Busca por cargo/anexo | Índices de tópicos, vagas, atribuições, BM25 e contraprovas | Integrada/testada; requer avaliação independente adicional |
| Memória, bootstrap e persistência | AGENTS, rules, hooks, eventos, projeções e CI | Infraestrutura testada; invocação universal dos gates não comprovada |
| Segurança | Bloqueio de resultados pessoais ativo; `main` protegida com `validate` obrigatório | Verificado em nível de branch; hooks dos agentes continuam cooperativos |
| Ingestão GP-1 | Contratos, fixtures e protótipo isolado com 15 testes | Implementação real de IGP-12/13/14 ainda não integrada |
| Pedagogia adaptativa | Especificações v1.0–v1.8 e 102 critérios | Documentada; não há execução integral do motor |
| Cognitive Gates | PR #5 com PLAN r2 e CHECKS C1–C27 | 0/27 provas funcionais; GQ-D exige reauditoria independente |
| Tutor, Coach e integrações | Contratos e POCs sintéticas Zapia | Serviço integrado não homologado; Gemini Notebook/Projects não comprovados de ponta a ponta |
| Dados de estudo | `state/CURRENT.json`: 0 eventos, 0 resultados | Escrita individual bloqueada |

## Fila de execução

**Estados permitidos:** `planejado`, `em_andamento`, `implementado_nao_homologado`, `bloqueado`, `homologado`. A classificação é rastreável por evidência do HEAD, não percentual arbitrário.

| ID | P | Frente / gate | Estado de partida | Definition of Done |
|---|---|---|---|---|
| RM-00 | P0 | Governança, ROADMAP, START/DELIVERY | em_andamento | Bootstrap e branch protection verificados; faltam gate independente de workflow alterável, implementação nos orquestradores e parecer externo |
| RM-01 | P0 | ENG-00 / GP-0: edital, recortes e retificações | implementado_nao_homologado | Fonte/versionamento verificados, alerta conhecido preservado, monitoramento efetivo |
| RM-02 | P0 | ENG-01/02 / GP-1: contratos, tentativas e ingestão | bloqueado | IGP-12/13/14 integrados, migração sem perda histórica, testes negativos/CI |
| RM-03 | P1 | ENG-03 / GP-2: evidências E0–E4 | planejado | Projeção reprodutível, origem e incerteza claras, sem inferir domínio |
| RM-04 | P1 | ENG-04 / GP-2: fila adaptativa 523/324 | planejado | Ranking determinístico por snapshot e política, justificativas auditáveis, sem dupla contagem |
| RM-05 | P1 | ENG-05 / GP-2: prescritor de cadernos | planejado | Filtros realistas, fallback e estado do caderno sem inventar ID externo |
| RM-06 | P1 | ENG-06 / GP-3: testes adversariais | planejado | Rastrear/implementar/registrar execução dos 102 cenários e mutantes aplicáveis |
| RM-07 | P1 | GQ-D/C/O do harness cognitivo | bloqueado | Reauditar 9 NCs do PR #5, executar 27 checks funcionais; sem confundir validação documental com operacional |
| RM-08 | P2 | ENG-07 / GP-4: ciclo Tutor–Coach | bloqueado | Recomendação → execução humana → resultado → reavaliação, persistência/replay consentidos |
| RM-09 | P2 | Integrações gratuitas necessárias | planejado | Provas de autorização e fluxo com Gemini Notebook, Zapia e GitHub Projects; sem reabrir PR #3 |
| RM-10 | P2 | ENG-08 / GP-5: piloto | bloqueado | Privacidade, autorização, observações reais e avaliação prudente de utilidade |

**Dependências:** RM-00 e RM-01 podem avançar em paralelo; RM-02 → RM-03 → RM-04 → RM-05, com RM-06 testando cada incremento; RM-07 requer avaliação independente própria; RM-08/09 e RM-10 dependem de gates técnicos, segurança e autorização.

## Critérios de promoção

Para mudar status, registrar no mesmo fluxo de entrega: `roadmap_id`, base/HEAD SHA, escopo, diff, testes por cenário e commit, resultados da CI, readback, auditoria independente quando exigida, autorização humana quando aplicável, decisão e próximos bloqueadores. `SKIP`/`NOT_RUN` não é `PASS`. A validação de infraestrutura não comprova eficácia pedagógica; protótipos e POCs sintéticas não equivalem a dados reais.

**Contratos permanentes:** estudar pelo edital original enquanto se monitoram retificações verificadas; TEC/Qconcursos operados legitimamente pelo estudante, sem acesso privado presumido; adaptação flexível, sem cronogramas rígidos; preservar event logs, integridade documental e evidências de correção. Não duplicar entregas ou inventar desempenho.

## Checkpoint de tratamento de não conformidades — 04/11/2026

- Auditoria independente do PR #9: **G0 e GQ-H REPROVADOS**, 2 NCs P0 e 4 P1. CI verde não revoga esse parecer.
- **NC-PR9-01 (P0):** [PR #10](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/10) propõe gate de governança da base protegida e assinatura Ed25519; **ainda não está na main nem é required check**. Necessita auditoria externa e evitar falsificação de check pelo mesmo aplicativo GitHub Actions.
- **NC-PR9-02 (P0):** [PR #11](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/11) propõe admissão Tutor/Coach com START fail-closed; **sem serviço remoto, sem migração de credenciais e sem prova de cobertura universal**. As ações externas permanecem bloqueadas no protótipo.
- **NC-PR9-03 (P1):** esta candidata agora fixa linha de base de prioridade, estado e critério de conclusão de cada RM-00 a RM-10, com contraprovas de promoção, rebaixamento de prioridade e enfraquecimento de critério. A baseline é código do próprio PR e **não prova aprovação humana independente nem mérito semântico**. Alterações futuras exigem mudança auditada do contrato e evidência.
- **NC-PR9-04 (P1):** documento `docs/API_WRITE_GOVERNANCE.md` atualizado com estado vigente da branch e observações históricas; auditoria independente deve verificar ausência de contradições restantes.
- **NC-PR9-05 (P1):** adaptador `scripts/api_write_guard.py` permanece intencionalmente restrito ao PR #1 histórico, **não cobre o PR #9**; não remover guardrails para simular fechamento.
- **NC-PR9-06 (P1):** proteção `main.protected=true` e `validate` obrigatório são confirmados; auditor obteve 403 para a política administrativa detalhada. Confirmação completa ainda requer leitura independente com permissão adequada.
- **Gate de saída:** reauditoria G0/GQ-H do novo HEAD, testes de adversário contra fonte de check externa confiável, broker real com credenciais confinadas e aceite humano para qualquer merge.

## Referências

- [AGENTS](AGENTS.md) · [Settings](settings.json) · [Handoff técnico](memory/HANDOFF.md) · [Handoff pedagógico](docs/pedagogia/HANDOFF.md)
- [Plano de implementação ENG-00–08](docs/pedagogia/PLANO_IMPLEMENTACAO_GATES_v1.8.md) · [102 critérios GP-0–GP-5](docs/pedagogia/RASTREABILIDADE_GATES_v1.8.md)
- [PR #5: Cognitive Gates](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/5) · [Auditoria histórica](docs/auditorias/AUDITORIA_BRANCHES_E_MERGES_2026-11-04.md)
