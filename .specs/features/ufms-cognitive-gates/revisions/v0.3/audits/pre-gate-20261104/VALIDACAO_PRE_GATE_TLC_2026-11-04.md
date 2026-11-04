# Gate TLC — diagnóstico estático, objeto PR #5

**Data:** 2026-11-04 (America/Campo_Grande). **Modalidade:** pré-gate local, read-only sobre cópias do objeto congelado. **Não é execução dos validadores oficiais.**

## Identidade verificada

- Repositório: `Andraus35/UFMS-MEU-ESTUDO`; PR **#5**, draft.
- **HEAD de entrada (não o novo commit de relatório):** `64a0a66d290f6fc7d01318403b6948f43adbe385`.
- PLAN aprovado no aceite humano: SHA do commit de apresentação `aa66ac2945cc35c72bbd06401db977903dcbb3c4`; blob Git `4257e971f1417cc82461cf3e9117c5598afb7967` e SHA-256 `fa37d9c5cc2fb4288c477c4b175c8ec923ebb419be2aa9e785b32471b850c70c`.
- CHECKS congelados documentalmente: blob Git `a6ec782fa01db96098b78d95c42a8706ee6d3525`, SHA-256 `50dff7d0f8ff6f9d6ce7a66ea624cd06d6a6f90bb8055be18dd74461b5481bc0`.
- Aceite do usuário **“APROVO”** está registrado em `approval-receipt.json` e `APPROVAL_v0.3-r1.md`. Não autoriza modificação normativa, merge, implantação ou acesso a dados pessoais.

## Referência oficial inspecionada

Código da skill `tech-leads-club/agent-skills`, diretório `packages/skills-catalog/skills/(development)/tlc-spec-lean/scripts/`:

| Artefato oficial | Git blob SHA-1 |
| --- | --- |
| `lean_config.py` | `b751517ba653478cd69330e590c8f0de7a739c24` |
| `validate_plan.py` | `82f7c754fb9542e659e13a9732cf89d9a25def1f` |
| `validate_checks.py` | `be14d1956cc5afaba6009608c71d7ec1a216c29f` |
| `validate_verification.py` | `b2035193543df146dc5c714979b27a94972d8da4` |

**Fonte das regras:** `lean_config.py`, `plan_approved()` / `APPROVED_RE`; `validate_checks.py`, linhas 285–288 (exige aprovação literal no `plan.md` irmão); `validate_checks.py`, linhas 446–461 (`--execute` roda `Build:` no checkout). `validate_verification.py`, linhas 391–393 exige o mesmo marcador. Esses são achados por inspeção de código oficial, não por execução dos scripts.

## Resultados do pré-gate (não homologação)

| Verificação | Estado | Evidência |
|---|---|---|
| `SHA_plan.md` | **PASS** | fa37d9c5cc2fb4288c477c4b175c8ec923ebb419be2aa9e785b32471b850c70c |
| `SHA_checks.md` | **PASS** | 50dff7d0f8ff6f9d6ce7a66ea624cd06d6a6f90bb8055be18dd74461b5481bc0 |
| `APPROVAL_RECEIPT` | **PASS** | aceite externo vinculado a snapshot e checks, não incorporado no PLAN |
| `TLC_APPROVED_IN_SIBLING_PLAN` | **BLOCKED** | O validate_checks.py oficial exige uma linha **Approved**: YYYY-MM-DD - user: "..." no plan.md; arquivo separado não atende essa condição |
| `SECTIONS` | **PASS** | {'Checks': True, 'Coverage': True, 'Swept': True} |
| `CHECKS_27_AND_PROOFS` | **PASS** | {'total': 27, 'unique': 27, 'with_proof': 27} |
| `TLC_BUILD_EXECUTE_SINGLE_HEAD` | **BLOCKED** | PR #5 HEAD não possui scripts/ci_gate_contract.py, scripts/write_policy.py e scripts/validate.py; Build refere-se ao PR #1 em outro SHA |
| `COMPOSITION_MANIFEST_CURRENCY` | **WARN** | Manifesto antigo: foi produzido antes de v0.3-r1 e da aprovação; não pode ser recibo da candidata atual |
| `TLC_OFFICIAL_EXECUTION` | **NOT_RUN** | npx falhou EAI_AGAIN registry.npmjs.org; script oficial não executado |
| `INDEPENDENT_GQD` | **PENDING** | auditor independente ainda não examinou HEAD novo |
| `FUNCTIONAL_PROOFS` | **NOT_RUN** | 0/27 provas funcionais da feature |

## Falhas e limites relevantes

1. **FORMATO DE APROVAÇÃO (BLOQUEIO FORMAL):** os bytes aprovados do PLAN não contêm `**Approved**: YYYY-MM-DD - user: "APROVO"`. O registro externo é legítimo e está vinculado por SHA, mas `plan_approved()` do upstream não lê arquivos de aprovação separados. **Não adicionar linha silenciosamente**: alteraria SHA-256 e blob da versão aprovada. Opções, sujeitas à decisão de governança: (a) obter aprovação expressa de anotação administrativa e criar nova versão com novo hash; (b) executar validação oficial sobre visão derivada com marcador injetado, declarando claramente que o snapshot analisado é distinto e que o PLAN original não passou literalmente no gate; (c) adotar gate documental equivalente com exceção explicitamente aprovada. Nenhuma foi autorizada/executada neste ciclo.
2. **DEPENDÊNCIA DE COMPOSIÇÃO (BLOQUEIO `--execute`):** os comandos `Build:` apontam para `scripts/ci_gate_contract.py`, `scripts/write_policy.py` e `scripts/validate.py` no **PR #1** SHA `1079d7aa2cadb97d099d1e478f9e83b36180a624`, ausentes do HEAD isolado do PR #5. A solução de testes precisa montar workspace de verificação read-only por commits exatos, comprovando a identidade da composição, sem presumir um único SHA Git.
3. **MANIFESTO DEFASADO:** `composition-manifest.json` é proposta antiga anterior ao PLAN v0.3-r1 aprovado; inclui `candidate_plan_sha256` antigo e anotação de aprovação pendente. Não reutilizá-lo como recibo atual, embora seus SHAs históricos sejam úteis para reconstrução.
4. **SKILL OFICIAL NÃO EXECUTADA:** `npx @tech-leads-club/agent-skills install --skill tlc-spec-lean` retornou **`EAI_AGAIN`** (`registry.npmjs.org`). Não afirmar `validate_plan`, `validate_checks` ou `validate_verification` PASS.
5. **PROVAS FUNCIONAIS 0/27:** o conjunto de 27 CHECKS é contrato, não teste executado de comportamento do harness. Nenhuma autorização real, Gateway ou LLM foi testado.

## Evidência de testes locais

- `python -m unittest discover -s tests -v` no pacote de diagnóstico: **10/10 PASS**; são testes da verificação estática e mutações de bytes/recibo.
- Suíte anterior da especificação aprovada: **16/16 PASS** na cópia local, também somente documental.
- Falso positivo evitado: injetar a linha de aprovação no PLAN faria o parser upstream aceitar o formato, porém o verificador de integridade detecta alteração dos bytes normativos aprovados.
- A suíte não substitui verificação semântica independente. **GQ-D continua REPROVADA** pelo parecer anterior até reauditoria do novo candidato; GQ-C NOT_RUN; GQ-O BLOCKED.

## Próxima ação objetiva

1. Executar scripts oficiais em checkout de avaliação com acesso legítimo ao catálogo Tech Leads Club, registrando seus blobs e saída integral; não vender o resultado de um espelho/overlay como prova do objeto original.
2. Resolver expressamente a incompatibilidade de aprovação inline **sem adulterar o PLAN aprovado**.
3. Atualizar ou substituir `composition-manifest.json` para referenciar o snapshot aprovado e a candidata atual, com política anticolisão e hash da composição, mantendo os PRs #1/#2 separados.
4. Encaminhar o **HEAD final** desta branch a verificador independente adversarial; exigir parecer `PASS/FAIL/NOT_VERIFIABLE` por NC-UFMS-GQD-01..09. GQ-C e GQ-O ficam separados.

**Guarda:** sem merge; sem mudança de PLAN/CHECKS; sem deploy; sem resultado pessoal real; sem nova autorização de ferramenta externa.
