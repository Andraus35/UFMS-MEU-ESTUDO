# Política de entrega e reconciliação — UFMS Oracle Bridge v0.2

Status: protótipo sujeito a auditoria independente. Não implantado em Oracle.

## Modos de envio

1. **Lembretes manuais**: criados pelo aluno no Telegram, no horário pedido,
   com possibilidade de pausa. Não entram na cota das mensagens espontâneas.
2. **Notificações proativas**: exigem opt-in explícito, validação de destinatário,
   categoria e referência, janela 07–22h, uma hora entre tentativas e máximo
   quatro tentativas por dia no conjunto Tutor+Coach.

## Incidente de ACK ambíguo

Telegram pode aceitar uma mensagem e a conexão falhar antes de confirmar a
operação ao cliente. Por isso, lembretes e alertas proativos usam os estados:

\`pending -> sending -> sent\` (ACK confirmado), ou
\`sending -> uncertain\` (erro sem confirmação).

Queda do processo enquanto \`sending\` permanece assim após reinício;
\`sending\` e \`uncertain\` **não são reenviados automaticamente**.

Isso dá prioridade a **evitar reenvios automáticos duplicados**, mas NÃO
garante recebimento: uma mensagem pode não ser enviada se houver queda entre
o claim e a chamada de rede. Também não garante exatamente uma entrega; o
protocolo não oferece confirmação de visualização pelo destinatário.

## Reconciliação pelo operador (na VM, após conferir o Telegram)

\`\`\`bash
docker compose exec ufms-bridge python -m bridge.reconcile list
docker compose exec ufms-bridge python -m bridge.reconcile mark-delivered reminder 12
docker compose exec ufms-bridge python -m bridge.reconcile cancel proactive 8
\`\`\`

A listagem apresenta apenas ID, papel e estado; não registra mensagens,
identificadores pessoais ou credenciais. O operador **deve conferir** a
existência da mensagem do bot antes de marcar como entregue. Para tentar
reenviar após confirmar que não chegou, usar uma **nova ação** explicitamente
aprovada, com nova chave idempotente e motivo; esse fluxo ainda não existe
na CLI.

## Gates restantes

- Limitar tamanho/cota de entrada dos lembretes manuais.
- Implementar backups, retenção configurável e política de exclusão.
- Validar OAuth/Telegram/Oracle ponta a ponta em conta e ambiente autorizados.
- Auditoria de autenticação de produtor de IA antes de aceitar notificações.
- CI no commit exato + testes de restauro e falhas em rede simulada.
