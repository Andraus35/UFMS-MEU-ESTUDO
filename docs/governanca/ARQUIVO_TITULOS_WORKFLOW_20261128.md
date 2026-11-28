# Arquivo dos títulos completos da fila do WORKFLOW (28/11/2026)

**Natureza:** arquivo **sem alteração de texto**. Os títulos abaixo foram encurtados em `state/WORKFLOW.json` (itens já feitos) para o documento caber no limite de 64 KiB do START automático (`agent_entrypoint`), que o último recibo de merge deixou a ~550 bytes do teto. O estado vivo continua em `state/WORKFLOW.json`; aqui mora o texto integral original de cada título. Complementa `ARQUIVO_TITULOS_WORKFLOW_20261125.md`. Ficaram inteiros os títulos que testes fixam (E1, E2, E3, HOOK2, L2, N2, Z1 e os que citam S21).

## C3

Roteiro do Termux da C3 (ato do proprietário): cria `entrada` privado, confere forks e colaboradores, limita as ações, guarda o segredo do fluxo e instala o fluxo com o SHA fixado; o roteiro é código offline com teste, a execução é do proprietário

## L1

Módulo offline de leitura somente leitura (S9-R2 a R5): lista de domínios, recusa de escrita, limite de taxa com relógio injetado, saída sem cookie, token nem HTML e filtro de instrução embutida; sem rede e sem navegador, com páginas sintéticas

## C5R

Roteiro do Termux da primeira metade da C5 (ato do proprietário), com a flag desligada: o token "zapia token" grava um arquivo sintético na fila de entrada, o fluxo roda, o runner responde FLAG_DESLIGADA e dados não muda; o roteiro é código offline com teste, a execução é do proprietário; a promoção até dados exige a C6

## V4F

Subcomando consentir-v4 do ufms.sh (ato do proprietário): registra consent-v4.json no repositório privado só com a frase CONSINTO v4 e leitura de volta, a partir do texto aprovado; não habilita a flag nem a leitura por sessões (C6)

## C6A

Guarda offline da leitura de projeções por sessões do app Claude (S6-R9): exige consentimento v4 íntegro, projeção em lista fechada proposta sem texto de questão nem identificador de conta, recusa histórico bruto; não liga a flag nem dá acesso a sessão alguma (a C6 é PR próprio com aprovação expressa)

## C6B

Promoção exige o consentimento v4 (decisão do proprietário de 18/11/2026): o runner lê consent-v4.json e só aceita o v4 íntegro (o v2 e o v3 não bastam), com contraprovas; a flag segue falsa e o fluxo instalado precisa ser reinstalado com o novo SHA pelo proprietário

## C6C

Flag própria do fluxo privado (storage.private_flow_promotion_enabled, falsa) lida pelo runner e pelo executor da caixa, no lugar da personal_results_writes_enabled do público, que fica falsa para sempre (decisão do proprietário de 18/11/2026); a C6 liga só a nova, em PR próprio com aprovação expressa

## C6D

Marca de evento sintético (decisão do proprietário de 18/11/2026): a entrada aceita o campo opcional sintetico (só o booleano true), o histórico guarda a marca no envelope e as projeções descartam o evento de teste (fail-closed: marca ambígua ou registro malformado também sai); prepara a segunda metade da C5 sem poluir o histórico real; a flag segue falsa

## C5P

Roteiro do Termux da segunda metade da C5 (ato do proprietário), com a flag do fluxo ligada pela C6: a Zapia grava uma entrada sintética na fila, o fluxo a promove a dados com a marca de teste no envelope, e o roteiro confere sucesso do fluxo, +1 evento, cabeça de dados, envelope, fila consumida e recibo; bloqueia se a flag não estiver ligada no SHA fixado pelo fluxo; o evento sintético fica no histórico (só de acréscimo)

## C6

C6, janela curta: liga só private_flow_promotion_enabled (a do público nunca liga), por PR próprio com aprovação expressa do proprietário; o fluxo só passa a valer depois de reinstalado com o SHA do merge (ATUALIZAR); o fechamento é outro PR que volta a flag a false mais nova reinstalação

## C5F

Correções da prova real de 18/11/2026: o runner diz qual token está malformado (conjunto fechado, nunca o valor); o roteiro da C3 recusa token com CR, invisível ou espaço; os dois roteiros da C5 não caem quando a conclusão do fluxo vem vazia; a prova da promoção exige a fila vazia; a janela da C6 segue aberta até a prova passar

## C5G

Causa real da falha do fluxo na prova de 18/11/2026: o GITHUB_TOKEN do Actions (rótulo entrada) passava de 255 caracteres e o runner o recusava (TOKEN_INVALIDO:entrada); o teto vai a 1024 (ASCII imprimível, sem espaço), o diagnóstico passa a trazer comprimento e se é imprimível (metadados, nunca o valor) e os roteiros do Termux alinham o limite; a janela da C6 segue aberta até a prova passar

## PROJ

Gerador offline de projeções para as sessões do app Claude (decisão do proprietário de 18/11/2026): função pura que recebe registros do histórico já (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## PF

Pré-voo do piloto (S11-R2): script somente leitura, tudo ou nada, com leituras injetadas: duas flags false em repouso, hash do fluxo igual ao modelo do SHA da main, repositórios privados sem forks e convites, consentimento v4 íntegro, validade dos tokens com margem, CI verde no HEAD; contraprova por item vermelho; saída sem segredo

## PREL

Relatório do ciclo e semáforo do piloto (S11-R10, R11, R13): script que monta o relatório sem dado pessoal (contagens, SHAs, hashes, níveis, as oito etapas com prova ou NÃO PROVADA, lacunas, linha Não provado) e decide vermelho, âmbar ou verde pelos gatilhos fixados antes; recusa campo fora da lista

## S14

Especificação do runtime operacional do harness (regra do proprietário de 19/11/2026: LLM livre na cognição, condicionado nas leituras e entregas por (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## GE

Verificador de entrega (S14-R5 a R8, R11, R13, R17): envelope fechado, alegações declaradas e verificadas contra edital e projeção, modo sombra e modo bloqueio, registro sem dado pessoal; COMANDO sempre em bloqueio; sem rede, credencial nem modelo

## HOOK3

Prorrogação do hook Stop de entrega final até o fim do piloto (decisão do proprietário de 20/11/2026, por escolha em pergunta de fim de rodada): .claude/hooks/entrega_final.py hoje vale só até 20/11/2026; a mudança é pequena (a data limite passa a ser o fechamento da janela do piloto), altera .claude/ (arquivo de contrato, CODEOWNERS) e o merge continua sendo o Mesclar dele; o hook falha aberto e segue sendo lembrete, não controle (S14-R17)

## RS

Recibo de START verificável (S14-R2, R3): o broker emite o recibo (SHA, papel, hashes) e o verificador recalcula no repositório no SHA fixado; recusa (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## AE

Avaliação offline do verificador de entrega (S14-R12a): suíte de envelopes sintéticos válidos e adversariais com resultado esperado determinístico; fecha parte de RM-06 e RM-07 só para o que é gateável; nenhum portão chama modelo

## RG

Ligação do recibo de START ao verificador de entrega (S14-R3): o delivery_gate recalcula o recibo esperado no checkout do contrato, no SHA fixado, com o start_receipt; papel sem START definido, SHA ruim ou falha ao calcular deixam o recibo não conferido (fail-closed); sem rede e sem modelo. Mesma frente do RS, do GE e do AE (lote S14); item registrado na decisão do proprietário de 21/11/2026

## HOOK4

Alinhamento do hook Stop de perguntas de fim de rodada à regra de merge por lote do AGENTS.md (E11): troca 'Uma tarefa por vez' por 'Um lote por vez'; arquivo de contrato em .claude/, merge só com aprovação expressa do proprietário; item registrado na decisão de 21/11/2026

## S15

Orquestração do ciclo: fluxo, rotina e fonte de tempo (decisão do proprietário de 21/11/2026): unifica as decisões de fluxo e rotina de Tutor, Coach, Zapia e estudante (S1 a S14, PRODUCT.md) e define como proposta a fonte de verdade do tempo (relógio injetado em UTC, fuso e dia de estudo, idade da projeção, quem acorda os agentes, prova do gatilho sem efeito); pesquisa obrigatória; não implanta nem homologa; liga ao RM-09

## S16

Rotina de estudo UFMS 2027 (requisitos do proprietário de 21/11/2026): top 10 por matéria pelos percentuais do guia TEC, hierarquia e origem de cada nó, filtros, entrega diária, comandos de início e encerramento, Notebook e lacunas do guia; separa intenção, especificado, implementado, testado e bloqueado; registra pendências P1 a P5 e conflitos C1 a C3 sem inventar regra; não lista o top 10 nem implanta; liga ao RM-09

## S17

Pesquisa e autonomia cognitiva do Tutor e do Coach (requisito do proprietário de 21/11/2026): pesquisa web só leitura para estado da arte e melhores (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## TOP1

S16 T1: nó do TEC com caminho inteiro, origem, modalidade e percentuais da matéria e do caderno com denominador (S16-R1, R2, R3, R5); offline, sintético, sem gravar resultado; recusa pai marcado folha, soma de folhas acima de 100% e identidade repetida; desconhecido nunca é preenchido

## TOP2

S16 T2: seleção do top 10 por matéria a partir de percentuais fornecidos (S16-R4, R5, R6; P1 a P5, P7, P8): só modalidade 1 e nós terminais, empate no 10º incluído até o teto de 15 (acima, decisão do proprietário sem lista), lista parcial com menos de 10 folhas, PENDENCIA_ABERTA para amostra ausente, não definitiva ou instável, recusa sem nenhum percentual; correspondência com o guia só por mapa explícito; função pura, sem lista embutida

## TOP3

S16 T3: entrega diária (S16-R7, R8, R9) e recorte do plano ao top 10 (C2, R4, R14): cargo, matéria, caminho, posição e percentual só quando (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## S18

Inteligência Motivacional e Comportamental (IMC) do Coach (pedido do proprietário de 21/11/2026): especificação com pesquisa obrigatória; canônico (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## S19

Tutor e Coach usam os recursos da Zapia como interface com o estudante (pedido do proprietário de 21/11/2026, com o PDF "Agendamentos e gatilhos na (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## HOOKG

Hook geral claude-context-guard (pedido do proprietário de 21/11/2026): mede a janela de contexto e, aos 50%, injeta a ordem de preparar memória e o (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## HOOKP

Hook de perguntas de fim de rodada pergunta só o que mudou (pedido do proprietário de 21/11/2026): o hook continua só lendo e usa o transcript (último Estado lido agora igual ao atual e AskUserQuestion depois dele: não bloqueia de novo; estado mudado: mostra antes e agora); altera .claude/hooks/perguntas_boas_praticas.py (contrato, aprovação expressa do texto e do merge); na dúvida pergunta como antes; não observado em Claude Code real

## S20

Automação ponta a ponta: Tutor e Coach acionam a Zapia, e o Gemini Notebook por ela, sem o proprietário colar prompts (pedido de 21/11/2026): especificação com pesquisa (D-16), mapa do que falta (P1 a P8), decisões D1 a D3 do proprietário sem adoção e fases F0 a F5; só especifica, não implanta; fecha com S5, S6, S10, S14, S15 e S19

## HOOKR

Hook de passagem desarma a sessão quando a medição cai abaixo do limite (pedido do proprietário de 21/11/2026, depois do falso alarme de 52% com (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## GAP-A

Lote da fila de gaps de 21/11/2026 (docs/governanca/FILA_GAPS_E_DIVERGENCIAS_20261121.md); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA; GA-1 a GA-5: esquema de params por operação, filtros no texto de params do COMANDO, hash do prompt, LEMBRETE com várias atividades e formato único da chave de idempotência

## GAP-A2

Lote da fila de gaps de 21/11/2026 (docs/governanca/FILA_GAPS_E_DIVERGENCIAS_20261121.md), continuação do GAP-A: GA-3 a GA-5 (hash do prompt (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## GAP-B

Lote da fila de gaps de 21/11/2026 (docs/governanca/FILA_GAPS_E_DIVERGENCIAS_20261121.md); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA; GB-1 e GB-2: classificação do dia (S15-R16) como função pura e gerado_em como instante UTC

## GAP-C

Lote da fila de gaps de 21/11/2026 (docs/governanca/FILA_GAPS_E_DIVERGENCIAS_20261121.md); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA; GC-1 a GC-3: resumo de estudo de uma página, SHA externo do START e reconciliação das divergências documentais

## GAP-D

Lote da fila de gaps de 21/11/2026 (docs/governanca/FILA_GAPS_E_DIVERGENCIAS_20261121.md); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA; GD-1 a GD-5: formato Tutor→Coach, meta pretendida, filtro de dado pessoal, âncora da Lei 8.112 e decision_queue

## GAP-E

Lote da fila de gaps de 21/11/2026 (docs/governanca/FILA_GAPS_E_DIVERGENCIAS_20261121.md); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA; GE-1 e GE-2: derivado paginado do Manual (texto integral só no privado) e gates G-MOT verificáveis; aplicar em agents/ exige aprovação expressa

## COR-A

Lote de correção da fila de auditoria Tutor e Coach de 21/11/2026 (docs/governanca/FILA_AUDITORIA_TUTOR_COACH_20261121.md); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA; AT-1, AT-2, AC-1 e AC-2: entrega integrada (o delivery_gate confere o prompt do Notebook, a idade da projeção e recalcula o hash do lembrete com os ids; formato único do prompt)

## COR-B

Lote de correção da fila de auditoria Tutor e Coach de 21/11/2026 (docs/governanca/FILA_AUDITORIA_TUTOR_COACH_20261121.md); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA; AC-3, AC-4, AC-8 e o decisor do teto diário (S8-R1, S15-R17): id fixo da chave briefing, descanso e pendência no lembrete2, chave em maiúsculas, teto da janela, data de consultar_agenda_minima

## COR-C

Lote de correção da fila de auditoria Tutor e Coach de 21/11/2026 (docs/governanca/FILA_AUDITORIA_TUTOR_COACH_20261121.md); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA; AT-3 a AT-7: filtros de conteúdo (URL sem esquema, instrução embutida e homóglifo, texto de questão no prompt, URL e instrução nas mensagens e no handoff, tokens de efeito em inglês na leitura de plataformas)

## COR-D

Lote de correção da fila de auditoria Tutor e Coach de 21/11/2026 (docs/governanca/FILA_AUDITORIA_TUTOR_COACH_20261121.md); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA; AC-5, AC-6 e AC-7: gates G-MOT ligados à entrega, fail-closed em tipo não booleano, paráfrases e falsos positivos, léxico de desempenho e disponibilidade (continua heurístico); aplicar em agents/ exige aprovação expressa

## ZAPIA-F1

Ligação do Tutor e do Coach à Zapia, F0/F1 offline (pedido do proprietário de 22/11/2026): notificação na Zapia em nome dos agentes, com recibo de volta conferido por código; provado em 22/11/2026 com par sintético (E21); detalhe em docs/governanca/E20_ZAPIA_ENTREGA_F1.md e E21_ZAPIA_F1_PROVA_REAL.md

## COR-E

Lote de correção da fila de auditoria Tutor e Coach de 21/11/2026 (docs/governanca/FILA_AUDITORIA_TUTOR_COACH_20261121.md); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA; AT-8 e AC-9: lista de permissão de caminhos de leitura, citação por palavra inteira e hash por página no manifesto do Manual, idade da projeção por data

## ZAPIA-F2a

Rotina de teste da Zapia, execução única (S20-R6, S15-R4, S8-R8; pedido do proprietário de 22/11/2026, depois do F1 provado): roteiro com a frase (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## ZAPIA-APL

Aplicação da operação agendar_rotina (E24, aprovada pela decisão do proprietário de 23/11/2026 de excluir o AUTORIZO, E26): operação compartilhada (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## ZAPIA-CTX

Alimentar o runner real da caixa com o contexto do agendar_rotina (E27): hashes_promovidos (leitura dos recibos de comandos/recibos) e (título integral em docs/governanca/ARQUIVO_TITULOS_WORKFLOW_20261125.md)

## ZAPIA-F3

Teste 'rotina cria rotina' (E25, E29): REFUTADO em 23/11/2026 (a Zapia respondeu que não consegue criar rotina de dentro de rotina); a antecedência mínima de 90 min foi aplicada; detalhe no E29, E30 e E32

## ZAPIA-EMISSOR

Lote 1 da ligação (E33): emissor pelo fluxo (o entrada abre a issue-campainha ao promover, título fixo, corpo vazio) e emenda do D-28 (hook de Gmail só com remetente e assunto como campainha); contrato: PRODUCT.md e fluxo, aprovação expressa do texto e do merge; detalhe no E33 e no E34

## ZAPIA-SUBAGENTS

Lote 2 da ligação (E33): Tutor e Coach como subagents somente leitura, offline e sintético, com harness que valida cada comando pelos gates e produz a matriz operação x gate, com contraprovas; o que é só verificável ou não gateável não vira enforçado; sem Zapia e sem entrada; detalhe no E33 e no E35
