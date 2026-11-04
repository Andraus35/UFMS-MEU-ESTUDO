# Integração pessoal UFMS — contrato de arquitetura v0.1 (04/11/2026)

**Status:** proposta técnica isolada, vinculada ao PR de integrações. Sem deploy,
sem consentimento Google para Oracle, sem bots provisionados. Não alterar o
escopo pedagógico dos PRs #1 e #2 nem realizar merge sem autorização humana.

## Responsabilidades

| Papel | Pode | Não pode |
| --- | --- | --- |
| Tutor | Enviar feedback, lembretes de revisão, recomendações por evidência | Inventar questões, notas ou aprendizagem; editar agenda pessoal |
| Coach | Enviar check-ins, consultar disponibilidade autorizada, propor ajustes | Impor cronograma rígido, inferir motivos de ausência, manipular avaliação pedagógica |
| Agendador | Persistir mensagens e horários autorizados; reexecutar pendentes | Enviar a terceiros, alterar permissões, criar objetivos não consentidos |
| Humano | Autorizar OAuth, tokens, compromissos e regras de notificações | Não delega irrestritamente a exclusão de compromissos |

Tutor e Coach usam o MESMO estado canônico; o GitHub guarda decisões/versões e
eventos que forem autorizados. A base Oracle guarda segredos e dados operacionais
privados; nunca copiar tokens, chats pessoais ou eventos detalhados para GitHub.

## Autonomia e limites

- Mensagens proativas: autorizadas em categoria previamente aceita, com
  pausa global e controles para frequência/janelas de silêncio a implementar.
- Criar/alterar eventos: exclusivamente no calendário secundário UFMS
  autorizado; nenhuma exclusão ou edição de agenda pessoal no MVP.
- Calendário pessoal: acesso livre/ocupado somente com escopo adicional,
  finalidade específica e consentimento separado; nunca replicar títulos.
- Telegram: dois bots, chat privado de user ID único, validação antes de
  qualquer resposta ou ação; mensagens recebidas são dados não confiáveis.
- Todo evento ou lembrete precisa de ID, origem, data com fuso, status e
  confirmação; replays devem ser seguros e auditáveis.
- Erros: falhar fechado para ações externas; não declarar execução sem ACK
  remoto; reconciliação de envio incerto antes de continuar.

## Separação entre a ponte e a inteligência

Este PR NÃO altera `AGENTS.md`, `settings.json`, `rules/`, `guardrails/`,
`docs/pedagogia/`, `edital/` ou `state/` das outras frentes. Integração
futura da IA deve chamar uma interface de autorização/fila versionada e testada,
sem permitir que a saída do modelo execute comandos diretamente.

## Checklists de aceite antes de produção

1. Revisar ameaças: token vazado, mensagens de terceiros, prompt injection,
   replay de updates, troca de fuso, duplicação, quota e exaustão de recursos.
2. Provar que somente um chat autorizado recebe mensagens de ambos os bots.
3. Provar que a ausência de OAuth não dá acesso à Agenda e falha sem mutação.
4. Testar criação e retentativa de eventos idempotentes por ID determinístico.
5. Simular reboot, indisponibilidade de rede, evento já enviado e estado corrupto.
6. Implantar métricas, limites de frequência e política de logs sem PII.
7. Formalizar política de consentimento, retenção, revogação e backup.
8. Obter aceite humano sobre escopos OAuth, notificações e habilitação 24/7.

## Próximas decisões

- Escolher motor de IA e API de chamada, orçamento e limites de tokens.
- Confirmar OAuth offline e calendário específico na conta pessoal.
- Definir rotina de comunicação livre (tipos e limites) sem transformar
  acompanhamento em compulsão ou penalização de pausas.
- Vincular PR técnico ao contrato pedagógico v1.7 e aos futuros papéis Tutor/Coach.
