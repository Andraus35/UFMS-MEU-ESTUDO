# PRODUCT — UFMS MEU ESTUDO

Versão: 1.0 · Aprovado pelo proprietário em 07/11/2026 · Mudança somente por PR com aprovação humana

## 0. Como ler

- **Ordem do START de engenharia:** `AGENTS.md`, `ROADMAP.md`, `PRODUCT.md`, `memory/HANDOFF.md`, `state/CURRENT.json`, `state/WORKFLOW.json`. O START de estudo (Tutor e Coach) não inclui este arquivo.
- **Precedência em conflito:** `AGENTS.md` (segurança e contrato do agente) > `PRODUCT.md` (o que construir e por quê) > `ROADMAP.md` (fila e criticidade) > `docs/` (detalhe e histórico).
- **Este arquivo não contém estado.** Fila, status, tarefa ativa, PR e SHAs vivem em `ROADMAP.md`, `state/WORKFLOW.json` e `memory/HANDOFF.md`. Se precisar de um deles aqui, aponte; não copie.
- **Não duplicar:** onde já existe documento, apontar para ele (seção 10).
- **Dúvida ou divergência:** perguntar ao proprietário e corrigir por PR. Não inventar dado, integração, decisão nem acesso.
- **Termos ambíguos:** ver o glossário (seção 9), em especial "caderno" e "Gemini Notebook".

## 1. Propósito

Assistente de estudos por questões, de uso pessoal e de um único usuário (o proprietário), para os cargos UFMS 523 e 324 do Edital PROGEP/UFMS 152/2026, banca FAPEC. Ele persiste o contexto entre sessões e entre modelos, decide o próximo caderno, confere os resultados devolvidos e conduz revisões. Datas e pesos da prova: `config/concursos.json`. Edital: `edital/INDEX.md`.

## 2. Atores e responsabilidades

| Ator | Papel | Não faz |
|---|---|---|
| Estudante | cria e resolve cadernos no TEC Concursos ou Qconcursos, devolve resultados, aprova mudanças estruturais e merges | — |
| Tutor (persona Aragonê) | agente que **decide**, com base no harness, o que estudar, o caderno a recomendar, a validação de resultados e o conteúdo da revisão; emite os comandos e os prompts que a Zapia executa | executar ferramentas por conta própria, receber credenciais |
| Coach (persona Carter) | agente que **decide**, com base no harness, o acompanhamento, as mensagens e os lembretes; emite os comandos que a Zapia executa | executar ferramentas por conta própria, receber credenciais |
| Zapia | **interface** entre o proprietário e os agentes Tutor e Coach, e **executora** das ferramentas (GitHub pela API REST, Gemini Notebook pela interface web, Calendar, Tasks e mensagens); guarda as credenciais; **só executa comandos do Tutor e do Coach, e só dentro das diretrizes do harness**; os prompts enviados ao notebook vêm do Tutor ou do Coach, nunca dela; não há MCP de GitHub nem de Notebook conectado (E-01) | decidir, criar conteúdo pedagógico, escolher o que estudar, redigir prompts de revisão ou mensagens por conta própria, gravar ou enviar algo sem comando de um agente, ir além das diretrizes do harness |
| Harness (este repositório) | fonte de verdade persistente: regras, validadores, edital indexado, fila, prescritor, pontuação de simulados, insumos e validador do prompt de revisão | executar ação externa por conta própria |
| Gemini Notebook | ambiente de revisão e fonte de método (NotebookLM); recebe, por meio da Zapia, o prompt do Tutor ou do Coach e devolve a revisão | ser fonte normativa do edital, guardar dado pessoal além do prompt mínimo |
| TEC Concursos e Qconcursos | plataformas de questões, operadas pelo estudante | — |
| Agentes construtores (Claude, GPT e outros) | constroem e auditam o harness, sempre por PR | operar estudo real, receber credencial de escrita pessoal, mesclar |

## 3. Fluxo ponta a ponta

- **F1 Iniciar:** o proprietário fala com a Zapia, que encaminha ao Tutor; o Tutor faz o START de estudo (4 arquivos, pelo ponto de entrada controlado) e identifica a situação: nada pendente, caderno pendente ou resultado a processar.
- **F2 Recomendar:** o Tutor entrega ao Coach o plano de estudos (D-11) e decide, com a fila determinística e a prescrição do harness (assunto, nível, filtros em camadas, quantidade, justificativa), o caderno do dia; a Zapia apresenta um caderno principal ao proprietário. Nunca afirma disponibilidade de questões.
- **F3 Resolver:** o estudante cria e resolve o caderno na plataforma.
- **F4 Devolver:** o estudante estuda no TEC Concursos e no Qconcursos e entrega, pela Zapia, a exportação do caderno de desempenho ou, quando não houver, total, acertos, erros, data e resultado por tópico.
- **F5 Validar:** o Tutor aplica o contrato de ingestão do harness (coerência de contagens, escopo, convenção de contagem); inconsistência é recusada ou esclarecida, nunca corrigida em silêncio.
- **F6 Registrar:** o Tutor emite o comando de registro e a Zapia, como executora, grava o evento no repositório privado, sob os controles P1 a P9 do ADR-013 (ver D-02); a Zapia recusa o comando que violar as diretrizes do harness. Sem todas as condições cumpridas, o resultado fica pendente e não é declarado registrado.
- **F7 Reavaliar:** o harness recalcula evidência (E0 a E4) e fila; o Tutor decide a nova intervenção; o que é desconhecido permanece desconhecido.
- **F8 Revisar:** o Tutor elabora o prompt de revisão a partir dos insumos do harness, do edital, do cronograma da prova e do que foi estudado por questões (D-08); o harness valida que o prompt é mínimo e exige fonte verificada; a Zapia o envia ao Gemini Notebook pela interface web (E-01) e devolve a resposta ao Tutor, que confere a fonte e a entrega ao estudante; o harness guarda só metadados (assunto, data, fonte).
- **F9 Acompanhar:** o Coach acompanha o proprietário diariamente no plano, decide as mensagens e os lembretes e comanda a Zapia a enviá-los, dentro de rotina previamente autorizada, com limites, idempotência e readback.
- **Simulados:** pontuação ponderada e comparabilidade conforme `docs/pedagogia/PROTOCOLO_SIMULADOS_v1.4.md`; nunca declarar aprovação.

## 4. Fronteiras de dados

- **Repositório público (este):** regras, código, edital, fixtures sintéticas. Nunca dado pessoal.
- **Repositório privado `Andraus35/ufms-meu-estudo-dados`:** resultados e eventos, somente depois de criado pelo proprietário, com consentimento registrado e controles P1 a P9.
- **Gemini Notebook:** recebe só o mínimo do prompt (assunto, lacuna, método, exigência de fonte). Enviar dado a terceiro é ação sensível, e a retenção na conta do Gemini não foi verificada (E-06, OPEN-05).
- **Em lugar nenhum:** CPF, documentos, credenciais, tokens, exports brutos, capturas de tela, texto integral de questões ou comentários de professores.

## 5. Decisões do proprietário

- **D-01 (07/11/2026):** repositório privado separado `Andraus35/ufms-meu-estudo-dados`. A criação é ato do proprietário.
- **D-02 (07/11/2026):** a Zapia, como executora, grava os resultados desde o início, **só por comando do Tutor** e dentro das diretrizes do harness, pela API REST do GitHub com credencial própria dela. Revisa a decisão anterior de que o proprietário gravaria manualmente. A habilitação continua condicionada aos controles P1 a P9, à resolução de OPEN-01 e OPEN-02 e a PR próprio com aprovação humana; até lá `personal_results_writes_enabled` permanece `false`.
- **D-03 (07/11/2026):** retenção até a prova mais 30 dias; revogação efetiva é apagar o repositório privado inteiro.
- **D-04 (07/11/2026):** texto de consentimento **v2** aprovado, sem ajustes (texto no ADR-013); substitui o v1. Ele cobre a Zapia e o Google e informa que apagar o repositório privado não elimina as cópias nesses serviços (E-09).
- **D-05 (07/11/2026):** o prompt de revisão vem do Tutor ou do Coach, com insumos e validação do harness; a Zapia apenas o envia ao Gemini Notebook e só metadados voltam ao repositório. O mecanismo observado é a interface web, não MCP (E-01); a escolha do mecanismo por parte do proprietário precisa ser reconfirmada.
- **D-06 (07/11/2026):** o recorte GP-3-MVP8 foi aceito como cobertura técnica mínima sintética.
- **D-07 (07/11/2026):** este arquivo é leitura obrigatória no START de engenharia, como 3º arquivo.
- **D-08 (07/11/2026):** o Tutor cria o material de revisão com base no edital, no cronograma e no que foi estudado por questões no TEC Concursos e no Qconcursos. Palavras do proprietário; "cronograma" é entendido como o da prova no edital, e o harness não impõe cronograma de estudo (interpretação a confirmar, OPEN-07). Alinha-se à memória da Zapia (E-08).
- **D-09 (07/11/2026):** o proprietário criará para a Zapia um token fine-grained restrito a este repositório, com expiração; o repositório privado de dados terá outro token, separado, depois de criado. Até a verificação (PR-010), o alcance atual do token (E-03) permanece risco conhecido.
- **D-10 (07/11/2026):** a Zapia é **apenas a interface** entre o proprietário e os agentes Tutor e Coach e a executora das ferramentas. Os agentes decidem com base no harness do repositório e executam por meio da Zapia, que se conecta ao NotebookLM com o prompt vindo do Tutor ou do Coach, e não de si mesma. A Zapia fica **restrita às diretrizes do harness e aos comandos do Tutor e do Coach**. Corrige a descrição anterior deste arquivo, que atribuía à Zapia os papéis de Tutor e Coach (E-10).
- **D-11 (07/11/2026):** o plano de estudos entregue ao humano segue o Método 4.2 (Prof. Rafael Barbosa) e a revisão espaçada em 7, 15 e 30 dias, como padrão que o Tutor pode ajustar com justificativa. O repositório não tinha essa especificação; ela foi criada em `docs/pedagogia/PLANO_DE_ESTUDOS_METODO_4_2_E_REVISAO_7_15_30.md` e implementada em `scripts/study_plan.py`. Exige emenda do `AGENTS.md` e de `rules/`, que consta do PR que registra esta decisão.
- **D-12 (07/11/2026):** os agentes são criados agora, com perfis em `agents/`. O **Tutor** cuida do ensino, do aprimoramento do estudo, da revisão, da fixação, da busca na memória e das técnicas de estudo; o **Coach**, da motivação, da organização dos estudos, das estatísticas de desempenho e das sugestões e recomendações. **O conteúdo é produzido apenas pelo Tutor.** O Tutor deve acessar o NotebookLM diretamente; a Zapia só faz a ponte se isso não for possível (prioridade ao acesso direto). O TEC Concursos e o Qconcursos fornecem cadernos e estatísticas que os agentes usam para conduzir revisões e melhorias; o humano exporta o caderno de desempenho e o entrega pela Zapia, que o grava no repositório. O ciclo vai até fechar o edital ou o conteúdo priorizado.

## 6. Não objetivos e proibições

- Não acessar TEC Concursos ou Qconcursos por robô nem fazer scraping.
- Não inventar questões, gabaritos, notas, cadernos, disponibilidade, resultados, citações ou fontes.
- Não conceder token de escrita pessoal a agente construtor, Tutor ou Coach; as credenciais ficam só com a Zapia, e o modelo dos agentes nunca as recebe. Não gravar credencial em arquivo ou prompt.
- Não permitir que a Zapia decida, gere conteúdo pedagógico, redija prompts de revisão ou mensagens, ou aja sem comando do Tutor ou do Coach (D-10).
- Não gravar dado pessoal no repositório público, nem com a flag de escrita ativada.
- Não consultar Google Calendar nem Tasks sem autorização específica para a consulta, e nunca de forma ampla (listar tudo): usar identificadores próprios e consultas mínimas (E-07).
- Não criar lembrete ou tarefa de uma atividade sem antes conferir, no estado do harness, que ela está pendente (E-07).
- Não declarar integração (Zapia, Gemini, agenda) sem prova; não confundir CI verde com eficácia pedagógica.
- Não declarar que apagar o repositório privado elimina todas as cópias dos dados: elas também existem na plataforma da Zapia e, no mínimo necessário, no Google (E-09).
- Não impor cronograma, meta universal ou intervalo de revisão fora do padrão do proprietário (D-11), que o Tutor pode ajustar com justificativa.
- Não ser produto multiusuário nem comercial.

## 7. Requisitos de produto

- **PR-001 START determinístico:** o START de engenharia lê este arquivo como 3º, com hash, e o gate de estrutura o valida. Aceite: `python scripts/bootstrap.py --mode engineering` lista `PRODUCT.md` na 3ª posição com SHA-256 e `python scripts/product_gate.py --check` passa. Elo: RM-00.
- **PR-002 Insumos e validação do prompt de revisão:** o harness fornece insumos determinísticos (assunto, lacuna, método, exigência de fonte) e valida o prompt que o Tutor ou o Coach elabora antes de a Zapia enviá-lo: exige fonte verificada, separa títulos citados mas não verificados e recusa dado pessoal além do mínimo. Aceite: testes com fixtures sintéticas, inclusive prompt com dado pessoal recusado e prompt sem fonte recusado. Elo: RM-09.
- **PR-003 Escrita no repositório privado por comando do Tutor:** o Tutor emite o comando; a Zapia executa com proposta, validação P1 a P6, commit e readback. Aceite: provas P1 a P3 e P5 a P6 contra o repositório privado real, com OPEN-01 e OPEN-02 resolvidos. Elo: RM-08.
- **PR-004 Repositório privado criado e verificado:** Aceite: leitura autenticada devolve `private=true` e o consentimento v2 (D-04) fica registrado no repositório privado antes do primeiro evento (controle P3); dono: proprietário. Elo: RM-08.
- **PR-005 Metadados da revisão:** registro de assunto, data e fonte, sem texto integral. Aceite: esquema validado e teste negativo que recusa texto integral. Elo: RM-09.
- **PR-006 Ciclo ponta a ponta real:** F1 a F8 com um resultado real e consentido, com readback. Aceite: relatório do ciclo e CI verde no HEAD. Elo: RM-08.
- **PR-007 Rotina do Coach executada pela Zapia:** mensagens e lembretes decididos pelo Coach e executados pela Zapia por comando dele, criados só depois de conferir no estado do harness que a atividade está pendente. Aceite: prova de autorização, idempotência e limites, e recusa de lembrete para atividade já concluída (falha real observada, E-07). Elo: RM-09.
- **PR-008 Simulados no fluxo:** pontuação e comparação de simulados usadas em F5 e F7. Aceite: `scripts/simulado_score.py` e `scripts/simulado_session.py` acionados nesses passos, com teste. Elo: RM-06.
- **PR-009 Retomada entre sessões e modelos:** estado reconstruído dos eventos e dos arquivos do START, nunca da conversa. Aceite: `python scripts/rebuild.py --check` passa e nenhum estado existe só em conversa. Elo: RM-00.
- **PR-010 Credencial mínima da Zapia (D-09):** token de escopo único por repositório, sem administração nem workflows e com expiração; o repositório privado usa credencial própria, sem alcance sobre o público. Aceite: o proprietário confirma o escopo nas configurações do GitHub e a Zapia comprova, em teste sintético, que a escrita fora do repositório designado é recusada. Elo: RM-08.
- **PR-011 START de estudo dos agentes:** como a Zapia não lê o repositório sozinha no início da sessão (E-05), o START de estudo do Tutor e do Coach é um procedimento explícito: obter o repositório e executar `python scripts/bootstrap.py --mode study`, informando os SHA-256 dos 4 arquivos. Onde os agentes rodam e como leem o harness é o OPEN-09; se a obtenção for delegada à Zapia, que executa Python (E-04) mas não tem Git (E-08), será por arquivo compactado via API, alternativa ainda não testada. Aceite: relatório com hashes iguais aos do repositório e teste do procedimento com fixture; é procedimento, não trava técnica. Elo: RM-00.
- **PR-012 Material de revisão pelo Tutor e acesso ao NotebookLM:** o Tutor cria ou usa um notebook próprio, alimentado com fontes públicas do edital, e elabora a revisão (D-08), pelo caminho direto (prioridade, D-12) ou, se impossível, pela Zapia. Aceite: teste sintético, sem dado pessoal, de criar o notebook, adicionar uma fonte de texto, enviar o prompt do Tutor, ler a resposta e abrir uma citação, com relatório que registra qual caminho funcionou; nada disso foi testado até hoje (E-08). Elo: RM-09.
- **PR-013 Contrato de comandos dos agentes para a Zapia:** esquema versionado e validado de comandos (operação permitida, parâmetros, destino, idempotência, origem), que a Zapia só executa se vierem do Tutor ou do Coach identificados e cumprirem as diretrizes do harness; caso contrário, recusa e registra. Aceite: esquema no repositório e testes que rejeitam comando fora do esquema, de origem desconhecida, com destino não designado e com dado pessoal além do mínimo (OPEN-09). Elo: RM-07.
- **PR-014 Perfis dos agentes Tutor e Coach:** perfis em `agents/` que separam as responsabilidades, sem estado e sem segredo. Aceite: `python scripts/agents_gate.py --check` passa (estrutura, ausência de estado e segredos, cada operação exclusiva em um só agente) e o bootstrap de engenharia o executa. Elo: RM-08.
- **PR-015 Plano de estudos padrão:** gerador determinístico do ciclo do Método 4.2 e das revisões em 7, 15 e 30 dias (D-11). Aceite: `scripts/study_plan.py` com testes de contraprova (ciclo 4/2/1, no máximo 120 minutos por disciplina, revisões nos intervalos, fase final, entradas inválidas) e padrões lidos de `settings.json`. Elo: RM-08.
- **PR-016 Ingestão da exportação de desempenho:** contrato de ingestão validado contra amostras reais anonimizadas do TEC Concursos e do Qconcursos (OPEN-11). Aceite: amostras reais, testes de contraprova e rejeição de arquivo fora do formato. Elo: RM-02.

## 8. Ordem de construção

Dependências, não status (o status vive no `ROADMAP.md`):

- **B1:** PR-001 e PR-011.
- **B2:** PR-004 (proprietário).
- **B3:** PR-002, PR-013, PR-014 e PR-015 (independentes, offline).
- **B4:** PR-003 (depende de B2, de PR-010 e de OPEN-01 e OPEN-02).
- **B5:** PR-005, PR-012 e PR-016 (dependem de B3; PR-016 depende também de OPEN-11).
- **B6:** PR-006 (depende de B4 e B5).
- **B7:** PR-007 e PR-008.

## 9. Glossário

- **Caderno:** conjunto de questões criado pelo estudante no TEC Concursos ou Qconcursos.
- **Gemini Notebook:** ambiente de revisão no Gemini usado pela Zapia (por exemplo o notebook "Como estudar"). Não é caderno de questões.
- **`notebook_prescriber`:** prescreve cadernos de questões; não gera prompts para o Gemini.
- **Prescrição:** plano de caderno sem efeito externo. Recomendação, confirmação e execução são estados distintos.
- **Tutor e Coach:** agentes que decidem com base no harness e comandam a Zapia, com as personas Aragonê (Tutor) e Carter (Coach). O Tutor orienta, escolhe intervenções e elabora as revisões; o Coach acompanha e lembra. Não são papéis da Zapia (D-10), embora nas POCs de 04/11/2026 ela os tenha desempenhado em conversas de teste (E-10).
- **Zapia:** interface com o proprietário e executora das ferramentas, restrita ao harness e aos comandos do Tutor e do Coach (D-10).
- **Harness:** este repositório (regras, estado, validadores).
- **Revisão:** estudo guiado de um assunto com lacuna, elaborado no Gemini Notebook.
- **E0 a E4:** níveis de evidência definidos em `docs/pedagogia/MODELO_EVIDENCIAS_v1.2.md`.

## 10. Mapa de fontes

Apontar, não copiar:

- Contrato e segurança do agente: `AGENTS.md`.
- Fila e criticidade: `ROADMAP.md`. Tarefa ativa: `state/WORKFLOW.json`. Retomada: `memory/HANDOFF.md`. Resultados de estudo: `state/CURRENT.json`.
- Método, decisão, evidências, estratégia, simulados e cadernos: `docs/pedagogia/README.md` (índice).
- Persistência privada: `docs/governanca/ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md` e `memory/DECISIONS.md`.
- O que impede cada frente: `docs/pedagogia/MAPA_DESBLOQUEIO_FRENTES_20261107.md`.
- Edital: `edital/INDEX.md` e `docs/EDITAL.md`.
- Provas de conceito da Zapia (sintéticas): `poc/README.md`.
- Agentes, plano de estudos e pesquisa: `agents/README.md`, `docs/pedagogia/PLANO_DE_ESTUDOS_METODO_4_2_E_REVISAO_7_15_30.md` e `docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md`.
- Operação, START e DELIVERY: `docs/OPERACAO.md`.
- **Substituído como porta de entrada de construção:** `docs/pedagogia/PROMPT_TRANSFERENCIA_TECNICA_v1.8.md` (histórico).

## 11. Evidências de referência

Fatos datados, não estado. Os itens E-01 a E-06 são **autorrelato da Zapia** (07/11/2026), registrado em `docs/governanca/RESPOSTA_VERIFICACAO_ZAPIA_20261107.md`; nenhum agente construtor os reverificou, exceto o que consta naquele documento.

- **E-01 Mecanismo de acesso:** GitHub pela API REST, por HTTP a partir do ambiente de execução da Zapia, com credencial em gerenciador seguro; a tentativa de conectar o MCP oficial do GitHub foi recusada. Gemini Notebook pela interface web autenticada do navegador; não há MCP de Notebook. As POCs de 04/11/2026 existem em `poc/README.md` e são provas sintéticas.
- **E-02 Capacidades testadas:** GitHub: ler arquivo, criar branch e gravar commit. Não testadas: abrir PR, ler CI, apagar. Notebook: abrir, ler fontes, enviar prompt, ler a resposta e conferir uma citação. Não testadas: listar, adicionar fonte, criar, apagar.
- **E-03 Credencial (rodada 2, `docs/governanca/RESPOSTA_RODADA2_ZAPIA_20261107.md`):** guardada em gerenciador seguro e usada por referência; a Zapia afirma não receber o valor como texto (documentado, não verificável por agente construtor). É um token de acesso pessoal, provavelmente fine-grained (subtipo não confirmado), **sem informação de expiração**. Alcança **3 repositórios públicos** (este e dois outros do proprietário, com `push=true`) e **nenhum privado**; administração efetiva não comprovada (a proteção da `main` retornou 403). Credenciais separadas por referência nominal são possíveis (documentado).
- **E-04 Controles:** não há trava técnica que force a checagem de visibilidade nem a confirmação humana antes de escrever; existe apenas protocolo conversacional. A Zapia executa comandos e Python. Os commits das POCs constam com a autoria do proprietário, então o histórico não distingue quem gravou.
- **E-05 Memória e rotina:** memória persistente própria; não lê o repositório sozinha no início da sessão. Conta no plano Free (até 20 automações ativas). O app é o único canal com comprovante de envio e visualização; WhatsApp e Telegram não têm comprovante. Um lembrete estático no app foi entregue em 04/11/2026; WhatsApp não está comprovado como recebido pelo aparelho; Telegram exige aprovação; a exclusão de eventos do Calendar não foi confirmada por leitura.
- **E-06 Privacidade do Gemini:** o prompt e o contexto do notebook vão ao serviço do Google; retenção e política da conta **não verificadas**.

- **E-07 Google Calendar e Tasks (autorrelato, `docs/governanca/ADENDO_AUDITORIA_ZAPIA_20261107.md`):** evento e tarefa foram criados e relidos, e a tarefa mudou de `completed` para `needsAction`; a exclusão lógica foi **comprovada na rodada 2** (evento com `status=cancelled`, tarefa com `deleted=true`, HTTP 410 na segunda exclusão), mas a eliminação física dos dados não. Uma tarefa foi criada como pendente para atividade já concluída, sem conciliar o estado. Houve consulta ao calendário antes da autorização específica e uma leitura de Tasks expôs ao contexto da Zapia títulos de tarefas alheias ao teste. Só um disparo único de lembrete no app foi observado; nenhuma rotina recorrente nem ciclo completo sem intervenção humana.
- **E-08 Ambiente, Gemini e rotinas (rodada 2):** o Git **não está disponível** no ambiente de execução da Zapia; Python executa; um script próprio pode persistir. O notebook "Como estudar" é **público, de terceiros (Bloomsbury), com 36 fontes, e não consta nos notebooks do proprietário**; os notebooks do proprietário são outros. O agendador aceita tarefas únicas e recorrentes, e uma tarefa com execução de agente pode usar ferramentas, mas escrita no GitHub ou Python agendados não foram comprovados. Calendar e Tasks têm escopos de leitura e escrita, e não há deduplicação automática. A memória da Zapia descreve o Tutor como quem "prepara material de revisão no Gemini Notebook", o que difere do fluxo F8.
- **E-09 Privacidade da plataforma da Zapia (rodada 2, documentado):** conversas, memórias e arquivos ficam em servidores nos Estados Unidos, com retenção geral de até 36 meses após o encerramento da conta e até 90 dias para áudios, PDFs, vídeos e imagens processados; por padrão não treina modelos; exclusão e portabilidade por pedido, sem backup apagado comprovado. Logo, a revogação por apagar o repositório privado (D-03) não elimina essas cópias.
- **E-10 Divergência de arquitetura:** nas POCs e na memória da Zapia, ela própria atua como Tutor e Coach (personas Aragonê e Carter); a arquitetura-alvo decidida pelo proprietário (D-10) separa os agentes da Zapia, que passa a ser só interface e executora. O `AGENTS.md` já descrevia a Zapia como interface de comunicação.
- **E-11 Pesquisa (07/11/2026, `docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md`):** o Método 4.2 é público (Prof. Rafael Barbosa, 2018) e não menciona revisão em 7, 15 e 30 dias; a API oficial do NotebookLM existe só na edição Enterprise, e o acesso direto por agentes é por MCP não oficial; a ajuda oficial do TEC e do Qconcursos não pôde ser lida, então a exportação de desempenho não está verificada.

As POCs não provam execução recorrente, acesso às plataformas de questões nem domínio pedagógico.

## 12. Pontos a confirmar

Cada ponto vira decisão ou requisito por PR; até lá, não afirmar o mecanismo. Roteiros de perguntas: `docs/governanca/PROMPT_VERIFICACAO_ZAPIA_20261107.md` (rodada 1) e `docs/governanca/PROMPT_VERIFICACAO_ZAPIA_RODADA2_20261107.md` (rodada 2). Só respostas com status `OBSERVADO` ou `DOCUMENTADO` resolvem um ponto.

- **OPEN-01:** não há trava técnica que garanta o controle P1 (visibilidade `private=true` antes de gravar) nem a confirmação antes de escrever (E-04). Até existir mecanismo técnico, por exemplo a credencial de escopo único de PR-010 e a checagem de visibilidade como passo do fluxo, **o PR-003 está bloqueado**.
- **OPEN-02:** tipo exato, expiração e redução do alcance do token que a Zapia usa hoje (E-03): hoje alcança dois repositórios do proprietário alheios a este projeto. A conferir e corrigir pelo proprietário no GitHub.
- **OPEN-03:** estabilidade e regras da automação pela interface web do Gemini Notebook, que depende de sessão, de mudanças de interface e das regras do Google (E-01, E-02).
- **OPEN-04:** credencial própria e de menor permissão para o repositório privado, ainda inexistente.
- **OPEN-05:** retenção e política de privacidade da conta do Gemini usada (E-06).
- **OPEN-06:** a eliminação **física** dos dados em Google Calendar e Tasks não está verificada; a exclusão lógica está comprovada (E-07).
- **OPEN-07:** a criação de notebook e a adição de fontes de texto pelo Tutor (D-08) não foram testadas (E-08), e "Como estudar" é público e de terceiros; falta provar o procedimento em teste sintético com fontes públicas (PR-012) e confirmar com o proprietário que "cronograma" significa o cronograma da prova no edital.
- **OPEN-09:** os agentes serão criados (D-12), mas falta definir onde rodam (modelo e ambiente), como leem o harness, como emitem comandos à Zapia (canal e formato) e como a Zapia verifica a origem de cada comando; sem isso, a restrição da Zapia aos comandos dos agentes é só protocolo (E-04).
- **OPEN-10:** o acesso direto do Tutor ao NotebookLM só existe hoje por MCP não oficial, que exige sessão Google logada no ambiente do Tutor (uma credencial na prática); falta decidir se isso é aceito, com conta Google dedicada, ou se a ponte pela Zapia prevalece (E-11).
- **OPEN-11:** formato real da exportação de desempenho do TEC Concursos e do Qconcursos, que não pôde ser verificado; faltam amostras reais anonimizadas (E-11).
