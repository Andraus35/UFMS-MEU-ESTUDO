# Monitor FAPEC — rotina proposta, somente leitura

## Objetivo

Executar uma checagem diária da página FAPEC do certame UFMS mediante
scripts/monitor_fapec.py --live. Esta é uma **candidata SIM-03/PR #21** em draft:
**schedule do GitHub Actions não roda automaticamente em branch de PR**.
Após eventual merge aprovado para main, o GitHub poderá executar a sonda
no horário agendado e guardar a saída em logs de workflow (conforme
políticas de retenção do GitHub).

A rotina usa GitHub Actions com permissão contents: read, checkout sem
credenciais persistidas, sem secrets de usuário, sem criação de issues,
PRs, mensagens, alterações de arquivos, commits ou atualizações de
retificação. Custo estimado zero para repositório público sob disponibilidade
do GitHub Actions; não constitui garantia de execução.

## Estados

- Código 0: no_change_observed_on_single_page. ÚNICA página parece
  estável; outras fontes continuam fora do escopo.
- Código 2: needs_manual_review. Job falha e emite warning; revisar
  publicação, identidade do concurso e documento original antes
  de qualquer registro normativo.
- Código 3: unverifiable. Job falha e emite warning; possível
  indisponibilidade de portal, bloqueio de rede ou conteúdo estranho.
  Não confundir com ausência de retificação.
- Outros erros: job falha sem afirmar conclusão.

Se configuradas pelo proprietário, notificações nativas de falha do
GitHub Actions podem ajudar a perceber o problema. Não há comunicação
Zapia, Telegram ou calendário integrada.

## Contrato de segurança

A página monitorada é
https://portal.concurso.fundacaofapec.org.br/edital/ver/22.
A sonda não verifica o boletim UFMS nem baixa automaticamente novas
retificações. Ao surgir uma candidata, realizar readback e preservar
bytes oficiais em fase separada, com SHA-256, conferência de fonte e
revisão humana conforme docs/RETIFICACOES_E_PROVENIENCIA.md.

Este PR atualiza apenas o estado de trabalho, o roadmap e o handoff, mas não altera settings, dados pessoais ou edital
e não deve ser mesclado sem a aprovação de segurança/documental aplicável.
Os testes de CI são offline e não atestam conectividade do runner.

## Execução local opcional

python scripts/monitor_fapec.py --live

Não considerar retorno zero aprovação de vigência oficial. Nenhum
dado pessoal deve ser publicado no repositório.

## Reconciliação com a main após PR #20

Origem: branch histórica `automation/fapec-readonly-schedule-20261105`, SHA `fd0a81823405e72a0b5fb91abf2a73cb5af685dc`. A recuperação é feita na única branch SIM-03/PR #21, a partir da `main` com os controles de privacidade e API já integrados. O workflow tem gatilho diário às 12:17 UTC (08:17 no horário de Campo Grande, MS, UTC−4) e acionamento manual. GitHub Actions pode atrasar ou deixar de executar jobs agendados; os logs não substituem leitura oficial. Em caso de atualização candidata/inconclusão, o job falha com warning e requer revisão manual; não há publicação normativa automática. A próxima frente é SIM-05 e não se habilitam dados pessoais.
