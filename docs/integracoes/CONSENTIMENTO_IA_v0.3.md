# Gate de privacidade e consentimento — Tutor/Coach e API de IA

**Estado:** contrato técnico do PR #3 (proposta, não produção). Data 04/11/2026.

## Problema observado
A ponte usava \`UFMS_LLM_ENABLED=1\` no servidor como autorização suficiente
para encaminhar automaticamente mensagens de texto dos chats Telegram para
uma API de terceiros. A configuração da infraestrutura **não substitui**
o consentimento explícito do usuário que conversa com os bots.

## Correção de fronteira
1. Requer habilitação operacional na Oracle (\`UFMS_LLM_ENABLED=1\`)
   **e** comando \`/ativar_ia\` em chat Telegram privado, por usuário
   autorizado. Padrão: consentimento ausente e envio bloqueado.
2. \`/ia_status\` consulta o estado; \`/desativar_ia\` revoga e limpa
   os metadados locais de requisição registrados pelo módulo de IA.
3. A verificação ocorre **também** dentro da transação de reserva da
   \`AgentBridge\`, impedindo que chamadas diretas ao módulo ignorem o roteador.
4. \`store:false\` é solicitado na Responses API, porém **não implica**
   ausência universal de retenção do provedor; aplicar a política de dados
   contratual e não enviar segredos, fichas médicas ou relatórios integrais.
5. Antes de opt-in não é enviada mensagem de texto à API, nem há gravação
   de requisição. Resposta do bot apenas instrui como autorizar.
6. Se revogado durante uma solicitação já em voo, a chamada HTTP existente
   poderá concluir; não é possível revogação retroativa de dados já enviados.

## Separação de autorizações
- \`/ativar_ia\`: textos recebidos podem ir ao provedor de IA; vale para Tutor
  e Coach. **Não habilita alertas espontâneos.**
- \`/ativar_alertas\`: notificações proativas; não autoriza compartilhamento
  de textos com a API de IA.
- OAuth Google Calendar: autorização própria, restrita ao calendário UFMS;
  não herdada do ChatGPT nem dos dois consentimentos Telegram.
- \`/pausar\`: pausa notificações, não exclui histórico do Telegram.

## Próximos gates
- Consultar política atual de dados do provedor antes do piloto.
- Exercitar corrida entre revogação e envio HTTP usando simulação de rede.
- Política de retenção dos dados operacionais SQLite e backup criptografado.
- Confirmar métodos de revogação OAuth Google e rotacionar tokens BotFather.
- Auditoria externa independente e aceite humano para produção.
