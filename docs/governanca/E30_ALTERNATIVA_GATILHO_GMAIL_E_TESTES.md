# E30: alternativa à "rotina cria rotina": gatilho por Gmail (campainha) e dois testes sem efeito (23/11/2026)

**Natureza:** registro de **decisão do proprietário** (respostas de 23/11/2026, depois da refutação do F3 no E29) e roteiro de **dois testes sem efeito externo**. **Não altera contrato.** A parte que mexe em contrato (D-28 do `PRODUCT.md`, leitura de e-mail pelo hook; fluxo instalado em `entrada`) é **proposta**, **fica para PR próprio** depois do merge do #189, com aprovação expressa do texto. **Nada aqui está provado.** Zapia, Gmail e hook não foram testados.

## Decisões dele (23/11/2026)

1. **Canal da campainha: Gmail.** Fonte de hook documentada pela própria Zapia (autorrelato, confiança C). Outlook (D-28: só código de acesso do TEC, sem ler e-mail; não citado como fonte de hook) e WhatsApp (não conectado) ficam fora.
2. **Escopo: só sinal, remetente e assunto fixos.** *(Ajuste de 23/11/2026: a Zapia relatou que o hook de Gmail só filtra por `senders`, `labels`, `subject_contains` e `text_contains`, sem prefixo de assunto. Ele autorizou **`senders` = notifications@github.com mais `subject_contains` = "[Andraus35/ufms-meu-estudo-entrada] SINAL"**, sem `labels` nem `text_contains`; o prefixo é conferido pela Zapia depois do disparo. Resto de risco: e-mail forjado ou outro com o trecho só acorda o hook.)* O e-mail é **campainha**: o hook acorda a Zapia; ela lê o repositório e confere hash, e **nunca obedece texto do e-mail**. Corpo ignorado, sem dado pessoal. Se o hook do Gmail não puder filtrar por remetente e prefixo de assunto, **não se cria** (senão leria a caixa inteira).
3. **Emissor: notificação nativa do GitHub** (uma issue ou comentário no `entrada` privado gera o e-mail). Muda o fluxo instalado (reinstalação por ele) e é **proposta para PR próprio**; no teste, a issue é aberta à mão.
4. **Primeiro teste:** inventário da rotina + hook que só relata (abaixo). O teste recorrente de 3 disparos fica para depois.

## Teste 1: inventário de ferramentas da rotina (resolve a causa do F3)

Prompt para a Zapia (cole na conversa; substitua `HORARIO_UTC` por um horário daqui a **15 minutos ou mais**):

```text
TESTE DE INVENTÁRIO, uma vez só, SEM EFEITO. Crie UMA rotina nativa de execução única para HORARIO_UTC (UTC), com esta instrução, sem traduzir nem resumir (depois de salvar, leia de volta e me mostre):
"At the scheduled one-time fire only, read the UTC clock. Do NOT call any tool and do NOT create, change or delete anything. From what you can see in this execution, report in this chat: (1) the UTC time; (2) the exact names of every tool or function available to you in this execution, names only; (3) for each of these, answer exists or does not exist: create routine, list routines, update routine, delete routine, HTTP or curl, hook tool, send notification, file read, web search; (4) say literally whether you are able to see a tool that creates routines. If you cannot tell, write: cannot tell. Do not retry. One execution only."
Não crie nenhuma outra rotina, hook ou lembrete agora.
```

**Passa (informativo):** a rotina acorda e lista os nomes. Se a ferramenta de criar rotina **não** está na lista, a causa do F3 é **falta da ferramenta no contexto de rotina** (autorrelato B com captura). Se está na lista, a causa foi decisão ou bloqueio dela, e vale **um** teste a mais, só com tentativa e erro literal. **Refuta/inconclusivo:** não acorda, ou "cannot tell".

## Teste 2: hook de Gmail que só relata

Prompt para a Zapia (versão de 23/11/2026, com o filtro que o hook de fato oferece):

```text
TESTE DE HOOK DE E-MAIL, SEM EFEITO. Crie UM hook de Gmail com EXATAMENTE estes filtros e nenhum outro: senders = notifications@github.com e subject_contains = "[Andraus35/ufms-meu-estudo-entrada] SINAL". NÃO use labels nem text_contains. Se a ferramenta não conseguir salvar exatamente esses dois filtros, NÃO crie o hook e me diga o motivo literal. Me mostre o filtro salvo, lido de volta. Quando disparar: confira se o assunto COMEÇA com "[Andraus35/ufms-meu-estudo-entrada] SINAL"; se não começar, relate apenas "assunto fora do padrão" e a hora UTC e pare. Se começar, relate neste chat apenas (1) a hora UTC do disparo e (2) a linha de assunto; NÃO abra nem cite o corpo, NÃO chame o GitHub, NÃO grave nada, NÃO crie rotina nem lembrete. Dispare no máximo UMA vez e depois desative ou apague o hook (se não conseguir, diga literalmente).
```

Depois que ela confirmar o filtro, no Termux (a sessão **não** tem acesso ao `entrada`):

```text
gh issue create -R Andraus35/ufms-meu-estudo-entrada -t "SINAL teste F4" -b "teste sem dado pessoal"
gh issue view -R Andraus35/ufms-meu-estudo-entrada <numero> --json createdAt
gh issue close -R Andraus35/ufms-meu-estudo-entrada <numero>
```

**Passa (autorrelato B, captura sua):** a Zapia acorda **uma vez**, relata hora e assunto (o assunto começa com o prefixo) e **nada além**; o atraso entre `createdAt` e o relato fica anotado (tolerância proposta: **15 min**, ajustável). **Refuta:** o hook não filtra por remetente e assunto, nunca acorda, acorda mais de uma vez, ou cita o corpo.

**Atenção:** o GitHub pode não enviar e-mail de ação do próprio autor; se nada chegar, confira em Configurações → Notificações o item "incluir minhas próprias atualizações" (verifique no seu aparelho; **não confirmei** o padrão).

## Riscos declarados

- **Leitura de e-mail:** mesmo com filtro, o hook roda sobre a caixa dele. Só vale com o filtro **lido de volta** e a emenda do D-28 aprovada. Antes dela, o teste 2 é **autorizado por ele só como teste único e sem efeito**, com desativação ao fim.
- **Atraso, perda e duplicação** do e-mail são possíveis; o campainha **não** garante pontualidade em relação ao `agendado_utc`.
- **Origem não provada:** o e-mail só prova que algo mudou; quem decide é o hash conferido no repositório.
- **Autorrelato:** a Zapia diz o que vê; a prova depende da captura dele e do carimbo.

## Próximo (outro lote, depois do merge do #189)

Emenda do D-28 (proposta de texto, aprovação expressa) e, se o teste 2 passar, o emissor por issue no fluxo (reinstalação dele). **Até lá nada disso está em vigor.**
