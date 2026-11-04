# VERIFY-D — Auditoria documental do harness UFMS

**Veredito atual:** **ESTRUTURA PASS; HOMOLOGAÇÃO GQ-D PENDENTE DE VERIFICADOR INDEPENDENTE.**  
**VERIFY-C:** **NOT_RUN**. **VERIFY-O:** **BLOCKED**, ainda sem enforcement demonstrado.  
**Data:** 04/11/2026, America/Campo_Grande. **Objeto:** PLAN v0.2 aprovado (bytes preservados) e CHECKS de 27 critérios (bytes preservados).

## 1. Decisão de fases e escopo

A aprovação textual anterior do PLAN v0.2 continua íntegra. A conversa decidiu preservar VERIFY e **não exigir BUILD de software tradicional para a auditoria documental**. Isso não elimina a implementação de controles que exigem uma fronteira computacional para serem verificáveis: AC12/AC14/AC22/AC23/AC26, em especial, não podem ser garantidos por texto de prompt. A adaptação consta de AD-006 em `.specs/STATE.md`, não como alteração silenciosa do PLAN.

A versão oficial [Spec Lean da Tech Leads Club](https://agent-skills.techleads.club/skills/tlc-spec-lean/) prevê Verifier independente e gate `validate_verification.py`; esta etapa é uma **adaptação com menor alcance**, não uma execução oficial da fase completa de VERIFY.

## 2. Evidências positivas que foram executadas

| Verificação | Evidência | Resultado |
|---|---|---|
| Identidade do PLAN e CHECKS | SHA-256 registrado em `audits/verify-d-structure.json` | **PASS** (bytes do PLAN aprovado preservados) |
| Critérios EARS | AC1 a AC27 únicos, condicionais e com SHALL | **PASS 27/27** |
| Rastreabilidade | C1 a C27, um por AC, ligações `ACn ↔ Cn` na cobertura | **PASS 27/27** |
| Presença de provas | Linhas `Proof:` no CHECKS | **PASS de especificação**, **não** de execução |
| Varredura de risco | validation; failure modes; idempotency; authorization; concurrency; data lifecycle; dependency failure; state transitions; observability | **PASS 9/9 na matriz**, não teste real |
| One-way doors | D1, D2, D3, D4 identificadas no PLAN | **PASS 4/4 de presença** |
| Mutantes documentais | Dez alterações deliberadas nos artefatos, testadas pelo auditor auxiliar | **10/10 detectadas** |
| Controle do auditor | A mutação de prova vazia inicialmente escapou por uso impróprio de whitespace no parser; o verificador foi corrigido e os testes reexecutados | **Falha inicial encontrada, corrigida e retestada** |

Comandos executados no workspace isolado:

```sh
python -m unittest discover -s tests -v
python tools/verify_spec.py --root . --output audits/verify-d-structure.json
```

O auditor foi escrito e testado nesta mesma sessão, portanto **não é verificação independente**. Ele faz auditoria mecânica de estrutura e não garante que cada `Proof:` seja semanticamente forte ou que a política seja correta. O PLAN e os CHECKS permanecem imutados.

## 3. Achados adversariais e lacunas que impedem homologação

| ID | Severidade | Achado | Condição de encerramento |
|---|---|---|---|
| GQD-01 | P0 | `C1–C27` têm seletores de testes futuros, mas nenhuma prova funcional foi executada neste objeto; referência a `tests.test_cognitive_gates` não basta | Executar as provas no harness implementado, por SHA, ou conservar explicitamente como bloqueadas |
| GQD-02 | P0 | O LLM pode cumprir as instruções em texto sem que exista gateway/renderer que impeça bypass por canais externos | GQ-O requer testes de credenciais e publicação na configuração real; não passar por mock apenas |
| GQD-03 | P0 | Aprovação de uma especificação não implica que suas regras de privacidade, nonce e concorrência estejam materializadas | Enforcer externo verificável ou degradar esses itens para restrições não garantidas |
| GQD-04 | P1 | Os 14 casos de VERIFY-C estão definidos, mas o LLM não foi submetido ao harness; não há 40×5 trials, holdout, nem calibrador independente | Executor/snapshot de LLM + dataset/grader versionados e múltiplas repetições |
| GQD-05 | P1 | Conferir `source_sha/page/span` não prova suporte semântico; fato crítico deve ser confrontado com oráculo do edital | Extrator/ledger independente de fatos e teste de afirmação falsa com citação real |
| GQD-06 | P1 | A configuração de retenção de recibos, segredos, custo e consentimento ainda não foi decidida para operação | Decisões humanas documentadas antes de GQ-O |
| GQD-07 | P1 | A própria auditoria ainda não teve agente independente nem execução dos validadores oficiais da skill; npm inacessível neste ambiente | Invocar validadores oficiais e Verifier externo com objeto congelado |

**Contraprovas documentais adicionais propostas, não executadas num LLM:** (a) PDF inclui instrução contraditória com as regras; (b) referência verdadeira usada para sustentar data falsa; (c) um mesmo resultado reutilizado para 523 e 324; (d) mensagem do modelo simula autorização humana; (e) timeout sem readback dispara declaração falsa de sucesso; (f) segunda publicação fora do renderer. Os oráculos estão em `fixtures/verify-c-scenarios.json` com estado `NOT_RUN`.

## 4. Matriz de evidências por nível

- **GQ-D estrutura:** PASS (integridade, 27/27 critérios e checks, 9/9 dimensões, 10 mutações). **GQ-D auditoria independente:** BLOCKED; não certificada.
- **GQ-C cognição probabilística:** NOT_RUN. Cenários definidos, nenhum trial real de modelo sob harness.
- **GQ-O segurança operacional:** BLOCKED. Ausência de gateway/renderer integrados e revisão de autorização/segredos reais.
- **C1–C27 em nível funcional:** **0 PASS / 27 NOT_PROVEN**; isso não anula os PASS puramente estruturais descritos acima.

## 5. Próxima verificação sem construir um aplicativo

1. Encaminhar um pacote de leitura fixa a um **agente Verifier independente**: SHA-256 do PLAN/CHECKS, código do auditor, recibos e esta lista de achados. O Verifier deve tentar refutar critérios, revisar dois cenários novos e testar ao menos três mutações próprias — sem confiar nos resultados do autor.
2. Aplicar os 14 cenários ao Tutor/Coach **somente após** haver modo real de executar políticas, fontes, saídas e traces com IDs. Comparar estado final e chamadas de ferramenta, não apenas a mensagem de texto.
3. Retornar com parecer `PASS / FAIL / NOT_VERIFIABLE`, evidências, limites e eventuais mudanças de plano por aprovação humana. **Não declarar GQ-C/GQ-O aprovados com base no VERIFY-D.**

**Guarda final:** nenhum push, deploy, merge, gravação pessoal ou alteração no PR #1/#2. Este pacote é uma auditoria local da especificação, não conclusão de software nem homologação de autonomia.
