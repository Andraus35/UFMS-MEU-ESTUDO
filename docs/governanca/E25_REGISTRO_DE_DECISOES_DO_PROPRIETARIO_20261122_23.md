# E25: registro das decisões e necessidades do proprietário (sessão de 22 e 23/11/2026)

**Leitura obrigatória do construtor antes de abrir o lote da Zapia (F2a), da S21 (revisão) ou qualquer item que as cite.** **Natureza:** registro fiel do que o proprietário **decidiu, pediu ou escolheu** nesta sessão, para o construtor ler **de forma holística**, sem depender do chat. **Não é contrato:** nada aqui altera `PRODUCT.md`, `AGENTS.md`, `agents/` nem o esquema de comandos. Cada decisão só vira regra por PR próprio com a aprovação expressa do proprietário (`PRODUCT.md` > `ROADMAP.md`; em conflito, vale `AGENTS.md`). Onde a decisão é **proposta pelo construtor e ainda não confirmada**, está marcada **(PROPOSTA)**. Sem dado pessoal. Palavras do proprietário entre aspas são relato dele.

## A. Direção geral (o que ele quer do produto)

1. **Tutor e Coach ligados à Zapia de forma automatizada**, com notificação na Zapia em nome dos agentes (pedido de 22/11/2026). A COR-E ficou atrás do ZAPIA-F1 até ele estar garantido, testado e validado (feito: F1 provado em 22/11, E21).
2. **O harness é: Tutor e Coach dão prompts e instruções à Zapia, e não o contrário.** Logo, os horários e as instruções de agendamento saem dos agentes, via repositório, e a Zapia **cria no app dela** a rotina agendada. A Zapia **deve necessariamente usar o recurso nativo de rotina agendada** para disparar a notificação ao estudante.
3. **O Tutor é quem instrui o aluno pela Zapia**: solicita informações do TEC e envia prompts para a Zapia criar revisões no Gemini Notebook. Por isso **tanto o Tutor quanto o Coach emitem** a operação de agendamento (decisão de 23/11/2026), cada modelo preso à sua origem.
4. O Tutor deve **acordar a Zapia e dar instruções de agendamento de estudo**: matéria, assunto do dia e **quantidade de questões**; no dia seguinte, o mesmo. O proprietário pediu "garanta isso agora". **Limite declarado:** isso **não é garantível por código** (a Zapia é um modelo); só é **verificável depois**, pelo recibo de volta e pela captura da lista de rotinas do app.
5. Todas as escolhas e necessidades da sessão ficam **gravadas no repositório para o construtor ler** (este registro).

## B. Zapia: o que está provado e o que depende dele

- **Provado em 22/11/2026** (`CAPACIDADES_ZAPIA_VERIFICADAS.md`, `E22`, `E21`): a Zapia lê e escreve em `entrada` por HTTP com o token dela (não precisa de conector de GitHub) e fez o caminho de ida F1 com par **sintético manual**: leu, conferiu o hash, mostrou a notificação do Coach e gravou o recibo de volta (confiança B).
- **Não provado:** promoção pelo fluxo (flag e janela PJ), rotina agendada, notificação espontânea, pontualidade em 3 dias (S15-R4), que a Zapia crie rotina a partir de comando do repositório.
- Ato dele registrado: frase **`AUTORIZO rotina automática agora`** (22/11/2026) para a rotina de teste. **Criar a rotina na Zapia é ato dele** (S19-R4, S20-R6, S8-R8); o `AUTORIZO` vale por turno.
- **Escolhas dele nesta frente:** (a) tratar o F1 antes da COR-E (feito); (b) o teste da rotina é de **disparo único com par sintético**, pelo **roteiro atual**, **sem esperar** a E24; (c) abrir a **proposta de contrato** da operação de agendamento (E24) no #185; (d) **uma só branch de trabalho** (`ccr-ae23a584-dzxoku`; a antiga `ccr-9c6a8507-2f8tri` foi apagada por ele); (e) variante de **2 dias** como indício, com campo `rotina_id_relatado` e verificador (`scripts/zapia_disparo.py`).
- **Rotina contínua (escolha dele, 23/11/2026):** depois do teste, o Tutor emite **um pedido por semana** e a Zapia **agenda 7 dias** (cada dia usa um comando validado novo, de 24 h de validade). Isso pede um modelo novo `ROTINA_ESTUDO_SEMANAL` (origem `tutor`), **fora da aprovação da E24 atual**, com `AUTORIZO` por turno.
- **Pendente dele:** aprovar o texto da **E24** (`docs/governanca/E24_PROPOSTA_OPERACAO_AGENDAR_ROTINA.md`: operação `agendar_rotina` compartilhada, destino `zapia_rotina`, modelos `F1_ENTREGA_UNICA` e `ROTINA_ESTUDO_DIARIA`, janela de 15 min a 24 h, 1 pedido por dia por origem, instrução vinda de **modelo versionado e nunca do comando**, `AUTORIZO` por turno) e depois o merge da aplicação (altera `agents/`, esquema e `agents_gate.py`); **rodar a rotina de teste** (`ROTEIRO_ZAPIA_ROTINA_TESTE_20261122.md`) e trazer saídas e capturas para o **E23**.

## C. S21: controle de revisão por escopo (requisitos dele, 23/11/2026; a especificar)

Frente **nova**: abre só depois do merge do #185 (regra de lote do `AGENTS.md`). O padrão de revisão em 7, 15 e 30 dias (D-11) é **substituído**, o que exige emenda do `PRODUCT.md` com aprovação expressa, em PR próprio.

1. **Necessidade original:** um controle de matérias, assuntos e subassuntos **relançados individualmente ou em bloco** para revisão (exemplo dele: um assunto em 24 h, o bloco de assuntos da matéria em 15 dias, a matéria completa em 30 dias). Histórico: ele chegou a pedir "24 h, 7, 15 e 30 dias"; a versão **final e vigente** é a do item 2.
2. **Ciclo vigente (palavras dele resumidas):** em cada matéria há um **top 10 de assuntos** (do top 10 da S16, só FAPEC). Ele estuda **um assunto por dia**. **24 h depois** revisa o primeiro assunto, e assim por diante. **Após 5 dias** (metade do top 10) revisa os 5 assuntos de uma vez. **Após 10 dias** revisa o top 10 inteiro de uma vez. **Após 20 dias** novamente o top 10; **após 30 dias** novamente. **Ciclo de revisão: 24 h, 5 d, 10 d, 20 d e 30 d.**
3a. **Tamanho do top (escolha dele):** o top pode ter menos de 10 folhas ou até 15 por empate no 10º (S16-R6). Os **marcos de 24 h, 5, 10, 20 e 30 dias ficam fixos**: 10, 20 e 30 dias revisam **todo o conjunto estudado**; o marco "metade" usa a metade **arredondada para cima** (7 assuntos: 4; 15: 8).
3. **Contagem:** os prazos partem do **dia 1 do ciclo da matéria**, em **dias corridos**; **bloco** = assuntos estudados no mesmo ciclo; cada matéria tem **ciclo independente**, e a carga do dia soma o que vence em todas (o Tutor pode redistribuir com justificativa). **(PROPOSTA a confirmar):** a revisão que cai em dia de descanso é **apresentada** no primeiro dia de estudo seguinte, sem mudar a data de vencimento registrada.
4. **Erro em revisão:** o **Tutor decide caso a caso**, com justificativa e evidência.
5a. **Esclarecimento dele (23/11/2026) sobre o que vai ao Notebook:** o Tutor **terá acesso às questões estudadas** pelo estudante e, usando-as como **referência**, formula o método de revisão no Gemini Notebook, **sem levar o mesmo enunciado**: pode **reformular a questão** como julgar. **Conflito registrado, a resolver na S21 com emenda:** hoje o validador do prompt (`scripts/notebook_prompt_validator.py`, S10-R3) recusa dado pessoal e texto de questão; a questão **reformulada** é texto derivado de questão e pode ser recusada pelo filtro. A decisão dele é a **fonte**; falta definir os limites da reformulação (sem enunciado literal, sem gabarito, sem nome, sem contagem pessoal, sem credencial) e emendar S10 e o validador, em PR próprio com a aprovação expressa. **Enquanto a emenda não existir, o validador continua valendo.**
5. **Insumo e canal:** **todas as revisões** usam os **cadernos de acertos e erros feitos no TEC** como insumo para o **Tutor criar o método e o material** apropriados; a revisão é **exclusivamente no Gemini Notebook**, com os recursos dele (o Tutor emite `enviar_prompt_notebook`; a Zapia só transporta).
6. **Lembrete ao aluno:** o Tutor **define** a revisão e o Coach **lembra** no briefing diário (S8-R1); a entrega diária do Tutor precisa de uma linha de **revisões do dia**, vazia quando não há nenhuma.
7. **Limites:** o estudo está em E0, sem resultado gravado; os cadernos do TEC são resultado pessoal (só no piloto, pela fila e pelo portão); o top 10 depende da amostra definitiva da Zapia (S16) e os números não são versionados; a S21 é **especificação sintética**, sem prova de eficácia.

## D. Regras de trabalho que ele reafirmou ou aplicou

- Merge **só por pedido expresso dele, citando PR e head** ("Mesclar #184, head ..." foi dado e usado). Pedido pendente: o do #185 (head `7cf91cdecddb428f0698513cf7a88dc34277813b`).
- **Um lote por vez; outra frente só depois do merge.** A S21 espera o #185.
- Contratos (`agents/`, esquema, `AGENTS.md`, `PRODUCT.md`) **não mudam sem aprovação expressa do texto**.
- Perguntas automatizadas ao fim de cada rodada, com opção recomendada; ele pediu **linguagem de estudante** nas explicações de fundamento.
- Pedido de comandos **para o Termux** quando o ato é dele (ex.: apagar branch, rodar roteiros).

## D2. Fim do `AUTORIZO` nas automações (decisão dele, 23/11/2026)

- **Decisão:** "excluir a necessidade do criador ou estudante dar `AUTORIZO` nas automações entre agentes e Zapia e Gemini". Vale para a criação de rotinas, lembretes e hooks na Zapia e para o fluxo de comandos Tutor e Coach para a Zapia e o Gemini Notebook.
- **Estado:** **decidida e emendada na E26** (`E26_EMENDA_FIM_DO_AUTORIZO_NAS_AUTOMACOES.md`, D-31 do `PRODUCT.md` e seção "Emenda do AUTORIZO (E26)" em S5, S6, S8, S14, S15, S19 e S20), **no PR #185; só entra em vigor com o merge dele** (pedido expresso do proprietário, citando PR e head). Antes disso o `AUTORIZO` continua exigido (S5-R9, S8-R8, S19-R4, S20-R6). O construtor **não** deve dispensar a frase antes do merge.
- **(PROPOSTA)** Substituição: autorização permanente registrada (a aprovação da E24 e da emenda), escopo fechado, travas determinísticas, parada e recibo de volta (detalhe na E24). **Risco aceito por ele:** sem confirmação humana por rotina, uma automação errada só aparece no recibo ou na notificação.
- **O que a emenda toca:** S5, S6, S8, S14, S15, S19, S20 e `PRODUCT.md` (D-31); `AGENTS.md` e `agents/` não citam a frase e não mudam; a chave de parada versionada, se adotada, é arquivo de contrato e vai no lote de aplicação.
- **Limites que a plataforma impõe:** Zapia, TEC (login por código de e-mail, CAPTCHA) e Gemini podem manter confirmação própria; o repositório não os remove (E26).
- **O que não muda:** consentimento v4, flags de resultado pessoal, janela PJ, merge por pedido expresso e os limites do contrato (dado pessoal e credencial continuam fora; o `AUTORIZO` não era a barreira de privacidade).

## E. Como o construtor usa este registro

1. Ler este arquivo junto do START (o `memory/HANDOFF.md` aponta para ele).
2. **Não reabrir** o que está marcado como decidido; confirmar só o que está **(PROPOSTA)**.
3. Ao especificar a S21, citar os itens C.1 a C.7 e propor a emenda do D-11; ao aplicar a E24, citar B e o texto da E24.
4. Atualizar este registro **só** com nova decisão dele (nunca por inferência), com a data.
