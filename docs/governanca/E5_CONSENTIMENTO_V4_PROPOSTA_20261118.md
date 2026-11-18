# Consentimento v4 — PROPOSTA (18/11/2026)

**Situação: PROPOSTO. Só vale quando o proprietário o aprovar por PR e o registrar com o próprio ato.** Este arquivo **não registra** consentimento algum, **não habilita** a escrita de resultados (`personal_results_writes_enabled` segue `false`) e **não dá** a nenhuma sessão acesso a dado pessoal.

## Por que um v4
O v3 (ADR-013) cobre plano e resultados e cita a **Zapia** e o **Google**, mas **não o app Claude**. Pelo D-25 e pela S6-R9, o Tutor e o Coach rodam em **sessões do app Claude na nuvem** e, para recomendar com base em resultado, precisam **ler projeções** do estado pessoal (nível por tópico, pendências, revisões): isso significa que **o app Claude processa dado pessoal**. Antes de qualquer sessão ler projeção, é preciso um consentimento que o cite. O desenho agora tem **dois** repositórios privados: `ufms-meu-estudo-entrada` (fila; a Zapia grava só ali) e `ufms-meu-estudo-dados` (histórico; só o fluxo grava), e a fila também deixa cópia no histórico do Git.

## Texto proposto

> Autorizo o registro, nos repositórios privados `ufms-meu-estudo-entrada` (fila de entrega) e `ufms-meu-estudo-dados` (histórico), do meu plano de estudos (datas, disciplinas, minutos por dia, dia de descanso, revisões e os horários de estudo que eu informar) e dos resultados dos meus cadernos e simulados de estudo (data, caderno relacionado, convenção de contagem e totais por tópico quando eu informar), exclusivamente para orientar meus estudos para os cargos UFMS 523 e 324. Autorizo também que sessões do app Claude (Tutor e Coach), em ambiente de nuvem, leiam, **somente leitura**, **projeções** desse histórico (nível por tópico, pendências e revisões), **nunca o histórico bruto**, para decidir recomendações de estudo. Não autorizo registrar CPF, documentos, credenciais, exports brutos, capturas de tela nem texto de questões, e as projeções não podem conter texto de questão nem identificador de conta. Entendo e aceito que esses dados passam pela plataforma Zapia (servidores nos Estados Unidos, retenção conforme a política dela), pelas sessões do app Claude (retenção conforme a política do serviço, que não foi verificada) e, no mínimo necessário, pelo Google (Gemini Notebook, Calendar e Tasks), e que a fila `entrada` também deixa cópia no histórico do Git. Os dados serão mantidos nos repositórios privados até 16/02/2027 (17/01/2027 mais 30 dias). Posso revogar este consentimento a qualquer momento, o que suspende novas gravações e leitura por sessões e leva ao apagamento dos dois repositórios privados; **apagar os repositórios não elimina as cópias na Zapia, no Google nem no app Claude, que devo pedir separadamente a cada serviço.** Versão: v4.

## O que este documento NÃO faz
- **Não registra** o consentimento: o registro é ato do proprietário (arquivo próprio, como `consent-v3.json`), por ferramenta que **ainda não existe** (`consentir-v4`, tarefa futura).
- **Não habilita** a flag nem dá acesso de leitura a sessão alguma (C6 e S6-R9: teste de que a leitura exige v4 válido).
- **Não cobre** leitura de e-mail (D-28: a conexão do Outlook não autoriza leitura) nem o relatório do TEC pela Zapia (E3, bloqueada).
- **Não verifica** a política de retenção do app Claude nem a da Zapia: o texto declara isso ao proprietário.

## Ordem prevista
C5 (primeira metade, conferida em 18/11/2026) → **aprovação e registro do v4 pelo proprietário** → C6 (habilitação da flag, PR próprio com aprovação expressa) → segunda metade da prova (promoção até `dados`).
