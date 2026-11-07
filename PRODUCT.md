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
| Zapia | assistente de IA do produto; executa os papéis Tutor (persona Aragonê) e Coach (persona Carter); acessa o GitHub pela API REST, com credencial em gerenciador seguro, e o Gemini Notebook pela interface web autenticada; não há MCP de GitHub nem de Notebook conectado (E-01) | acessar contas das plataformas por robô, inventar dados, mudar regras |
| Harness (este repositório) | fonte de verdade persistente: regras, validadores, edital indexado, fila, prescritor, pontuação de simulados, gerador de prompt de revisão | executar ação externa por conta própria |
| Gemini Notebook | ambiente de revisão e fonte de método; recebe o prompt e devolve a revisão | ser fonte normativa do edital, guardar dado pessoal além do prompt mínimo |
| TEC Concursos e Qconcursos | plataformas de questões, operadas pelo estudante | — |
| Agentes construtores (Claude, GPT e outros) | constroem e auditam o harness, sempre por PR | operar estudo real, receber credencial de escrita pessoal, mesclar |

## 3. Fluxo ponta a ponta

- **F1 Iniciar:** a Zapia faz o START de estudo (4 arquivos) e identifica a situação: nada pendente, caderno pendente ou resultado a processar.
- **F2 Recomendar:** o harness fornece a fila determinística e a prescrição (assunto, nível, filtros em camadas, quantidade, justificativa); a Zapia apresenta um caderno principal. Nunca afirma disponibilidade de questões.
- **F3 Resolver:** o estudante cria e resolve o caderno na plataforma.
- **F4 Devolver:** o estudante entrega total, acertos, erros, data e, quando houver, resultado por tópico.
- **F5 Validar:** a Zapia aplica o contrato de ingestão do harness (coerência de contagens, escopo, convenção de contagem); inconsistência é recusada ou esclarecida, nunca corrigida em silêncio.
- **F6 Registrar:** a Zapia grava o evento no repositório privado, sob os controles P1 a P9 do ADR-013 (ver D-02). Sem todas as condições cumpridas, o resultado fica pendente e não é declarado registrado.
- **F7 Reavaliar:** o harness recalcula evidência (E0 a E4) e fila; o que é desconhecido permanece desconhecido.
- **F8 Revisar:** o harness gera um prompt mínimo de revisão; a Zapia o envia ao Gemini Notebook pela interface web (E-01); a revisão volta à Zapia e ao estudante; o harness guarda só metadados (assunto, data, fonte).
- **F9 Acompanhar:** a Zapia, no papel de Coach, envia mensagens e lembretes dentro de rotina previamente autorizada, com limites, idempotência e readback.
- **Simulados:** pontuação ponderada e comparabilidade conforme `docs/pedagogia/PROTOCOLO_SIMULADOS_v1.4.md`; nunca declarar aprovação.

## 4. Fronteiras de dados

- **Repositório público (este):** regras, código, edital, fixtures sintéticas. Nunca dado pessoal.
- **Repositório privado `Andraus35/ufms-meu-estudo-dados`:** resultados e eventos, somente depois de criado pelo proprietário, com consentimento registrado e controles P1 a P9.
- **Gemini Notebook:** recebe só o mínimo do prompt (assunto, lacuna, método, exigência de fonte). Enviar dado a terceiro é ação sensível, e a retenção na conta do Gemini não foi verificada (E-06, OPEN-05).
- **Em lugar nenhum:** CPF, documentos, credenciais, tokens, exports brutos, capturas de tela, texto integral de questões ou comentários de professores.

## 5. Decisões do proprietário

- **D-01 (07/11/2026):** repositório privado separado `Andraus35/ufms-meu-estudo-dados`. A criação é ato do proprietário.
- **D-02 (07/11/2026):** a Zapia grava os resultados desde o início, pela API REST do GitHub com credencial própria dela. Revisa a decisão anterior de que o proprietário gravaria manualmente. A habilitação continua condicionada aos controles P1 a P9, à resolução de OPEN-01 e OPEN-02 e a PR próprio com aprovação humana; até lá `personal_results_writes_enabled` permanece `false`.
- **D-03 (07/11/2026):** retenção até a prova mais 30 dias; revogação efetiva é apagar o repositório privado inteiro.
- **D-04 (07/11/2026):** texto de consentimento v1 aprovado (texto no ADR-013).
- **D-05 (07/11/2026):** o harness gera o prompt, a Zapia o envia ao Gemini Notebook e só metadados voltam ao repositório. O mecanismo observado é a interface web, não MCP (E-01); a escolha do mecanismo por parte do proprietário precisa ser reconfirmada.
- **D-06 (07/11/2026):** o recorte GP-3-MVP8 foi aceito como cobertura técnica mínima sintética.
- **D-07 (07/11/2026):** este arquivo é leitura obrigatória no START de engenharia, como 3º arquivo.

## 6. Não objetivos e proibições

- Não acessar TEC Concursos ou Qconcursos por robô nem fazer scraping.
- Não inventar questões, gabaritos, notas, cadernos, disponibilidade, resultados, citações ou fontes.
- Não conceder token de escrita pessoal a agente construtor; não gravar credencial em arquivo ou prompt.
- Não gravar dado pessoal no repositório público, nem com a flag de escrita ativada.
- Não declarar integração (Zapia, Gemini, agenda) sem prova; não confundir CI verde com eficácia pedagógica.
- Não impor cronograma, meta universal ou intervalo fixo de revisão.
- Não ser produto multiusuário nem comercial.

## 7. Requisitos de produto

- **PR-001 START determinístico:** o START de engenharia lê este arquivo como 3º, com hash, e o gate de estrutura o valida. Aceite: `python scripts/bootstrap.py --mode engineering` lista `PRODUCT.md` na 3ª posição com SHA-256 e `python scripts/product_gate.py --check` passa. Elo: RM-00.
- **PR-002 Gerador de prompt de revisão:** função offline e determinística que monta o prompt mínimo de F8 a partir de assunto, lacuna, método e exigência de fonte; exige fonte verificada, separa títulos citados mas não verificados e recusa dado pessoal. Aceite: testes com fixtures sintéticas, inclusive prompt com dado pessoal recusado e prompt sem fonte recusado. Elo: RM-09.
- **PR-003 Escrita da Zapia no repositório privado:** proposta, validação P1 a P6, commit e readback. Aceite: provas P1 a P3 e P5 a P6 contra o repositório privado real, com OPEN-01 e OPEN-02 resolvidos. Elo: RM-08.
- **PR-004 Repositório privado criado e verificado:** Aceite: leitura autenticada devolve `private=true`; dono: proprietário. Elo: RM-08.
- **PR-005 Metadados da revisão:** registro de assunto, data e fonte, sem texto integral. Aceite: esquema validado e teste negativo que recusa texto integral. Elo: RM-09.
- **PR-006 Ciclo ponta a ponta real:** F1 a F8 com um resultado real e consentido, com readback. Aceite: relatório do ciclo e CI verde no HEAD. Elo: RM-08.
- **PR-007 Rotina do Coach pela Zapia:** mensagens e lembretes autorizados. Aceite: prova de autorização, idempotência e limites. Elo: RM-09.
- **PR-008 Simulados no fluxo:** pontuação e comparação de simulados usadas em F5 e F7. Aceite: `scripts/simulado_score.py` e `scripts/simulado_session.py` acionados nesses passos, com teste. Elo: RM-06.
- **PR-009 Retomada entre sessões e modelos:** estado reconstruído dos eventos e dos arquivos do START, nunca da conversa. Aceite: `python scripts/rebuild.py --check` passa e nenhum estado existe só em conversa. Elo: RM-00.
- **PR-010 Credencial mínima da Zapia:** token de escopo único por repositório, sem administração nem workflows e com expiração; o repositório privado usa credencial própria, sem alcance sobre o público. Aceite: o proprietário confirma o escopo nas configurações do GitHub e a Zapia comprova, em teste sintético, que a escrita fora do repositório designado é recusada. Elo: RM-08.
- **PR-011 START de estudo executável pela Zapia:** como ela não lê o repositório sozinha no início da sessão (E-05) e executa Python (E-04), o início passa a ser um procedimento explícito: obter o repositório, executar `python scripts/bootstrap.py --mode study` e informar os SHA-256 dos 4 arquivos. Aceite: relatório com hashes iguais aos do repositório e teste do procedimento com fixture; é procedimento, não trava técnica. Elo: RM-00.

## 8. Ordem de construção

Dependências, não status (o status vive no `ROADMAP.md`):

- **B1:** PR-001 e PR-011.
- **B2:** PR-004 (proprietário).
- **B3:** PR-002 (independente, offline).
- **B4:** PR-003 (depende de B2, de PR-010 e de OPEN-01 e OPEN-02).
- **B5:** PR-005 (depende de B3).
- **B6:** PR-006 (depende de B4 e B5).
- **B7:** PR-007 e PR-008.

## 9. Glossário

- **Caderno:** conjunto de questões criado pelo estudante no TEC Concursos ou Qconcursos.
- **Gemini Notebook:** ambiente de revisão no Gemini usado pela Zapia (por exemplo o notebook "Como estudar"). Não é caderno de questões.
- **`notebook_prescriber`:** prescreve cadernos de questões; não gera prompts para o Gemini.
- **Prescrição:** plano de caderno sem efeito externo. Recomendação, confirmação e execução são estados distintos.
- **Tutor e Coach:** papéis executados pela Zapia, hoje com as personas Aragonê (Tutor) e Carter (Coach); não são agentes permanentes separados. O Tutor orienta e escolhe intervenções; o Coach acompanha e lembra.
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
- Operação, START e DELIVERY: `docs/OPERACAO.md`.
- **Substituído como porta de entrada de construção:** `docs/pedagogia/PROMPT_TRANSFERENCIA_TECNICA_v1.8.md` (histórico).

## 11. Evidências de referência

Fatos datados, não estado. Os itens E-01 a E-06 são **autorrelato da Zapia** (07/11/2026), registrado em `docs/governanca/RESPOSTA_VERIFICACAO_ZAPIA_20261107.md`; nenhum agente construtor os reverificou, exceto o que consta naquele documento.

- **E-01 Mecanismo de acesso:** GitHub pela API REST, por HTTP a partir do ambiente de execução da Zapia, com credencial em gerenciador seguro; a tentativa de conectar o MCP oficial do GitHub foi recusada. Gemini Notebook pela interface web autenticada do navegador; não há MCP de Notebook. As POCs de 04/11/2026 existem em `poc/README.md` e são provas sintéticas.
- **E-02 Capacidades testadas:** GitHub: ler arquivo, criar branch e gravar commit. Não testadas: abrir PR, ler CI, apagar. Notebook: abrir, ler fontes, enviar prompt, ler a resposta e conferir uma citação. Não testadas: listar, adicionar fonte, criar, apagar.
- **E-03 Credencial:** guardada em gerenciador seguro e usada por referência; a Zapia afirma não receber o valor como texto (documentado, não verificável por agente construtor). Escopo, permissões e expiração do token **não verificados**. Acesso verificado apenas ao repositório deste projeto.
- **E-04 Controles:** não há trava técnica que force a checagem de visibilidade nem a confirmação humana antes de escrever; existe apenas protocolo conversacional. A Zapia executa comandos e Python. Os commits das POCs constam com a autoria do proprietário, então o histórico não distingue quem gravou.
- **E-05 Memória e rotina:** memória persistente própria; não lê o repositório sozinha no início da sessão. Um lembrete estático no app foi entregue em 04/11/2026; WhatsApp não está comprovado como recebido pelo aparelho; Telegram exige aprovação; a exclusão de eventos do Calendar não foi confirmada por leitura.
- **E-06 Privacidade do Gemini:** o prompt e o contexto do notebook vão ao serviço do Google; retenção e política da conta **não verificadas**.

As POCs não provam execução recorrente, acesso às plataformas de questões nem domínio pedagógico.

## 12. Pontos a confirmar

Cada ponto vira decisão ou requisito por PR; até lá, não afirmar o mecanismo. Roteiro de perguntas: `docs/governanca/PROMPT_VERIFICACAO_ZAPIA_20261107.md`. Só respostas com status `OBSERVADO` ou `DOCUMENTADO` resolvem um ponto.

- **OPEN-01:** não há trava técnica que garanta o controle P1 (visibilidade `private=true` antes de gravar) nem a confirmação antes de escrever (E-04). Até existir mecanismo técnico, por exemplo a credencial de escopo único de PR-010 e a checagem de visibilidade como passo do fluxo, **o PR-003 está bloqueado**.
- **OPEN-02:** escopo, permissões e expiração do token que a Zapia usa hoje (E-03), a conferir pelo proprietário no GitHub, e se a mesma credencial alcança repositórios privados.
- **OPEN-03:** estabilidade e regras da automação pela interface web do Gemini Notebook, que depende de sessão, de mudanças de interface e das regras do Google (E-01, E-02).
- **OPEN-04:** credencial própria e de menor permissão para o repositório privado, ainda inexistente.
- **OPEN-05:** retenção e política de privacidade da conta do Gemini usada (E-06).
