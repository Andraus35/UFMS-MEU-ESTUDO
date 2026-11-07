# Mapa de desbloqueio das frentes pedagógicas (RM-02 a RM-10)

**Data:** 07/11/2026 · **Base:** `main@f2c855b` (CI push `42411892072`: success) · **Natureza:** diagnóstico; não promove nenhum status.

Tipos de bloqueio: **A** = resolvível por código offline, autônomo · **D** = decisão do proprietário · **R** = exige dado real ou uso real · **X** = exige auditor independente.

## Quadro por frente

| Frente | Estado | O que impede a homologação | Tipo | Próximo passo autônomo |
|---|---|---|---|---|
| RM-02 ingestão GP-1 | implementado_nao_homologado | plataforma real não homologada; zero eventos reais | R, D | nenhum (o contrato e as contraprovas já existem) |
| RM-03 evidências E0–E4 | implementado_nao_homologado | `CURRENT.json` está em E0, sem evidência real | R, D | nenhum |
| RM-04 fila adaptativa | implementado_nao_homologado | pesos provisórios sem calibração em dados reais | R | nenhum; calibrar sem dados seria inventar |
| RM-05 prescritor de cadernos | implementado_nao_homologado | plataforma real não homologada | R | nenhum |
| RM-06 GP-3 (102 cenários) | implementado_nao_homologado | 46 cenários sem teste canônico; 0 end-to-end PASS | X, R | **esgotado**: o restante não é computável offline (ver abaixo) |
| RM-07 gates GQ-D/C/O | implementado_nao_homologado | reauditoria independente; 1 NC aberta | X | dossiê de reauditoria |
| RM-08 ciclo Tutor–Coach | bloqueado | persistência consentida, replay, execução humana real | D, R, X | P1–P3/P5–P6 já em guard offline (PR #59) |
| RM-09 integrações | planejado | depende de persistência e privacidade | D | nenhum antes de RM-08 |
| RM-10 piloto GP-5 | bloqueado | privacidade, autorização, observações reais | D, R | nenhum |

**Conclusão objetiva:** RM-02 a RM-05 **não podem ser homologadas por código**. O que falta é uso real (eventos de estudo) e, para isso, a decisão de persistência (ADR-013). Enquanto `CURRENT.json` estiver em E0, qualquer "calibração" ou "validação" seria fabricada, o que as regras proíbem.

## O que é autônomo: backlog de GP-3

Dos 60 cenários sem teste canônico, **14 foram resolvidos** até aqui, com função pura ou teste e contraprovas: SIM-01, 02, 03, 04 e 10 em `scripts/simulado_score.py` (pontuação ponderada, sem inferência, sem declarar aprovação, restrição eliminatória só sinalizada) e SIM-05, 06, 07, 08 e 09 em `scripts/simulado_session.py` (sessão combinada sem nota conjunta, queda sem inferir fadiga, independência nunca presumida, comparação sem tendência sustentada, versão parcial rotulada sem inventar estoque); CDO-14 e FIQ-10 em `scripts/notebook_prescriber.py` (caderno pendente duplicado exige reutilização ou substituição explícita e justificada), PRD-01 em `tests/test_bootstrap_doc_sync.py` (contagem de arquivos do bootstrap nos documentos confere com `settings.json`) e PED-15 em `tests/test_retomada_sessao.py` (processo novo reconstrói as projeções versionadas). Restam 46.

Classificação **preliminar por título, não item a item**, dos 46 restantes:

- **Computáveis offline:** nenhum candidato restante identificado. Os 4 que restavam foram tratados neste ciclo (PED-15 só na parte de reconstrução das projeções, não na retomada pelo Tutor).
- **Dependem da camada cognitiva do Tutor/Coach** (decisões de intervenção, justificativa, reavaliação): PED-05, 06, 07, 09, 16, 17, 19; COMP-01 a 12; EFA-01 a 08; FIQ-03, 05 a 08, 12, 14, 15, 18. Testar com fixtures de código não prova o comportamento do Tutor; isso é escopo da RM-07/RM-08 e exige avaliação independente.
- **Dependem de plataforma ou arquivo real:** CDO-05, 06, 07, 11, 13, 15, 18; PRD-10, 11, 13, 14, 16.

Um teste unitário correlato leva o cenário a `PARTIAL`, nunca a `PASS` (política da matriz).

## Recibo do GP-3-MVP8

Os 8 cenários do recorte mínimo (`GP3_MVP_PESSOAL_8_20261105.md`) têm referências que resolvem para métodos de teste reais, verificado por `tests/test_gp3_mvp8_rastreabilidade.py`. Os 8 testes passam no HEAD, e o run de CI de `main` `42411892072` executou a suíte completa com sucesso. O próprio documento do MVP8 diz que ele pode ser **aceito como cobertura técnica mínima sintética após CI verde**; essa aceitação é decisão do proprietário. Não equivale a GP-3 integral, a GP-4 nem a eficácia pedagógica.

## Decisões que só o proprietário pode tomar

1. ~~Aceitar o GP-3-MVP8~~ **Decidido em 07/11/2026: aceito** como cobertura técnica mínima sintética.
2. **ADR-013:** decidido em 07/11/2026 o repositório (`ufms-meu-estudo-dados`, privado), o escritor (a Zapia, pela API REST do GitHub com credencial própria; revisado em 07/11/2026) e a retenção (até a prova mais janela curta; revogação = apagar o repositório). Consentimento v1 aprovado e janela de 30 dias definidos em 07/11/2026. **Em aberto:** **criação do repositório pelo proprietário** e registro formal do consentimento antes do primeiro evento. Sem isso, nada de real é gravado e RM-02 a RM-05 e RM-08 não avançam.
3. **Começar a registrar uso real**, o que só vale depois do item 2.

## Limites

Nenhuma alteração de `settings.json`, regras, guardrails, `CURRENT.json`, `PROGRESS.csv` ou eventos. Nenhum dado pessoal. Nenhuma promoção de status de frente.
