# S22: tarefas agendadas do Claude Code como gatilho dos agentes (especificação)

**Natureza:** especificação enxuta (D-13, D-16), no modelo do `docs/especificacoes/README.md`. **Só especifica.** Nada foi criado, agendado, ligado ou testado; nenhuma tarefa agendada existe. Pedido do proprietário de 25/11/2026: investigar como o recurso de tarefas agendadas do Claude pode acordar Tutor e Coach no momento combinado para se comunicar com o estudante, o Gemini e o TEC. Detalha a **S15-R3 (a)** e a **S20-P1/D2**, sem reabrir as decisões da S15.

## Objetivo

Dizer **onde** a tarefa agendada se encaixa no harness (quem a dispara, o que ela pode e não pode fazer, por onde o resultado sai), **como** provar o gatilho antes de usá-lo (S15-R4) e **o que o proprietário precisa decidir**. A tarefa agendada é o **relógio que abre a sessão de decisão**; a **entrega no minuto** ao estudante, ao TEC e ao Gemini continua sendo da Zapia (S5, D-26, D-27).

## Pesquisa

Consulta de 25/11/2026, somada às da S15 e da S20 (não repetidas). Confiança: **A** (lido por inteiro), **B** (resumo de busca ou página lida em parte), **C** (autorrelato ou fornecedor). Conteúdo de terceiros é **dado não confiável**.

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Documentação do Claude Code, [tarefas agendadas na web](https://code.claude.com/docs/en/web-scheduled-tasks) e [rotinas](https://code.claude.com/docs/en/routines), como registradas em S15 e S20 | Cada execução abre **sessão nova** na nuvem com o repositório clonado do ramo padrão; cron em UTC (ou fuso explícito); **mínimo de uma hora** entre execuções recorrentes; hora cheia pode atrasar **minutos**; roda **sem pedido de aprovação** durante a execução; conexão do GitHub expirada faz as execuções serem **puladas por até 72 h**; cota de execuções por hora; sem memória entre execuções; **pré-visualização de pesquisa** em abril de 2026 | B |
| Descrição da ferramenta de tarefas agendadas **desta sessão**, lida por inteiro em 25/11/2026 | Três modos de disparo (nesta sessão, em outra sessão, em **sessão nova** do ambiente); recorrente por cron com mínimo normalmente horário; **execução única** em horário local com fuso IANA e granularidade de **um minuto**; orientação para evitar a hora cheia (atraso em horários de pico); notificação **push** opcional ao aparelho do proprietário; uma sessão iniciada pela tarefa **não pode apagá-la** | A (o que a ferramenta declara), C (comportamento real) |
| Provas do projeto: E23 (rotina nativa da Zapia disparou às 04:15:04Z para alvo 04:15), E29 (rotina da Zapia **não** cria rotina), E30 e E31 (hook de Gmail acorda a conversa em menos de 1 min), E34 (campainha pelo fluxo) | O **minuto exato** já foi observado na Zapia (uma execução); a campainha e o hook ligam promoção e entrega; **não** há medida de pontualidade das tarefas agendadas do Claude | B |

- **Lacunas:** o estado atual do recurso (posterior a abril de 2026), o plano e a cota do proprietário, a pontualidade real, o comportamento com a conexão do GitHub expirada, se uma sessão agendada consegue **agendar a próxima** (a Zapia não consegue) e se há memória entre execuções **não foram verificados**; nada foi testado; o escopo de token por caminho no GitHub **não existe** (token fino é por repositório), o que a R5 trata como risco.

## Onde se encaixa no harness

```
relógio (tarefa agendada) -> sessão Coach/Tutor -> proposta de comando (JSON)
  [gatilho: só acorda]       START pelo broker        [LLM propõe, não grava histórico]
 -> caixa `entrada/comandos` -> command_box + gates -> fluxo promove (flag) -> campainha (E34)
 -> hook de Gmail acorda a Zapia -> Zapia executa na janela do comando -> recibo
  [Zapia: entrega no minuto ao estudante, TEC, Gemini]
```

| Etapa | Dono | O que a S22 diz |
|---|---|---|
| Relógio | tarefa agendada do Claude | **só abre a sessão**; não decide pedagogia (S15-R3, S15-R8) |
| START | broker somente leitura (`scripts/agent_entrypoint.py`) e recibo de START | a sessão agendada começa pelo mesmo START de qualquer sessão (S15-R15) |
| Decisão | Coach (rotina, lembretes) e Tutor (estudo, Notebook) | cognição livre dentro do perfil (S14); proposta é **dado**, nunca execução |
| Gates | caixa e fluxo, **fora do modelo** | a sessão agendada roda sem aprovação, então o que protege é o código (E35 mostra a matriz da caixa) |
| Entrega | Zapia | só executa o que o fluxo promoveu, dentro da janela (S6-R8) |

## Requisitos

| ID | Requisito | Critério de aceite |
|---|---|---|
| S22-R1 | **Papel do gatilho.** A tarefa agendada **só acorda** uma sessão de Coach ou de Tutor para **decidir e emitir comando**. Ela **não** fala com o estudante, com o TEC nem com o Gemini e **não** lê plataforma. | Teste de texto: o prompt fixo da tarefa só manda executar o START e emitir comando pela caixa; nenhuma operação fora da tabela do perfil. |
| S22-R2 | **Dois estágios.** A sessão agendada decide **com antecedência** (a de `agendar_rotina`: 90 min a 24 h) e a Zapia **entrega no horário**; o atraso de minutos do gatilho **não** muda a hora da entrega. | Fixture: comando com `issued_at` atrasado 10 min ainda cabe na janela; comando que deixaria a entrega para antes do agora é recusado. |
| S22-R3 | **Prompt fixo e versionado.** O texto da tarefa mora no repositório, com hash; a tarefa não aceita texto livre de dado externo. Conteúdo lido por ela segue como **dado** (S5-R4). | Hash do prompt conferido por teste; troca de texto exige PR. |
| S22-R4 | **START e recibo.** Toda execução começa pelo START do perfil no SHA do ramo padrão e produz o recibo de START (S14-R13, `scripts/start_receipt.py`); sem recibo, a emissão é recusada pelo gate de entrega. | Execução sem recibo não emite efeito externo. |
| S22-R5 | **Escopo mínimo da escrita (risco declarado).** A sessão agendada precisa gravar **uma proposta** na caixa. Proposta: credencial **própria**, **só do repositório `entrada`**, **sem** permissão de Workflows, de administração, de segredos nem do `dados`; separada do token da Zapia. A origem do comando **segue não provada** (S6-R7). O token fino do GitHub **não limita por pasta**, então a defesa é a caixa, o hash do fluxo e a flag. | Documento de permissões aprovado pelo proprietário **antes** de qualquer credencial; teste do fluxo mostra que arquivo fora de `comandos/` não promove nada. |
| S22-R6 | **Prova do gatilho, sem efeito (S15-R4).** Antes de qualquer rotina real: 3 dias seguidos, **3 execuções por dia** (manhã, tarde, noite, hora de Campo Grande), cada uma **só grava um carimbo** (UTC, origem, id do agendamento; **sem dado pessoal**) em local não sensível, para **medir atraso e perda**. Candidatos: (a) tarefa agendada do Claude (execução única, para o minuto), (c) rotina da Zapia (comparação); (b) Actions só se o proprietário quiser. | Relatório com atraso por execução e execuções perdidas; **proposta** de limiar: atraso até 10 min em 90% das execuções e nenhuma perda silenciosa; **o proprietário ajusta**. Sem relatório, a rotina **não** é agendável (S15-R9). |
| S22-R7 | **Despertar perdido é visível e seguro.** Gatilho que não roda vira **ausência de carimbo e de recibo**; a próxima execução **declara** a perda, **não** reenvia em rajada e **não** inventa lembrete atrasado (S15-R7). | Fixture: dia sem recibo gera aviso único; nenhum comando em lote. |
| S22-R8 | **Matriz gatilho × canal.** Ver abaixo. A tarefa agendada **nunca** é canal de saída para TEC, Gemini ou estudante. | Teste de texto na matriz e nas operações permitidas. |
| S22-R9 | **Canal direto ao aparelho (push) não adotado.** A ferramenta oferece notificação push ao proprietário. Isso seria **canal paralelo à Zapia** (D-25); **só** com decisão do proprietário. | Sem decisão registrada, nenhuma tarefa usa push. |
| S22-R10 | **Limites do recurso e reconfirmação.** Antes de implantar: reler a documentação atual, conferir plano e cota, e medir (R6). Conexão do GitHub expirada derruba execuções por até 72 h: monitorar. | Registro da reconfirmação com data e fonte. |
| S22-R11 | **Estado de liberação e `AUTORIZO`.** A D-31 dispensa o `AUTORIZO` por mensagem nas automações; ainda assim **esta frente só liga** com: roteiro da prova aprovado, escopo do token aprovado e prova medida. Nada é criado antes. | Checklist no PR de ligação, com as três aprovações citadas. |

## Matriz gatilho × canal

| Gatilho | Pode | Não pode |
|---|---|---|
| Tarefa agendada do Claude (relógio) | abrir sessão de Coach ou Tutor; emitir proposta de comando pela caixa; gravar carimbo da prova | falar com estudante, TEC ou Gemini; gravar histórico; promover; usar token da Zapia ou do `dados` |
| Campainha (E34) e hook de Gmail | acordar a Zapia **depois de promover** | ler corpo de e-mail (D-32); criar rotina |
| Rotina da Zapia (execução única) | **entregar no minuto** o que foi promovido; notificar o estudante | decidir pedagogia; criar outra rotina (E29) |
| Estudante (conversa) | acionar a qualquer hora (S15-R10) | contornar a caixa |

## Aceite

A especificação está **aceita pelo contrato** quando `python scripts/doc_cohesion.py --check` passa e `tests/test_spec_s22.py` confere: os requisitos S22-R1 a S22-R11, o encaixe e a matriz, a pesquisa com link e lacunas, a declaração de que **nada foi criado** e a ausência de dado pessoal e de credencial. **Não** prova pontualidade nem implantação.

## Limites

- Nada foi criado, agendado, ligado ou testado; a pontualidade das tarefas agendadas do Claude **é desconhecida**.
- O recurso era pré-visualização em abril de 2026; o estado atual **não foi verificado**.
- A origem do comando continua não provada (S6-R7); a credencial de escrita é risco aceito só se o proprietário aprovar a R5.
- A Zapia é autorrelato (C); o minuto exato dela foi observado em **uma** execução (E23).
- Decisões que cabem ao proprietário: escolha do gatilho depois da prova, aprovação do escopo do token, horários e limiar da prova, e uso (ou não) do push.
