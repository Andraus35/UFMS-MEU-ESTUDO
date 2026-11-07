# RM-08-BASELINE — baseline formal do ciclo Tutor–Coach

**Data da avaliação:** 07/11/2026  
**Objeto congelado:** `main@33b3b18ed741a53e4d9e22c3573c1154ffc1f5a2`  
**Último merge confirmado:** PR #54, merge commit `33b3b18ed741a53e4d9e22c3573c1154ffc1f5a2`  
**Natureza:** subescopo de diagnóstico, reconciliação e critérios de entrada.  
**Decisão:** baseline registrada; RM-08 formal permanece `bloqueado`.

## 1. Resultado executivo

O repositório já contém um protótipo offline do encadeamento Tutor–Coach e componentes técnicos para validação de fontes, renderer local e gateway fail-closed. Isso é avanço de engenharia, mas não demonstra um ciclo operacional com estudante, recepção de resultado real, persistência consentida e recuperação entre sessões.

A baseline separa três níveis que não podem ser confundidos:

1. **Implementação técnica:** módulos e testes unitários/sintéticos existem na `main`.
2. **Validação funcional integrada:** as provas ponta a ponta C1–C27 continuam sem aprovação registrada.
3. **Operação real:** não há integração externa verificada, persistência pessoal autorizada ou evidência de uso real.

A CI pós-merge do PR #54 está verde. O run `42349701319` concluiu o job `validate` com sucesso, incluindo governança, fluxo serial, bootstrap, privacidade, composição GQ-D, recibo r2, testes, benchmarks e rebuild. Esse resultado valida o commit de engenharia; não homologa GP-3, GQ-D, GQ-C, GQ-O ou GP-4.

## 2. Evidência congelada e proveniência

| Fonte | Identidade / conteúdo relevante |
|---|---|
| `AGENTS.md` | blob `ada3ae00bf84f378740f7976aee6ad712b3dffb7`; limites de escrita, integração e START |
| `ROADMAP.md` | blob `10b75c0cfc64e30d6a5dac7487de110805292871`; RM-08 bloqueada e RM-08-PREP não homologa GP-4 |
| `state/CURRENT.json` | blob `8699fdf77208c8dda2863405a135aedf5005d114`; E0, zero eventos/resultados |
| `docs/pedagogia/AUDITORIA_RM06_COBERTURA_102_20261105.md` | blob `88a65ab809ced68eaf72c5b454f544c07ce6bd2b` |
| `docs/pedagogia/GP3_MVP_PESSOAL_8_20261105.md` | blob `a4451e4adfbfec82b4cdba20db71d99249ac78f3` |
| `docs/governanca/RM07_GATEWAY_PROTOTIPO_20261105.md` | blob `9676d01781fbeb511421bb42b734b5214ffc08f6` |
| `docs/governanca/RM07_REAUDITORIA_9NC_27CHECKS_20261105.md` | blob `05e4d2abdbf511992637d14415a004008955f630`; fotografia anterior, não prevalece sobre atualização posterior do gateway |
| `docs/pedagogia/RM08_PREPARACAO_OFFLINE_SINTETICA_20261106.md` | blob `74bc986b32016975b8eba33f460133d5e90d5e7e` |
| `docs/governanca/SPEC_COGNITIVE_GATES_R2.md` | blob `eed2d11f7cba9401863a6af107db1daaa53e7ffd`; aprovação documental do PLAN r2, não aprovação funcional |

A matriz RM-07 antiga foi construída sobre `main@8fda9754846b4fba65cd88244260653cbb606720`, 92 commits antes do objeto atual. A atualização posterior `RM07_GATEWAY_PROTOTIPO_20261105.md` registra a situação após os incrementos de gateway, source/fact gates e renderer; por isso, os totais antigos da matriz não devem ser repetidos como estado atual. O histórico antigo permanece preservado.

## 3. Estado técnico dos gates

### GP-3 — cobertura dos cenários

A auditoria RM-06 registra 102 cenários no catálogo: 42 com teste unitário correlato (estado parcial), 60 sem teste canônico e zero cenários completos aprovados ou executados como roteiro end-to-end. O documento GP3-MVP8 seleciona oito cenários essenciais para um recorte de uso pessoal; os outros 94 permanecem no backlog.

O MVP8 é cobertura técnica mínima sintética, não homologação integral de GP-3 nem avaliação qualitativa da eficácia pedagógica. A baseline não promove o estado de GP-3.

### GQ-D / GQ-C / GQ-O — estado mais recente documentado

A atualização do protótipo de gateway registra nove não conformidades: **1 OPEN, 6 PARTIAL_IN_MAIN, 2 PARTIAL_CANDIDATE_NOT_MAIN e 0 CLOSED**.

| NC | Estado documentado | Limite que permanece |
|---|---|---|
| GQD-01 | PARTIAL_IN_MAIN | Gateway offline; caller/issuer sem isolamento de processo e segredo comprovado |
| GQD-02 | OPEN | Quatro mutantes semânticos e oráculos humanos independentes ausentes |
| GQD-03 | PARTIAL_CANDIDATE_NOT_MAIN | Manifesto/composição na branch legada, sem prova funcional integrada |
| GQD-04 | PARTIAL_IN_MAIN | Source/fact gates curados; não verificam suporte semântico geral de alegações arbitrárias |
| GQD-05 | PARTIAL_IN_MAIN | Rate limit atômico local; sem store durável e sem chamadas externas reais |
| GQD-06 | PARTIAL_IN_MAIN | Renderer local; runner integrado completo de estados/saídas ainda ausente |
| GQD-07 | PARTIAL_IN_MAIN | Recibo r2 comprova derivação documental, não GQ-D nem autorização de BUILD |
| GQD-08 | PARTIAL_IN_MAIN | Context binding em prévia local, sem rota de publicação externa |
| GQD-09 | PARTIAL_CANDIDATE_NOT_MAIN | Validadores Spec Lean executados na branch legada, não integrados como prova funcional atual |

**GQ-D:** permanece pendente de reauditoria independente; o recibo r2 registra reprovação anterior e não altera essa conclusão.  
**GQ-C:** NOT_RUN.  
**GQ-O:** BLOCKED.  
**C1–C27:** 0 PASS / 27 NOT_RUN_END_TO_END.

O protótipo `scripts/tool_gateway.py` não contém cliente de rede; usa adaptador fornecido pelo chamador, identidade de caller simulada e SQLite em memória por padrão. As contraprovas locais são úteis, mas não provam isolamento do emissor/chaves, identidade de processo, armazenamento durável nem zero efeitos em uma implantação real. O renderer atual limita a emissão a `local_preview`; Zapia/Telegram/Agenda e publicação externa não estão implantados.

### RM-08-PREP — ciclo sintético

`scripts/tutor_coach_offline_cycle.py` exercita recomendação, simulação de execução humana, relatório sintético, validação em memória, reconstrução e reavaliação. O protótipo rejeita execução real, plataforma externa e referências não sintéticas. Não grava eventos, `CURRENT.json`, `PROGRESS.csv` ou armazenamento; não usa rede nem integrações.

É uma prova útil de encadeamento sintético, mas não demonstra execução humana real, recepção operacional de resultado, persistência, replay ou recuperação intersessões.

## 4. Estado de privacidade e dados

- Repositório público.
- `settings.json`: `personal_results_writes_enabled=false`.
- `state/CURRENT.json`: `evidence_level=E0`, `event_count=0`, `results_count=0`.
- Nenhum resultado individual deve ser incluído no repositório público. A flag não é autorização.
- Zapia é a interface pretendida, não integração comprovadamente implantada.
- Não alterar `CURRENT.json`, `PROGRESS.csv`, `state/events/` ou dados pessoais nesta tarefa.

## 5. Critérios propostos para a entrada da RM-08 formal

Esta seção define critérios de avaliação, não concede autorização para executá-los:

1. **Recomendação rastreável:** snapshot, versão do edital, tópicos, cargo, fatores, justificativa e proveniência reproduzíveis.
2. **Execução humana identificável:** o estudante executa o caderno manualmente na plataforma escolhida; não presumir acesso automatizado ou disponibilidade de questões.
3. **Resultado verificável:** receber relatório com origem, data, caderno/recomendação relacionados, convenção de contagem e resultados por tópico quando disponíveis; rejeitar inconsistências e preservar desconhecidos.
4. **Reavaliação prudente:** recalcular a fila com evidência observada; não inferir domínio, retenção ou chance de aprovação a partir de percentual agregado isolado.
5. **Persistência consentida isolada:** somente em armazenamento privado e separado do repositório público, com consentimento explícito, minimização, revogação, controle de acesso e readback. A implementação permanece suspensa até autorização e desenho específico.
6. **Replay e recuperação:** reconstrução determinística a partir de eventos, idempotência, prevenção de duplicidade, concorrência/CAS, interrupção parcial, timeout sem retry cego e recuperação em nova sessão.
7. **Privacidade negativa:** provar que ausência/revogação de consentimento, tentativa de escrita no repositório público, corrupção, divergência de identidade ou resultado inconsistente não produzem persistência nem efeitos externos.

## 6. Bloqueadores e decisão de saída

| Bloqueador | Evidência necessária antes da promoção |
|---|---|
| Reauditoria GQ-D | Auditor independente reexecuta no HEAD aplicável; comprova oráculos e trata NCs P0/P1 sem promover protótipo a gateway confiável |
| GQ-C | Execução e recibo de validação conforme seu contrato; não basta NOT_RUN ou CI documental |
| GQ-O | Prova operacional de enforcement e bypass para qualquer efeito externo que venha a ser habilitado; sem implantação, manter NOT_IMPLEMENTED/BLOCKED |
| GP-3 | Delimitar formalmente o uso do MVP8 e o tratamento dos 94 cenários restantes; não chamar GP-3 integral de homologado |
| Persistência/replay | Arquitetura isolada e consentida, testes adversariais e readback real em ambiente permitido |
| Ciclo Tutor–Coach | Execução humana, recepção real, reavaliação e recuperação entre sessões demonstradas sem dados fictícios |

**Decisão:** RM-08 formal continua **BLOQUEADA**. A baseline não aprova GP-3, GQ-D, GQ-C, GQ-O ou GP-4; não habilita BUILD, credenciais, integração externa ou escrita de resultados pessoais. A próxima ação após esta baseline é reauditar e resolver os gates precedentes aplicáveis, mantendo RM-08 em espera até haver prova suficiente.

## 7. Limites desta avaliação

Esta baseline é uma consolidação documental baseada nos blobs e evidências referenciados no HEAD congelado. Não é auditoria independente GQ-D, teste E2E do Tutor/Coach, prova de implantação, nem execução dos hooks locais. As alterações desta frente são feitas pela API GitHub; hooks locais não foram executados e CI não os substitui.
