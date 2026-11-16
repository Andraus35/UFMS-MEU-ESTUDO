# Resultado do consentimento v3 e do plano guardado (16/11/2026)

**Natureza:** **relato do proprietário**, com uma captura de tela do Termux ao rodar o script avulso `pendencias.sh` (não versionado neste repositório) e dois comandos `gh`. **O agente construtor não viu o repositório privado:** a sessão não tem acesso a ele, como o ADR-013 manda nesta etapa. O registro tem só hashes e o estado dos controles. **Omite de propósito a data de início, o nome e o hash do arquivo de plano e qualquer conteúdo dele** (dado pessoal; o repositório é público). **Não habilita a escrita automática de resultados.**

## Verificado pelo agente construtor

| Item | Resultado |
|---|---|
| Clone do proprietário | `main`, HEAD `85dbf66a`, igual à `main` remota, sem alteração local. É o merge do PR #92. |
| START de estudo | Os quatro hashes impressos no aparelho (`AGENTS.md 8dfcc59468aa`, `ROADMAP.md aeb79ef3f79a`, `memory/HANDOFF.md 892cc73101fc`, `state/CURRENT.json a22c52235efa`) **coincidem** com os que o agente calculou na `main` no mesmo commit. |

## Relato do proprietário (não verificado)

| Controle | Observado na captura | Situação |
|---|---|---|
| **P1**, visibilidade | O diagnóstico imprimiu "repositório privado de dados: existe, private=true". | cumprido, por relato |
| Consentimento v2 | `consent.json` presente, blob `1db27796a192` (o mesmo de antes). | inalterado |
| **P3**, consentimento v3 | `gh api .../contents/consent-v3.json --jq '.sha'` devolveu o blob `d1a72470ebccdc82859557d4b1e5ba16d743d25f`: o arquivo **existe**. | presente, por relato |
| Plano | `gh api .../contents/planos --jq '.[].name'` listou **um** arquivo de plano. | guardado, por relato |
| Escrita automática de resultados | `settings.json: false`. | desabilitada |
| Token da Zapia (passo 6 do script) | "token DIVERGE ou não conferido: não o entregue à Zapia". **A causa não foi vista**: pode ter sido o token ainda não criado ou colado, ou uma divergência real do perfil privado. | **pendente** |

## O que esta captura não mostra

- As linhas `[P3] ... confirmado por readback` e `[P6] ... confirmado por readback` dos passos 3 e 5 **não apareceram** (só o diagnóstico final e os dois comandos). A presença dos arquivos é o que o relato prova; o readback dos dois passos **não foi visto**.
- Não se sabe se o conteúdo gravado é o texto do v3 do ADR-013 nem o que o plano contém.
- O diagnóstico do script não cobria o v3 nem os planos, e imprimia o dicionário inteiro do próximo item da fila: **corrigido neste mesmo PR** (agora mostra o v3, a contagem de planos e só o `id`).

## Continua aberto

- O resultado do `token privado` (linha `RESULTADO`), sem o token, para saber se o perfil privado confere.
- P4 (escritor), P7, P8 e P9, OPEN-01 e OPEN-02, a S7 e a habilitação da flag, que é PR próprio com aprovação humana.
- Confirmação independente de P1, P3 e do plano, que só vale por leitura autenticada fora do modelo.
