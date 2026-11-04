# P0-2 — Entrada obrigatória para Tutor/Coach (protótipo bloqueante)

**Estado: PR de implementação isolada; NÃO OPERACIONAL / NÃO HOMOLOGADO.** Não há serviço em Oracle ou Termux executando este código, e nenhum conector com credenciais de escrita foi migrado. Não afirmar que todos os agentes estão sujeitos a este gate.

## O que realmente implementa

`scripts/agent_entrypoint.py` é um componente Python somente leitura:

1. Exige o SHA do checkout explicitamente confiado pelo supervisor (`UFMS_TRUSTED_HEAD_SHA`), em vez de aceitar o SHA sugerido pelo modelo.
2. Compara o SHA ao HEAD Git real, rejeita checkout sujo, caminhos obrigatórios ausentes, arquivos vazios, symlinks, listas obrigatórias fora de ordem, roadmap incompleto e ausência de 11 IDs RM-00 a RM-10.
3. Calcula SHA-256 dos **dez documentos de bootstrap**, fornece AGENTS e ROADMAP para inclusão real no contexto do modelo e registra o escopo local.
4. Permite apenas `start` e `inspect` sem efeitos externos. Bloqueia `telegram.send`, `calendar.create`, escrita GitHub, merge, resultados e quaisquer ações não cadastradas.
5. Reprova antes de emitir um recibo quando o START não passa. O recibo é **diagnóstico**, não uma autorização ou token transferível.

**Limites:** o código **não** verifica compreensão cognitiva de um LLM, não observa chamadas externas feitas por outros processos e **não impõe** execução se o agente possuir credenciais diretas. Também não expõe HTTP nem realiza operações de Tutor/Coach, portanto não registra resultados pessoais.

## Contrato futuro para a operação real

- O **supervisor de execução**, não o LLM, escolhe e fixa o SHA confiável e controla os binários executados.
- O supervisor mantém em armazenamento restrito todas as credenciais de Telegram, Agenda, GitHub etc.; Tutor/Coach não recebem tokens, URLs administrativas ou APIs paralelas de escrita.
- Toda ação passa por `AgentBroker.request()` antes de qualquer efeito real; operações novas precisam de autorização, código, testes de negativa e auditoria próprios. Por enquanto todas as escritas são negadas.
- Após o bootstrap, o orquestrador precisa **realmente enviar os documentos obrigatórios ao modelo**, distinguindo leitura de bytes de leitura semântica. Para arquivos extensos do edital, cumprir o índice e a recuperação seletiva previstos em AGENTS.
- O serviço/handler deve registrar em log mínimo HEAD, role, ação, digest e resultado de bloqueio (sem dados pessoais), recusando tentativas de acesso por caminho alternativo.
- Um teste de ponta a ponta deve provar que chamar Telegram, Calendar ou GitHub diretamente **não é possível** usando credenciais dos agentes; sem esse teste a NC-PR9-02 segue aberta.

## Dependência

Este PR é baseado na main atual, que ainda não contém `ROADMAP.md`. Isso é intencional: **um START real nesta base deve falhar**. A execução operacional somente poderá ser experimentada quando o roadmap for integrado após reauditoria G0/GQ-H e autorização explícita. A CI usa fixtures sintéticas isoladas para validar casos positivos e negativos sem executar o tutor real.

Teste de desenvolvimento, sem efeitos:

```sh
python -m unittest tests.test_agent_entrypoint -v
python -m unittest discover -s tests -v
```

Teste local de bloqueio (no checkout que **não** tenha os dez documentos):

```sh
UFMS_TRUSTED_HEAD_SHA="$(git rev-parse HEAD)" python scripts/agent_entrypoint.py --role tutor --check
```

O resultado correto nessa base é `BLOCKED` por ROADMAP ausente. Não fornecer credenciais ao protótipo.

## Gates que ainda faltam

1. Revisão independente do próprio código deste PR.
2. Integração do ROADMAP validado; execução em snapshot de main limpo com SHA fixado pelo supervisor.
3. Implementação do adaptador de chamadas reais e testes E2E negativos para todas as rotas externas, na plataforma escolhida pelo proprietário.
4. Remoção de credenciais diretas dos agentes; comprovar isso por auditoria administrativa de permissões.
5. Comprovar comportamento do Tutor/Coach em modo real, incluindo versão, prioridades, bloqueios e eventuais recusas.

**Veredito atual:** controle preventivo local de escopo restrito, ainda não a garantia universal exigida pela auditoria.
