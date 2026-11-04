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

## Ciclo 7 desta retomada — revogação e antifila obsoleta

- HEAD anterior: \`807cf108ba6fb640af768c351855da0e3ac7f618\`.
- CI prévia no SHA: \`41796129859\` e \`41796136364\` SUCCESS,
  cada uma com três matrizes de 50 testes e smoke Docker.
- Correção: \`enqueue()\` agora exige opt-in ativo dentro da mesma transação
  e \`set_enabled(False)\` cancela todos os proativos ainda pendentes.
  Reativar não ressuscita notificações antigas.
- Testes ajustados para consentimento antes de enfileirar; contraprovas
  específicas de revogação/reentrada.
- \`sending\` não é cancelável retroativamente e pode estar em trânsito.
- Sem chamadas reais a Telegram, Google ou OpenAI; sem deploy Oracle.

## Ciclo 8 desta retomada — produtor mínimo de avisos autônomos

- START anterior: \`b8ba689ea7d9fa5d8205da8e1fc4c679542752fd\`;
  CI anterior duas execuções SUCCESS (matriz + contêiner).
- Adicionado gerador determinístico \`bridge/checkins.py\`, com agendamento
  piloto Tutor 18h e Coach 19h no fuso Campo Grande, sem supor desempenho.
- Opt-in duplo: UFMS_GENERIC_CHECKINS=1 na Oracle e /ativar_alertas pelo aluno.
  Padrão desativado; sem catch-up após 10 minutos; chave por papel/dia.
- Contraprovas com mock: não enviar sem consentimento, idempotência,
  revogação, horários, ausência de progresso inventado.
- Sem implantação nem mensagem real; conferir CI e readback remoto.

## Correção do ciclo 8 — contraprova de idempotência

- START anterior: \`8e640214fdd058e508e6e68a455799d03b39bb00\`.
- Run \`41796805674\` identificou FAIL em \`test_idempotent_within_slot\`:
  o teste esperava erroneamente contagem 1 para segunda invocação com a
  mesma chave diária e data diferente. A implementação falha fechada
  e não cria evento duplicado, comportamento correto.
- Corrigida a expectativa para 0. Comprovação necessária no novo SHA;
  não herdar PASS de runs anteriores.


## Ciclo seguinte — privacidade na interface de IA

- START no PR #3: \`9976b7db92ee86fece350a4f72e4715678b247e2\`
  aberto draft, não mesclado. PRs #1 e #2 independentes.
- NC-PV-01: habilitar \`UFMS_LLM_ENABLED\` na Oracle habilitava encaminhar
  texto do Telegram à API sem opt-in do usuário no chat. **Corrigido
  por contrato no código proposto**: /ativar_ia, /desativar_ia, /ia_status,
  consentimento global separado da outbox e verificação transacional no módulo.
- Revogação limpa metadados de requisições; chamadas já em voo não são
  revertíveis. Sem exposição de segredos ou execução real da API.
- Novas contraprovas: nenhum texto sem opt-in; opt-in/revogação cruzados entre
  papéis; chamada direta bloqueada; metadados removidos; servidor desabilitado.
- CI e readback remoto obrigatórios no novo SHA. Sem merge/produção.


## Complemento do gate de privacidade — transporte Telegram

- START verificado: \`f2b89d051577eccf17280b0eb88fdc98190e68d0\`.
- Análise: URL Bot API inclui token, e falhas HTTP cruas poderiam vazar
  dados ao traceback ou logs. Agora há sanitização da exceção no cliente.
- Contraprovas com token sintético: traceback e mensagem sem credencial,
  falha HTTP 401 e resposta \`ok:false\` não tratadas como sucesso.
- Os logs de infraestrutura e serviços externos continuam fora deste teste;
  requer auditoria de implantação em VM.

## RATE-01 — entrega de cotas e retenção (04/11/2026)

- START exato: PR #3 `31b101e06bb132f7905d1c52a82fe8723480004d`,
  draft não mesclado. PRs #1/#2 continuam em branches independentes.
- Limites de lembretes manuais: 20 novos por 24h e 30 ativos em conjunto
  Tutor+Coach; ambos sob `BEGIN IMMEDIATE`, com replay idempotente exato.
- Normalização de datas de vencimento para UTC; validação de entrada
  inclusive quando a API de Store é chamada diretamente.
- Migração aditiva de `finalized_utc`. Limpeza opcional `--apply`,
  padrão dry-run e somente sent/cancelled cuja finalização provada excede
  30 dias; estados uncertain/sending/pending preservados.
- Novos testes com dados fictícios para quotas, migração, retenção, privacidade
  e rejeição; validação por CI no SHA resultante **ainda obrigatória**.
- Sem eventos reais no Google Agenda, Telegram, Oracle ou OpenAI;
  não houve exclusão de dados pessoais. Auditoria independente G0 pendente.
- Próxima pendência: proteção de backup criptografado, limites de credenciais
  e operação Oracle somente com autorização humana.
