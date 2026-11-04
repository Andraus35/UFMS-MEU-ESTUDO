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
