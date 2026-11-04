# Ponte UFMS: Telegram + Google Calendar (MVP isolado)

**Estado:** proposta técnica EXECUTÁVEL EM TESTES LOCAIS; NÃO implantada na Oracle,
NÃO conectada ao Tutor/Coach LLM, NÃO autorizada no Google Calendar remoto.
O PR fica em draft e não deve ser mesclado sem auditoria independente e aceite humano.

## Escopo

- Dois bots Telegram distintos para Tutor/Coach; somente conversas privadas do
  ID autorizado. Não existem endpoints públicos nem acesso a terceiros.
- Comandos `/start`, `/ajuda`, `/status`, `/lembrete`, `/cancelar`,
  `/pausar`, `/retomar`, `/evento`.
- SQLite persistente para lembretes e offsets de atualização, retomada após restart.
- Mensagens proativas são as de lembretes explicitamente registrados; o canal
  está preparado para futura integração com o motor de IA, que NÃO está implementada.
- Google OAuth de acesso offline é **independente** da conexão ChatGPT.
  Criação de calendário secundário por comando local explícito e, depois,
  criação de eventos somente no calendário de ID configurado.

## Executar testes (sem chamadas de rede)

```bash
cd integrations/oracle_bridge
PYTHONPATH=. python -m unittest discover -s tests -v
```

## Configuração (operador, na Oracle)

1. Criar dois bots no BotFather e iniciar conversa privada com cada um.
2. Obter o `user_id` numérico via procedimento de confiança do Telegram; nunca
   expor tokens ou IDs pessoais em issues, commits ou logs.
3. Copiar `.env.example` para `.env` **somente no servidor** e proteger com
   permissões restritas, preferencialmente usar um gerenciador de segredos.
4. Opcional: configurar Google OAuth de aplicativo próprio com acesso offline.
   Usar consentimento humano, `calendar.app.created` para o calendário criado
   pela aplicação e escopo `calendar.events.freebusy` somente se se decidir
   ler disponibilidade dos demais calendários. O MVP **não lê** eventos pessoais.
5. Uma única vez, após OAuth: `python -m bridge.cli provision-calendar`;
   armazenar ID retornado em `UFMS_GOOGLE_CALENDAR_ID`. Esta ação CRIA
   um calendário real; não execute repetidamente.
6. `docker compose up -d --build` na VM. Implantar **uma única réplica**:
   offset, agendamento e envio ainda não suportam múltiplas instâncias.
7. Não configurar webhook nos mesmos bots: esta versão usa `getUpdates`
   por long polling. Não abrir porta pública ou expor a aplicação.
8. Fazer backup criptografado do volume SQLite e validar restauração.

## Limitações e riscos conhecidos

- Sem credenciais, os bots não iniciam. Google OAuth e BotFather requerem
  intervenção humana explícita.
- O campo de fuso é obrigatório nas datas ISO; períodos usam UTC internamente.
- Se o Telegram receber a mensagem, mas a confirmação falhar, pode haver
  reenvio na retomada. Sem garantia exactly-once; analisar idempotência do
  envio no próximo gate.
- Falta política de retenção, telemetria segura, quotas antispam, integração
  ao estado do Tutor e Coach e validação ponta a ponta na Oracle.
- O MVP não é um agente LLM: texto livre apenas retorna ajuda.
- A conta Google conectada no ChatGPT não disponibiliza tokens para esta VM.
- Apenas alertas de lembretes originados no Telegram são executados; nenhum
  check-in de IA é disparado automaticamente nesta versão.
- Operações que falharem remotamente não devem ser declaradas concluídas.
- Não inserir dados de desempenho reais antes de validar privacidade/consentimento.

## Fontes oficiais

- Telegram Bot API: https://core.telegram.org/bots/api
- Google OAuth offline: https://developers.google.com/identity/protocols/oauth2/web-server
- Escopos Calendar: https://developers.google.com/workspace/calendar/api/auth
- Calendars.insert: https://developers.google.com/workspace/calendar/api/v3/reference/calendars/insert

## Próximo gate técnico

G0: testar cenários adversariais; G1: verificar OAuth/escopos e segredo no
ambiente; G2: ponta a ponta Telegram com dois bots, recuperação após reinício;
G3: calendário secundário e evento real autorizados; G4: integração com
motor pedagógico pós-PR #1/#2; G5: piloto e aceite humano.

## Envio proativo (ciclo 2 — ainda sem motor LLM)

- Os comandos privados \`/ativar_alertas\`, \`/desativar_alertas\`, \`/alertas\`
  gerenciam consentimento independente da pausa global \`/pausar\`.
- A fila \`ProactiveOutbox\` permite que um **produtor de confiança futuro**
  enfileire eventos Tutor/Coach com categoria (\`review\`, \`checkin\`,
  \`deadline\`, \`strategy\`), referência e chave idempotente.
- Nenhuma saída textual de modelo de IA chama \`enqueue\` diretamente.
  Integrar depois de autenticação, validação, autorização e testes dos papéis.
- Padrão: opt-in desligado, 4 mensagens proativas por dia **somando os dois bots**,
  uma a cada 60 minutos, somente das 07:00 às 22:00
  (\`America/Campo_Grande\`); cada sessão é sem agendamento compulsório.
- Lembretes criados explicitamente pelo aluno no comando \`/lembrete\`
  não entram nessa cota; seguem a política de pausa global.
- \`sending\` e \`uncertain\` não são reenviados após falhas/crash.
  **Trade-off:** reduz duplicação automática mas pode perder um aviso; operador
  precisa reconciliar com o Telegram antes de qualquer reenvio manual.
- A implementação atual é um núcleo de agendamento, não coach conversacional.
  Falta canal confiável do motor pedagógico para a outbox, política de retenção
  e controles ajustáveis pelo usuário.

## Tratamento de confirmação incerta (ciclo 3)

Consulte [Política de entrega e reconciliação](../../docs/integracoes/POLITICA_ENTREGA_v0.2.md).
Agora **ambos** os tipos de mensagem (lembretes manuais e proativas) evitam
reenvio automático após ACK incerto ou queda do processo no meio do envio.
Isso é entrega conservadora **at-most-once automático**, não garantia de
recebimento. `bridge.reconcile` permite marcar estado após verificação
humana, sem expor os conteúdos. A CI testa reinício, migração SQLite antiga,
tentativa duplicada, payload sigiloso e troca de estado.

## Correção Google Calendar (ciclo 4)

- ID estável de evento é codificado em **base32hex**, não hexdigest,
  respeitando os caracteres [0-9a-v] exigidos pela API Google.
- No HTTP 409, o serviço faz leitura de \`events.get\` e somente confirma
  sucesso se ID, título e instantes de início/fim corresponderem; conflitos
  divergentes ou não verificáveis falham sem afirmar criação.
- Datas sem fuso, duração inválida e título/chave vazios são rejeitados
  antes da rede. Não houve chamadas reais à conta Google neste ciclo.

## Conversas Tutor/Coach com IA (ciclo 5 — desativadas por padrão)

- Definir no ambiente seguro \`UFMS_LLM_ENABLED=1\`,
  \`UFMS_OPENAI_API_KEY\`, \`UFMS_OPENAI_MODEL\` (padrão configurável:
  \`gpt-6-luna\`) e \`UFMS_LLM_DAILY_LIMIT\` (padrão 30 interações/dia
  somando os dois bots).
- **OpenAI Responses API** somente para texto. A mensagem do Telegram é
  enviada à API após validação de identidade. É necessário consentimento do
  proprietário para esse processamento e verificar custo por token.
- Não existem ferramentas de criação de agenda, acesso a repositório, scraping
  ou execução na chamada de IA; respostas são apenas texto. Comandos seguros
  do Telegram continuam sendo roteados separadamente.
- \`store=false\` é solicitado à API. SQLite registra apenas papel, chave do
  update e horário de consumo para evitar nova cobrança em replays; não guarda
  conteúdo do chat. Sem memória conversacional nesta primeira integração.
- O Tutor evita afirmar leitura do edital sem evidência; o Coach evita impor
  cronograma e criar compromisso por simples sugestão. Papéis distintos.
- **Ainda não é um agente adaptativo completo**: não recupera automaticamente
  chunks do edital, resultados pessoais ou handoff dos PRs #1 e #2. Essa
  integração demanda versionamento, consentimento, provedor de contexto
  autorizado, persistência e testes antes de afirmar continuidade real.

## Gate de contêiner (ciclo 6)

A CI passa a testar a imagem real com \`docker build --pull\` e inicialização
como usuário não-root. O teste verifica imports de Tutor/Coach, persistência
SQLite em \`/data\`, política de opt-in desativada e base de fusos
\`America/Campo_Grande\`. O smoke não envolve credenciais, rede Telegram,
conta Google ou chamadas reais à OpenAI API. Não é validação de produção
Oracle nem substitui os testes ponta a ponta consentidos.

## Revogação de consentimento (ciclo 7)

- Antes de inserir notificação proativa, o servidor exige consentimento ativo
  **na mesma transação**. Não há fila proativa pré-consentimento.
- \`/desativar_alertas\` revoga consentimento e cancela avisos ainda pendentes.
  Se o usuário reativar depois, nada da antiga fila volta automaticamente;
  eventos novos precisam de nova chave idempotente e nova decisão rastreável.
- Uma mensagem em trânsito (\`sending\`) pode já ter alcançado o Telegram
  quando a revogação ocorre; não há cancelamento retroativo de rede.
  O estado é mantido para reconciliação. O serviço não deve prometer
  ausência absoluta de mensagens que já estavam em envio.

## Check-ins genéricos e opt-in duplo (ciclo 8)

O produtor \`bridge/checkins.py\` permite envio proativo sem um motor LLM
com contexto, mas **somente** com \`UFMS_GENERIC_CHECKINS=1\` no servidor
**e** \`/ativar_alertas\` na conversa privada do Telegram. Por padrão
está **desligado**. Horários-piloto: Tutor 18h, Coach 19h no fuso
\`America/Campo_Grande\`; ambos respeitam limite global e intervalo mínimo.

- Mensagens perguntam se há dúvidas ou necessidade de ajustes; nunca
  mencionam progresso, resultado, calendário ou erro que não tenham observado.
- Cada bot gera no máximo uma chave por dia. Reinício fora dos 10 minutos
  iniciais da janela não provoca check-in atrasado.
- Cancelar consentimento descarta fila pendente. Reativação não ressuscita
  check-ins cancelados.
- Não chamar esses check-ins de coaching adaptativo: falta conexão com
  evidências e feedback real do motor pedagógico.


## Consentimento separado para conversas com IA (gate de privacidade)

Mesmo com \`UFMS_LLM_ENABLED=1\`, textos privados **não** são enviados à
Responses API até o estudante usar \`/ativar_ia\` em um dos bots autorizados.
O consentimento cobre Tutor e Coach; pode ser consultado em \`/ia_status\`
e revogado em \`/desativar_ia\`. A revogação impede novas requisições,
apaga metadados locais \`llm_requests\` e não cancela um HTTP já enviado.
Permissão para conversas é independente da permissão para alertas proativos
e do OAuth Google Calendar. Ver
[gate de privacidade](../../docs/integracoes/CONSENTIMENTO_IA_v0.3.md).


## Segurança do transporte Telegram (gate técnico)

- O cliente HTTP converte falhas de transporte/HTTP/JSON em mensagem genérica
  sem URL ou parâmetros; a URL de chamada do Telegram contém o token do bot.
- O traceback exposto para esse tipo de falha não inclui o token quando a
  exceção é encadeada como \`from None\`; verificar logs de infraestrutura
  antes de produção, pois outras camadas podem registrar URLs.
- Resposta \`ok:false\` nunca confirma envio. Isso preserva a política
  conservadora de mensagens \`uncertain\`.

## RATE-01 — Cotas e retenção de lembretes

Implementado controle transacional por usuário: até 20 lembretes novos em 24h
compartilhados entre os bots e até 30 ativos. Chaves de requisição idênticas
não consomem nova cota; conteúdo divergente não pode reutilizar a chave.
Os horários são normalizados para UTC. A manutenção de histórico é
**manual por padrão** e começa em modo de visualização sem deletar dados;
`--apply` remove somente lembretes finalizados há mais de 30 dias,
nunca itens pendentes ou de confirmação incerta. Não há limpeza automática
nem apagamento de backups. Ver
[contrato RATE-01](../../docs/integracoes/RATE_RETENCAO_v0.4.md).


## OPS-01 — Backup criptografado, restauração offline e credenciais

O módulo \`bridge.ops_backup\` implementa:
- \`backup\`: snapshot consistente SQLite (online), validação de integridade,
  criptografia \`age\` para uma chave **pública** e publicação atômica
  sem sobrescrever arquivos; cópia temporária em \`/tmp\` (tmpfs).
- \`verify\`: descriptografa para memória temporária em disco volátil, confere
  integridade e estrutura SQLite, sem sobrescrever o banco.
- \`restore\`: exige \`--confirm-restore\`; para substituir banco existente
  também exige \`--replace-existing\`. Recusa se o gateway estiver ativo
  (lock exclusivo) ou se existirem arquivos WAL/SHM. Não há restauração
  automática após falhas.
- A chave privada \`age\` NUNCA é incluída na imagem, no repositório ou no
  serviço de produção; é entregue somente ao operador de restauração.
- Arquivo \`.env\`, chaves Telegram, OAuth e OpenAI não entram em commits,
  issues, logs ou backups documentais. Segredos do ambiente Oracle exigem
  configuração externa.
- Script não faz upload, rotação ou eliminação de backups automaticamente;
  ciclo de vida e armazenamento fora da instância permanecem pendentes.

**Operação e contraprovas:** consulte
[OPS-01 — Procedimento operacional](../../docs/integracoes/OPS01_BACKUP_ORACLE_v0.5.md).

## Aplicativo Android complementar mantido — Gemini Notebook

O aluno pode usar o **Gemini Notebook (antigo NotebookLM)** para estudar
fontes públicas e autorizadas, fazer perguntas e revisar conteúdos pelo
Android/web no acesso **padrão gratuito**, sem assinatura. Ele complementa
os bots Tutor/Coach, mas **não está automaticamente integrado** à ponte
Oracle e não fornece ao modelo dos bots acesso a seus notebooks.
O único aplicativo Google com integração de conta prevista no MVP é
**Google Agenda**. Os limites gratuitos do Gemini Notebook devem ser
respeitados, sem upgrade automático e sem novas credenciais nesta etapa.
Veja [decisão de ferramentas mínimas](../../docs/integracoes/DECISAO_STACK_MINIMA_GRATUITA.md).

## PoC Gemini Developer API — somente backend, sem conexão real

O módulo `GeminiAgentBridge` implementa payload REST de texto em
`generateContent` para `gemini-3.5-flash-lite` (modelo listado no Free
Tier em 04/11/2026). Continua **desativado por padrão** e requer parâmetros
explícitos `UFMS_LLM_ENABLED=1`, `UFMS_LLM_PROVIDER=gemini`,
`UFMS_GEMINI_FREE_PROJECT_ATTESTED=1`,
`UFMS_GEMINI_PRIVACY_REVIEWED=1`, chave e modelo reconhecido.
A configuração não seleciona API OpenAI faturada e removeu o identificador
não verificado de modelo. Os flags de confirmação são somente declarações;
**não garantem** que a conta Google esteja sem cobrança.

**Estado da integração:** PoC isolada, sem habilitação de conversas no gateway
Telegram. O módulo exige consentimento específico `gemini_data_consent`
e consentimento LLM na transação SQLite, mas o comando Telegram de
consentimento específico ainda não foi integrado: a API não pode receber
mensagens pelo caminho normal do bot nesta entrega.

Os testes são de protocolo e respostas sintéticas. Sem uso de chave real,
sem chamadas à nuvem Google, sem acesso ao Gemini Notebook, sem cobrança
ou integração com dados pessoais. <https://ai.google.dev/gemini-api/docs/pricing>.
