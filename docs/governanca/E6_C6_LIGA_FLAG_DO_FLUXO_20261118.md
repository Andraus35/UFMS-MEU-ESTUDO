# E6 — C6: liga a flag do fluxo privado (18/11/2026)

**Natureza:** registro da C6 (S6). **Situação: proposta aguardando a aprovação expressa do proprietário; o merge só sai por pedido dele, citando PR e head.** É PR de **janela curta** (decisão dele): liga, prova e desliga na mesma sessão.

## O que muda
| Onde | Antes | Depois |
|---|---|---|
| `settings.json`, `storage.private_flow_promotion_enabled` | `false` | **`true`** |
| `settings.json`, `storage.personal_results_writes_enabled` | `false` | **`false` (não muda, nunca liga)**: é a flag do repositório **público**, que não guarda resultado |
| `tests/test_promotion_runner.py` | esperava a flag do fluxo falsa | espera **verdadeira** só enquanto a janela estiver aberta; o PR de fechamento volta o valor |

## O que ligar NÃO faz sozinho
- **Nada muda no GitHub real** enquanto o fluxo instalado em `entrada` fixar o SHA antigo (`294b9c3`): o fluxo lê a flag do `settings.json` **do SHA que fixa**, não do `main`. Para valer, o proprietário **reinstala o fluxo** (`bash scripts/termux/prepara_entrada.sh`, etapa 4, frase **`ATUALIZAR`**, porque o fluxo já existe) depois de atualizar o clone na `main` com este PR.
- **Não habilita leitura por sessões** (S6-R9): continua sem gerador de projeções e sem acesso de sessão ao estado pessoal.
- **Não promove resultado pessoal:** a prova usa um evento **sintético** `caderno_recomendado` com `sintetico: true`, que as projeções descartam.

## Pré-condições conferidas antes de ligar (o roteiro da prova as confere de novo)
Consentimento **v4** registrado em `dados` (`consentir-v4`, leitura de volta, relato do proprietário de 18/11/2026); o runner e o portão **exigem** o v4 (C6B); `entrada` e `dados` privados com forks zerados; token da Zapia **só `entrada`**, conferido por sonda; primeira metade da C5 conferida; marca de evento sintético e descarte nas projeções (C6D); roteiro da segunda metade pronto (C5P).

## Janela e fechamento
1. Mesclar **este PR** (aprovação expressa) → atualizar o clone na `main`.
2. **Reinstalar o fluxo** (`prepara_entrada.sh`, `ATUALIZAR`) com o SHA do merge desta C6.
3. Rodar `bash scripts/termux/prova_c5_promocao.sh` (`PROMOVER`, token `zapia token`); cola a saída sem token.
4. **Fechar a janela, em seguida:** PR próprio que volta `private_flow_promotion_enabled` a `false`, e **nova reinstalação** (`ATUALIZAR`) com o SHA desse merge. **Mesclar o PR sem reinstalar NÃO desliga o fluxo.**
5. O evento sintético **permanece** em `dados` (histórico só de acréscimo), marcado como teste.

## Limites
O PR de fechamento **não** pode ficar aberto em paralelo (regra de PR único): abre logo depois da prova. Se a prova falhar, fechar a janela vale do mesmo jeito. Nada aqui foi executado no GitHub real; a prova é ato do proprietário. A flag ligada no `main` não é o estado desejado de repouso.
