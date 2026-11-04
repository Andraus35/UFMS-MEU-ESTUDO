# Auditoria de branches, commits e integração — UFMS MEU ESTUDO

**Data:** 2026-11-04. **Escopo:** repositório `Andraus35/UFMS-MEU-ESTUDO`.
**Modo:** inspeção autenticada via GitHub; sem checkout local, sem execução local dos hooks, sem avaliação de credenciais externas ou das provas em contas pessoais. Os resultados de CI foram verificados por SHA.

## Inventário inicial: 9 branches

| Branch | Commits à frente da main inicial | Arquivos na diferença | Destinação |
|---|---:|---:|---|
| `main` | 0 | somente README inicial | base `c020f78ba07ebb4e2949021b45a7f9b8f2c26d42` |
| `setup/harness-memory-v0-2` | 161 | 159 | **PR #1 MERGED** |
| `docs/especificacao-pedagogica-v1-2` | 18 | 30 | **PR #2 MERGED** |
| `feature/oracle-telegram-calendar-bridge` | 21 | 36 | **PR #3 ENCERRADO SEM MERGE — FORA DE ESCOPO** |
| `spec/ufms-cognitive-gates-verify-d-20261104` | 1 | 15 | **PR #4 BLOQUEADO / supersedido** |
| `spec/ufms-cognitive-gates-gqd-correction-v0-3` | 10 | 61 | **PR #5 BLOQUEADO** |
| `poc-ufms-003-zapia` | 2 | 1 | incorporada pela descendente POC-007 |
| `poc-ufms-005-zapia` | 5 | 2 | incorporada pela descendente POC-007 |
| `poc-ufms-007-zapia` | 7 | 3 | arquivada como **PR #6 MERGED** |

Contagens relativas à `main` inicial, antes das integrações. As POCs têm ancestralidade comum (003 → 005 → 007); **não** somar 2+5+7 como commits distintos. Foram enumerados os históricos remotos das nove branches e conferidos os diffs acumulados; não houve revisão manual linha a linha dos 219 commits distintos inicialmente alcançáveis. Não declarar auditoria integral de cada linha de código.

## Integrações autorizadas e efetivadas

1. **PR #2 — pedagógico:** `6e1fa661a33565d580f99962c3510d5361decbe6` → merge `fe63d583fabfa7d23f5707b0c747f7a1e24aa700`. Documentação apenas; GP-1 ainda pendente e os 102 cenários são contratos, não testes completos de produção.
2. **PR #1 — harness:** `1079d7aa2cadb97d099d1e478f9e83b36180a624` → merge `1ff563e4de6228504b140f96474072fffccedd92`. Check `validate` passou no HEAD exato da candidata e na `main` após o merge. `state/CURRENT.json` continua sem resultados e `personal_results_writes_enabled=false`.
3. **PR #6 — arquivo sintético Zapia:** HEAD `03f1a4e4c615ba9f92b0466c8dacf27f527e182f` → merge `c23c1808ec39ca4b6ccf9bcbc2c3688c643826d7`. Check `validate` da candidata passou. A branch preserva toda a ancestralidade POC-003/005/007. `poc/README.md` proíbe usar os experimentos como estado real.

Os três merges empregaram método `merge`, sem reescrever o histórico ou fazer force push.

## Branches preservadas como draft — não mesclar

- **PR #3:** **ENCERRADO SEM MERGE em 04/11/2026, por decisão expressa do usuário; fora do escopo.** A CI de unidade/contêiner havia aprovado o HEAD `757e61c7e880fb8b38c4b215eb063c6c9f1e7cbe`, mas a implantação e a auditoria operacional nunca foram homologadas. Não retomar essa frente nem integrar seus arquivos sem nova autorização. A branch experimental pode permanecer no GitHub apenas como registro histórico até exclusão separada.
- **PR #4:** snapshot documental anterior, sem homologação GQ-D. Há uma versão corretiva no PR #5; não promover ambos como fontes concorrentes.
- **PR #5:** plano aprovado e validação formal TLC verde no SHA `652634b70a411ed4641cb7a202b0ae2f9a19ed1b`, mas o próprio PR registra **GQ-D independente reprovada**, nove NCs pendentes, C1–C27 funcionais `NOT_RUN`, GQ-C `NOT_RUN` e GQ-O bloqueado. A aprovação documental não é autorização de merge.

## Riscos e controles obrigatórios

1. **Visibilidade:** repositório **público** na leitura autenticada. Nenhuma das nove branches iniciais tinha proteção ativa; consulta à API administrativa de proteção retornou 403 por falta de permissão da integração. O campo `protected=false` foi confirmado em `main`.
2. **Privacidade:** resultados pessoais, credenciais, dados de conta TEC/Qconcursos, exportações brutas e dados privados de agenda **não devem entrar no repositório público**. A flag de escrita pessoal está desabilitada. O POC contém somente dados marcados como fictícios.
3. **Desatualização documental:** `docs/API_WRITE_GOVERNANCE.md` dizia que o repositório era privado; corrigido neste pacote de auditoria. Anotações anteriores sobre estado privado são históricas e não retratam o estado corrente.
4. **CI não é gate administrativo:** `validate` verde comprova testes implementados e executados, não proteção de branch, hooks nativos em todas as interfaces, auditoria independente ou segurança operacional.
5. **Edital:** `ALERTA-DOC-01` (cronograma literalmente conflitante na p. 13) e verificação de retificações permanecem abertos; não alterar a fonte por inferência.
6. **Automações:** qualquer rotina ainda vinculada ao PR #1 draft deve ser reavaliada após seu merge; não continuar gravando em candidato encerrado.
7. **Próximos gates:** controlar `main` administrativamente, reconciliar GP-1, resolver GQ-D para PR #5, executar testes integrados Tutor/Coach no escopo atual (Zapia/Notebook/Calendar/Tasks) e manter dados reais em armazenamento privado autorizado. O PR #3 está encerrado e não integra a fila.

**Veredito histórico de integração:** integração parcial e seletiva das três candidatas verificáveis. **Atualização de escopo (04/11/2026):** PR #3 encerrado sem merge; apenas PRs #4 e #5 permanecem abertos e bloqueados para reavaliação.
