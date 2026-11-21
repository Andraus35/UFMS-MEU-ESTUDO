# Plano de retomada até o fim do projeto (21/11/2026)

**Natureza:** instrução para a **próxima sessão** saber **exatamente por onde começar** e **esgotar**, em ordem, as pendências, a fila (`work_queue`) e o roadmap. **Não contém estado volátil** (SHA, número de PR, head): o estado vive em `state/WORKFLOW.json`, `ROADMAP.md` e `memory/HANDOFF.md`. Em conflito, valem `AGENTS.md`, `PRODUCT.md` e `ROADMAP.md`, nessa ordem.

## 0. Por onde começar (nesta ordem, sem pular)

1. Ler `AGENTS.md`, `ROADMAP.md`, `PRODUCT.md`, `memory/HANDOFF.md` (bloco "Retomada da próxima sessão"), `state/CURRENT.json` e `state/WORKFLOW.json`; rodar `python scripts/bootstrap.py --mode engineering` e `python scripts/next_task.py`.
2. **Confirmar no GitHub autenticado** o PR indicado em `active` de `state/WORKFLOW.json`: estado, branch, base, head, `merged_at` e CI. **Não inferir por memória.**
   - **PR ainda aberto:** trabalhar **só nele**; se não houver pedido de merge do proprietário, **aguardar** (o merge de arquivo de contrato exige o pedido expresso citando PR e head; "Mesclar" vale só com um único PR aberto).
   - **PR mesclado:** abrir o lote seguinte (seção 3) numa branch de trabalho nova, com `python scripts/record_merge_receipt.py` no **primeiro commit**; depois ajustar `next_task_after_merge` e a linha "Próxima tarefa" dos quatro documentos para **RM-08** (o gate recusa repetir a tarefa ativa e o script deixa RM-09).
3. Rodar `python scripts/single_flow_gate.py --check`, `python scripts/roadmap_gate.py --check`, `python scripts/governance_sync_gate.py` e `python scripts/doc_cohesion.py --check` antes de escrever e depois de cada commit.
4. Seguir a seção 3, **um lote por vez**: micro tarefas coesas da mesma frente no mesmo PR draft; se o próximo trabalho for de **outra frente**, o merge do lote atual vem **antes**.

## 1. Regras que não mudam

- **Uma tarefa → uma branch → um PR draft → testes → merge aprovado → próxima.** Merge só por pedido expresso do proprietário, com CI verde no head exato.
- **Arquivos de contrato** (`AGENTS.md`, `PRODUCT.md`, `agents/`, `config/agent_command_schema.json`, `scripts/agents_gate.py`, `.claude/`, `.github/`): só mudam com a **aprovação expressa do texto e do merge**.
- **A Zapia está liberada** a acessar TEC, Qconcursos e Gemini Notebook livremente (D-27, 21/11/2026). **Não reintroduzir** restrição de acesso, cota ou condição prévia às plataformas e ao Notebook (o teste `tests/test_sem_restricoes_de_acesso.py` trava isso na CI). Ao resolver conflito de merge, **não** trocar um arquivo inteiro pela versão do outro lado sem conferir (já houve regressão disso no `memory/HANDOFF.md`); depois de qualquer merge, rodar a suíte e comparar com o `main`.
- **Nenhum resultado pessoal** no repositório público; a flag `personal_results_writes_enabled` segue `false`; credencial nunca vai ao modelo.
- **Honestidade:** documento, teste offline e prompt **não provam** orquestração entre Zapia, Tutor e Coach, nem acesso à web, nem eficácia pedagógica.
- Tarefa do WORKFLOW só aceita id `RM-nn` ou `SIM-nn`; item novo em `work_queue` exige atualizar `tests/test_retomada_proxima_sessao.py`; `docs/canonicos` tem hash e não se edita sem refazer o hash; após cada squash o push normal é recusado: `git merge -s ours origin/<branch>` e empurrar (push forçado é negado pelo ambiente).

## 2. Mapa: o que está feito, o que é da sessão e o que é do proprietário

| Frente | Estado | Quem age |
|---|---|---|
| Liberação da Zapia, S9, S10, S15, S16, S17 (especificações) | Entregues; a S17 e a base cognitiva ficam no PR do lote A1 até o merge | Proprietário: pedido de merge do PR aberto |
| Referências canônicas nos perfis do Tutor e do Coach | No PR do lote A1 (contrato) | Proprietário: aprovar no merge |
| S16 T1 a T3 (nó do TEC, top 10, entrega diária) | **Não iniciadas**; offline e sintéticas | **Sessão**, sem depender de ninguém |
| E3 (pedir relatório; "Iniciar estudos" e "finalizar estudos") | Proposta de texto entregue; **não aplicada** | Proprietário aprova o texto e o merge; sessão aplica |
| Amostra FAPEC do 523 (137 contra 187) | Divergência não reconciliada | Proprietário traz nova amostra pela Zapia |
| P9 (renovar `zapia_dados` e `zapia token`) | **Pendente**; vence em 18/12/2026, aviso em 04/12/2026 | Proprietário |
| PJ (janela do piloto), RT, CM | **PJ bloqueada** pela aprovação expressa citando PR e head; RT depende da PJ; CM depende da RT e de ato no GitHub | Proprietário |
| N1 (teste real do Gemini Notebook), Z1 (exportação do TEC) | Nunca executados; a Zapia está liberada | Proprietário envia o prompt exato; sessão registra o relato |
| RM-08 (ciclo Tutor–Coach) | **Bloqueado**; reavaliação de 21/11/2026 | Depende da PJ, de resultado real consentido e da reauditoria do GQ-D |
| RM-09 (integrações) | `planejado`; Notebook, Zapia e GitHub Projects | Sessão especifica e prepara; provas reais dependem do proprietário |
| RM-10 (piloto) | **Bloqueado** | Depende da PJ e da privacidade provada |
| Já feitos pelo proprietário (conferidos em `owner_priorities`) | P1 a P8: Z1 respondida, risco registrado, C3, consentimento v4, C6, P7, P8 | Nada a fazer |

## 3. Fila de execução, em ordem (um lote por vez)

**Lote A, merge do PR aberto (ato do proprietário).** Entrada: CI verde no head atual. A sessão **confere** head e CI e **espera** o pedido ("Mesclar", se for o único PR aberto, ou com PR e head). Depois do merge, registrar o recibo no primeiro commit do lote B.

**Lote B, S16 T1 a T3 (autônomo, offline, sintético).** Mesma frente da rotina de estudo; deve terminar com um único PR.
1. **T1:** estrutura do nó do TEC com caminho completo, origem, modalidade (1 ou 2) e percentuais da matéria e do caderno, cada um com denominador (S16-R2, R3, R5).
2. **T2:** seleção do top 10 por matéria a partir de percentuais fornecidos: nós terminais sem somar pai e filho, ordem decrescente, empate no 10º incluído até o teto de 15 (acima, apresentar ao proprietário), lista parcial com menos de 10 folhas, recusa com `PENDENCIA_ABERTA` para amostra não definitiva (específicos do 523) e para percentual ausente (S16-R4, R6).
3. **T3:** formato da entrega diária (cargo, matéria, caminho, posição e percentual verificados, material, atividade, quantidade definida pelo Tutor, filtros, objetivo) e recorte do plano ao top 10 (S16-R8, R9, C1 e C2 decididos).
Testes de contrato e **contraprovas** (ALTA e MEDIA exigem testes negativos); **sem** dado real, sem rede, sem gravação de resultado, sem versionar os números das amostras (P6 da S16).

**Lote C, roteiros do proprietário (documentação, sem executar nada por ele).** Passo a passo, com comandos prontos e frases literais, para: **P9** (renovação dos tokens antes de 04/12/2026), **PJ** (abertura e fechamento da janela do piloto, com os dois `ATUALIZAR`), **CM** (identidade do agente e `CODEOWNERS` ativo) e a **reconciliação do 523** (repetir a consulta FAPEC e comparar com os 137). Entrega em `docs/governanca/`, com teste de contrato.

**Lote D, RM-09 offline.** Especificar e preparar as provas de autorização do fluxo com Gemini Notebook (N1), Zapia e GitHub Projects (sem reabrir o PR legado da ponte Telegram e Calendar, arquivado sem merge), **só como roteiro e teste de contrato**; a prova real é do proprietário.

**Lote E, E3 aplicada.** Só depois da **aprovação expressa do texto** da E3 e da janela do piloto provar o fluxo (decisão F3): aplicar a operação `pedir_relatorio_desempenho` e os eventos de início e fim no esquema, no gate e em `agents/`, com os testes do gate de agentes.

**Lote F, destravar o RM-08 e o RM-10.** Só quando houver **resultado real consentido** e a PJ aprovada: tarefas RT, CM, depois a avaliação do RM-08 e o piloto (RM-10). Nada disso é da sessão sozinha.

## 4. Quando a sessão pode dizer "esgotado"

A sessão declara esgotado **somente** quando: (1) não há PR aberto sem pedido de merge pendente do proprietário; (2) os lotes B, C e D estão mesclados; (3) cada item restante de `work_queue` (E3, PJ, RT, CM) e de `owner_priorities` (P9) tem, no HANDOFF, **o ato exato do proprietário, a frase literal e o que ele destrava**; (4) o RM-08 e o RM-10 estão `bloqueado` com a causa e o insumo que falta; (5) os gates e a suíte completa estão verdes. **Antes disso, continuar o próximo lote**; não parar por conforto.

## 5. O que fazer em cada situação inesperada

- **CI vermelha por corrida (primeiro `validate` do push):** reexecutar só o job; se persistir, ler o log e corrigir no mesmo PR.
- **Dois PRs abertos:** o `single_flow_gate --remote` reprova; **não** abrir outro; resolver com o proprietário (fechar um ou mesclar o outro).
- **Conflito de merge nos quatro documentos de estado:** refazer o recibo com `record_merge_receipt.py` sobre a versão do `main`, depois rodar os gates e a suíte (o teste de regressão de acesso reprova se uma restrição retirada voltar).
- **Divergência de dados da Zapia (ex.: 137 e 187):** registrar como "não definitivo"; **não** inventar regra nem reconciliar por estimativa.
- **Pedido novo do proprietário de outra frente:** terminar e mesclar o lote atual, **depois** abrir o novo.

## Limites

Este plano é **instrução**, não prova de que algo funcione: não implanta, não testa em conta real e não substitui a revisão humana. O proprietário pode mudar a ordem por decisão expressa.
