# RATE-01 — Cotas e retenção de lembretes manuais v0.4

Data: 04/11/2026. **Status: implementado e testável com dados fictícios;
NÃO implantado, NÃO auditado independentemente e NÃO homologado.**

## Regras do gateway
- Quota por pessoa autorizada, **compartilhada** entre Tutor/Coach: máximo
  **20 lembretes novos em 24h móveis**, inclusive os cancelados/concluídos.
- Máximo **30 lembretes ativos** simultâneos, contadas as situações
  \`pending\`, \`sending\` e \`uncertain\`. Reconciliar estados incertos libera
  capacidade; nenhuma mensagem de destino diferente pode reutilizar chave.
- Operações são transacionais \`BEGIN IMMEDIATE\` no SQLite para impedir
  que duas conversas contornem cotas. Replay idêntico por request_key retorna
  o ID existente antes da verificação da cota; replay divergente é recusado.
- Mensagem entre 1 e 500 caracteres, data com fuso e escrita em UTC.
- O Telegram autoriza chat privado antes de passar ao armazenamento.
  A agenda externa e as notificações proativas usam políticas próprias.

## Retenção dos lembretes
- Período-padrão: **30 dias depois da finalização**, não da criação.
- Elegíveis: somente estados \`sent\` ou \`cancelled\`, cuja data de
  \`finalized_utc\` comprovadamente ultrapassou o prazo; registros legados
  \`sent\` usam \`sent_utc\` quando disponível.
- Estados \`pending\`, \`sending\`, \`uncertain\` nunca são expurgados
  automaticamente, ainda que sejam antigos.
- O padrão é **dry-run**. A ação \`--apply\` é explícita e deve ser executada
  pelo operador após aceite da política, backup criptografado e verificação.
- A manutenção exibe somente contagens, jamais conteúdo de mensagens,
  IDs de Telegram ou dados pessoais.
- Limpeza de linhas SQLite não implica apagamento criptográfico ou exclusão
  de backups, snapshots e registros do próprio Telegram. Política de backup,
  rotação de chaves e expurgo de cópias continuam como gate externo.

## Operação futura (não executada nesta sessão)
\`\`\`bash
docker compose exec ufms-bridge python -m bridge.maintenance
docker compose exec ufms-bridge python -m bridge.maintenance --days 30 --apply
\`\`\`
O \`--apply\` deve ser usado somente após autorização operacional e backup
consistente. SQLite mantém \`bot_offsets\` após limpeza de lembretes para
impedir reaplicação de atualizações antigas; restaurar um backup antigo sem
reconciliar offsets pode produzir reprocessamento.

## Contraprovas exigidas
1. Limites compartilhados entre bots e chats autorizados.
2. Uma chave duplicada não conta como nova criação; divergência é rejeitada.
3. Filas com \`uncertain\` não escapam ao limite de pendências.
4. Atividades finalizadas antigas são expurgadas somente com \`--apply\`.
5. Finalização recente de evento criado há meses é preservada.
6. Evento legado sem data confiável de finalização não é apagado.
7. Migração SQLite não destrói dados.
8. Respostas da ferramenta não revelam conteúdo pessoal.
9. CI verde no SHA congelado e smoke de contêiner Docker.

**Gate RATE-01:** controle de cotas e retenção implementado no protótipo.
Pendente verificação de uso real e auditoria independente antes de produção.
