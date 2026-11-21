# Roteiro PJ — abrir e fechar a janela do piloto (ato do proprietário)

**Natureza:** passo a passo para **você** decidir e executar; **a sessão não abre a janela, não liga flag e não executa os roteiros do Termux**. Base: `docs/especificacoes/S11_CICLO_PILOTO.md` (R2, R3, R5, R7, R10, R12), `scripts/piloto_preflight.py`, `scripts/piloto_relatorio.py`, `docs/governanca/E6_C6_LIGA_FLAG_DO_FLUXO_20261118.md` e `E7_FECHAMENTO_JANELA_C6_20261118.md`. **Meta que você fixou:** até **04/12/2026**, antes do aviso de renovação dos tokens.

**O que o piloto é:** **um** estudante, **um** caderno real, **um** evento de resultado, para provar que o encanamento F1 a F8 funciona **uma vez**, com leitura de volta e fechamento. **Não prova** utilidade pedagógica nem homologa a RM-08 ou a RM-10; se der verde, registra-se só **"ciclo funciona uma vez"**.

## Antes de pedir a janela (pré-condições)

1. **P9 feita** (roteiro `ROTEIRO_P9_RENOVAR_TOKENS_20261121.md`): os dois tokens com **mais de 8 dias** de validade.
2. **Fluxo reinstalado no SHA atual da `main`** (P7 continua valendo): se qualquer merge mudou a `main` desde o último `ATUALIZAR`, o pré-voo fica **vermelho** até você reinstalar.
3. **Um caderno real escolhido e resolvido por você** no TEC ou no Qconcursos; o resultado vai pela **entrada manual** (total, acertos, erros, não respondidas, data e resultado por tópico), que é o caminho de referência. Leitura automática do TEC **não** é pré-condição.
4. A flag `personal_results_writes_enabled` **fica `false`** durante todo o piloto (é a do repositório **público**; nunca liga).

## Sequência da janela (S11-R3)

| # | Passo | Quem | Observação |
|---|---|---|---|
| 1 | **Pré-voo de abertura** verde: `python scripts/piloto_preflight.py --modo abertura --leituras <arquivo.json>` | você (as leituras do GitHub são suas; o script **não usa rede**) | VERDE=0, ÂMBAR=3, VERMELHO=1. Vermelho **para** tudo. Leituras sem segredo |
| 2 | **Aprovação expressa** da janela, citando **PR e head** | **você**, no chat ou no próprio PR | O atalho "Mesclar" **não vale** para a janela |
| 3 | A sessão abre o **PR de janela**: liga **só** `storage.private_flow_promotion_enabled`, com data e hora de abertura (UTC) e **limite de 24 h** | sessão | Sem merge antes do passo 2 |
| 4 | **Mesclar** o PR de janela (passo 2) e atualizar o clone na `main` | você | |
| 5 | **Reinstalar o fluxo no SHA do merge da janela:** `bash scripts/termux/ufms.sh atualizar` e `bash scripts/termux/prepara_entrada.sh`, etapa 4, frase **`ATUALIZAR`** | você | Sem isso a flag ligada **não vale**: o fluxo lê a flag **no SHA que fixa** |
| 6 | **Pré-voo pós-janela** verde: `--modo pos_janela` | você | `private_flow_promotion_enabled=true` só no SHA fixado; `personal_results_writes_enabled=false` sempre |
| 7 | **Ciclo:** a Zapia entrega o resultado do caderno na fila `entrada`; o fluxo promove **um** evento a `dados` | você e a Zapia | Sem marca de sintético; **sem leitura de volta o resultado fica PENDENTE**, não registrado |
| 8 | **Conferir o evento no privado** (id, SHA do commit, hash) **sem colar valores** | você | A sessão **não lê** o privado; sua conferência é relato com captura |
| 9 | **Fechar:** PR de fechamento volta a flag do fluxo a `false` | sessão abre, você mescla | Dentro de **24 h** ou ao ler o evento de volta, o que vier **primeiro** |
| 10 | **Reinstalar o fluxo de novo** no SHA do merge do fechamento (`ATUALIZAR`) | você | **Mesclar sem reinstalar NÃO desliga o fluxo** (E7) |
| 11 | **Pré-voo de repouso** verde: `--modo repouso` | você | As duas flags `false` **e** o hash do fluxo conferem |
| 12 | **Relatório do ciclo** (`piloto_relatorio.py`): contagens, SHAs, hashes, oito etapas com prova ou NÃO PROVADA, linha **"Não provado:"** | sessão, com seus relatos | Sem dado pessoal; **nenhum segundo caderno** antes do fechamento |

## Quando parar na hora (VERMELHO)

Dado pessoal no repositório público; escrita sem leitura de volta declarada como feita; flag do público `true`; token ou segredo exposto; hash do fluxo diferente do esperado; consentimento inválido ou revogado; evento gravado fora de `dados`; `dados` ou `entrada` não privado; janela aberta há **mais de 24 h**; fechamento sem reinstalar o fluxo. Em vermelho: **fecha a janela do mesmo jeito** (passos 9 e 10); você pode **revogar o token** (S7-R8) e **apagar** o repositório privado, que é a única eliminação efetiva (D-03).

## Frases literais

- Aprovação da janela, no chat ou no PR: `Aprovo a janela do piloto: PR #<n>, head <sha completo>.`
- Autorização do merge da janela e do de fechamento: `Aprovo o merge do PR #<n>, head <sha completo>.` (uma para cada PR).
- Frases do roteiro do Termux: `ATUALIZAR` (reinstalar o fluxo), escritas por você na etapa 4 do `prepara_entrada.sh`.
- Relato de cada ato à sessão, **sem valores**: `Feito o passo <n> da janela às <hora UTC>; saída: <código ou resumo>.`

## Limites e o que ainda não existe

O **roteiro do Termux do piloto** (`scripts/termux/piloto.sh`, item **RT** da fila) **ainda não existe** e depende da PJ aprovada; este roteiro só descreve a sequência com os scripts que já existem. A janela, o consentimento v4 e o fluxo **não** provam utilidade pedagógica. Relato seu **não** é prova independente. A **reauditoria do GQ-D** (bloqueador da RM-08) **não** faz parte deste piloto.
