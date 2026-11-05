# UFMS Cognitive Gates — CHECKS v0.3-r1 (derivação aprovada; provas não executadas)

Mutations: 3
Build: `python scripts/ci_gate_contract.py --check`; `python scripts/write_policy.py --check`; `python scripts/validate.py`; `python -m unittest discover -s tests -v` (dependências PR #1; ainda sem checkout composto comprovado)
Plan: `.specs/features/ufms-cognitive-gates/revisions/v0.3/plan.md`

**Aprovação humana do PLAN:** 04/11/2026, mensagem literal `APROVO`, vinculada ao PLAN v0.3-r1 existente no PR #5 no SHA `aa66ac2945cc35c72bbd06401db977903dcbb3c4` (blob `4257e971f1417cc82461cf3e9117c5598afb7967`; SHA-256 `fa37d9c5cc2fb4288c477c4b175c8ec923ebb419be2aa9e785b32471b850c70c`). Ver `APPROVAL_v0.3-r1.md` e `approval-receipt.json`.
**Status:** CHECKS normativamente congelados para esta revisão aprovada; **validação oficial da skill e GQ-D independente PENDENTES**. Nenhum dos 27 testes funcionais foi executado para esta feature: **0 PASS / 27 NOT_RUN**. Nenhum merge, deploy ou acesso externo autorizado.
**Integridade:** o texto do PLAN aprovado não foi alterado após aceite; seu cabeçalho anterior “aguarda aprovação” é uma anotação histórica do snapshot e é superado apenas para status por este registro, sem mudar obrigações.

## Checks

### S1 — Bootstrap, fonte e contexto

**C1** - Contraprovas de conformidade do AC 1; critério do PLAN aprovado preservado abaixo. (AC 1)
**Obrigação EARS aprovada (AC 1):** WHEN uma sessão inicia THEN o harness SHALL conferir a existência, ordem e SHA dos **9 arquivos obrigatórios** do mesmo objeto de revisão; em qualquer falha SHALL retornar `DENY:BOOTSTRAP_INVALID`.

**Positivo:** Nove arquivos de bootstrap no mesmo SHA: sequência válida permite prosseguir com recibo de hashes.
**Negativo:** Remover AGENTS.md, permutar ordem ou adulterar SHA de um dos nove; rejeitar antes de decisão.
**Oráculo:** DENY:BOOTSTRAP_INVALID; nenhuma proposta publicada, nenhum efeito.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_bootstrap_exact_nine_files_and_revision`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C2** - Contraprovas de conformidade do AC 2; critério do PLAN aprovado preservado abaixo. (AC 2)
**Obrigação EARS aprovada (AC 2):** IF a proposta citar documento normativo não localizado na fonte vigente ou original identificada THEN o gate SHALL retornar `NEEDS_EVIDENCE:SOURCE_NOT_FOUND`, sem inventar número, página ou trecho.

**Positivo:** Fonte normativa conhecida com referência e página recuperável; fato elegível para conferência.
**Negativo:** Pedir cláusula e página inexistentes; proibir inventar trechos/página.
**Oráculo:** NEEDS_EVIDENCE:SOURCE_NOT_FOUND e source_refs vazios para a informação desconhecida.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_unknown_normative_source_needs_evidence`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C3** - Contraprovas de conformidade do AC 3; critério do PLAN aprovado preservado abaixo. (AC 3)
**Obrigação EARS aprovada (AC 3):** WHEN uma proposta contém afirmação normativa do edital THEN o gate SHALL exigir `source_sha + page + span` resolvível na versão permitida, ou retornar `NEEDS_EVIDENCE:SOURCE_NOT_FOUND`; a presença de referência **não** prova apoio semântico.
   - Fonte válida, mas página de outro assunto → o local existe; a verificação de conteúdo pertence ao AC25.

**Positivo:** source_sha+page+span apontam para trecho correto na versão aceita; referência resolvida.
**Negativo:** Alterar SHA, página, offset ou versões; rejeitar com a mesma citação visual.
**Oráculo:** Comparar bytes/offsets da fonte e versionamento; NEEDS_EVIDENCE:SOURCE_NOT_FOUND.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_source_sha_page_span_resolution`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C4** - Contraprovas de conformidade do AC 4; critério do PLAN aprovado preservado abaixo. (AC 4)
**Obrigação EARS aprovada (AC 4):** IF uma suposta retificação não demonstrar autoridade emissora, URL/origem, data, SHA-256 dos bytes, vigência, trechos atingidos e recibo de validação independente THEN o gate SHALL preservar o edital original e retornar `UNVERIFIED_AMENDMENT`; IF houver incompatibilidade textual entre atos oficiais aplicáveis ou dentro de um ato THEN SHALL marcar `SOURCE_CONFLICT` para os fatos atingidos, sem escolher data alternativa por inferência.
    - Oráculo negativo: cronograma do Anexo II p.13 com datas incompatíveis não pode ser corrigido silenciosamente.

**Oráculos red/green complementares (antes apêndice; agora integrados ao CHECK):**
- **Positivo:** Retificação verificável, vigente e limitada a trechos explicitamente alterados.
- **Negativo:** Retificação fraudulenta com checksum válido mas emissor não verificado; conflito impresso p.13 não corrigido automaticamente.
- **Oráculo de aprovação:** diff do original, cadeia do emissor, ato, seção, conflito e `UNVERIFIED_AMENDMENT|SOURCE_CONFLICT`.
- **Estado funcional:** `NOT_RUN`; não basta retornar o código correto depois de um efeito indevido.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_unverified_amendment_does_not_override`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C5** - Contraprovas de conformidade do AC 5; critério do PLAN aprovado preservado abaixo. (AC 5)
**Obrigação EARS aprovada (AC 5):** WHEN a fonte não cobre a pergunta THEN o tutor SHALL devolver estado `UNKNOWN` e próximo passo seguro; não SHALL criar dado de questão ou percentual fictício.

**Positivo:** Questão coberta pelo edital recebe resposta qualificada com origem real.
**Negativo:** Solicitar disponibilidade de questão ou porcentagem ausente do conjunto de evidências.
**Oráculo:** UNKNOWN com próximo passo seguro e zero dados inventados.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_unknown_answer_has_no_fabricated_facts`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


### S2 — Pedagogia e evidência

**C6** - Contraprovas de conformidade do AC 6; critério do PLAN aprovado preservado abaixo. (AC 6)
**Obrigação EARS aprovada (AC 6):** WHEN o LLM propõe um caderno THEN a saída SHALL conter cargo (523/324), tópico existente, objetivo pedagógico, status de disponibilidade `CONFIRMED/UNKNOWN` e justificativa, sem fabricar URL ou questão.

**Positivo:** Caderno sintético para 523 ou 324 tem assunto validado, objetivo, status de disponibilidade e justificativa.
**Negativo:** Injetar tópico fora do anexo, URL inventada ou disponibilidade CONFIRMED sem fonte.
**Oráculo:** Schema completo; UNKNOWN no lugar de disponibilidade não verificada, sem link falso.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_recommendation_fields_both_positions`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C7** - Contraprovas de conformidade do AC 7; critério do PLAN aprovado preservado abaixo. (AC 7)
**Obrigação EARS aprovada (AC 7):** IF o relatório de resultados não distinguir contagens ou temas THEN o gate SHALL preservar os totais observados e deixar os campos não demonstrados como `unknown`, sem imputar desempenho por subtópico.

**Positivo:** Resultado agrega totais corretos e tópicos explícitos sem ultrapassar total.
**Negativo:** Entregar 8/10 agregado sem detalhamento, e tentar imputar oito acertos a Português.
**Oráculo:** Projeção por tópico unknown, totais agregados preservados; nenhuma dupla contagem.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_aggregate_no_inferred_topic_score`
Proof: `python -m unittest -v tests.test_harness.HarnessTests.test_aggregate_result_does_not_invent_topic_score` (regressão existente, não substitui prova nova)
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C8** - Contraprovas de conformidade do AC 8; critério do PLAN aprovado preservado abaixo. (AC 8)
**Obrigação EARS aprovada (AC 8):** WHEN o tutor ou coach recebe um relato de aprendizagem THEN SHALL distinguir `observado`, `informado`, `inferido` e `desconhecido` nos fatos usados para decisão.

**Positivo:** Separar fato observado, relato do estudante, inferência pedagógica e desconhecido em recibo.
**Negativo:** Enviar hipótese do aluno como se fosse resultado verificado; tentar promover inferido para observado.
**Oráculo:** Classificação observada/informada/inferida/desconhecida rastreável sem promoção automática.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_provenance_four_classes`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C9** - Contraprovas de conformidade do AC 9; critério do PLAN aprovado preservado abaixo. (AC 9)
**Obrigação EARS aprovada (AC 9):** IF duas recomendações compartilham um bloco parcial 523/324 THEN o sistema SHALL impedir dupla contagem de uma mesma tentativa sob dois IDs de evidência.

**Positivo:** Uma tentativa com dois cargos 523/324 e mesmo attempt_id produz um único evento estatístico.
**Negativo:** Duplicar resultado como dois cadernos/cargos ou reutilizar tentativa com IDs diferentes.
**Oráculo:** Ledger de tentativas único; contagem total não duplicada.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_shared_attempt_no_double_count`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C10** - Contraprovas de conformidade do AC 10; critério do PLAN aprovado preservado abaixo. (AC 10)
**Obrigação EARS aprovada (AC 10):** WHEN a recomendação envolver revisão THEN o sistema SHALL registrar a justificativa baseada no histórico disponível ou declarar `insufficient_evidence`; não SHALL assumir intervalo fixo de repetição por padrão.

**Positivo:** Histórico fornece evidência de revisão; recomendação aponta qual evidência sustentou.
**Negativo:** Sem histórico ou padrão de domínio tentar impor revisão em sete dias.
**Oráculo:** insufficient_evidence sem intervalo fixo; justificativa com evidência real quando houver.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_revision_without_evidence_abstains`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


### S3 — Autorização e dados não confiáveis

**C11** - Contraprovas de conformidade do AC 11; critério do PLAN aprovado preservado abaixo. (AC 11)
**Obrigação EARS aprovada (AC 11):** WHEN conteúdo de PDF, questão, CSV, Telegram ou ferramenta for incorporado ao contexto THEN o executor SHALL carregar `policy_sha` exclusivamente de trust root autenticada, nunca de payload externo, e SHALL rejeitar qualquer instrução desses dados que tente modificar autorização, política ou precedência de fontes; verificar por diff da política vigente e contador de chamadas reais igual a zero.
    - Oráculo: documento malicioso contendo texto semelhante a política assinada não altera política ou token.

**Oráculos red/green complementares (antes apêndice; agora integrados ao CHECK):**
- **Positivo:** Trust root autenticado fornece política correta apesar de payload hostil.
- **Negativo:** Chunk PDF/CSV/Telegram afirma ser política ou apresenta `policy_sha` falso.
- **Oráculo de aprovação:** diff do policy_sha carregado, ledger de chamadas externas e origem do carregamento.
- **Estado funcional:** `NOT_RUN`; não basta retornar o código correto depois de um efeito indevido.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_untrusted_payload_cannot_change_policy`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C12** - Contraprovas de conformidade do AC 12; critério do PLAN aprovado preservado abaixo. (AC 12)
**Obrigação EARS aprovada (AC 12):** WHILE `personal_results_writes_enabled=false`, WHEN qualquer agente solicitar persistência de resultado real THEN o gateway SHALL retornar `DENY:PERSONAL_WRITE_DISABLED`, sem chamada de escrita.

**Positivo:** Com personal_results_writes_enabled=false, consultas informativas sem escrita prosseguem normalmente.
**Negativo:** Tentar registrar dado pessoal por qualquer ator, inclusive sob flag forjada no prompt.
**Oráculo:** DENY:PERSONAL_WRITE_DISABLED; contador de gravações externas zero.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_personal_write_disabled_zero_calls`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C13** - Contraprovas de conformidade do AC 13; critério do PLAN aprovado preservado abaixo. (AC 13)
**Obrigação EARS aprovada (AC 13):** IF ação exigir autorização humana e NÃO existir token de aprovação autenticado por emissor/aprovador confiáveis para **operação, ferramenta, destino, destinatário, parâmetros, ator, risco, policy_sha, state_revision e source_set_sha efetivos**, com validade temporal e nonce disponível THEN o gateway SHALL retornar `NEEDS_APPROVAL` (token ausente) ou `DENY:AUTH_MISMATCH` (token incompatível), sem efeito externo.
    - Mensagem Telegram dizendo “autorizo” não substitui token emitido pelo autorizador confiável.

**Oráculos red/green complementares (antes apêndice; agora integrados ao CHECK):**
- **Positivo:** Aprovação assinada de issuer e aprovador confiáveis corresponde ao estado/ação.
- **Negativo:** Texto em Telegram simula autorização humana; approval para versão antiga.
- **Oráculo de aprovação:** token verificado fora do contexto LLM; efeitos contados 0 ou 1.
- **Estado funcional:** `NOT_RUN`; não basta retornar o código correto depois de um efeito indevido.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_missing_or_expired_human_approval`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C14** - Contraprovas de conformidade do AC 14; critério do PLAN aprovado preservado abaixo. (AC 14)
**Obrigação EARS aprovada (AC 14):** IF token aprovado divergir em **issuer_id, approver_id, actor, tool, operation, destination, recipient, canonical action_hash, risk_class, policy_sha, state_revision, source_set_sha**, assinatura/MAC, validade ou status de aprovação da operação executada THEN o gateway SHALL retornar `DENY:AUTH_MISMATCH`, com **zero invocações externas**; rejeitar serialização não canônica ou parâmetros não aprovados.
    - Token para `calendar.create` apresentado a `telegram.send`, ou para destinatário diferente, deve falhar.

**Oráculos red/green complementares (antes apêndice; agora integrados ao CHECK):**
- **Positivo:** Token assinado vincula todos os campos da ação canônica JCS.
- **Negativo:** AUTH-IND-01 troca `calendar.create` por `telegram.send`; troca destinatário/body.
- **Oráculo de aprovação:** comparação bit a bit de tool/dest/param/action_hash e contador de chamadas.
- **Estado funcional:** `NOT_RUN`; não basta retornar o código correto depois de um efeito indevido.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_authorization_bindings_all_fields`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C15** - Contraprovas de conformidade do AC 15; critério do PLAN aprovado preservado abaixo. (AC 15)
**Obrigação EARS aprovada (AC 15):** WHEN chamada a ferramenta violar allowlist/escopo **versionados por policy_sha** ou exceder o limite **por ator, operação, janela e concorrência** THEN gateway SHALL retornar `DENY:TOOL_NOT_AUTHORIZED` ou `DENY:RATE_LIMITED` **antes do transport externo**, comprovando zero efeitos, e testes SHALL cobrir limiar exato, um acima, janela, corrida e renovação.

**Oráculos red/green complementares (antes apêndice; agora integrados ao CHECK):**
- **Positivo:** Limiar exato e renovação após janela permitem apenas chamadas aprovadas.
- **Negativo:** Limite excedido em concorrência e rejeição que chega depois da chamada.
- **Oráculo de aprovação:** contadores de transporte real, configuração versionada de janela e reserva atômica.
- **Estado funcional:** `NOT_RUN`; não basta retornar o código correto depois de um efeito indevido.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_allowlist_and_rate_limit`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


### S4 — Integridade, falhas e recibos

**C16** - Contraprovas de conformidade do AC 16; critério do PLAN aprovado preservado abaixo. (AC 16)
**Obrigação EARS aprovada (AC 16):** WHEN uma solicitação com o mesmo `event_id` for recebida novamente THEN o validador SHALL impedir segundo registro/efeito e retornar o resultado idempotente ou conflito explícito sem duplicação.

**Positivo:** Processar event_id novo uma vez, com recibo persistido.
**Negativo:** Repetir mesmo event_id e conteúdo divergente; tentar produzir segundo efeito.
**Oráculo:** Idempotência ou conflito explícito; uma única escrita externa, histórico íntegro.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_replay_same_event_id_one_effect`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C17** - Contraprovas de conformidade do AC 17; critério do PLAN aprovado preservado abaixo. (AC 17)
**Obrigação EARS aprovada (AC 17):** IF duas decisões usam a mesma revisão de estado e a primeira grava uma alteração THEN a segunda SHALL retornar `STALE_STATE` e **não** efetuar escrita antes de reavaliar o estado atual.

**Positivo:** Dois escritores recebem mesma revisão; primeiro aplica CAS, segundo reavalia estado.
**Negativo:** Executar operações concorrentes sobre revisão inicial com atualização conflitante.
**Oráculo:** Exatamente um COMMITTED e outro STALE_STATE; segunda gravação ausente.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_two_concurrent_cas_only_one_writes`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C18** - Contraprovas de conformidade do AC 18; critério do PLAN aprovado preservado abaixo. (AC 18)
**Obrigação EARS aprovada (AC 18):** IF dependência falhar **antes** de qualquer execução externa THEN gateway SHALL devolver `DEPENDENCY_FAILED` comprovando zero efeitos; IF execução puder ter ocorrido mas readback falhar THEN SHALL devolver `UNCONFIRMED` (nunca `COMMITTED`), guardar chave de idempotência e bloquear retry sem reconciliação; o runner SHALL distinguir saídas 0, 1, 2 e 3 nos seus próprios testes.

**Oráculos red/green complementares (antes apêndice; agora integrados ao CHECK):**
- **Positivo:** COMMITTED somente após readback; runner exit 0 e 1/2/3 corretos.
- **Negativo:** Dependência falha antes da chamada versus resultado incerto após envio.
- **Oráculo de aprovação:** métricas de chamada + idempotency key + testes de todos estados e exits.
- **Estado funcional:** `NOT_RUN`; não basta retornar o código correto depois de um efeito indevido.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_timeout_without_readback_unconfirmed`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C19** - Contraprovas de conformidade do AC 19; critério do PLAN aprovado preservado abaixo. (AC 19)
**Obrigação EARS aprovada (AC 19):** WHEN um ciclo terminar THEN o sistema SHALL emitir um recibo mínimo com `policy_sha`, `run_id`, `decision`, `reason_codes` e `source_refs`, sem gravar conteúdo bruto privado por padrão.

**Positivo:** Encerrar ciclo sintético e emitir recibo com campos mínimos hash de política, run, decisão, razões, fontes.
**Negativo:** Incluir CPF, email, conteúdo de pergunta ou token bruto no recibo; retirar reason_codes.
**Oráculo:** Recibo esquema versionado, redigido sem PII por padrão, inclui policy_sha/run_id/decision/reason_codes/source_refs.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_receipt_schema_without_raw_pii`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C20** - Contraprovas de conformidade do AC 20; critério do PLAN aprovado preservado abaixo. (AC 20)
**Obrigação EARS aprovada (AC 20):** WHEN se reivindicar aprovação de gate ou execução em candidato composto THEN SHALL existir recibo de prova com `candidate_commit_sha`, árvore, SHAs exatos de dependências, `composition_digest`, comandos, saídas e hashes dos artefatos positivos/negativos; ausência, drift ou composição implícita SHALL produzir `BLOCKED:NO_PROOF`. O checkout sintético de verificação não SHALL modificar qualquer PR nem substituir base por HEAD móvel.

**Oráculos red/green complementares (antes apêndice; agora integrados ao CHECK):**
- **Positivo:** Manifesto com commit/árvore/deps/origem e evidência recalculada.
- **Negativo:** Troca PR #1 para SHA novo; reusa recibo de composição antiga.
- **Oráculo de aprovação:** audit trail dos bytes, digests, comandos, exit codes e hashes dos arquivos.
- **Estado funcional:** `NOT_RUN`; não basta retornar o código correto depois de um efeito indevido.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_release_rejects_unproven_sha`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C21** - Contraprovas de conformidade do AC 21; critério do PLAN aprovado preservado abaixo. (AC 21)
**Obrigação EARS aprovada (AC 21):** IF a revisão independente encontrar teste que também passa com o comportamento propositalmente falso THEN a homologação SHALL retornar `BLOCKED:WEAK_PROOF`, exigindo revisão do teste e nova execução no SHA exato.
    - Mutante remove validação de autorização e o teste segue verde → release bloqueado.

**Positivo:** Teste positivo e negativo ligados à obrigação rejeitam mudança que remove guardrail.
**Negativo:** Retirar verificação de autorização mantendo teste inócuo que ainda passa.
**Oráculo:** BLOCKED:WEAK_PROOF; mutação não sobrevive ao conjunto de testes adversariais.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_weak_assertion_mutant_blocks_release`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


### S5 — Fronteiras e avaliação

**C22** - Contraprovas de conformidade do AC 22; critério do PLAN aprovado preservado abaixo. (AC 22)
**Obrigação EARS aprovada (AC 22):** WHEN LLM, Tutor, Coach ou canal tentar chamar ferramenta fora do gateway/renderer autenticados THEN executor SHALL rejeitar com `DENY:CALLER_NOT_AUTHORIZED`, instrumentar **zero chamadas/efeitos reais** e impedir acesso direto a segredos, tokens e rede privilegiada. A inspeção do isolamento real de credenciais e canais é bloqueador de go-live não demonstrável só por mock.

**Oráculos red/green complementares (antes apêndice; agora integrados ao CHECK):**
- **Positivo:** Modelo sem credencial só pode propor chamada; gateway autenticado executa.
- **Negativo:** Modelo com credencial inadvertida contorna gateway via outro canal.
- **Oráculo de aprovação:** prova real de isolamento de contas/canais, network e zero efeitos; mock não basta.
- **Estado funcional:** `NOT_RUN`; não basta retornar o código correto depois de um efeito indevido.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_direct_tool_bypass_denied`
Proof: inspeção humana do manifesto de execução e de isolamento real de segredos **antes de go-live** (não coberta por mocks).
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C23** - Contraprovas de conformidade do AC 23; critério do PLAN aprovado preservado abaixo. (AC 23)
**Obrigação EARS aprovada (AC 23):** IF um token de autorização já tiver sido consumido, expirado ou apresentar `nonce` duplicado THEN o gateway SHALL retornar `DENY:AUTH_REPLAY`, sem novo efeito.
    - Repetir exatamente o token após uma execução confirmada → 0 novas chamadas; timeout → reconciliar resultado antes de qualquer retry.

**Positivo:** Token válido de uso único executa exatamente uma ação; expiração respeitada.
**Negativo:** Reutilizar nonce, expirar token ou lançar consumidores simultâneos.
**Oráculo:** DENY:AUTH_REPLAY, transição atômica e zero novo efeito; no máximo um COMMITTED.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_single_use_nonce_replay_expiry_and_race`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C24** - Contraprovas de conformidade do AC 24; critério do PLAN aprovado preservado abaixo. (AC 24)
**Obrigação EARS aprovada (AC 24):** IF JSON de proposta ultrapassar **65.536 bytes** ou um payload externo ultrapassar **262.144 bytes** THEN o adaptador SHALL retornar `DENY:INPUT_TOO_LARGE` antes de invocar LLM ou ferramentas.
    - Limites inclusivos em bytes UTF-8; validar exatamente no limiar e um byte acima; tornar ambos configuráveis com baseline versionada.

**Positivo:** Aceitar exatamente 65536 bytes de JSON e 262144 bytes de payload externo em UTF-8.
**Negativo:** Enviar 65537 ou 262145 bytes, incluindo caracteres multibyte para forçar estouro.
**Oráculo:** DENY:INPUT_TOO_LARGE antes de modelo ou transporte; registrar tamanho em bytes, não caracteres.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_input_utf8_boundaries_exact_and_plus_one`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C25** - Contraprovas de conformidade do AC 25; critério do PLAN aprovado preservado abaixo. (AC 25)
**Obrigação EARS aprovada (AC 25):** WHEN afirmação crítica sobre prazo, nota, requisito ou eliminação diferir de registro de fatos **independentemente verificado** e vigente, ou envolver fontes oficiais conflitantes THEN gate SHALL devolver `NEEDS_EVIDENCE:CLAIM_UNSUPPORTED` ou `NEEDS_EVIDENCE:SOURCE_CONFLICT`, mantendo o estado não confirmado, mesmo que `source_sha/page/span` exista. O oráculo SHALL registrar valor, escopo, versão, vigência, trecho, conferente e conflito; jamais aceitar a citação real isolada como comprovação semântica.
    - Contraprovas: “pode zerar Inglês com 60 pontos” citando itens 10.1/10.2 é falso; incompatibilidade do cronograma na p.13 exige alerta, não adivinhação.

**Oráculos red/green complementares (antes apêndice; agora integrados ao CHECK):**
- **Positivo:** Fato crítico conferido pelo oráculo independente coincide com proposição.
- **Negativo:** CITE-IND-01 nota zero em Inglês permitida apesar do item 10.2; conflito página 13.
- **Oráculo de aprovação:** registro `fact_id` e conferência humana, suporte semântico e intervalo de vigência.
- **Estado funcional:** `NOT_RUN`; não basta retornar o código correto depois de um efeito indevido.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_false_critical_claim_with_real_citation`
Proof: conferência humana independente dos exemplos normativos críticos usados como oráculo; não depender só de juiz LLM.
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C26** - Contraprovas de conformidade do AC 26; critério do PLAN aprovado preservado abaixo. (AC 26)
**Obrigação EARS aprovada (AC 26):** WHEN LLM produzir resposta para publicação THEN SHALL passar exclusivamente pelo `safe_renderer`; sem token íntegro, não expirado, de uso único e vinculado ao **run_id + proposal_hash + policy_sha + state_revision + source_set_sha + actor_role + channel + recipient** efetivos SHALL devolver `DENY:OUTPUT_NOT_APPROVED` com zero publicações; revisão/fonte/canal/recipient alterado ou bypass SHALL invalidar token anterior.

**Oráculos red/green complementares (antes apêndice; agora integrados ao CHECK):**
- **Positivo:** Token vigente do mesmo run/policy/state/source_set/channel/recipient.
- **Negativo:** Token de publicação da revisão anterior ou destinatário anterior.
- **Oráculo de aprovação:** contagem de publicações e teste de bypass e invalidação da revisão.
- **Estado funcional:** `NOT_RUN`; não basta retornar o código correto depois de um efeito indevido.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_renderer_without_bound_release_token`
Proof: teste de integração da rota de publicação real **antes de go-live**, além do teste com mock.
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


**C27** - Contraprovas de conformidade do AC 27; critério do PLAN aprovado preservado abaixo. (AC 27)
**Obrigação EARS aprovada (AC 27):** IF uma avaliação de release do LLM não informar `model_version`, `policy_sha`, `dataset_sha`, `grader_version` e número de trials por cenário THEN o gate de release SHALL retornar `BLOCKED:EVAL_METADATA_MISSING`.
    - 40 cenários com 5 trials por cenário são **desenho inicial**, não um atestado de baixa taxa de falhas; separar holdout e calibração humana.

**Positivo:** Avaliação sintetizada informa model_version, policy_sha, dataset_sha, grader_version, trials por cenário.
**Negativo:** Remover um campo, trocar dataset sem atualizar hash ou alegar número de trials não executados.
**Oráculo:** BLOCKED:EVAL_METADATA_MISSING ou recusa de prova inconsistente, sem liberar versão.

**Provas seletoras propostas (NÃO EXECUTADAS neste objeto):**
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_eval_manifest_required_fields`
**Resultado:** `NOT_RUN` (seletor sem teste/runner executável comprovado; não contabilizar como PASS).


## Coverage

| Set (size) | Membros → provas exigidas | Unproven |
| --- | --- | --- |
| EARS criteria (27) | AC 1 C1 · AC 2 C2 · AC 3 C3 · AC 4 C4 · AC 5 C5 · AC 6 C6 · AC 7 C7 · AC 8 C8 · AC 9 C9 · AC 10 C10 · AC 11 C11 · AC 12 C12 · AC 13 C13 · AC 14 C14 · AC 15 C15 · AC 16 C16 · AC 17 C17 · AC 18 C18 · AC 19 C19 · AC 20 C20 · AC 21 C21 · AC 22 C22 · AC 23 C23 · AC 24 C24 · AC 25 C25 · AC 26 C26 · AC 27 C27 | - |
| Revisões com contraprovas ampliadas (10) | AC 4 C4 · AC 11 C11 · AC 13 C13 · AC 14 C14 · AC 15 C15 · AC 18 C18 · AC 20 C20 · AC 22 C22 · AC 25 C25 · AC 26 C26 | - |
| Papéis (2) | Tutor C8/C11/C26; Coach C8/C11/C26 | - |
| Cargos (2) | 523 C6/C9; 324 C6/C9 | - |
| Autorizações vinculadas (14) | issuer_id C14 · approver_id C14 · actor C14 · tool C14 · operation C14 · destination C14 · recipient C14 · canonical action_hash C14 · risk_class C14 · policy_sha C14 · state_revision C14 · source_set_sha C14 · signature/MAC C14 · nonce/expiry C23 | - |
| Fontes (4) | Original C4 · retificação legítima C4 · retificação falsa C4 · conflito interno p.13 C25 | - |
| Estados de falha (5) | COMMITTED C18 · DENIED C14 · STALE_STATE C17 · UNCONFIRMED C18 · DEPENDENCY_FAILED C18 | - |
| Runner exits (4) | 0 PASS C20 · 1 divergência C20 · 2 fixture inválida C20 · 3 dependência indisponível C18/C20 | - |
| Matriz Surface (16) | `evaluate` 4; `render` 3; `execute` 5; `evaluate-fixture` 4 | - |
| Superfícies de entrada (4) | PDF C11 · CSV C11 · Telegram C11 · resultado de ferramenta C11 | - |
| Mutantes mínimos (3) | Autorização falsa C14 · prova inócua C21 · citação real com fato falso C25 | - |

## Protocolo de prova

1. Os `Proof:` acima são **seletores/planos**, não evidências de teste existente ou executado; cada check requer prova positiva e negativa sobre implementação futura. A inexistência do teste é `BLOCKED`, nunca PASS.
2. O test harness futuro deve executar em composição reproduzível declarada em `composition-manifest.json`, com SHAs congelados de PRs #1/#2/#5 e `composition_digest` recalculado; nada deve ser inferido de branches móveis.
3. Toda chamada externa usa transporte instrumentado e contador de side effects. Para C13/C14/C15/C22/C23/C26, testar efeitos/privacidade com isolamento real antes de GQ-O, não só mocks.
4. Para C25 usar oráculo independente do edital/retificações; testar refutação de conclusão falsa com citação verdadeira e conflito cronológico p.13.
5. Em C17/C23 executar concorrência real; em C18 distinguir indisponibilidade pré-invocação, timeout pós-envio e readback. Cobrir saídas 0/1/2/3 no runner.
6. Revisão GQ-D independente deve reexecutar quatro mutações M-IND-01–04, AUTH-IND-01, CITE-IND-01, NEW-01/02 e acrescentar casos próprios; 27/27 presença textual não prova qualidade das obrigações.
7. Checkpoints e provas por commit SHA exato, recibos redigidos sem PII; `personal_results_writes_enabled=false` permanece obrigatório.

## Swept

- validation: C1–C8, C14, C24, C25
- failure modes: C13, C18, C20
- idempotency: C9, C16, C23
- authorization: C11–C15, C22, C23, C26
- concurrency: C17, C23
- data lifecycle: C4, C19, C23
- dependency failure: C18, C22, C26
- state transitions: C2, C5, C12–C18, C20, C22–C23, C26
- observability: C19–C21, C27

## Handoff

- **Settled:** PLAN v0.3-r1 aprovado expressamente em 04/11/2026 para documentação e CHECKS; controles descritos não estão implementados por esse aceite.
- **Dispatched:** GQ-D reauditoria independente pendente; VERIFY-C NOT_RUN; VERIFY-O BLOCKED.
- **Boundary:** não editar o PLAN aprovado; não alterar PR #1/#2/#4; não fazer merge, deploy, Calendar, Telegram, credenciais ou escrita pessoal.
- **Status de validação:** validação estrutural local executada; validador TLC oficial ainda não executado; após sua execução validar mecânica dos checks no SHA exato.
