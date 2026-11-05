# HANDOFF vigente — UFMS MEU ESTUDO

**Checkpoint 05/11/2026.** Autoridade operacional: `state/WORKFLOW.json` e GitHub autenticado.

## Estado
- Repositório público; `main` protegida; check obrigatório observado: `validate`. Dados individuais, tokens e relatórios privados não podem ser gravados.
- PRs integrados: #9, #19, #20, #21, #22, #23, #24, #27 e #28.
- Último merge: PR #28 / SIM-09, commit `c93fbfc8850133e2b12d8be2d56c98e2cc70a5cb`; CI pós-merge `42064489228`: **317 testes, success**.
- Única frente: SIM-03 / PR #29, branch `fix/sim03-fapec-cli-e2e-20261105`, base `main@c93fbfc8850133e2b12d8be2d56c98e2cc70a5cb`, fase `review`.
- SIM-03: monitor FAPEC read-only já integrado no PR #21; este PR adiciona prova CLI offline dos estados 0/2/3 e confirma que a execução por fixture não altera o edital original nem o registro de fontes.
- Limite: o workflow contém cron e `workflow_dispatch`, mas não foi observada execução com `event=schedule`; cron real permanece **NOT_VERIFIED**. A consulta cobre somente uma página FAPEC.
- Fonte canônica e alerta cronológico do Anexo II, p. 13, permanecem preservados; retificações não são aplicadas automaticamente.
- SPEC Cognitive Gates r2 continua documental: 0/27 provas E2E; GQ-D REPROVADA pendente de reauditoria, GQ-C NOT_RUN, GQ-O BLOCKED.
- Inventário SIM-09: 20 branches de trabalho além de `main`: 8 refs de PRs integrados e 12 refs históricas fechadas sem merge. Nenhuma branch apagada.
- Próxima tarefa após merge de SIM-03: SIM-06, conforme prioridade remanescente da fila. SIM-10 permanece `documentado`; não reabrir.

## START desta sessão — somente API GitHub
- HEAD remoto de origem: `c93fbfc8850133e2b12d8be2d56c98e2cc70a5cb`.
- Arquivos obrigatórios lidos no mesmo HEAD: `AGENTS.md` blob `047176c3a21befc6c1f85612e85a32f7d380ba69`; `ROADMAP.md` blob `6c63f266459db8fcda0c12f57c818ebf6145a566`; `memory/HANDOFF.md` blob `dc0024e9256208e77c7f565b60b3105fffa39a19`; `state/CURRENT.json` blob `f2df048a2bf5ffa4876298a4ebf66bed1767c45a`; `state/WORKFLOW.json` blob `7c2c6a9144d4677879e93c3ec2d96d771db18d2e`.
- `settings.json` lido: blob `ded39535d4a640cb2f7d34f15d3ef936d293bd76`; política confirmou `personal_results_writes_enabled=false`.
- **Limite de execução:** sem checkout local, bootstrap/roadmap/write hooks não foram executados nesta sessão. A alteração é feita somente em branch/PR; a CI remota executará os gates no SHA candidato. Não declarar equivalência aos hooks locais.
- `state/CURRENT.json`, `state/PROGRESS.csv`, eventos e PDF canônico não são modificados.

## Retomada
1. Confirmar PR único #29, HEAD exato, check `validate` e CI remota.
2. Revisar o diff do monitor e os testes CLI; corrigir qualquer falha no mesmo PR.
3. Antes do merge, exigir CI `success` no HEAD exato e branch `main` protegida; merge com SHA esperado.
4. Após merge, confirmar novo HEAD, CI pós-merge e ausência de PR aberto.
5. Manter branches históricas preservadas; nenhuma exclusão sem backup e pedido específico.

## Objetivo
Estudo UFMS cargos 523 e 324, edital 152/2026. O repositório é público; resultados individuais não são persistidos.
