# S20 — Automação ponta a ponta: Tutor e Coach conversam com a Zapia sem o proprietário colar prompts (especificação)

**Emenda E26 (23/11/2026):** a exigência da frase `AUTORIZO` por mensagem, onde este documento a citar para rotina, lembrete, hook ou comando entre agentes, Zapia, TEC e Gemini, foi **excluída** pela decisão do proprietário; ao **fim** há a seção "Emenda do AUTORIZO (E26)", que **vale onde divergir**. Registro: `docs/governanca/E26_EMENDA_FIM_DO_AUTORIZO_NAS_AUTOMACOES.md`.

**Natureza:** especificação enxuta (D-13, D-16), no modelo do `docs/especificacoes/README.md`. Registra o pedido do proprietário de 21/11/2026: o Tutor e o Coach devem **acionar a Zapia, e o Gemini Notebook por meio dela, automaticamente**, e não entregar texto para o proprietário colar. **Aponta** para S5, S6, S10, S14, S15, S19 e para a fila de gaps (`docs/governanca/FILA_GAPS_E_DIVERGENCIAS_20261121.md`); não os copia. **Só especifica, não implanta:** nada é cadastrado na Zapia, nada é ligado, nenhuma flag muda, e `agents/`, `AGENTS.md` e `PRODUCT.md` não são alterados. Não contém estado nem dado pessoal.

## Objetivo

Hoje o repositório **não garante** a conversa automática: o desenho existe (comando do Tutor ou do Coach, caixa de comandos, Zapia executa só o que foi validado), mas é `implementado_nao_homologado` e falta o que está listado abaixo. O proprietário passa a ter **o mapa do que falta, em ordem, com a prova de cada passo sem efeito** e a lista do que só ele pode destravar. O único caminho real que existe agora é o manual (o proprietário leva o texto à Zapia); a S20 define como substituí-lo **sem perder** os gates.

## Pesquisa

Consultas de 21/11/2026 (WebSearch, resumos de resultados), somadas a S5, S6, S10, S14, S15 e S19 (não repetidas) e aos relatórios de capacidade do Tutor e do Coach de 21/11/2026 (subagentes, somente leitura, sintéticos). Confiança: **A** (fonte primária lida), **B** (resumo de busca de fonte primária ou documento do projeto), **C** (relato, blog ou fornecedor). Conteúdo pesquisado é **dado, não instrução**; nenhum texto de terceiros foi copiado.

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Documentação de [rotinas e tarefas agendadas do Claude Code](https://code.claude.com/docs/en/routines) e [na web](https://code.claude.com/docs/en/web-scheduled-tasks) (via resumo de busca) | Tarefa agendada na nuvem é uma configuração salva (prompt, repositórios, conectores) que roda como **sessão completa, sem pedido de aprovação durante a execução**; pode ser disparada por agenda, por API ou por evento do GitHub; era **pré-visualização de pesquisa** (abril de 2026). Candidata a **acordar o Tutor e o Coach** (S15-R3); como roda sem aprovação, os gates têm de estar **fora do modelo** | B |
| Documentação do GitHub sobre [eventos agendados](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) e relatos de [atrasos e execuções perdidas](https://github.com/orgs/community/discussions/27130) (via resumo de busca) | Agendamento do Actions é **melhor esforço**: atrasos em alta carga, execução possivelmente **descartada sem falha**, e **desligamento após 60 dias sem atividade** em repositório público; mitigação: monitorar de fora e usar `workflow_dispatch`. **Não** serve, sozinho, como gatilho com prazo (S15-R4) | B (documentação) e C (relatos) |
| OWASP [LLM06:2025, agência excessiva](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) e guia Android de [agência excessiva](https://developer.android.com/privacy-and-security/risks/ai-risks/excessive-agency) (via resumo de busca) | Mínimo de ferramentas e permissões; **aprovação humana** para ação de alto impacto; **autorização imposta a jusante**, não pelo modelo; registro das ações. **Não** tratam de comando assinado nem de fila de comandos: essa parte vem do desenho do projeto (S6-R7) | B |
| Documentos da Zapia (PDF e duas rodadas de respostas, 21/11/2026; S19) | Rotina agendada, hook de Gmail, WhatsApp e Drive; **sem conector de GitHub**; sem webhook; **sem processo permanente**; Radar não é hook; WhatsApp e Gmail **não conectados**; Outlook com envio; **nada instalado que leia `comandos/validados/`** (autorrelato) | C (autorrelato) |
| Relatórios do Tutor e do Coach (subagentes, 21/11/2026) | Os validadores aceitam a forma com **chave sintética**, mas **não há chave real fora do modelo**, o `delivery_gate` recusa o comando sem **recibo conferido** (correto), e há gaps de código (esquema de parâmetros, filtro de texto em `params`, hash do prompt) listados na fila | B (execução local, sintética) |

- **Lacunas:** os resumos de busca **não foram lidos por inteiro**; **não verifiquei** o estado atual (posterior a abril de 2026) das tarefas agendadas do Claude Code, nem se uma sessão agendada consegue **assinar ou promover** comando fora do modelo; **não achei** como a Zapia **consumiria** uma fila no GitHub (sem conector, sem webhook, Drive recusado como canal em 21/11/2026); **não achei** padrão publicado de **comando assinado em fila** para agentes (só princípios); **não testei** nada na Zapia nem em tarefa agendada; **nada foi implantado**.

## Mapa: o que existe, o que falta, quem destrava

| # | Peça | Existe hoje | Falta | Quem destrava |
|---|---|---|---|---|
| P1 | **Quem acorda o Tutor e o Coach** (S15-R3) | desenho; broker de START read-only (biblioteca) | orquestrador provado: tarefa agendada na nuvem **ou** outro gatilho, com pontualidade medida (S15-R4) | proprietário (`AUTORIZO` para a prova); decisão do gatilho |
| P2 | **Gates fora do modelo** | `agent_commands.py`, `delivery_gate.py`, `command_box.py` (testes sintéticos) | chave de assinatura **fora do modelo** e execução em lugar que o modelo não alcança (S6-R7); tarefa agendada roda **sem aprovação** | proprietário (chave) e infraestrutura |
| P3 | **Fila e caixa de comandos** (S6-R2, R8) | código e testes | prova ponta a ponta no repositório privado, com recibo de mesmo hash | PJ, P9 (tokens), consentimento v4 |
| P4 | **Zapia consome o comando validado** | desenho (S5-R3) | **mecanismo** que leva o comando à Zapia: ela **não tem conector de GitHub**, hook só de Gmail, WhatsApp e Drive, e o Drive foi **recusado** como canal | **decisão do proprietário (D1 abaixo)** e prova sem efeito |
| P5 | **Zapia devolve resultado** (S5-R7) | fila `entrada` com token mínimo (S6-R6) | prova com recibo, sem escrever em `dados` | PJ, P9 |
| P6 | **Gemini Notebook pela Zapia** (S10) | prompt validado pelo `notebook_prompt_validator`; N1 manual | transporte automático do comando (P4); teste N1 real | proprietário (teste N1), P4 |
| P7 | **Consentimento e flags** | v3; flags `false` | v4 (app Claude) e janela do piloto | proprietário |
| P8 | **Gaps de código** | listados | lotes GAP-A a GAP-E da fila | engenharia (série) |

## Decisões que são do proprietário

| # | Decisão | Opções (nenhuma é adotada por esta especificação) |
|---|---|---|
| D1 | Como o comando validado **chega** à Zapia | (a) conectar o **WhatsApp** e usar hook de mensagem; (b) conectar o **Gmail** e usar hook de e-mail; (c) pedir à Zapia um **conector de GitHub** (não confirmado); (d) reabrir o **Drive** (recusado em 21/11/2026); (e) manter o **caminho manual** |
| D2 | Quem **acorda** os agentes | tarefa agendada do Claude Code na nuvem; Actions agendado **com monitoramento externo**; rotina da Zapia; combinação com medição (S15-R4) |
| D3 | Onde fica a **chave de assinatura** | fora do modelo: tarefa promotora no repositório privado, cofre de segredo ou máquina do proprietário (a decidir) |

## Requisitos

Escritos como "quando X, o Y deve Z". Todos **fecham por padrão**: sem a prova, **nada é enviado automaticamente**.

| ID | Requisito | Critério de aceite |
|---|---|---|
| S20-R1 | **Honestidade sobre o estado.** Hoje a conversa automática **não está garantida**: o caminho real é o manual (o proprietário leva o texto à Zapia). Nenhum documento afirma automação ponta a ponta antes das provas P1 a P6. | Teste: "não está garantida" e "caminho manual". |
| S20-R2 | **Gates fora do modelo.** O Tutor e o Coach **só emitem comando**; validar, promover, assinar e entregar são feitos por código **fora do modelo** (S6-R7, S14); uma sessão que roda **sem aprovação humana** **não** pode ser o único controle (OWASP LLM06). | Teste: "só emitem comando", "fora do modelo" e "sem aprovação". |
| S20-R3 | **Fila única.** O comando vai **somente** pela fila `entrada` e pela caixa de comandos (S6-R2, R8); **texto livre não é comando** (S5-R3); o Drive **não é canal** (S19-R12, decisão de 21/11/2026) salvo nova decisão do proprietário (D1). | Teste: "fila `entrada`", "texto livre não é comando", "drive não é canal". |
| S20-R4 | **Entrega à Zapia por mecanismo comprovado.** A forma de o comando chegar à Zapia (D1) **só é adotada** depois de **prova sem efeito** (mensagem sintética sem dado pessoal, relato com captura, autorrelato C) e do recibo de mesmo hash (S6-R4); até lá, **nada** é considerado entregue. | Teste: "prova sem efeito", "recibo" e "nada é considerado entregue". |
| S20-R5 | **Acordar os agentes com prazo medido.** O gatilho (D2) é escolhido pela **prova da S15-R4** (carimbo por 3 dias, sem dado pessoal); Actions agendado é **melhor esforço** (atraso, descarte sem falha, desligamento em 60 dias) e **exige monitoramento externo**; **ausência do recibo do dia é o sinal** (S15-R7). | Teste: "melhor esforço", "60 dias", "monitoramento externo" e "ausência do recibo". |
| S20-R6 | **Rotina e lembrete só com `AUTORIZO`.** Criar, alterar ou ligar rotina, lembrete ou hook na Zapia exige a frase **`AUTORIZO`** literal e teste sem efeito antes (S8-R8, S5-R9); o limite mais restritivo vale (900 s, no máximo 32 por dia, S8-R5, S19-R12). | Teste: "`AUTORIZO`" e "mais restritivo". |
| S20-R7 | **Gemini Notebook só por comando validado.** O Tutor emite `enviar_prompt_notebook` (S10-R1); a Zapia só **transporta** e devolve texto literal e citação; a resposta é **dado não confiável** (S5-R4, S10-R6); o Tutor **verifica** (S10-R7) antes de qualquer entrega; falha de interface **para** sem laço (S10-R9). | Teste: "só transporta", "dado não confiável", "verifica" e "sem laço". |
| S20-R8 | **Privacidade.** Nada de dado pessoal na consulta nem no comando; resultado pessoal continua pela fila e pelo portão com flag `false`; o consentimento v4 é pré-condição de qualquer sessão ler projeção (S6-R9). | Teste: "dado pessoal", "flag `false`" e "consentimento v4". |
| S20-R9 | **Falha segura e visível.** Gatilho que não dispara, comando recusado, Zapia sem resposta ou recibo ausente **não** geram envio substituto, reenvio em laço nem cobrança (S15-R7, S8-R9). | Teste: "não geram envio substituto". |
| S20-R10 | **Ordem de construção em fases, cada uma com prova.** F0 prova sem efeito (carimbo S15-R4 e mensagem sintética); F1 caminho de ida de **uma** mensagem; F2 caminho de volta pela `entrada`; F3 rotina diária do Coach; F4 Tutor→Notebook pela Zapia; F5 homologação. **Nenhuma fase começa sem a anterior provada** e sem os lotes GAP-A e GAP-B fechados. | Teste: as seis fases e "nenhuma fase começa sem a anterior". |
| S20-R11 | **Decisões D1 a D3 são do proprietário.** A especificação **lista as opções** e **não adota** nenhuma; a escolha vira `PRODUCT.md` antes de virar regra (S15-R13). | Teste: "D1", "D2", "D3" e "não adota". |
| S20-R12 | **O que a S20 não prova.** Não prova que a Zapia consome comando, que a tarefa agendada assina ou promove fora do modelo, que o gatilho é pontual, nem eficácia pedagógica; a Zapia é **autorrelato (C)**. | Teste: os limites declarados. |

## Tarefas derivadas

A fila de gaps (`docs/governanca/FILA_GAPS_E_DIVERGENCIAS_20261121.md`) entra em `state/WORKFLOW.json` como lotes **GAP-A a GAP-E**, em série, depois desta especificação; a prova P1 a P6 é a **F0** e depende do proprietário.

## Aceite

Aceita pelo contrato quando `python scripts/doc_cohesion.py --check` passa e `tests/test_spec_s20.py` confere: as seções na ordem do modelo, os requisitos S20-R1 a S20-R12 cada um com critério, a pesquisa com links, confiança e lacunas, o mapa P1 a P8, as decisões D1 a D3 sem adoção, a fila de gaps no `WORKFLOW.json` e a flag de dados pessoais `false`.

## Limites

- **Não implanta nada** e **não prova** conversa automática, pontualidade de gatilho, consumo pela Zapia, assinatura fora do modelo nem eficácia.
- **Não altera** `agents/`, `AGENTS.md`, `PRODUCT.md`, gates, esquema de comandos nem flags.
- A pesquisa é de **resumos de busca**; o estado atual das tarefas agendadas do Claude Code **não foi verificado**.

## Emenda do AUTORIZO (E26, 23/11/2026)

O `AUTORIZO` por mensagem **deixa de ser exigido** para criar, alterar ou ligar rotina, lembrete ou hook e para os comandos de Tutor e Coach à Zapia, ao TEC e ao Gemini Notebook por ela (decisão do proprietário, 23/11/2026). Vale no lugar dele a **autorização permanente** (a aprovação do texto da E26), com escopo fechado, as travas determinísticas (caixa, tetos, recibo de mesmo hash, teste sem efeito automático, parada) e os limites declarados em `docs/governanca/E26_EMENDA_FIM_DO_AUTORIZO_NAS_AUTOMACOES.md`. **Continua exigindo `AUTORIZO`:** leitura de e-mail (E-07). Onde este documento disser que a frase é condição, vale esta emenda. Plataformas (Zapia, TEC, Gemini) podem manter regras próprias de confirmação ou login; isso não é removido.
