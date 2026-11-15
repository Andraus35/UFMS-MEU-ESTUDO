# Resultado de P1 e P3 da persistência privada (15/11/2026)

**Natureza:** **relato do proprietário**, com capturas de tela do Termux, sobre a execução de `scripts/termux/cria_repo_privado.sh` (versão autônoma, com o texto do consentimento v2 embutido). **O agente construtor não verificou nada no repositório privado:** a sessão não tem acesso a ele, como o ADR-013 manda nesta etapa. O registro tem só hashes e o estado dos controles, sem dado pessoal. **Não habilita a escrita de resultados.**

## O que o proprietário mostrou

| Controle | Observado nas capturas | Situação |
|---|---|---|
| Criação | O repositório `ufms-meu-estudo-dados` não existia; o script pediu `CRIAR` e o criou como privado. | feito |
| **P1**, visibilidade | `private=true` foi lido pelo script ("confirmado por leitura autenticada") e, depois, por `gh api repos/... --jq '.private'` na mão, que devolveu `true`, duas vezes. | **cumprido, por relato** |
| **P3**, 1ª tentativa | O proprietário digitou `CONSINTO` (sem ` v2`); o script respondeu "consentimento NÃO registrado". O `consent.json` não existia (404, "This repository is empty"). | nada gravado, como esperado |
| **P3**, 2ª tentativa | Com `CONSINTO v2`, o script registrou o consentimento v2 e confirmou por readback (SHA-256 do arquivo começando em `d47189920fd9`). `gh api .../contents/consent.json --jq '.sha'` devolveu o blob `1db27796a192171e1c8ac9b5912591472d3946f6`. | **cumprido, por relato** |
| P6, readback | O próprio script comparou o SHA-256 do arquivo gravado com o local e confirmou. | cumprido no script |

## O que continua aberto

- **Prova independente de P1 e P3:** só vale por leitura autenticada fora do modelo; a sessão não tem acesso ao repositório privado (e não deve ter, nesta etapa).
- **P2, P5 e P9** estão cobertos por testes offline com fixtures; **P4** (escritor), **P7** (reconstrução a partir de eventos privados reais), **P8** (revogação: só texto) e **P9** em repositório real **não estão provados**.
- **Credencial mínima (PR-010, D-09)**, OPEN-01 e OPEN-02.
- **A flag `personal_results_writes_enabled` continua `false`.** Habilitá-la é PR próprio, com aprovação humana expressa, só depois de P1 a P9.
- O consentimento v2 inclui a Zapia (servidores nos Estados Unidos) e o Google; apagar o repositório não elimina essas cópias.
