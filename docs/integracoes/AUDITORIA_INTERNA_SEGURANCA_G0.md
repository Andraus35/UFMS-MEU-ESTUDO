# Auditoria interna de segurança — ponte Oracle/Telegram/Calendar

**Data:** 04/11/2026  
**Modalidade:** análise técnica interna e contraprovas de unidade; **NÃO auditoria independente**.
**Objeto:** PR #3 em draft, branch \`feature/oracle-telegram-calendar-bridge\`.

## Escopo verificado

- Autorização por \`user_id\` e chat privado Telegram; comandos separados
  de textos livres; ausência de ferramentas de execução na chamada do modelo.
- Consentimento por finalidade: LLM, notificações proativas e OAuth Google.
- Estado da fila, retenção mínima de metadados LLM, limites de chamadas.
- Replays do Telegram e estado em \`sending/uncertain\` após falha.
- Criação de evento em calendário secundário Google com ID determinístico.
- Docker não-root, SQLite, timezone e CI.

## Achados e estado

| ID | Severidade | Achado | Tratamento |
|---|---|---|---|
| PRIV-01 | Alta | LLM habilitado na VM processava texto antes de opt-in Telegram | Corrigido no código: consentimento por comando + gate transacional |
| PRIV-02 | Média | Erro HTTP do Telegram poderia trazer token em URL | Sanitização e contraprova; logs externos ainda precisam de inspeção |
| DEL-01 | Alta | Confirmação ambígua permitia retry de lembretes | Corrigido anteriormente: \`sending/uncertain\`, reconciliação manual |
| CONS-01 | Média | Revogação não anulava fila proativa antiga | Corrigido anteriormente: cancelamento transacional dos pendentes |
| CAL-01 | Alta | ID de evento Calendar inválido e 409 tratado como sucesso sem leitura | Corrigido anteriormente: base32hex e verificação via \`events.get\` |
| RATE-01 | Média | Lembretes manuais ainda sem limite total por usuário e retenção configurável | **Pendente** |
| OPS-01 | Alta | Sem evidência de OAuth real, BotFather, VM, backups e secret management | **Bloqueado** |
| PED-01 | Alta | Sem integração verificável com estado real dos PRs #1/#2 | **Bloqueado** |

## Limites da evidência

- Testes usam dados fictícios/stubs; nenhum HTTP externo ou serviço Oracle foi exercitado.
- CI prova cenários implementados, não segurança integral nem disponibilidade 24/7.
- \`store:false\` na API de IA não substitui política de retenção do fornecedor.
- Conteúdo de lembretes/alertas fica em SQLite da Oracle até política de expurgo.
- Confirmação \`sent\` confirma resposta da API, **não leitura pelo usuário**.
- Não há auditoria independente, aceite humano, análise de custos reais
  ou prova de continuidade do agente após atualizações de dependência.

## Próximo gate recomendado

1. RATE-01: limitar quantidade de lembretes pendentes e definir expurgo/backup
   sem excluir dados antes de aceite de política de retenção.
2. OPS-01: provisionamento autorizado de dois bots, OAuth e OCI; testes reais.
3. PED-01: contrato assinado de integração com state + fontes do edital;
   nenhuma inferência de resultados inexistentes.
4. Auditoria independente em HEAD congelado antes de habilitar produção.

**Resultado:** PR #3 continua em draft; G0 de segurança **PENDENTE**, mesmo com CI verde.
