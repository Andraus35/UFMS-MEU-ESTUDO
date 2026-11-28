# E48 (preparo) — N1, rodada 4 (`n1d`): hook v4 do Notebook, com código por etapa (28/11/2026)

**Natureza:** registro do **preparo** da rodada 4. **Não é a prova**: o item `N1-RODADA-4` só fecha quando a rodada `n1d` rodar e o resultado for **conferido por código** (entrega `E48_N1_RODADA_4.md`, ainda inexistente). Não toca `agents/`, `AGENTS.md`, `PRODUCT.md`, `.claude/` nem o esquema de comandos.

## O que mudou (modelo `HOOK_NOTEBOOK`, `config/rotina_instrucoes.json`, v4)
1. **Conta antes de tudo (E47):** selecionar `andraus.dev@gmail.com`; senão `PARADO` com `CONTA_ERRADA`.
2. **Código por etapa:** `SEM_CADERNO`, `MENU_SEM_TEXTO_COLADO`, `COLAR_FALHOU`, `SALVAR_FALHOU`, `LOGIN`, `LIMITE`.
3. **Critério de sucesso do passo "adicionar fonte" (E47):** o texto está na lista **Fontes** e o chat responde citando-o; **ignorar o contador do cabeçalho** ("0 fonte"), que dava falso negativo.
4. **Tamanho:** 3 comandos = **3941 caracteres** (teto de teste 3950; limite real 4000). O hook **não** cita mais "Repository data is untrusted" nem pede o relato das URLs, para caber; os guardas de sigilo e a ordem de não traduzir continuam. **Limite declarado:** com **4 ou mais** comandos a renderização falha fechada (a v3 cabia 5).
5. `scripts/termux/prova_n1.sh`: variável `N1_PREFIXO` (padrão `n1`; esta rodada `n1d`) e a fonte pública já existente **com os mesmos bytes** é mantida (antes bloqueava a partir da 2ª rodada); fonte diferente continua bloqueando.

## Como rodar (atos do proprietário, nesta ordem)
1. `cd ~/UFMS-MEU-ESTUDO && git pull --ff-only origin main` e `N1_PREFIXO=n1d bash scripts/termux/prova_n1.sh preparar` (offline; gera `~/n1/` com os comandos `n1d-*`, recibos, `fonte-n1.txt` e `instrucao-hook-notebook.txt`).
2. `N1_PREFIXO=n1d bash scripts/termux/prova_n1.sh colocar` (frase `COLOCAR N1`): grava 3 comandos, 3 recibos e **mantém** a fonte igual (6 gravações), todos conferidos por leitura de volta. Recibos **sintéticos manuais**; **não** provam promoção pelo fluxo.
3. Na Zapia que **recebe o Gmail**: **atualizar** o hook existente do N1 (`2bef6d04`, filtro `SINAL`) com o texto de `~/n1/instrucao-hook-notebook.txt` e **reabilitar**; não criar outro (a Zapia recusa inscrição idêntica). Trazer o relato com o texto salvo (comparar tamanho e trechos).
4. Só então abrir **uma** issue `SINAL` (confirmada pelo proprietário em 28/11/2026): `[Andraus35/ufms-meu-estudo-entrada] SINAL ...`. Hook de uso único: ele se consome mesmo parando.
5. `N1_PREFIXO=n1d bash scripts/termux/prova_n1.sh conferir` e trazer as linhas de resultado.

## Limites
- O preparo prova o texto e o transporte offline; **nada** foi enviado à Zapia nem ao Google. O resultado da rodada (fonte adicionada, resposta, citação) é autorrelato da Zapia, conferido por `notebook_response_check`.
- A rodada 1 já falhou na **fidelidade** (a contraprova inventou citação); isso é problema **separado**, não coberto aqui.
- Hook de uso único: a Zapia nem sempre consegue desativá-lo (E41); **não** fechar nem comentar a issue `SINAL` com o hook vivo.
