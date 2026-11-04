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
