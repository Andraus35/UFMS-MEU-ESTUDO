# E54 — Emenda da S6-R6: Issues em escrita no token da Zapia (28/11/2026)

**Natureza:** registro da decisão do proprietário de 28/11/2026 ("Aprovar o texto"). Altera `docs/especificacoes/S6_EXECUCAO_CANAL.md` (bloco de emenda no topo, como a E26), `scripts/termux/verifica_token.sh` (perfil novo) e o roteiro da P9. **Não** altera `agents/`, `AGENTS.md`, `PRODUCT.md`, `.claude/` nem o esquema de comandos. O merge continua só por pedido dele, citando PR e head.

## Texto aprovado
O token da Zapia no `entrada` passa a ter também **Issues: Read and write**, **somente no repositório `entrada`** e **somente para abrir a issue `RESP eng-NNNN`** do canal de engenharia (E49, passo 5). Continuam **proibidos**: Workflows, Secrets, Actions, Administration, Pull requests, qualquer outro repositório e qualquer acesso a `dados`. Validade 30 dias. A Zapia **não** comenta nem fecha issues, e a rotina de despertar só usa o **título** exato `RESP eng-NNNN`, sem corpo.

## Por que
A prática de 28/11/2026 já usava o estado: depois de o proprietário acrescentar Issues ao token (validade 31/07/2027, relato), o passo 5 funcionou (`eng-0011` e seguintes; a rotina de despertar acordou nas `eng-0012` a `eng-0015`). Antes, o `POST` da issue recebia HTTP 403.

## O que mudou
- `verifica_token.sh`: perfil **`privado_issues`** (REPO padrão `entrada`; criar issue PODE; comentar PODE, porque a API não separa; gravar arquivo PODE; pull request NÃO; escrita em qualquer outro repositório NÃO; só o `entrada` alcançável entre os privados; validade obrigatória; classic recusado). O perfil `privado` (do `dados`) segue recusando Issues. 6 testes novos em `tests/test_termux_verifica_token_privado.py`; mutação que troca o esperado de issue é morta.
- Roteiro da P9: tabela do `zapia token` com Issues.

## Riscos e limites
- Issues em escrita permite à Zapia (um modelo) abrir, editar e fechar issues no `entrada`; como a rotina acorda por qualquer issue aberta, a Zapia passa a poder **acordar sessões**. Limites do desenho: título exato `RESP eng-NNNN`, o hook proíbe comentar, o prompt da rotina encerra se o título não casar. **O filtro de autor da rotina não foi verificado.**
- A proibição de comentar é **do prompt**, não da permissão (a sonda `comentar` espera PODE neste perfil).
- A emenda **não prova** nada sobre o token real: ele só é conferido quando o proprietário roda `PERFIL=privado_issues bash scripts/termux/verifica_token.sh` no Termux e mostra o resultado sem o valor do token.

## Verificação real do token (28/11/2026, 13:08, captura do proprietário no Termux, confiança B)
Rodada `ISSUE=12 PERFIL=privado_issues bash scripts/termux/verifica_token.sh` sobre a `main` em `1f53718` (token **não** mostrado): token **fine-grained** da conta `Andraus35`, **validade 2027-07-31 04:00 UTC**; entre os repositórios **privados** alcança **só** `ufms-meu-estudo-entrada`; **criar issue, comentar (#12) e gravar arquivo: PODE** (a validação falhou depois da autorização; nada foi criado); **abrir pull request, gravar no repositório público, em `Inteligencia-SOT` e em `Sistema-Operacional-de-Trading--SOT`: NÃO (403)**; **`RESULTADO: CONFERE com o perfil privado_issues`**, saída 0. Uma primeira rodada (sem `ISSUE=12`) divergiu só no comentário, porque a issue #75 padrão não existe no `entrada` (404 enganoso); o perfil foi corrigido no lote seguinte (`E56_FILTRO_CPF_EM_HASHES.md`). **Limites:** é uma observação de um instante, por captura; não prova o que a Zapia faz com o token, só o que ele permite.

