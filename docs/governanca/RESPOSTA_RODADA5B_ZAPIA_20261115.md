# Resposta da Zapia, rodada 5b (15/11/2026): V9, V4 simples e V6 adaptado

**Natureza:** **autorrelato** da Zapia (conta exclusiva, D-19) ao roteiro `docs/governanca/ROTEIRO_VALIDACAO_ZAPIA_RODADA4_20261109.md` (SHA-256 `0b8250b00b2ef07fda7ccd5546868a6636ab84fa29a1de1fc31a13362fa593b9`), com `AUTORIZO DESATIVAR JOBS, V2, V4, V6, V8a, V11` (primeiro prompt unificado) e `AUTORIZO V9, V4, V6` (segundo). Relatado pelo proprietário, sem dado pessoal, conta, e-mail nem credencial. Continua a `RESPOSTA_RODADA5_ZAPIA_20261115.md`. **Resultado parcial: não promove nenhum requisito.**

## Verificado pelo agente construtor (cálculo local)

| Item | Resultado |
|---|---|
| Hash de `scratch/v4.txt` | O SHA-256 de `arquivo-v4-ok` (13 bytes, sem quebra de linha) é `784de58a5cf0a745c8a87bd0cdde48a71d423cc65f10b5fc005337b674b63800`, igual ao informado. |
| Limite de frequência do V6 | 15 minutos projetam 96 execuções por dia (1440 / 15), acima das 32 do plano; o intervalo mínimo efetivo é 45 minutos (1440 / 32). |

## Autorrelato, não reverificado

| Etapa | Resultado |
|---|---|
| Radar | Os três jobs Radar (07:31, 13:31 e 19:31) ficaram **pausados, não apagados**; 0 jobs ativos; nenhum outro job listado. |
| Instrução persistente | Tudo `DESCONHECIDO`: a Zapia não lê o texto das próprias instruções persistentes, nem a finalidade da conta Google. |
| V8a | `rev-001` (pendente) criaria lembrete; `rev-002` (concluída) não. Nada criado. Correto. |
| V2 | Mensagem `UFMS-V2 teste de entrega 2026-11-15T12:21:03Z` enviada no app, **sem identificador nem comprovante de leitura**. O texto chegou ao proprietário (ele o colou), mas ele não informou o horário de recebimento nem se houve notificação push. |
| V4, primeira tentativa | Job executou uma vez às 08:23 em Cuiabá; o resultado **não confirmou** marcador, credencial, Python nem arquivo. Inconclusivo. |
| V4 simples | O job respondeu exatamente `MARCADOR_EM_INSTRUCOES=não; MARCADOR_NA_MEMORIA=não; ARQUIVO=arquivo-v4-ok`. Job e arquivo removidos. |
| V6 | **Recusado pelo agendador** duas vezes: primeiro por intervalo mínimo de 900 s (300 s pedidos) e depois por limite diário (96 execuções projetadas contra 32). Nenhum job nem log criado. |
| V9 | Notebook "Revisão UFGD — Direito Administrativo — Lei 8.112" **não encontrado** na conta Google acessada ("Nenhum notebook encontrado"). Nada criado nem alterado. |
| V11 | Aguardando o proprietário colar os dois textos; **não executado** nesta rodada. |

## Conclusões e limites

- **S5-R13:** no V4 simples, o job **leu o arquivo, mas não viu o marcador** nem nas instruções persistentes nem na memória. Se o marcador estava mesmo nas instruções (o proprietário não confirmou por escrito que o recolocou), instrução persistente e memória **não chegam a jobs agendados**. Logo, o START do repositório precisa constar **na tarefa de cada job**, não só nas instruções.
- **Cron do plano Free:** intervalo mínimo de 900 s e no máximo 32 execuções por dia. Não afeta o briefing diário (uma mensagem), mas o V6 do roteiro (3 execuções de 5 em 5 minutos) é inviável nesta conta; a pontualidade e a duplicidade do cron (Q21) seguem **sem resposta**.
- **V9:** o notebook não existe na conta Google acessada, coerente com uma conta nova (D-19), sem provar que é a conta só de estudos. Decisão do proprietário: criar o notebook **manualmente** na conta de estudos, com fontes públicas da Lei 8.112, e repetir o V9 só de leitura. Criação pelo Tutor (PR-012) é outro teste, ainda não especificado.
- **V2:** sem comprovante; mantém-se como não comprovado até o proprietário informar recebimento e notificação.

## Situação por teste

| Teste | Status |
|---|---|
| Desativar Radar, V8a | executados, autorrelato |
| V4 simples | executado, **observado** (marcador não chegou ao job) |
| V2 | executado, **sem comprovante** |
| V6 | **recusado pelo plano**, não executado |
| V9 | **bloqueado**: notebook inexistente |
| V3, V5, V8b, V10, V11 | `NAO_EXECUTADO` |
