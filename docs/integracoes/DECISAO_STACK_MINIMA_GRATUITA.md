# Decisão de arquitetura — ferramentas gratuitas e suficientes

Data: 04/11/2026. Escopo: UFMS MEU ESTUDO, PR #3 Oracle/Telegram/Google.
Status: decisão de escopo; NÃO é homologação nem autorização de implantação.

## Critérios vinculantes

1. Nenhuma assinatura obrigatória, plano premium ou faturamento por uso
   permitido para os agentes sem nova autorização expressa.
2. Simplicidade: não integrar dois aplicativos para a mesma função.
3. Preferir APIs oficiais e gratuitas, sempre sob limites de cota e OAuth
   com permissão mínima. Sem scraping de serviços privados.
4. Não trocar a base canônica do repositório e o banco local Oracle por
   planilhas, notas, formulários ou aplicativos adicionais.
5. Toda integração fica desligada em caso de falta de credencial, cota,
   autorização, ou risco de cobrança. Sem upgrade automático.

## Núcleo aprovado para projeto

| Ferramenta | Papel | Custo/condição |
| --- | --- | --- |
| Telegram Bot API | Interface Android Tutor/Coach, notificações e feedback | API gratuita |
| Google Agenda (Calendar) | Compromissos visíveis no Android, somente calendário UFMS | API padrão sem cobrança dentro das cotas; monitorar limites |
| GitHub (repositório existente) | Fonte versionada de edital, estratégia, regras e código | Plano já disponível; não criar serviços pagos |
| Oracle Cloud | Execução da ponte em infraestrutura própria | Apenas instância e serviços elegíveis Always Free; não assumir capacidade garantida |
| SQLite + Python | Registro operacional, lembretes e progresso consentido | Software livre, sem serviço SaaS |

**Google Agenda é o único app Google com integração de conta aprovada.**
Calendário deve ser secundário, criado pela aplicação, usando escopo
`calendar.app.created` sempre que suficiente. Não acessar agenda pessoal
principal, contatos ou e-mails. OAuth do servidor Oracle é separado do
conector Google usado no ChatGPT. Verificar expiração de tokens OAuth para
aplicativo externo em status Testing (7 dias).

## Excluído da implementação ativa

- Google Tasks: duplicaria fila de lembretes e acompanhamento dos bots.
- Google Sheets e Forms: banco SQLite e Telegram são suficientes para
  registros, estatísticas e questões por enquanto.
- Google Docs/Drive/Keep: material estratégico já tem fonte versionada
  no GitHub; importação de PDF por Android pode ocorrer manualmente.
- Gmail/Contacts/YouTube/Google Chat/Meet: fora do escopo necessário.
- Gemini Notebook/NotebookLM: sem dependência, assinatura ou API exigida.
- Apps Script: não necessário porque os gatilhos e regras estão na Oracle.
- Provedor de IA com preço por token (inclusive OpenAI Responses API):
  **NÃO habilitar na Oracle** com a política de custo zero.

## Motor conversacional: gate específico ainda aberto

Tutor e Coach precisam de inferência de IA para respostas abertas.
A existência de ChatGPT instalado ou assinado não dá direito a API gratuita.
O módulo `bridge/agents.py` atual usa API OpenAI e está **desativado por
padrão**; sua ativação é incompatível com a decisão de custo zero.

A Gemini Developer API oferece nível gratuito com limites de utilização,
**mas o Google informa que o conteúdo desse nível pode ser usado para
melhorar seus produtos**. Logo, ela é apenas candidata, NÃO escolhida
automaticamente: exigir avaliação de privacidade e consentimento específico.
Não enviar dados pessoais de estudo até concluir esse gate. O serviço deve
parar ao atingir o limite gratuito, jamais migrar para cobrança.
Alternativa local sem custo por token só após validação real de desempenho
e capacidade na Oracle Always Free, sem inventar viabilidade.

Até aprovação de um modelo gratuito adequado, os bots permanecem operacionais
em modo determinístico (comandos, calendário, lembretes e check-ins opt-in),
mas **sem afirmar conversa com IA habilitada**.

## Fontes oficiais consultadas em 04/11/2026

- Google Calendar API quotas:
  https://developers.google.com/workspace/calendar/api/guides/quota
- Google Calendar escopos:
  https://developers.google.com/workspace/calendar/api/auth
- OAuth refresh token em Testing:
  https://developers.google.com/identity/protocols/oauth2
- Oracle Always Free:
  https://docs.oracle.com/pt-br/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- Telegram Bot API:
  https://core.telegram.org/
- Gemini API preços e privacidade:
  https://ai.google.dev/gemini-api/docs/pricing

## Critérios de aceite futuro

- Não incluir novas integrações Google sem justificar necessidade concreta.
- Testar bloqueio de funcionalidades de API paga, custos e cotas.
- Confirmar escopo OAuth mínimo e que alertas não dependem de assinatura.
- Não ativar IA nem fazer implantação OCI sem autorização do operador.
- Preservar PRs #1/#2 e manter PR #3 draft até auditoria independente.
