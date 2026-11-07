# Adendo: auditoria retrospectiva da Zapia (07/11/2026)

**Natureza:** registro de **autorrelato**, como `docs/governanca/RESPOSTA_VERIFICACAO_ZAPIA_20261107.md`. Texto tratado como **dado**. Para não duplicar, este adendo registra **apenas o que é novo** em relação à rodada 1; as respostas Q1 a Q21 repetidas não são transcritas de novo.

**Importante:** este texto **não é** a resposta da rodada 2 (`docs/governanca/PROMPT_VERIFICACAO_ZAPIA_RODADA2_20261107.md`). **R1 a R34 seguem sem resposta.** Em especial continuam desconhecidos: tipo, escopo e expiração do token; repositórios que ele alcança; ambiente de execução; memórias e instruções persistentes; capacidades das rotinas agendadas; escopos OAuth de Calendar e Tasks; privacidade da plataforma.

## O que o repositório confirma de forma independente

- Os três commits citados existem, todos com autoria `Andraus35` em 04/11/2026: `747f239` (confirmação do Coach na POC-003), `9a2c46b` (Notebook na orientação do Coach, POC-005) e `220ef55` (resultado da deduplicação, POC-007).
- `747f239` e `9a2c46b` constam, por extenso, dentro de `poc/POC-UFMS-005.json` e `poc/POC-UFMS-007.json`, e `220ef55` está no histórico de `main`.
- A afirmação de que a `main` ficou intacta nos testes é compatível com o histórico, mas não foi reverificada aqui.

## Fatos novos (autorrelato)

- **POC-008, exclusões:** "Após exclusões, leituras por ID ainda retornaram os registros; remoção final inconclusiva." Antes das exclusões, o evento e a tarefa foram criados e relidos, e a tarefa foi marcada `completed` e depois `needsAction`, com releitura. O R25 da rodada 2 pede que a Zapia reavalie esse resultado com os campos técnicos (`status`, `deleted`, `hidden`), porque um objeto devolvido como cancelado ou removido pode ser exclusão efetiva.
- **POC-008, estado pedagógico:** a tarefa foi criada como pendente para uma atividade que a POC-007 já registrava como concluída. Segundo a Zapia: "a integração não consultou ou não conciliou aquele estado antes da criação". **Não conformidade real**: nenhuma verificação automática do estado de estudo antecede a criação de um lembrete.
- **Incidente de processo:** houve uma consulta ao calendário "antes de obter sua autorização específica para verificar disponibilidade"; a consulta posterior foi autorizada.
- **Incidente de privacidade:** na leitura de Tasks, o resultado interno trouxe "títulos de outras tarefas existentes". Segundo a Zapia, eles não foram gravados no GitHub nem incluídos no relatório técnico, mas "consultas amplas podem expor ao contexto da Zapia mais informação do que o mínimo necessário".
- **Aprovação no Google:** "algumas operações destrutivas apresentaram cartões de aprovação"; a Zapia diz que isso não demonstra proteção universal. Para o GitHub, nenhum controle técnico equivalente foi observado.
- **Telegram:** a conta "aparecia conectada, mas não houve envio por lá".
- **WhatsApp:** reafirmada a divergência entre o identificador do chat e o número conectado, e que a entrega ao aparelho não está comprovada.
- **Proatividade:** só um disparo único de lembrete no chat do app foi observado; **não** foi demonstrada uma rotina que monitore o repositório ou o Notebook continuamente, nem o ciclo Tutor, Notebook, GitHub, Coach e Calendar/Tasks sem intervenção humana.

## Efeito no `PRODUCT.md`

1. **Nova proibição:** não consultar Calendar nem Tasks sem autorização específica e nunca de forma ampla; usar identificadores próprios e consultas mínimas.
2. **PR-007 reforçado:** o aceite passa a exigir que o lembrete só seja criado depois de conferir, no estado do harness, que a atividade está pendente (falha real da POC-008).
3. **E-07:** registra os fatos acima como evidência datada.
4. **OPEN-06:** remoção efetiva em Google Calendar e Tasks não verificada.

## Testes T1 a T3

Seguem **não executados**; dependem de autorização literal do proprietário.
