# SIM-08 — decisão sobre a ponte Oracle/Telegram/Google Calendar (#3)

**Origem:** branch `feature/oracle-telegram-calendar-bridge`, SHA `757e61c7e880fb8b38c4b215eb063c6c9f1e7cbe`. PR #3 foi encerrado sem merge. Esta nota registra a avaliação, não instala serviço.

## O que existe na candidata

- MVP isolado em Python/SQLite, dois bots Telegram (Tutor e Coach), comandos de lembrete e check-in, outbox proativa e integração opcional ao Google Calendar secundário.
- Gateway de comandos e adaptador LLM com consentimento por finalidade; IA e alertas desativados por padrão.
- Docker, backup age e testes unitários offline.
- A própria README diz: não implantado na Oracle, não conectado ao Tutor/Coach LLM e não autorizado no Google Calendar remoto. Sem credenciais, bots não iniciam.
- A auditoria interna de segurança reconhece que não é auditoria independente; OAuth, BotFather, VM, backup e secret management reais não foram testados.

## Pendências explícitas da candidata

- RATE-01: limites globais e retenção configurável ainda pendentes.
- OPS-01: nenhum OAuth real, bot provisionado, VM, backup ou gerenciamento de segredos comprovado.
- PED-01: integração com o estado real do Tutor/Coach e fontes do edital bloqueada.
- O envio externo não oferece garantia exactly-once em todos os cenários; reconciliação de falha de ACK continua necessária.
- Testes são offline/stub; não provam rede, Oracle, OAuth, disponibilidade 24/7 ou políticas atuais do provedor de IA.

## Decisão para a main atual

**Não importar o código ou workflows da ponte neste ciclo.** A branch é uma aplicação separada de 21 commits, com nova superfície de operação, credenciais e dados. Não há prova de implantação, não existe E2E real, e a candidata assume Telegram como interface sem comprovar que essa é a interface final desejada. A `main` permanece o harness de estudo, com broker read-only, writer API inativo e dados pessoais bloqueados.

A decisão não descarta o trabalho: manter a branch original intacta para recuperação futura. Se a ponte for retomada, dividir em gates independentes: (1) decisão de interface e necessidade 24/7; (2) piloto sem LLM/Calendar, só comandos locais; (3) consentimento e privacidade; (4) OAuth Calendar em calendário secundário; (5) LLM opt-in com revisão de política/custo; (6) operação real, backup, rate limits, retenção, revogação e auditoria independente. Não ativar tudo em um único merge.

## Estado de segurança

- Nenhum token Telegram, OAuth, chave ou segredo foi copiado.
- Nenhum bot ou calendário foi criado; nenhuma chamada externa foi realizada.
- Não adicionar serviço 24/7 sem necessidade explícita e ensaio E2E.
- Não confundir testes offline aprovados com homologação de produção.
