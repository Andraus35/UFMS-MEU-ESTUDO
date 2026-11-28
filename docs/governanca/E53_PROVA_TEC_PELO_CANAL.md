# E53 — Prova do TEC pelo canal de engenharia (28/11/2026)

**Natureza:** entrega do item `ENG-V10-HOOK` da fila. **Registro de prova, não contrato.** O detalhe está no E49 (itens 19 a 21 e 24) e em `CAPACIDADES_ZAPIA_VERIFICADAS.md`; este arquivo só aponta e fixa os limites.

- **Hook aplicado na Zapia:** v10 (leitura crua do pedido) → v11 (sem a parada por login do TEC, decisão do proprietário) → v12 (`itens`) → v13 (pontuação) → **v14** (esqueleto JSON, parâmetros por operação), **3927 caracteres**, igual ao do repositório (autorrelato dela, comparado pelo tamanho e por trechos).
- **TEC pelo canal (confiança B, uma execução cada, conteúdo autorrelato):** `tec_listar_cadernos` (**`eng-0009`**, 25 itens) e `tec_estrutura_caderno` (**`eng-0010`**, estrutura de um caderno de 28 questões) foram **ACEITAS** pelo código; a `eng-0008`, ainda com a parada por login (v10), parou em `LOGIN`.
- **Passo 5:** a issue `RESP eng-0011` foi aberta depois de o proprietário acrescentar `Issues: Read and write` ao token (emenda E54 da S6-R6).
- **Não provado:** que a lista confira com a tela do TEC, a estabilidade em muitas ativações (houve **2 ativações perdidas em 6 envios**, resolvidas reenviando o sinal) e a sessão do TEC se manter logada.
- **Privacidade:** as respostas ficam só no `entrada` privado; nomes de cadernos não entram no repositório público.
