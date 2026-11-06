# RM-08-PREP — preparação offline sintética do ciclo Tutor–Coach

**Data:** 06/11/2026  
**Base:** `main@9525a2dd5a6e3646eaffee4da4b1dd1fca3e1fe7`  
**Natureza:** subescopo autorizado de preparação; não inicia nem promove a RM-08 formal.  
**Estado formal da RM-08:** `bloqueado`.

## Objetivo restrito

Exercitar em memória, com fixtures inteiramente sintéticas, o encadeamento:

1. recomendação determinística por snapshot de fila;
2. plano offline de caderno sem criação em plataforma;
3. simulação explícita de execução humana;
4. recepção e validação de resultado sintético;
5. reconstrução informacional e derivação E0–E4;
6. nova fila calculada com fatores explicitamente fornecidos.

A entrega é um protótipo puro em `scripts/tutor_coach_offline_cycle.py`, integrado aos componentes já existentes de fila, prescrição, ingestão e evidências. Não substitui esses contratos.

## Contrato do protótipo

A função `run_offline_cycle` exige:
- candidatos com IDs `SYNTH-`, cargos 523/324, tópicos, fatores e justificativa explícitos;
- snapshots temporais ISO 8601 com fuso, SHA Git e versão do edital;
- execução com `data_origin=synthetic_fixture`, `status=simulated` e referência `synthetic-fixture://`;
- relatório com IDs `SYNTH-`, referência sintética, plataforma `manual_search` e convenção de contagem explícita;
- tópico do resultado contido no escopo da recomendação.

A normalização usa `normalize_external_report`. A validação do schema usa `validate_attempt_events` somente dentro da sandbox sintética em memória; não concede autorização de persistência. A reconstrução usa `rebuild_attempts`; a qualidade de evidência usa `derive_evidence_level`.

## Reavaliação sem inferência indevida

A segunda fila usa uma lista `next_candidates` explicitamente fornecida, com fatores e justificativas próprios. O protótipo **não** converte percentual de acertos em domínio, retenção, chance de aprovação ou fator de prioridade. Sem dados por tópico, a projeção continua agregada (E1); com decomposição sintética válida por tópico, pode chegar a E2, sem afirmar independência.

## Barreiras verificáveis

- Não há chamadas de rede, API, TEC, Qconcursos, Zapia ou agenda.
- Não cria IDs de caderno de plataforma nem afirma que um caderno foi criado.
- Não escreve em `state/events`, `state/CURRENT.json`, `state/PROGRESS.csv` ou qualquer armazenamento.
- Não habilita `personal_results_writes_enabled` e não altera `settings.json`.
- Rejeita origem, IDs e referências não sintéticos, contagens incoerentes, tópico fora do escopo, plataforma externa e execução não simulada.
- Não altera a baseline formal da RM-08 e não homologa GP-4.

## Testes

`tests/test_tutor_coach_offline_cycle.py` cobre o caminho sintético completo, reprodutibilidade, E1/E2, ausência de efeitos, contagens incoerentes, origem/IDs/referências inválidas, recomendação divergente, IDs externos, tópicos fora do escopo, execução real e ausência de candidato elegível.

A CI central precisa executar a suíte no HEAD final do PR. A escrita via API GitHub não executa os hooks locais; esse limite deve permanecer no handoff.

## Critério de saída desta preparação

Protótipo, documentação, contraprovas e CI no HEAD do PR aprovados. Mesmo com CI verde, a conclusão será somente **preparação offline sintética testada**. RM-08 formal continua bloqueada até baseline auditada própria e gates técnicos/independentes; GP-4 real exige o ciclo controlado, readback autorizado e recuperação entre sessões em ambiente permitido.
