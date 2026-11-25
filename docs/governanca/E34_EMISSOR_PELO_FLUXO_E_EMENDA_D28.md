# E34: emissor pelo fluxo (campainha) e proposta de emenda do D-28

**Natureza:** registro do lote 1 `ZAPIA-EMISSOR` (E33) e **proposta de texto**. Não é contrato: o texto do `PRODUCT.md` abaixo **só vale quando o proprietário o aprovar** e o merge for pedido por ele. Nada foi instalado no `entrada`, nenhum fluxo foi executado, nenhum hook foi criado.

**Decisão do proprietário (25/11/2026):** a emenda limita-se a **assunto e hora** (sem corpo de e-mail). Escrita da sessão no `entrada` liberada na fase de engenharia, para revisão dele em seguida; **este lote não precisou dela** (nada foi gravado no `entrada`).

## O que o lote entrega

1. **`scripts/sinal_emissor.py`** (stdlib, transporte injetado): `--contar RESUMO.json` lê o resumo que o `command_box_runner` imprime e escreve `promovidos=N`; conta só itens `PROMOVER` de um resumo `PROCESSADO`, com flag verdadeira e zero falhas de registro. Qualquer dúvida vale 0. `--emitir` cria **uma** issue em `entrada` com **título fixo `SINAL comando-promovido` e corpo vazio**; sem a flag do fluxo não há rede nem token.
2. **Modelo `config/modelos_fluxo/promover.yml`:** o job `promover` ganha a saída `promovidos` e grava o resumo da caixa; novo job **`campainha`** (`needs: promover`, `if: needs.promover.outputs.promovidos != '0'`, `timeout-minutes: 5`, **só `issues: write`**, sem `contents`, sem segredo do histórico, sem checkout da fila). Ele busca o validador por SHA fixado e confere o hash de `sinal_emissor.py` (novo marcador `__VALIDADOR_EMISSOR_SHA256__`).
3. **`scripts/promotion_workflow_check.py`:** permissões por job (promover só `contents`; campainha só `issues: write`), job extra recusado, condição e dependência da campainha, conferência do emissor, ausência de texto livre (`--titulo`, `--body`, `gh issue`, `curl`), contagem e saída do job, `timeout` por job.
4. **`scripts/termux/prepara_entrada.sh`:** substitui também o marcador do emissor (o fluxo gerado continua passando no teste estático antes de instalar).
5. **Testes:** `tests/test_sinal_emissor.py` e `tests/test_promotion_workflow.py` (classe `CampainhaTest`) com contraprovas.

## Desvio declarado do E33

O E33 previa o título `SINAL <nome do comando>`. Este lote usa o título **fixo** `SINAL comando-promovido`: levar o nome do comando exigiria passar texto da caixa (dado não confiável) ao título. O hook filtra por `SINAL`, então o filtro provado no E30 e no E31 continua valendo. Se ele quiser o nome da operação, é decisão nova (lista fechada de operações, sem texto livre).

## Proposta de texto da emenda (PRODUCT.md, próxima numeração depois da D-31)

> **D-32 (proposta):** emenda a D-28 e a D-31. O hook de Gmail da Zapia **pode ler, de e-mails de `notifications@github.com` cujo assunto contenha `[Andraus35/ufms-meu-estudo-entrada] SINAL`, somente remetente, assunto e hora de recebimento**, para acordar a conversa depois de uma promoção. **Nunca** lê corpo, anexo nem outro e-mail, e nada disso passa ao modelo como instrução. O e-mail é só campainha: a Zapia então lê o `entrada` pelo HTTP com o token já provado. O fluxo do `entrada` abre a issue-campainha **somente depois de promover** comando, com título fixo e corpo vazio. O D-28 segue valendo para o Outlook (só o código de acesso ao TEC).

## Limites (não afirmar além)

- O fluxo **não promove hoje** (flag falsa): o emissor só é provado de ponta a ponta no lote 3 (`ZAPIA-LIGAR`), na janela do piloto.
- O assunto `Re: ...` do aviso de fechamento **contém** o filtro: fechar ou comentar a issue só depois do relato e nunca com hook vivo (E32).
- O hook de Gmail não tem prefixo de assunto: o filtro é "contém".
- O teste estático prova o texto do modelo, não a execução no GitHub. O hash do emissor é conferido pelo próprio fluxo, que é o que o está sendo verificado (limite já declarado no C2).
- A reinstalação do fluxo no `entrada` (`ATUALIZAR`, SHA do merge) é **ato do proprietário**, depois do merge.

## Pendente dele

Aprovar o texto da D-32 (PR próprio no `PRODUCT.md`, arquivo de contrato), pedir o merge citando PR e head, e reinstalar o fluxo depois.
