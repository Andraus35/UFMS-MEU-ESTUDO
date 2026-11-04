# Rastreabilidade dos 102 cenários aos gates — v1.8

**Natureza:** plano de testes **a implementar**. Não há execução de teste pedagógico nesta entrega. A catalogação original é [CRITERIOS_DE_ACEITACAO.md](CRITERIOS_DE_ACEITACAO.md); este documento não duplica descrições dos casos.

## 1. Inventário verificável

| Família | IDs | Quantidade | Natureza |
|---|---|---:|---|
| PED | PED-01–PED-20 | 20 | Evidência, retenção, privacidade e decisões básicas |
| COMP | COMP-01–COMP-12 | 12 | Dois cargos, riscos, escopo e prioridades |
| SIM | SIM-01–SIM-10 | 10 | Simulados e pontuação |
| EFA | EFA-01–EFA-08 | 8 | Eficácia e limites de inferência |
| FIQ | FIQ-01–FIQ-18 | 18 | Fila dinâmica e reordenação |
| CDO | CDO-01–CDO-18 | 18 | Prescrição, ingestão e estados |
| PRD | PRD-01–PRD-16 | 16 | Compatibilidade, bloqueios e governança |
| **TOTAL** | | **102** | **Documentados, ainda não executados como suíte do motor** |

IDs únicos são a chave de rastreabilidade. Um cenário pode contribuir para vários gates, mas deve ter **uma implementação canônica de teste**, reutilizada, não um segundo teste divergente com o mesmo nome.

## 2. Alocação por gate (sobreposição deliberada)

| Gate | Famílias/casos foco | Evidência técnica exigida |
|---|---|---|
| GP-0 — Fonte | PED-07, PED-09/10/18; COMP-03/11/12; FIQ-05/07/12; CDO-04/05; SIM-10; PRD-10/11/12 | Versão normativa, recorte cargo-assunto, negativa para norma/desatualização |
| GP-1 — Contratos e escrita | PED-02/08/12/13/14/15/20; CDO-01/02/09–18; FIQ-04/10/13/17; PRD-01–05/08/09/12/15 | Schema, integridade, nomes de campo, estado, autorização, eventos/correções |
| GP-2 — Decisões/evidências | PED-01/03–06/11/16–18; COMP-01/02/04–10; FIQ-01–03/06–09/14–16/18; CDO-03/06–08; EFA-01–04/07; PRD-06/07/14/16 | Projeção E0–E4, fila, comparador, criticidade, escolha e explicação |
| GP-3 — Suíte adversarial | **Todos PED, COMP, SIM, EFA, FIQ, CDO e PRD** | Registro de execução PASS/FAIL/SKIP, entradas, saídas, mutantes/negativos apropriados e SHA |
| GP-4 — Ciclo operacional | PED-14/15/17/20; COMP-05; SIM-02/05/07/09; EFA-01/03/06/08; FIQ-03/04/10/17; CDO-01/02/08/12–18; PRD-04/05/08/09/13/15 | Fluxo do caderno ao resultado, recuperação entre sessões, readback, privacidade |
| GP-5 — Piloto consentido | PED-04/05/19; COMP-06–09; SIM-06/08; EFA-01–08; FIQ-09/15/18; CDO-17/18; PRD-09/13/14 | Evidência real consentida, comparabilidade e avaliação de utilidade sem atribuição causal automática |

**Cobertura:** GP-3 exige implementar/verificar as 102 referências como conjunto integral, incluindo casos que também apoiam GP-0, GP-1, GP-2 ou GP-4. Não interpretar o número de uma linha como testes aprovados ou prontidão do gate.

## 3. Primeiro lote obrigatório para segurança

Casos que bloqueiam a confiança mínima antes de recomendar usando histórico ou persistir dados:
- **Integridade/proveniência:** PED-02, PED-12/14, CDO-09–13/16, PRD-03–06.
- **Permissão e confirmação de escrita:** PED-20, CDO-17, FIQ-17, PRD-09/15.
- **Escopo e sobreposição:** PED-08/18, COMP-03/05/11, FIQ-05/06/12, PRD-10/11.
- **Ausência de fatos fictícios:** CDO-01–05, FIQ-01/11/13, PRD-02/12.

A lista é uma ordem de prioridade **de engenharia**, não obrigatoriedade de estudar disciplinas em sequência.

## 4. Segundo lote: motor e valor pedagógico

Após os invariantes: PED-01/03–06/11/16/17/19, COMP-01/02/04/06–10, FIQ-02/03/07–10/14–16/18, EFA-01–05/07/08 e PRD-07/13/14/16. Incluir testes de decisão explicável sobre entradas sintéticas, casos contraditórios e mudança deliberada de snapshot.

**Simulados:** SIM-01–10 exigem motor de pontuação compatível com dados por área e provas separadas. A execução combinada do dia não é regra para todos os ciclos.

## 5. Formato do resultado por caso (futuro)

```text
test_id; gate_ids; fixture_sha; code_sha; expected; observed; status;
negative_case; explanation_ref; ci_run_ref; reviewer; limitation
```

Permitir `SKIP` e `BLOCKED` com motivo; nunca contar como PASS. O executor deve distinguir:
- **testes automatizados:** validador, projeção, transição de estado, idempotência, sorteio reprodutível;
- **avaliação humana/adversarial:** coerência qualitativa das escolhas, fidelidade ao edital, valor pedagógico;
- **piloto real:** coleta consentida e análise de sinais observados, sem promessa de causalidade.

## 6. Provas de conclusão por gate

- **GP-0:** referências normativas da versão vigente confirmadas; eventuais pendências delimitadas.
- **GP-1:** ingestão preserva dados incertos, permissões e histórico; entradas adversariais rejeitadas sem perda.
- **GP-2:** fila e evidências derivadas corretamente; decisões e desvios têm explicações reproduzíveis.
- **GP-3:** todos os testes exigidos para a candidata executados e reconciliados, com eventuais falhas explicitadas; nenhuma aprovação automática apenas por contagem.
- **GP-4:** fluxo de ponta a ponta realmente reproduzido e verificado em um ambiente permitido, incluindo retomada entre sessões.
- **GP-5:** autorização, privacidade e amostra real adequadas; avaliação da utilidade delimitada ao que os dados demonstram.

Uma reprovação de gate mantém os posteriores **pendentes/bloqueados** onde dependerem dele. Nenhum controle deste documento concede permissão para alterar branch protegida, aprovar PR ou efetuar merge.
