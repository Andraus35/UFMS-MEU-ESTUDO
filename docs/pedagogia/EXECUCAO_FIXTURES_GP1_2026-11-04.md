# Execução isolada das fixtures sintéticas GP-1 — ciclo 5

**Data:** 04/11/2026 (America/Campo_Grande).  
**Resultado:** **11 PASS · 0 FAIL · 3 NOT_IMPLEMENTED** (14 fixtures enumeradas).  
**Objeto:** [fixtures IGP-01 a IGP-14](FIXTURES_INGESTAO_GP1_2026-11-04.json).  
**Não é** aprovação de GP-1, execução integral dos 102 cenários, ensaio com dados pessoais ou prova de funcionamento do tutor adaptativo.

## 1. Proveniência: código efetivamente executado

| Fonte | SHA Git blob conferido no ambiente isolado |
|---|---|
| `scripts/core.py` do PR técnico #1 no commit `42530c1680fb328fb9064235d475d2951c3a7c51` | `28649e5b649c239cb03d748ab5822c352ddfe1db` |
| `config/topics.csv` do mesmo SHA técnico | `d733ec5af292934fa4efa0e892470c27603065f6` |
| `FIXTURES_INGESTAO_GP1_2026-11-04.json` do PR pedagógico #2 no commit `02610d347a46bb8435b845fe07afc6b90f059e72` | `bd060fd2263c686e7dc4f56bf0c97f5fc5112dfc` |

O módulo Python foi reconstruído localmente a partir de artefato anterior e diferenças do HEAD técnico; o CSV foi normalizado do CRLF para LF **sem alterar conteúdo lógico**; as fixtures foram reconstruídas a partir da definição documental. **Antes dos testes, os três arquivos foram comparados pelo Git blob hash e coincidiram exatamente com os blobs publicados nos SHAs listados**. Isso demonstra identidade dos bytes usados, não equivale a executar testes em um runner GitHub Actions.

As rotinas `validate_events` e `rebuild` foram importadas do **código exato**. A tabela de tópicos possuía 23 linhas válidas. Todos os eventos e números dos exemplos eram fictícios; o teste não gravou nenhum resultado pessoal ou arquivo de evento no repositório.

## 2. Resultado por fixture

| ID | Estado | Condição verificada |
|---|---|---|
| IGP-01 | `PASS` | Recomendação pendente, nenhum resultado atribuído |
| IGP-02 | `PASS` | Resultado desagregado consolidado corretamente |
| IGP-03 | `PASS` | Resultado agregado sem imputação de acerto por tópico |
| IGP-04 | `PASS` | Correção substitui projeção anterior |
| IGP-05 | `PASS` | Rejeição por total inconsistente |
| IGP-06 | `PASS` | Rejeição de acertos por tópico acima do total |
| IGP-07 | `PASS` | Rejeição de tópico fora de recomendação |
| IGP-08 | `PASS` | Rejeição de resultado duplicado do mesmo caderno |
| IGP-09 | `PASS` | Rejeição de timestamp sem fuso |
| IGP-10 | `PASS` | Bloqueio de resultado pessoal sem autorização de validação |
| IGP-11 | `PASS` | Rejeição de correção não vinculada ao evento anterior |
| IGP-12 | `NOT_IMPLEMENTED` | Normalização de convenção de relatório ainda depende de adaptador |
| IGP-13 | `NOT_IMPLEMENTED` | Identidade independente de tentativa ainda carece de schema |
| IGP-14 | `NOT_IMPLEMENTED` | Distinguir attempt_at de recorded_at exige contrato de engenharia |

- **IGP-01–11:** os 11 resultados observados coincidiram com a aceitação/rejeição e, quando aplicável, projeções esperadas do JSON.
- **IGP-12–14:** **não foram executados como testes do core** porque demandam pré-processador de relatório, esquema independente de tentativas e separação de temporalidade ainda não implementados. Não são três falhas de código executado nem três PASS.
- **GP-1:** permanece **PENDENTE**, com invariantes existentes comprovados no subconjunto testado.
- **GP-3:** continua **não demonstrado** como execução dos 102 casos, pois estes 11 não substituem a suíte completa.

Detalhes machine-readable desta execução: [RESULTADOS_EXECUCAO_GP1_2026-11-04.json](RESULTADOS_EXECUCAO_GP1_2026-11-04.json).

## 3. Limites e controle de privacidade

`allow_private=True` foi usado exclusivamente nos testes fictícios **em memória** para inspecionar regras de validação; isso não alterou `settings.json` e não concedeu permissão para persistir resultados reais. A ferramenta de escrita pessoal do harness permanece desabilitada.

Os três contratos sem implementação devem virar tarefas incrementais da engenharia, com suas próprias contraprovas: CDO-10/PRD-05, PRD-03/CDO-02 e PRD-04/CDO-09. Não criar IDs de aceitação novos para simular maior cobertura.

**Próxima ação técnica:** confirmar SHA atual do PR #1, implementar primeiro a camada de ingestão/temporalidade/identidades em branch própria e executar testes regressivos, sem merge e sem liberação de escrita pessoal. Esta sessão pedagógica limita-se a registrar evidências e requisitos.
