# RM-08 — reavaliação dos bloqueadores no HEAD vigente (21/11/2026)

**Objeto:** `main@2f908c4d781c9a92c2c86ea7f0412383fae0cb93` (PR #149 mesclado). **Base:** `docs/pedagogia/RM08_BASELINE_FORMAL_20261107.md` (baseline de 07/11/2026, `main@33b3b18`).
**Natureza:** reavaliação documental, só leitura do repositório. **Decisão: RM-08 formal permanece `bloqueado`.** Esta reavaliação não homologa GP-3, GQ-D, GQ-C, GQ-O nem GP-4, não habilita BUILD, credencial, integração externa nem escrita de resultados pessoais, e não altera a baseline.

## 1. O que mudou desde a baseline

Avanço de engenharia e de especificação, **sem prova operacional**:

| Frente | O que existe agora | Limite que permanece |
|---|---|---|
| Plataformas (S9, L1) | `scripts/platform_read_guard.py` com padrão liberado; a Zapia está **liberada** pelo proprietário (decisão de 21/11/2026, D-27) | Guarda offline; nenhuma leitura real foi provada |
| Notebook (S10, N2) | Especificação e validador offline do prompt do Tutor | Nenhum teste real no Notebook |
| Exportação do TEC (L2) | `scripts/tec_export_converter.py` sobre objeto já carregado | Sem execução real do pedido (Z1 não executada) |
| Runtime e entrega (S14) | Recibo de START (`scripts/start_receipt.py`) e verificador de entrega (`scripts/delivery_gate.py`) | Garantias verificáveis, não prova de compreensão nem de implantação |
| Orquestração e rotina (S15) | Especificação de fluxo, rotina e fonte de tempo | Só texto; nenhum job, lembrete ou tarefa criado |
| Canal de comandos | `scripts/command_box.py` e `scripts/command_box_runner.py` | Origem do comando não provada (S6-R7) |

## 2. Estado de cada bloqueador

| Bloqueador (baseline, seção 6) | Situação em 21/11/2026 |
|---|---|
| Reauditoria GQ-D | **Não feita.** Nenhuma auditoria independente nova no HEAD; a baseline segue o último registro |
| GQ-C | **NOT_RUN**, sem recibo novo |
| GQ-O | **BLOCKED**; sem implantação, nada a provar |
| GP-3 | **Não homologado**; o MVP8 segue como cobertura sintética mínima |
| Persistência e replay | **Ausentes**: `personal_results_writes_enabled=false`, repositório privado de dados e consentimento v4 sem prova |
| Ciclo Tutor–Coach | **Só sintético** (RM-08-PREP); sem execução humana real, sem resultado real, sem recuperação entre sessões |

Estado de dados conferido no HEAD: `state/CURRENT.json` em E0, zero eventos e zero resultados; a flag de escrita pessoal é `false`.

## 3. Insumos que faltam do proprietário

1. Primeiros **eventos reais de estudo** (resultado de um caderno resolvido no TEC ou no Qconcursos), pela entrada manual ou pelo caminho aprovado.
2. **Consentimento v4** e criação do repositório privado de dados, com a prova do fluxo de escrita.
3. **Reauditoria independente do GQ-D** no HEAD aplicável.

Enquanto faltarem esses itens, nenhuma implementação do RM-08 formal deve começar. Registrado que, na pergunta de insumos desta rodada, o proprietário não indicou preferência: **nenhum insumo novo foi assumido**.

## 4. Decisão e próxima ação

RM-08 formal **continua bloqueado**. O próximo item da fila é o RM-09 (integrações), por esta frente ser encerrada; a retomada do RM-08 depende dos insumos da seção 3.

## 5. Limites

Reavaliação documental no HEAD citado; **não** é auditoria independente, teste ponta a ponta nem prova de implantação. As frentes que avançaram são especificação e código offline; a CI verde valida o commit, não a eficácia pedagógica. Hooks locais e CI não substituem a revisão humana.
