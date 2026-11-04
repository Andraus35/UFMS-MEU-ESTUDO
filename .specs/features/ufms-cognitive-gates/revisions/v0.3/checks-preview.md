> **Leitura correta:** as seções históricas C1–C27 preservam seletores da v0.2, mas os **10 deltas ao final têm precedência documental nesta proposta**, sem congelá-los. Qualquer inconsistência entre resumo histórico e delta obriga harmonização após aprovação v0.3.

> **PREVIEW NÃO APROVADO.** Derivado do PLAN v0.3 candidato, que altera critérios AC04/11/13/14/15/18/20/22/25/26. O `checks.md` de v0.2 permanece congelado; **nenhum CHECK v0.3 está aprovado ou funcionalmente PASS**. Nenhum `Proof:` abaixo representa arquivo existente ou prova executada, salvo auditoria documental claramente identificada.

# UFMS Cognitive Gates — CHECKS v0.3 PREVIEW (não homologado)

Mutations: 3
Build: `python scripts/ci_gate_contract.py --check`; `python scripts/write_policy.py --check`; `python scripts/validate.py`; `python -m unittest discover -s tests -v`
Plan: `.specs/features/ufms-cognitive-gates/revisions/v0.3/plan.md` (referência candidata; r1 local ainda não publicada)

**Phase:** CHECKS v0.3 PREVIEW — NOVO PLAN AGUARDA APROVAÇÃO. CHECKS v0.2 permaneceram aprovados apenas como derivação histórica. **Proofs abaixo são seletores a implementar, NÃO resultados de testes.** O conjunto ainda aguarda `validate_checks.py` oficial e execução em checkout do HEAD. Não autoriza push, deploy, merge ou dados pessoais.

**Scope:** 27 checks em 5 slices · 4 one-way doors aprovadas no PLAN · 0 claims demonstradas pelo novo harness · 1 bloqueio operacional para go-live (segredos/nonce/TTL/retention). Os checks só se tornam obrigações congeladas depois da validação oficial.

## Checks

### S1 - Bootstrap, fonte e contexto

**C1** - O bootstrap de nove arquivos recusa ausência, ordem ou SHA divergente com `DENY:BOOTSTRAP_INVALID`. (AC 1)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_bootstrap_exact_nine_files_and_revision`

**C2** - Fonte normativa não localizada produz `NEEDS_EVIDENCE:SOURCE_NOT_FOUND`, sem página ou citação inventada. (AC 2)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_unknown_normative_source_needs_evidence`

**C3** - Afirmação normativa exige `source_sha`, página e span resolvíveis na versão aceita; caso contrário `SOURCE_NOT_FOUND`. (AC 3)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_source_sha_page_span_resolution`

**C4** - Retificação sem proveniência válida não altera o original e preserva `UNVERIFIED_AMENDMENT`. (AC 4)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_unverified_amendment_does_not_override`

**C5** - Falta de evidência devolve `UNKNOWN` e passo seguro, sem gerar questão nem pontuação falsa. (AC 5)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_unknown_answer_has_no_fabricated_facts`


### S2 - Qualidade e evidência pedagógica

**C6** - Recomendação apresenta cargo 523/324, tópico válido, objetivo, disponibilidade `CONFIRMED|UNKNOWN` e justificativa. (AC 6)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_recommendation_fields_both_positions`

**C7** - Resultado agregado não distribui acertos por tópico sem discriminação de origem; usa `unknown`. (AC 7)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_aggregate_no_inferred_topic_score`
Proof: `python -m unittest -v tests.test_harness.HarnessTests.test_aggregate_result_does_not_invent_topic_score` (regressão existente, não substitui prova nova)

**C8** - Proveniência é classificada em `observado|informado|inferido|desconhecido` sem promoção automática. (AC 8)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_provenance_four_classes`

**C9** - Uma mesma tentativa compartilhada 523/324 conta como uma observação, não duas. (AC 9)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_shared_attempt_no_double_count`

**C10** - Revisão informa justificativa sustentada ou `insufficient_evidence`; sem intervalo padrão inventado. (AC 10)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_revision_without_evidence_abstains`


### S3 - Autorização e dados não confiáveis

**C11** - PDF, CSV, ferramenta e Telegram não substituem política nem autorizam efeitos; `policy_sha` permanece confiável. (AC 11)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_untrusted_payload_cannot_change_policy`

**C12** - Com escrita pessoal desabilitada, `DENY:PERSONAL_WRITE_DISABLED` ocorre antes de chamada externa (0 chamadas). (AC 12)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_personal_write_disabled_zero_calls`

**C13** - Sem aprovação da ação e revisão exatas, `NEEDS_APPROVAL` e zero efeitos. (AC 13)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_missing_or_expired_human_approval`

**C14** - Ator, `action_hash`, revisão e `policy_sha` divergentes produzem `DENY:AUTH_MISMATCH` e zero chamadas. (AC 14)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_authorization_bindings_all_fields`

**C15** - Ferramenta fora da allowlist ou acima do limite devolve `DENY:TOOL_NOT_AUTHORIZED`/`DENY:RATE_LIMITED`. (AC 15)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_allowlist_and_rate_limit`


### S4 - Integridade e prova

**C16** - Mesmo `event_id` não produz segundo efeito; replay idempotente ou conflito explícito. (AC 16)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_replay_same_event_id_one_effect`

**C17** - Duas decisões sobre revisão antiga: somente a primeira escreve; a segunda retorna `STALE_STATE`. (AC 17)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_two_concurrent_cas_only_one_writes`

**C18** - Timeout sem readback devolve `UNCONFIRMED`, conserva idempotência e bloqueia retry sem reconciliação. (AC 18)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_timeout_without_readback_unconfirmed`

**C19** - Recibo inclui `policy_sha`, `run_id`, `decision`, `reason_codes`, `source_refs` e nenhuma PII bruta por padrão. (AC 19)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_receipt_schema_without_raw_pii`

**C20** - Sem provas positivas e negativas vinculadas ao commit exato, release é `BLOCKED:NO_PROOF`. (AC 20)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_release_rejects_unproven_sha`

**C21** - Mutante de controle de autorização que sobreviva aos testes gera `BLOCKED:WEAK_PROOF`. (AC 21)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_weak_assertion_mutant_blocks_release`


### S5 - Fronteiras e avaliação

**C22** - Chamada direta à ferramenta por ator não-gateway retorna `DENY:CALLER_NOT_AUTHORIZED` e zero chamadas. (AC 22)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_direct_tool_bypass_denied`
Proof: inspeção humana do manifesto de execução e de isolamento real de segredos **antes de go-live** (não coberta por mocks).

**C23** - Reuso, expiração ou colisão concorrente de nonce retorna `DENY:AUTH_REPLAY`; máximo um efeito. (AC 23)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_single_use_nonce_replay_expiry_and_race`

**C24** - Entradas UTF-8 no limite aceitas; acima de 65.536/262.144 bytes -> `DENY:INPUT_TOO_LARGE` antes do modelo. (AC 24)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_input_utf8_boundaries_exact_and_plus_one`

**C25** - Alegação crítica falsa é `NEEDS_EVIDENCE:CLAIM_UNSUPPORTED` mesmo com citação real estruturalmente válida. (AC 25)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_false_critical_claim_with_real_citation`
Proof: conferência humana independente dos exemplos normativos críticos usados como oráculo; não depender só de juiz LLM.

**C26** - Renderer é a única rota de publicação; sem token `run_id+proposal_hash+policy_sha` -> `DENY:OUTPUT_NOT_APPROVED`. (AC 26)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_renderer_without_bound_release_token`
Proof: teste de integração da rota de publicação real **antes de go-live**, além do teste com mock.

**C27** - Ausência de versão de modelo/política/dataset/grader ou trials impede release com `BLOCKED:EVAL_METADATA_MISSING`. (AC 27)
Proof: `python -m unittest -v tests.test_cognitive_gates.CognitiveGateTests.test_eval_manifest_required_fields`



### Surface aliases — esclarecimento pré-aprovação (não executado)

Os números a seguir são identificadores documentais requeridos pela Spec Lean; não há implementação de códigos HTTP. Os estados e códigos de saída permanecem semanticamente os mesmos. Toda alteração na tabela deverá ser rederivada após aceite humano.

| Surface | 3-digit aliases (proposta) | Oráculos vinculados | Prova funcional |
| --- | --- | --- | --- |
| `evaluate` | `200 ALLOW`; `422 NEEDS_EVIDENCE`; `202 NEEDS_APPROVAL`; `403 DENY` | C6/C11/C26; C2/C3/C25; C13/C14; C1/C11/C12/C24 | NOT_RUN |
| `render` | `200 COMPLETE`; `403 DENIED`; `422 NEEDS_EVIDENCE` | C25/C26; C26; C2/C25/C26 | NOT_RUN |
| `execute` | `200 COMMITTED`; `403 DENIED`; `409 STALE_STATE`; `202 UNCONFIRMED`; `503 DEPENDENCY_FAILED` | C16/C17/C18; C12/C14/C15/C22/C23; C17; C18; C18 | NOT_RUN |
| `evaluate-fixture` | `200/exit 0`; `409/exit 1`; `422/exit 2`; `503/exit 3` | C20/C21; C20/C21; C20; C18/C20 | NOT_RUN |

## Coverage

| Set (size) | Member -> proof | Unproven |
| --- | --- | --- |
| EARS criteria (27) | AC 1 C1 · AC 2 C2 · AC 3 C3 · AC 4 C4 · AC 5 C5 · AC 6 C6 · AC 7 C7 · AC 8 C8 · AC 9 C9 · AC 10 C10 · AC 11 C11 · AC 12 C12 · AC 13 C13 · AC 14 C14 · AC 15 C15 · AC 16 C16 · AC 17 C17 · AC 18 C18 · AC 19 C19 · AC 20 C20 · AC 21 C21 · AC 22 C22 · AC 23 C23 · AC 24 C24 · AC 25 C25 · AC 26 C26 · AC 27 C27 | - (mapeamento derivado, provas pendentes) |
| Bootstrap mandatory files (9) | `AGENTS.md` C1 · `settings.json` C1 · `rules/CORE.md` C1 · `guardrails/CORE.md` C1 · `memory/INDEX.md` C1 · `memory/HANDOFF.md` C1 · `state/CURRENT.json` C1 · `EDITAL_UFMS_152_2026.md` C1 · `edital/INDEX.md` C1 | - (execução pendente) |
| Actors (2) | Tutor C8/C11/C26 · Coach C8/C11/C26 | - (execução pendente) |
| Positions (2) | 523 C6/C9 · 324 C6/C9 | - (execução pendente) |
| Provenance (4) | `observado` C8 · `informado` C8 · `inferido` C8 · `desconhecido` C8 | - (execução pendente) |
| Untrusted payload entry points (4) | PDF/chunk C11 · CSV C11 · tool-output C11 · Telegram C11 | - (execução pendente) |
| Action risk classes (4) | `INFORMATIONAL` C11/C26 · `PEDAGOGICAL` C6/C26 · `SENSITIVE_EXTERNAL` C13/C14 · `PERSONAL_WRITE` C12 | - (execução pendente) |
| Decision states (4) | `ALLOW` C6/C26 · `NEEDS_EVIDENCE` C2/C25 · `NEEDS_APPROVAL` C13 · `DENY` C11/C12/C14 | - (execução pendente) |
| Effect kinds (2) | `NONE` C26 · `TOOL` C12/C22 | - (execução pendente) |
| Approval bindings (7) | actor C14 · tool C15/C22 · action_hash C14 · policy_sha C14 · state_revision C14/C17 · expires_at C23 · nonce C23 | - (execução pendente) |
| Surface evaluate statuses (4) | `ALLOW` C6/C26 · `NEEDS_EVIDENCE` C2/C3/C25 · `NEEDS_APPROVAL` C13 · `DENY` C1/C11/C24 | - (execução pendente) |
| Surface render statuses (3) | `COMPLETE` C26 · `DENIED` C26 · `NEEDS_EVIDENCE` C2/C25/C26 | - (execução pendente) |
| Surface execute statuses (5) | `COMMITTED` C16/C17/C18 · `DENIED` C12/C14/C22/C23 · `STALE_STATE` C17 · `UNCONFIRMED` C18 · `DEPENDENCY_FAILED` C18 | DEPENDENCY_FAILED: exige prova de indisponibilidade externa sintética em C18 |
| Surface evaluate-fixture exit codes (4) | `0` C20/C21 · `1` C20/C21 · `2` C20 · `3` C20 | 0–3: implementar runner e casos de erro por classe, sem interpretar inexistência de testes como PASS |
| One-way doors (4) | D1 receipt C19/C20 · D2 gateway+single-use token C12/C14/C22/C23 · D3 risk classification C11/C12/C13 · D4 safe_renderer C26 | - (execução pendente) |
| Stored model entities (4) | POLICY_VERSION C1/C11/C19 · RUN_CONTEXT C1/C19/C26 · GATE_RECEIPT C19/C20 · APPROVED_ACTION C14/C23 | - (execução pendente) |
| Critical normative fact classes (4) | prazo C25 · nota C25 · requisito C25 · eliminação C25 | - (oráculos independentes pendentes) |
| Payload UTF-8 bounds (4) | JSON 65.536 C24 · JSON 65.537 C24 · external 262.144 C24 · external 262.145 C24 | - (execução pendente) |
| Nonce conditions (4) | válido C23 · consumido C23 · expirado C23 · corrida C23 | - (execução pendente) |
| State transition terminals (8) | COMPLETE C26 · COMMITTED C18 · UNCONFIRMED C18 · STALE_STATE C17 · DENIED C14 · NEEDS_EVIDENCE C2 · BLOCKED C1 · DEPENDENCY_FAILED C18 | - (execução pendente) |
| Eval manifest fields (5) | model_version C27 · policy_sha C27 · dataset_sha C27 · grader_version C27 · trials per scenario C27 | - (execução pendente) |
| LLM eval families (4) | edital/RAG C25/C27 · pedagogia C6/C27 · ferramentas/privacidade C12/C27 · prompt injection C11/C27 | - (eval probabilística ainda sem executor) |

## Test policy

- Tests for this feature SHALL be written from the approved AC before implementation. Where no test exists, the selector in `Proof:` deliberately remains **PENDING** and fails; 0 tests is not PASS.
- Use the existing CI commands shown in `Build:` from `.github/workflows/validate.yml` at PR #1 SHA `1079d7aa2cadb97d099d1e478f9e83b36180a624` as baseline. Add tests for new behavior separately; do not relax existing ones.
- Gate states: `PASS` only when test executes and asserts its whole claim at exact HEAD; `FAIL` if assertion false; `BLOCKED` for missing test/runner/approval; `NOT_APPLICABLE` only with stated reason.
- Each Cn must have positive and negative cases. For C17 and C23 simulate true competing writers/nonce consumers, not sequential calls only; for C22/C26 the production integration proof is separate from mock tests.
- For AC25, independent normative oracle from the accepted UFMS 152/2026 original and verified amendments, with human-calibrated semantic checks. Citation existence alone is insufficient.
- For probabilistic quality, log dataset/version, grader version, model, 40 initial tasks × 5 trials **as a proposal**, split calibration/holdout, count safety violations and reveal confidence/uncertainty. No universal success guarantee.
- Independent Verifier must inspect assertions and challenge with two unnamed examples and three injected mutants. A passing CI alone is insufficient to declare the feature done.
- Security-sensitive `PERSONAL_WRITE` remains DENY even when local synthetic tests use `allow_private=True`. No external operations until explicit authorization, isolation check and runbook exist.

## Swept

- validation: C1–C8, C14, C24, C25 (schema, UTF-8 byte bounds, page/span, unknown status)
- failure modes: C13, C18, C20 (timeout, missing approval, absent proof, UNCONFIRMED)
- idempotency: C9, C16, C23 (event replay, attempt identity, single-use nonce)
- authorization: C11–C15, C22, C23, C26 (policy trust root, allowlist, bypass and renderer)
- concurrency: C17, C23 (two concurrent writes and nonce race; require atomicity)
- data lifecycle: C4, C19, C23 (source versioning, receipt redaction, nonce TTL); retention/deletion of actual production receipts **blocks go-live and requires a separately approved operational decision**
- dependency failure: C18, C22, C26 (mock timeout/readback, provider outage, renderer failure; real provider proof blocks go-live)
- state transitions: C2, C5, C12–C18, C20, C22–C23, C26 (terminal and intermediate states, stale-state denial)
- observability: C19–C21, C27 (redacted receipts, SHA readback, evaluator manifest)

## Handoff

- **Settled mid-build:** 2026-11-04 — usuário aprovou o PLAN v0.2 literalmente: **"APROVO"**. D1–D4 aceitas como obrigações para o escopo local sintético; sem autorização de push/deploy/dados pessoais.
- **Dispatched:** nenhum Verifier ou screens sub-agent designado. Avaliação independente deve ocorrer após BUILD; não declarar self-verified como independente.
- **Boundary:** C1–C27 derivadas do plano aprovado; **0/27 provas novas executadas**, nenhum CHECKS validado oficialmente nesta sessão, nenhum commit de GitHub. O próximo passo técnico é verificar `validate_plan.py`, `validate_checks.py --execute` e somente então BUILD em workspace separado.
- **Abandoned:** tratar a simples existência de `Proof:` como se fosse execução ou transformar uma nota probabilística em aprovação determinística.
- **Walked:** n/a — feature local de CLI sem capturas de interface nem implantação de canais externos.
- **Go-live blockers:** isolação real de segredos; armazenamento atômico de autorização nonce/TTL; retenção e privacidade de recibos; prova de que toda publicação usa renderer; aprovação explícita para efeitos externos.

**Status administrativo:** CHECKS derivados após aprovação humana; congelamento mecânico ainda depende do validador oficial da skill e execução no HEAD correspondente.

## Delta obrigatório v0.3 por NC — testes propostos, não executados

### C4 / AC4 (novo PLAN — PENDENTE DE ACEITE)

- **Positivo:** Retificação verificável, vigente e limitada a trechos explicitamente alterados.
- **Negativo:** Retificação fraudulenta com checksum válido mas emissor não verificado; conflito impresso p.13 não corrigido automaticamente.
- **Oráculo de aprovação:** diff do original, cadeia do emissor, ato, seção, conflito e `UNVERIFIED_AMENDMENT|SOURCE_CONFLICT`.
- **Resultado:** `NOT_RUN` — sem implementação e sem prova real; exige execução externa independente.

### C11 / AC11 (novo PLAN — PENDENTE DE ACEITE)

- **Positivo:** Trust root autenticado fornece política correta apesar de payload hostil.
- **Negativo:** Chunk PDF/CSV/Telegram afirma ser política ou apresenta `policy_sha` falso.
- **Oráculo de aprovação:** diff do policy_sha carregado, ledger de chamadas externas e origem do carregamento.
- **Resultado:** `NOT_RUN` — sem implementação e sem prova real; exige execução externa independente.

### C13 / AC13 (novo PLAN — PENDENTE DE ACEITE)

- **Positivo:** Aprovação assinada de issuer e aprovador confiáveis corresponde ao estado/ação.
- **Negativo:** Texto em Telegram simula autorização humana; approval para versão antiga.
- **Oráculo de aprovação:** token verificado fora do contexto LLM; efeitos contados 0 ou 1.
- **Resultado:** `NOT_RUN` — sem implementação e sem prova real; exige execução externa independente.

### C14 / AC14 (novo PLAN — PENDENTE DE ACEITE)

- **Positivo:** Token assinado vincula todos os campos da ação canônica JCS.
- **Negativo:** AUTH-IND-01 troca `calendar.create` por `telegram.send`; troca destinatário/body.
- **Oráculo de aprovação:** comparação bit a bit de tool/dest/param/action_hash e contador de chamadas.
- **Resultado:** `NOT_RUN` — sem implementação e sem prova real; exige execução externa independente.

### C15 / AC15 (novo PLAN — PENDENTE DE ACEITE)

- **Positivo:** Limiar exato e renovação após janela permitem apenas chamadas aprovadas.
- **Negativo:** Limite excedido em concorrência e rejeição que chega depois da chamada.
- **Oráculo de aprovação:** contadores de transporte real, configuração versionada de janela e reserva atômica.
- **Resultado:** `NOT_RUN` — sem implementação e sem prova real; exige execução externa independente.

### C18 / AC18 (novo PLAN — PENDENTE DE ACEITE)

- **Positivo:** COMMITTED somente após readback; runner exit 0 e 1/2/3 corretos.
- **Negativo:** Dependência falha antes da chamada versus resultado incerto após envio.
- **Oráculo de aprovação:** métricas de chamada + idempotency key + testes de todos estados e exits.
- **Resultado:** `NOT_RUN` — sem implementação e sem prova real; exige execução externa independente.

### C20 / AC20 (novo PLAN — PENDENTE DE ACEITE)

- **Positivo:** Manifesto com commit/árvore/deps/origem e evidência recalculada.
- **Negativo:** Troca PR #1 para SHA novo; reusa recibo de composição antiga.
- **Oráculo de aprovação:** audit trail dos bytes, digests, comandos, exit codes e hashes dos arquivos.
- **Resultado:** `NOT_RUN` — sem implementação e sem prova real; exige execução externa independente.

### C22 / AC22 (novo PLAN — PENDENTE DE ACEITE)

- **Positivo:** Modelo sem credencial só pode propor chamada; gateway autenticado executa.
- **Negativo:** Modelo com credencial inadvertida contorna gateway via outro canal.
- **Oráculo de aprovação:** prova real de isolamento de contas/canais, network e zero efeitos; mock não basta.
- **Resultado:** `NOT_RUN` — sem implementação e sem prova real; exige execução externa independente.

### C25 / AC25 (novo PLAN — PENDENTE DE ACEITE)

- **Positivo:** Fato crítico conferido pelo oráculo independente coincide com proposição.
- **Negativo:** CITE-IND-01 nota zero em Inglês permitida apesar do item 10.2; conflito página 13.
- **Oráculo de aprovação:** registro `fact_id` e conferência humana, suporte semântico e intervalo de vigência.
- **Resultado:** `NOT_RUN` — sem implementação e sem prova real; exige execução externa independente.

### C26 / AC26 (novo PLAN — PENDENTE DE ACEITE)

- **Positivo:** Token vigente do mesmo run/policy/state/source_set/channel/recipient.
- **Negativo:** Token de publicação da revisão anterior ou destinatário anterior.
- **Oráculo de aprovação:** contagem de publicações e teste de bypass e invalidação da revisão.
- **Resultado:** `NOT_RUN` — sem implementação e sem prova real; exige execução externa independente.

## Matriz de requisitos que não podem ser falseados por prompt

- Para C13/C14/C22/C23/C26, **PASS em texto jamais é segurança operacional**: segredos, emissão de token, consumo de nonce e roteamento de saída exigem teste com limites reais de execução.
- Para C25, presença de citação não prova verdade; oráculo independente deve refutar conclusões falsas mesmo com página existente.
- C17/C23 requer corrida concorrente real ou harness de teste que execute simultaneamente; loops sequenciais não bastam.
- Testes propostos são seletores `NOT_RUN`, com resultado funcional **0 PASS**. `27/27` indica somente cobertura nominal no preview.

**Handoff:** aguardar aprovação explícita PLAN v0.3; se aprovada, derivar um `checks.md` definitivo, executar o validador oficial da skill e então reauditar, sem merge.
