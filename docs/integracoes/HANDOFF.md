# Handoff — integração pessoal Telegram/Oracle/Google

Data: 04/11/2026; contexto: nova frente técnica isolada.
Repositório: Andraus35/UFMS-MEU-ESTUDO.
Branch proposta: feature/oracle-telegram-calendar-bridge.
Base inicial da main no START: c020f78ba07ebb4e2949021b45a7f9b8f2c26d42.
PR de engenharia #1 e PR pedagógico #2 já estão abertos como drafts; esta
entrega não altera qualquer arquivo desses PRs ou a main.

## Entrega

- MVP Telegram de dois bots com autorização pelo ID privado e long polling.
- Comandos de lembrete, pausa, retomada, status, cancelamento e evento na Agenda.
- SQLite de filas e offsets, separação de bots Tutor e Coach, replays básicos.
- Cliente Google OAuth offline com renovação de token e criação de calendário
  secundário e eventos com ID de requisição determinístico.
- Docker/Compose, testes isolados, documentação de operação e CI.
- Todos os mecanismos são protótipos de engenharia; NÃO há motor LLM, alertas
  espontâneos baseados em análise de aprendizagem, nem serviço Oracle ativo.

## Gates pendentes

1. Readback GitHub do commit exato e CI verde no mesmo SHA.
2. Revisão adversarial e correção de falhas de segurança e idempotência.
3. Tratamento de duplicidade de envio quando falha ACK do Telegram.
4. Proteção de segredos e backups na VM; limitação de frequência e retenção.
5. Consentimento OAuth independente; calendário secundário real, se autorizado.
6. BotFather: dois tokens, user ID e conversa iniciada com cada bot.
7. Integração posterior do Tutor/Coach e seus contratos com PR #1/#2.
8. Implantação, testes de reboot e aceite humano antes de produção.

## Restrições

Nenhuma alteração em AGENTS, edital, pedagógico, regras, guardrails ou estado.
Não commitar credenciais, dados reais, chat_id ou resultados pessoais.
Não executar merge sem autorização humana. Não afirmar conectividade real com
Telegram, Oracle ou Google a partir da simples existência de código.

## Ciclo autônomo desta sessão — notificação proativa (04/11/2026)

- START readback: HEAD anterior do PR #3 \`c0dfc4979c50a73fb9191cc57fbd15c90891f1d9\`.
- Adicionados \`bridge/proactive.py\`, testes adversariais sem rede e comandos
  \`/ativar_alertas\`, \`/desativar_alertas\` e \`/alertas\`.
- Política: desabilitado até consentimento explícito; limite global Tutor+Coach;
  silêncio 22–07, intervalo mínimo e bloqueio de destinatários não autorizados.
- Se houver incerteza no ACK, manter \`uncertain\` sem retry automático;
  queda após claim deixa \`sending\` sem retry. Requer conciliação manual,
  não equivale a entrega garantida. Um job de reconciliação ainda está pendente.
- Não foi criado servidor Oracle, não há bots reais nem OAuth Oracle; nenhum
  evento da sua agenda real foi criado ou modificado.
- Validar CI no novo SHA, depois testar isolamento e recuperação de estado.

## Ciclo 2 desta retomada — reconciliação conservadora

- HEAD esperado no início: `d0929c01a8376431846df4c96e554f813ec27ca8`.
- Gaps remediados: lembrete manual já não sofre retry cego após ACK ambíguo;
  migração aditiva da coluna `claimed_utc` é não destrutiva.
- Relatórios de conciliação exibem somente IDs, papéis e estados;
  `sending`/`uncertain` exigem decisão do operador.
- Contraprovas novas: queda após claim, confirmação ambígua, corrida entre
  duas conexões, idempotência, migração e ausência de texto pessoal no relatório.
- Limites permanecem: não há deploy Oracle, OAuth Google Oracle nem motor IA.
- Próximo ciclo: verificar CI, auditoria de integridade de dados e fronteira
  entre agenda, Telegram e memória pedagógica.

## Ciclo 3 desta retomada — validação Google Calendar

- START esperado: \`fb957fd9e167dea06296fab1decd116cf6c4f265\`.
- Bug identificado em auditoria: ID hexadecimal de SHA contém letras w-z,
  incompatíveis com a regra de IDs \`base32hex\` do Calendar API.
- Correção: base32hex determinístico; HTTP 409 agora exige \`events.get\` e
  comprovação de equivalência do evento, com erro em divergência.
- Contraprovas: 128 IDs válidos, duplicidade verdadeira versus falsa,
  datas sem UTC offset, intervalo invertido.
- Fonte: https://developers.google.com/workspace/calendar/api/v3/reference/events
- Nenhum evento real criado; validar CI/readback no novo SHA.

## Ciclo 4 desta retomada — correção de teste não determinístico

- START esperado: \`54dfc79a94cd30a09c41f2fe793ab56b091d372a\`.
- No SHA anterior, dois runs da CI divergiram: run \`41795395690\` FAIL,
  run \`41795401235\` PASS. A causa observada foi um teste antigo que gerava
  início e fim com duas chamadas a \`datetime.now()\`, podendo produzir
  intervalo nulo. A validação de intervalo do Calendar está correta.
- O teste agora usa instante fixo com duração de 1h. CI executa matriz
  com PYTHONHASHSEED 0, 11 e 97 para detectar mais instabilidade.
- Todas as execuções da matriz devem passar no SHA exato; a existência de
  um PASS isolado não cancela o FAIL anterior.

## Ciclo 5 desta retomada — conversa bidirecional por API de IA

- START verificado: \`59f930811839a2f556f872c6e8da587949c255f9\`;
  dois workflow runs da matriz 3/3 aprovados nesse SHA.
- Novo módulo \`bridge/agents.py\` com papéis explícitos Tutor/Coach,
  Responses API, quota global de chamadas, replay por update ID e
  \`store=false\`; nenhum dado de chat é persistido localmente.
- Respostas só texto; sem tools da IA, sem acesso automático a Google Agenda,
  GitHub, TEC ou histórico do estudante. Habilitação opt-in pelo operador Oracle.
- Não há API key no repositório; testes usam stub HTTP e mensagens fictícias.
- Próximo gate: CI exata; depois auditoria de privacidade/custo e integração
  ao motor pedagógico apenas com contexto real autorizado.

## Ciclo 6 desta retomada — validação do artefato Docker

- START esperado: \`698424f5204d16a88f1d0002e2db0c1a3a15cba3\`;
  CI anterior 2/2 runs com três matrizes cada, PASS.
- Gate de container adicionado ao workflow: Docker build da imagem Oracle,
  execução não-root, timezone Campo Grande e SQLite em /data.
- Sem privilégios Oracle, sem credenciais pessoais e sem produção.
- Verificar o resultado no commit exato; se falhar, corrigir com novo commit.
