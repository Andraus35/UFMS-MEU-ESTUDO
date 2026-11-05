# ROADMAP — UFMS MEU ESTUDO

> **ESTADO VIGENTE — SIM-06 / PR #23 (draft).** SIM-05/PR #22 integrado à `main` em `ace048a05d3a0100ef5f05884745969ff7221d83`; CI pós-merge aprovada com 307 testes e gate `awaiting_next_task=SIM-06`. Frente única: `spec/sim06-cognitive-gates-r2-20261105`, integração documental do PLAN v0.3-r2 aprovado e seus 27 CHECKS. Provas E2E 0/27; GQ-D REPROVADA, GQ-C NOT_RUN, GQ-O BLOCKED. Proposta r3 não aprovada. Próxima SIM-07 após merge #23.


**Versão:** 1.0 · **Referência:** 04/11/2026 · **Repositório:** `Andraus35/UFMS-MEU-ESTUDO`  
**Objetivo:** orientar o harness de estudos por questões dos cargos UFMS 523 (Gestão Pública) e 324 (Assuntos Estudantis). Documento de planejamento; não aprova software, PRs, gates ou escrita pessoal.

## Autonomia cognitiva e gates proporcionais

**Diretriz do proprietário (04/11/2026):** uso pessoal; Zapia é a interface pretendida de comunicação. O Tutor e o Coach têm liberdade para raciocinar, escolher intervenções, adaptar métodos e elaborar orientações, sem solicitar aprovação humana para cada mensagem. A liberdade cognitiva não equivale a acesso irrestrito a credenciais, arquivos ou serviços.

- **ORIENTACAO (efeito NONE):** explicações, diagnósticos, feedback, planejamento adaptativo e mensagens informativas podem ser entregues automaticamente ao estudante depois do gate de evidência, escopo e integridade. A entrega ocorre sem aprovação humana por mensagem; não criar gate `NEEDS_APPROVAL` para cada resposta comum.
- **ROTINA_AUTORIZADA (efeito TOOL):** mensagens ao próprio estudante pela Zapia e lembretes na agenda, quando integrações oficiais estiverem comprovadas, podem ser automáticos **dentro de consentimento prévio, destinatário/canal permitido, limites, minimização de dados, idempotência e readback**. A autorização é de escopo/rotina, não por mensagem. Sem conector autorizado ou credencial isolada, registrar `NOT_IMPLEMENTED`; não alegar envio.
- **SENSIVEL (efeito TOOL):** alterar políticas/credenciais, publicar a terceiros, expor dados pessoais ou integrar à `main` requer gate específico e autorização humana expressa quando prevista. Uma aprovação da atividade de estudo não concede poderes de administração.
- **Privacidade invariável:** este repositório é público; persistência de resultados pessoais permanece bloqueada até uma solução privada e verificável. O histórico não pode ser preenchido com dados inventados.
- **Controle proporcional:** aplicar GP-0/GP-1/GP-2/GP-3/GP-4/GP-5 às evidências e entregas pertinentes, sem converter testes de infraestrutura ou documentação em aprovação operacional do Tutor/Coach. Falha em ação sensível não bloqueia automaticamente orientação pedagógica independente daquela ação.

**Estado:** contrato documental para reconciliar PRs #9/#11/#5; não constitui integração real com Zapia, não reclassifica aprovações anteriores e não autoriza merge/deploy. A solução de duas GitHub Apps do PR #10 permanece proposta separada, não pré-requisito para toda orientação cognitiva.

## Governança e leitura obrigatória

1. **Antes de qualquer trabalho operacional**, todo agente participante (Tutor, Coach, engenheiro documental, pedagógico, auditor ou integrador) deve recuperar e interpretar `AGENTS.md` e **`ROADMAP.md`** do HEAD atual, nessa ordem, e consultar os outros dois obrigatórios (handoff e CURRENT) em `settings.json`; demais fontes sob demanda.
2. Em checkout local, executar `python scripts/bootstrap.py` e `python scripts/roadmap_gate.py --check` no START; verificar hash SHA-256 e identificar o item RM e eventuais bloqueadores. Sem checkout, ler os arquivos via GitHub autenticado e registrar HEAD e SHA de cada fonte. Se faltar leitura, integridade ou contexto, **não executar decisões nem mutações**.
3. Na entrega, atualizar este roadmap se houver alteração relevante de estado, dependência ou prioridade; registrar evidência do commit no `memory/HANDOFF.md`. Nenhum status será promovido apenas porque um documento ou teste de infraestrutura existe.
4. **Proteção administrativa aplicada:** o proprietário informou execução com `--check` retornando OK via Termux. Consulta GitHub autenticada verificou `main.protected=true` e status obrigatório `validate` aplicável a todos em 04/11/2026. O endpoint detalhado de proteção retornou 403 à integração, portanto estes detalhes adicionais dependem do check administrativo do proprietário. `scripts/protect_main.py` deve ser usado para **verificar**; não reaplicar PUT sem motivo e revisão. `.github/copilot-instructions.md` amplia instruções ao Copilot consultivo, sem constituir gate nativo universal. `.github/copilot-instructions.md` amplia as instruções para o Copilot consultivo, sem criar uma barreira universal.
5. **Limite verificável:** o bootstrap lê bytes, confere UTF-8, presença, ordem, fila RM e integridade local; isso não prova compreensão semântica por LLM. A proteção da `main` impõe check de CI na integração, **mas não impede agentes externos de ignorarem bootstrap ou alterarem código e workflow no mesmo PR**. Um verificador de fonte confiável e gates nos orquestradores de Tutor/Coach permanecem pendentes.
6. Não publicar resultados pessoais enquanto o repositório for público nem habilitar flag por simples alteração. Nenhum merge/deploy sem autorização humana. O PR #3 de ponte Oracle/Telegram está encerrado fora de escopo, sem autorização para retomada.

## Estado observado

Fotografia histórica substituída. Em 05/11/2026, `main` = `ace048a05d3a0100ef5f05884745969ff7221d83`; CI pós-merge do PR #22: **307 testes técnicos aprovados**, sem homologar o motor pedagógico.

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

## SIM-05 — reconciliação do broker (PR #22)

O broker atual `scripts/agent_entrypoint.py` já foi integrado e testado na `main`. A versão atual oferece `ReadOnlyAgentBroker`, perfis `tutor/coach` com START de quatro documentos e `engineer/auditor` com cinco, SHA externo confiável, checkout limpo, verificação de hashes, contexto documental e bloqueio de ações externas. As branches #11/#15 contêm versão anterior com lista de dez documentos, regras RM rígidas e API `AgentBroker` incompatível; sua composição exige métodos antigos que não existem na versão atual. As branches #12/#14 incluem snapshots de estado e documentos de governança desatualizados. Não copiar esses arquivos sobre a `main`. Os testes atuais de `tests/test_agent_entrypoint.py` já cobrem os invariantes ativos. Decisão de SIM-05: documentar a comparação, corrigir estado/handoff e manter branches originais preservadas; importar somente teste/código que demonstre lacuna funcional atual.

## SIM-06 — especificação Cognitive Gates v0.3-r2 (PR #23)

Recuperação estritamente documental da versão v0.3-r2 aprovada para especificação: PLAN, 27 CHECKS, recibo e verificador de proveniência. O aceite registrado limita-se ao plano e à derivação dos checks. O recibo registra 0/27 provas funcionais E2E, GQ-D REPROVADA, GQ-C NOT_RUN e GQ-O BLOCKED. A validação dos bytes não prova execução do Tutor/Coach. Não importar a proposta r3, não ativar gates de aprovação por mensagem e não habilitar ferramentas, credenciais ou persistência pessoal. Ver `docs/governanca/SPEC_COGNITIVE_GATES_R2.md`.

## Fila de execução

**Estados permitidos:** `planejado`, `em_andamento`, `implementado_nao_homologado`, `bloqueado`, `homologado`. A classificação é rastreável por evidência do HEAD, não percentual arbitrário.

| ID | P | Frente / gate | Estado de partida | Definition of Done |
|---|---|---|---|---|
| RM-00 | P0 | Governança, ROADMAP, START/DELIVERY | em_andamento | Bootstrap, CI e proteção main verificados; gates automáticos de entrega e teste funcional do Tutor/Coach pendentes |
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

## Repriorização proporcional dos bloqueadores (decisão do proprietário, 04/11/2026)

- O antigo gate P0 de duas Apps/atestado criptográfico do PR #10 é **opcional** para a governança de código de um harness pessoal; não é condição para orientar o estudante. Permanece documentado como alternativa de defesa aprofundada, sem homologação operacional e sem implantação.
- **RM-00** passa a requerer START/DELIVERY reproduzíveis, CI e proteção da `main` comprovadas, e gates automáticos de entrega. A eficácia funcional do Tutor/Coach depende de GP-0–GP-5 e não de Apps de administração do GitHub.
- O bloqueio de gravação pessoal em repositório público, a proibição de fingir integração com Zapia e a exigência de autorização humana para merge/alterações estruturais sensíveis permanecem. **Não** há aprovação humana exigida por mensagem de orientação ordinária.
- A reclassificação estratégica altera o contrato e sua baseline conjuntamente, com testes de regressão no mesmo commit; não promove RM-00 a `homologado` nem encerra NCs por mera declaração.

## Saneamento dos PRs e estado das dependências (04/11/2026)

- **PR #4:** encerrado sem merge por redundância verificável: seus 15 blobs coincidem exatamente com os 15 correspondentes do PR #5. O histórico permanece acessível.
- **PR #10:** encerrado sem merge como desenho de segurança avançada não implantado, inadequado como pré-requisito geral da cognição pessoal. Permanecem os riscos residuais de origem do check e privilégio administrativo; **não declarar homologação de #10**.
- **PR #9:** revisão do contrato de autonomia, RM-00 e contraprovas documentais. Head pré-checkpoint `215781e45ab3bedf458df8281fc9b83c8d60678c`, CI push [41937833645](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41937833645) e PR [41937839676](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41937839676), ambos `success`, **184 testes OK**. Não equivale a gate cognitivo funcional homologado.
- **PR #11:** permanece draft; a base agora é a branch do PR #9 para tornar explícita a dependência dos dez arquivos de START. Seu executor real, Zapia e gateway com credenciais isoladas continuam pendentes.
- **PR #5:** permanece draft; PLAN r2 aprovado apenas como especificação, proposta r3 não aprovada e 27 checks funcionais ainda `NOT_RUN`. A base antiga e a composição exigem revalidação antes de merge.
- **`main`:** inalterada. Não houve merge, implantação de App ou habilitação de gravação de dados pessoais. As alterações nesta documentação usam API GitHub, sem execução de hooks locais. O novo SHA de checkpoint e a sua CI exigem readback após publicação.

## Referências

- [AGENTS](AGENTS.md) · [Settings](settings.json) · [Handoff técnico](memory/HANDOFF.md) · [Handoff pedagógico](docs/pedagogia/HANDOFF.md)
- [Plano de implementação ENG-00–08](docs/pedagogia/PLANO_IMPLEMENTACAO_GATES_v1.8.md) · [102 critérios GP-0–GP-5](docs/pedagogia/RASTREABILIDADE_GATES_v1.8.md)
- [PR #5: Cognitive Gates](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/5) · [Auditoria histórica](docs/auditorias/AUDITORIA_BRANCHES_E_MERGES_2026-11-04.md)


## Fila de simplificação pessoal — 05/11/2026

**Finalidade:** eliminar burocracia de engenharia comercial sem sacrificar privacidade, fonte do edital, rastreabilidade, idempotência ou recuperação entre sessões. **Este bloco é a fila prioritária e operacional de saneamento.** A fila RM-00–RM-10 acima continua como backlog funcional legado até sua reconciliação; em caso de conflito de **ordem de trabalho de saneamento**, prevalece esta fila SIM. Não interpretar documento aprovado ou CI verde como funcionalidade operacional homologada.

**Próxima tarefa: SIM-06** — somente após merge comprovado do PR #22/SIM-05. SIM-06 será definida a partir das branches restantes, priorizando especificações cognitivas úteis e mantendo integrações externas fora do escopo até prova de necessidade.

**Critério de criticidade:** **ALTA** = exposição de dados, corrupção/duplicação de estado, erro oficial relevante ou escrita com efeito irreversível; **MEDIA** = continuidade, conflitos de integração, manutenção e baixa observabilidade; **BAIXA** = excesso de arquivos, branches históricas e apresentação sem dano imediato. ALTA e MEDIA demandam contraprovas negativas e CI no HEAD antes de encerramento. BAIXA exige inventário/justificativa e pode ser documentada sem bloquear uso cotidiano.

| ID | Criticidade | Problema e resultado exigido | Como executar e decisão de saída | Contraprovas exigidas / fonte de testes | Estado |
|---|---|---|---|---|---|
| SIM-01 | ALTA | Estado de visibilidade contraditório em documentos; nenhum resultado individual pode vazar | Conferir `get_repo.visibility`, reconciliar ADR-004 e documentos; testar rejeição da flag de dados; aceitar apenas leitura autenticada atual | `tests/test_write_policy.py`, `tests/test_ci_gate_contract.py`; teste: habilitação indevida deve falhar | concluido |
| SIM-02 | ALTA | Escrita por API pode burlar hooks ou perder confirmação; preservar histórico sem duplicar | Auditar cadeia PR #13→#17→#18 no HEAD real; contraprovar ACK perdido, CAS, readback de blob e cliente com token direto; consolidar só o essencial, sem alegar enforcement universal | `tests/test_api_write_guard.py`, `tests/test_ci_gate_contract.py`; ampliar E2E negativo antes da integração | concluido |
| SIM-03 | ALTA | Fonte do edital e retificações podem estar desatualizadas; datas oficiais têm inconsistência original | Manter PDF original imutável, comparar novas publicações oficiais e preservar alerta cronológico p. 13; nenhuma correção silenciosa | `tests/test_fontes_oficiais.py`, `tests/test_edital.py`; teste: alteração sem proveniência deve falhar | em_andamento |
| SIM-04 | MEDIA | Dez PRs draft/abertos e 22 branches criam frentes concorrentes e risco de merge indevido | Mapear árvore de dependências; manter #9 como fila, avaliar #9→#14→#15 e #13→#17→#18; consolidar uma entrega por capacidade, encerrar duplicados só após equivalência de blobs e testes, sem apagar branches com código exclusivo | `tests/test_ci_gate_contract.py`, `tests/test_agent_gates.py`; exigir diferença final e CI do HEAD | concluido |
| SIM-05 | MEDIA | Bootstrap de dez arquivos, inclusive edital integral, custa contexto e contradiz recuperação seletiva | Reduzir leitura por sessão a AGENTS, ROADMAP, HANDOFF e CURRENT; demais normas e chunks sob demanda; reconciliar `settings.json`, `agent_gates.py`, docs, testes e branches empilhadas no mesmo commit testado | `tests/test_agent_gates.py`, `tests/test_roadmap_gate.py`; mutantes: ordem errada, arquivo essencial ausente, edital carregado sempre | em_andamento |
| SIM-06 | MEDIA | Handoff extenso e antigos checkpoints confundem estado atual com histórico | Manter resumo vigente no topo e histórico imutável abaixo; cada entrega aponta SHA, CI, item SIM/RM, bloqueador e próximo comando; testar retomada usando só arquivos mínimos | `tests/test_agent_gates.py`, `tests/test_roadmap_gate.py`; teste: falta de próxima tarefa deve falhar | pendente |
| SIM-07 | MEDIA | Gate de orientação cognitiva misturado a operações externas bloqueia Tutor/Coach sem necessidade | Separar orientação automática de ferramentas com efeito; gatilhar consentimento por escopo para lembretes/Zapia, não por mensagem; negar envio inexistente/credencial exposta | `tests/test_write_policy.py`, `tests/test_agent_gates.py`; negativo: ferramenta não instalada não pode alegar envio | pendente |
| SIM-08 | MEDIA | Sobrecarga de gates, avaliações repetidas e docs redundantes atrasa estudo e CI | Executar suíte focada para mudança, depois CI central completa; conservar testes de privacidade, integridade do edital, estado e hooks; remover gates duplicados só com comparação antes/depois | `tests/test_ci_gate_contract.py`, `tests/test_harness.py`; teste: remoção de gate essencial deve falhar | pendente |
| SIM-09 | BAIXA | Branches antigas de PRs mesclados/fechados poluem visão, mas histórico é recuperável | Listar candidatas pós-merge e POCs; confirmar HEAD contido em `main` ou preservação no PR antes de pedir exclusão; não deletar nesta entrega | registro: `docs/auditorias/AUDITORIA_BRANCHES_E_MERGES_2026-11-04.md`; risco aceito até limpeza confirmada | documentado |
| SIM-10 | BAIXA | Múltiplos relatórios e especificações históricas não precisam ser lidos em toda sessão | Arquivar/rotular material consultivo antigo, preservar links e decisões; não eliminar conhecimento ou provas únicas | registro: `docs/pedagogia/README.md`; consultar sob demanda, sem bloquear Tutor/Coach | documentado |

### Procedimento obrigatório de retomada e entrega da fila SIM

1. **START:** identificar repositório, branch e HEAD; ler `AGENTS.md`, esta seção do `ROADMAP.md`, `memory/HANDOFF.md` e `state/CURRENT.json`. Conferir o próximo ID e dependências, **não** assumir resultados de sessões anteriores. Os demais arquivos são consultados sob demanda. A candidata SIM-05 reduz o START a quatro arquivos; CI e readback devem confirmar a implementação antes de integração à main.
2. **EXECUÇÃO:** apenas uma ação SIM de cada vez. Para ALTA/MEDIA, reproduzir contraprova negativa, corrigir, rodar testes de regressão e CI do HEAD final. Se a contraprova ainda não existe, o item continua aberto; referência a arquivo de testes não comprova execução ou cobertura.
3. **DELIVERY:** registrar no roadmap e handoff: ID, achado, antes/depois, testes realmente executados e falhas, SHA/CI e próxima ação; avançar status só com evidência. BAIXA pode permanecer `documentado`, com motivo de aceitação.
4. **Higiene:** somente fechar PR comprovadamente substituído; manter histórico no GitHub. Excluir branch somente depois de inspecionar dependentes e confirmar preservação, sem force-push nem reescrita de histórico.
5. **Antirregressão:** alteração desta fila exige atualizar seus testes de contrato no mesmo commit. O validador acusa ausência/reordenação/desclassificação ou perda de plano de teste em ALTA/MEDIA, mas não substitui auditoria funcional nem proteção administrativa.

**FOTOGRAFIA HISTÓRICA ANTERIOR AO SANEAMENTO — não usar para decidir:** `main` = `676dd5d3259c66ba97c3e7e3338451cfc4e5cd68`, protegida com check `validate`; repositório público; 22 branches, 10 PRs abertos (#5, #9, #11–#18) e 8 encerrados. São números de inventário, sujeitos a nova conferência; não usar como condição de teste permanente.


### HISTÓRICO — checkpoint SIM-05 de START leve (05/11/2026)

A candidata do PR #9 muda a carga de sessão de dez para **quatro arquivos** (`AGENTS.md`, `ROADMAP.md`, `memory/HANDOFF.md`, `state/CURRENT.json`). O edital integral segue imutável, acessível por índice/chunks sob demanda. Os 45 KB de checkpoints antigos ficam preservados em `memory/HANDOFF_ARCHIVE_2026-11-05.md`; somente o handoff vigente é lido em todo START. Exigir CI do HEAD completo, contraprovas negativas, readback remoto e reconciliação de PRs empilhados antes de declarar SIM-05 concluído. Não declarar que a mudança já chegou à `main`.


### HISTÓRICO / FOTOGRAFIA SUPERADA — inventário de branches/PRs (05/11/2026, antes do encerramento)

**FOTOGRAFIA SUPERADA, não vigente:** 22 branches; 10 PRs abertos, todos em draft; 8 PRs encerrados. Partição dos refs: 1 `main` protegida + 10 branches HEAD de PRs abertos + 5 branches de PRs já mesclados (#1, #2, #6, #7, #8) + 3 branches de PRs encerrados sem merge (#3, #4, #10) + 3 branches POC Zapia sem PR ativo. Não apagar pelo nome; confirmar HEAD, ancestralidade, dependentes e salvamento do trabalho.

**Mapa das dez propostas:**

| Cadeia ou frente | PRs abertos | Diretriz de consolidação sem perda |
|---|---|---|
| START/roadmap + saneamento documental + broker | #9 → #14 → #15; #11, #12 paralelos | Manter #9 como ponto de reforma; #14 reaplica a capacidade de #12; #15 propõe composição do broker de #11. **Os blobs dos scripts #11/#15 e #12/#14 não são idênticos**, então não fechar por suposição: comparar funcionalidade, arquivos e testes, e recongelar no novo HEAD de #9 antes de substituir os PRs isolados |
| Segurança de escrita API | #13 → #17 → #18 | Considerar somente a cadeia com correções acumuladas; testar casos negativos reais e reconciliação do HEAD; consolidar numa proposta integrada após homologação, sem merge automático de ancestrais redundantes |
| Motor cognitivo | #5 | Retomar quando os testes funcionais previstos estiverem implementados, sem usar documentação como prova de operação |
| Monitor FAPEC | #16 | Frente separada de monitoramento, sem efeitos externos indevidos; auditar idempotência, fonte e permissões antes da integração |

**Higiene segura:** primeiro obter CI e readback na candidata consolidada, depois comprovar com comparação de árvores/blobs e testes quais PRs podem ser fechados como substituídos; fechar PR não exclui branch, e exclusão só após comprovação de não dependência e preservação. As três POCs históricas e as branches de PRs mesclados são candidatas à limpeza posterior (SIM-09 BAIXA), não prioridade sobre privacidade e segurança de escrita. **Nenhum PR foi fechado ou branch removida por esta auditoria.**

**Alerta de integração:** modificar #9 altera a base lógica de #14/#15; a CI de cada HEAD antigo não valida automaticamente a composição contra o novo HEAD. Retarget/rebase e novos testes no commit efetivo são necessários. A `main` não é alterada por este inventário.


## Política permanente: uma tarefa → uma branch → um PR → um merge

**Decisão do proprietário em 05/11/2026:** é proibido desenvolver frentes em paralelo. **A única fonte do estado operacional é `state/WORKFLOW.json`**; o ROADMAP define a fila e criticidade, o HANDOFF orienta a retomada e `state/CURRENT.json` é exclusivamente a projeção de desempenho de estudos. Divergências devem bloquear a ação de engenharia até reconciliação.

**Transição excepcional:** o PR #9 é a única frente ativa, tarefa **SIM-04** (encerrar dispersão e fixar o contrato). **SIM-01** é a próxima tarefa *somente após o merge do #9*. O PR #9 possui trabalho de fases anteriores; esta exceção não autoriza novos desenvolvimentos de outros itens nesta mesma branch. Todos os demais PRs abertos em 05/11/2026 (#5, #11, #12, #13, #14, #15, #16, #17 e #18) devem ser encerrados **sem merge e com HEAD registrado** no estado para posterior recuperação sequencial. Branch histórica fechada não é branch de trabalho ativa. Não apagar ref histórico durante a transição.

**Protocolo determinístico entre sessões:**

1. **START:** ler `AGENTS.md`, `ROADMAP.md`, `memory/HANDOFF.md`, `state/CURRENT.json` e, para engenharia, `state/WORKFLOW.json` do mesmo HEAD. Executar `python scripts/single_flow_gate.py --check`; em CI há também `--remote` com listagem do GitHub. Se houver mais de um PR aberto ou PR diferente do estado, **parar e sanear**, nunca iniciar outra tarefa.
2. **TRABALHO ÚNICO:** atuar **somente** no item `active.task_id`; usar **uma única branch de trabalho e um PR draft** para todos os commits de correção e testes desse item. Não criar PR de teste, PR corretivo, PR de auditoria ou branch empilhada; revisões e contraprovas são commits na mesma branch.
3. **TESTES E GATES:** para ALTA/MEDIA, contraprovas negativas do risco, suíte focada, CI completa e readback do HEAD remoto; BAIXA pode ser documentada, sem bloqueio desnecessário. `SKIP` não é sucesso. Conclusões de CI não substituem auditoria funcional nem confirmação de privacidade.
4. **FIM DA TAREFA:** atualizar estado, ROADMAP e handoff na mesma branch. Somente após revisão/autorizações aplicáveis, checks válidos e decisão de integração, mesclar o PR na `main`. **Não iniciar a próxima tarefa enquanto a anterior não estiver efetivamente mesclada e seu estado reconciliado.**
5. **PRÓXIMO CICLO:** abrir então a próxima única branch diretamente da `main`, criar **um único PR draft** e atualizar `active` no estado. Recuperar apenas os arquivos de PRs encerrados que forem necessários, por SHA/PR histórico; nunca reabrir várias frentes.
6. **LIMPEZA:** branches históricas podem permanecer arquivadas sem PR aberto. Excluir uma branch só após conferir dependências, refs e preservação de código; não praticar `force-push`.

**Enforcement:** `scripts/single_flow_gate.py --check` valida o contrato e a coerência local; `--remote` compara a lista atual de PRs do GitHub com o único PR do estado e reprova workflow de branch concorrente. A CI observa **depois** do push: ela **não impede fisicamente** alguém com token de criar branch ou PR. Para proteção universal, manter `main` protegida e limitar credenciais e permissões; nunca confundir gate do PR com controle administrativo do GitHub.

### Ensaio adversarial do START — 05/11/2026 (SIM-04, apenas continuidade desta frente)

**Candidata ensaiada:** `8170e3771f8b29cfab51f9b4d95b3334e8cac717`. CI de push [42037230359](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/42037230359) e de PR [42037236502](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/42037236502) **success**, 215 testes. Contraprovas novas em `tests/test_start_effectiveness.py` (10) e contraprova de remoção da etapa em `tests/test_ci_gate_contract.py`. Histórico de CI é prova do checkout ensaiado; **este registro documental produzirá um SHA posterior que precisa de CI própria**.

- **Aprovado, com limite explícito:** o START comum lê quatro arquivos de bootstrap com recibo SHA-256; o novo comando `python scripts/bootstrap.py --mode engineering` exige quinto arquivo (`state/WORKFLOW.json`), valida tarefa/PR/branch e emite hashes de todos os cinco. A CI executa o START de engenharia mais a checagem remota do PR. `--mode study` continua independente do estado da engenharia.
- **Contraprovas negativas passando:** falta/corrupção de `WORKFLOW.json`, tarefa ausente da fila, arquivo obrigatório vazio, ordem incorreta e modo desconhecido resultam em falha; remoção do comando de CI também é detectada.
- **ALTA — risco remanescente:** não há prova nem controle nativo universal que obrigue qualquer sessão externa do ChatGPT, Zapia, Tutor ou Coach a chamar o START antes de responder ou escrever. Scripts/hashes provam leitura dos bytes por programa controlado, **não leitura/interpretação semântica por modelo**. Para eliminar o risco operacional, integrar futura execução real a um ponto de entrada que rejeite operações sem recibo válido; testar E2E com bypass deliberado.
- **MEDIA — risco remanescente:** hashes locais não vinculam automaticamente os arquivos ao mesmo HEAD **remoto** em clientes que buscam documentos isoladamente por API. Confirmar ref único e SHAs pelo conector em cada sessão de API. O Roadmap ainda contém fotografias históricas de PRs anteriores; a fonte vigente de trabalho é `state/WORKFLOW.json`, não os parágrafos históricos.
- **BAIXA — não bloqueante:** Roadmap longo; recuperar seção operacional e documentos adicionais sob demanda. Não eliminar histórico enquanto for fonte única de decisões.

**Decisão de fluxo:** não abrir branch nem PR novos; o PR #9 permanece tarefa SIM-04 até homologação e merge. Somente depois iniciar SIM-01. O fato de a suíte passar não significa homologação universal do START.

### Checkpoint de contraprova do broker (05/11/2026) — mesma frente SIM-04

O PR #9 incorpora um **broker local mínimo, somente leitura** em `scripts/agent_entrypoint.py`, adaptado seletivamente das propostas históricas #11/#15. Diferentemente do broker legado, usa o bootstrap vigente de **quatro arquivos para tutor/coach e cinco para engenharia/auditoria**, sem exigir a transcrição integral do edital. O broker não contém ações com efeito externo; seu método de contexto fornece textos e hashes a um futuro orquestrador de IA.

- **Candidata testada:** `7561cba812a4d5545635931594ddae2a99262c45`. CI push [42038174394](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/42038174394) e PR [42038187668](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/42038187668) **success**; **228 testes** com 12 novos casos de broker + contrato de presença na CI.
- **Negativos verificados:** sem SHA confiável, SHA Git divergente, checkout sujo, arquivo obrigatório ausente/corrompido, recibo reutilizado após alteração de bytes, symlink, papel desconhecido e ação de escrita/integração externa → **rejeição**. `model_context()` disponibiliza os textos do START validado e seus digests, mas não comprova que um LLM os compreendeu.
- **Pendência material de ALTA:** este código não é o executor implantado de Tutor/Coach, nem guarda credenciais de serviços. A eficácia universal da leitura somente poderá ser demonstrada quando um orquestrador real passar obrigatoriamente pelo broker, com contraprovas de bypass e bloqueio de tokens diretos; **não promover tal status por CI local**.
- **Transição preservada:** manter SIM-04 e PR #9 como única frente, sem abrir outro PR para retomar legado. Próxima tarefa SIM-01 somente após revisão e merge do #9. Este parágrafo produz nova revisão e requer CI própria.

### Saneamento determinístico da transição pós-merge — SIM-04 (05/11/2026)

**Não confundir fechamento com integração.** A candidata do PR #9 torna a resolução remota do ciclo explícita:

- **`active_pr`:** exatamente um PR aberto, cujo número e branch coincidem com `state/WORKFLOW.json`; só há trabalho nessa branch.
- **`awaiting_next_task`:** nenhum PR aberto, evento `push` na `main`, e consulta autenticada ao PR anterior comprova `state=closed`, `merged_at` preenchido, head/base corretos e checkpoint `phase=review` ou `merge_ready`. Neste estado, `active` é referência histórica do ciclo mesclado, e a próxima tarefa vem de `next_task_after_merge`.
- **`blocked`:** PR encerrado sem merge; PR concorrente; consulta GitHub indisponível; SHA/contexto divergente; tentativa de trabalhar em outra branch; evento desconhecido. Nenhum desses casos permite iniciar tarefa nova.
- A mensagem do `bootstrap.py` não confunde mais o ciclo local com estado remoto; a sincronização da próxima tarefa com o roadmap é obrigatória e testada.
- O handoff foi reduzido a instruções vigentes; inventários de dez PRs e cadeias antigas no histórico acima **não têm efeito de autorização**. Trabalhos exclusivos nos PRs encerrados permanecem guardados pelos SHAs.

**Critério desta entrega:** contraprovas de PR fechado sem merge, merge verdadeiro, base divergente, PR concorrente, ausência de leitura confiável, fase anterior não revisada, e compatibilidade dos testes com ciclos futuros; CI no HEAD final e readback do PR. Nenhum merge ou exclusão de branch realizado por esta correção.

### Integração legada — primeira frente SIM-01 (05/11/2026)

Após o merge comprovado do PR #9, a recuperação das 13 branches preservadas foi classificada em `docs/governanca/PLANO_RECUPERACAO_BRANCHES_20261105.md`. Uma delas já é ancestral da `main`; as 12 restantes não devem ser mescladas em bloco, pois contêm sobreposições, regras antigas e integrações sem implantação. SIM-01/PR #19 é a **única frente**; mantém a escrita de resultados pessoais proibida no repositório público, acrescenta contraprovas de vazamento do estado projetado, reconcilia ADR/handoff e encaminha API → SIM-02, FAPEC → SIM-03, broker/infra → fases posteriores. Nenhum código de cliente externo nem credencial é habilitado por esta documentação.

### SIM-02 — candidato API recuperado da cadeia #13→#17→#18 (05/11/2026)

O PR #20 é a única frente ativa; seu código deriva seletivamente da branch histórica `fix/api-postcommit-content-bound-20261105` (SHA `daec1f626c0bf43a22a565eaac3a290bc71f83c5`). Integra no PR os controles de `scripts/api_write_guard.py`, a transação `scripts/api_write_transaction.py` e seus testes, sem mesclar branches intermediárias nem substituir o bloqueio de privacidade do PR #19. O escritor permanece **opt-in** via `UFMS_ENABLE_GITHUB_WRITE=1`, requer `GH_TOKEN` no host confiável e não deve ser acionado por LLM ou por sessão sem credenciais controladas. O readback autenticado confere os bytes finais por Git blob SHA, CAS/fast-forward e dados de PR no GitHub; teste de CI sozinho não prova controle de clientes externos. A liberação operacional de escrita externa requer implantação e teste E2E próprios. **Nenhum efeito externo habilitado pela integração do código.**

### SIM-03 — sonda FAPEC recuperada (05/11/2026)

PR #21 recupera seletivamente o agendamento `.github/workflows/monitor-fapec.yml`, o teste `tests/test_monitor_fapec_schedule.py` e a nota `docs/governanca/MONITOR_FAPEC_SCHEDULE.md` da branch histórica #16. O workflow é somente leitura, usa `contents: read`, `persist-credentials: false`, nenhuma secret nem acesso a dados individuais, e não executa em push/PR. Quando integrado à `main`, poderá realizar **uma consulta pública diária** ao portal FAPEC, com `workflow_dispatch` manual. A sonda examina uma página e **não confirma ausência de retificações em outras fontes**; mudanças/inconclusões resultam em job falho para revisão humana, nunca em atualização automática do edital. O cron é UTC e execução depende do GitHub Actions. Próxima frente SIM-05 após testes e merge confirmado do PR #21.
