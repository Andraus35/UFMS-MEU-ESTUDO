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
| Token (passo 6 do script e depois `ufms.sh token privado`) | O verificador **reprovou** o token colado: **`RESULTADO: DIVERGE (3 pontos) no perfil privado`**. Ver a seção abaixo. | **reprovado: não entregar à Zapia** |

## Resultado do verificador de token (segunda captura, relato)

O proprietário rodou `ufms.sh token privado` e colou um token no prompt oculto (o valor não aparece na captura). Saída relatada:

| Ponto | Observado | Esperado no perfil privado |
|---|---|---|
| Tipo | fine-grained (`github_pat_`) | fine-grained |
| Validade | **vazia: token sem expiração** | com expiração (PR-010, D-09; escolhida: 30 dias) |
| Repositórios que alcança | **4**: o público do projeto, o de dados e **dois outros repositórios do proprietário, alheios ao projeto** (nomes omitidos aqui) | exatamente 1: o de dados |
| Gravar arquivo no repositório de dados | **recusado (403)** | permitido (Contents: Read and write) |
| Criar issue, comentar, abrir PR, gravar no público | recusados | recusados |

**Leitura do agente construtor:** não é o token mínimo do repositório de dados. Parece um token **mais amplo** (talvez o que a Zapia já usa, que o relato anterior E-03 dizia alcançar repositórios alheios), com acesso de leitura ao repositório de dados e sem permissão de escrita nele. **Não se sabe qual token foi colado**; o proprietário deve dizer. O verificador reprovou exatamente os três pontos que devia, e **nada foi entregue à Zapia**.

**O que fazer:** criar um token novo, só do repositório de dados, com **Contents: Read and write**, nenhuma outra permissão e validade de 30 dias, conferi-lo com `ufms.sh token privado` até dar `CONFERE` e só então cadastrá-lo no formulário seguro da Zapia. Se o token colado é o que a Zapia usa hoje, ele alcança repositórios alheios ao projeto e deve ser **revogado ou reduzido** (OPEN-02).

## O que esta captura não mostra

- As linhas `[P3] ... confirmado por readback` e `[P6] ... confirmado por readback` dos passos 3 e 5 **não apareceram** (só o diagnóstico final e os dois comandos). A presença dos arquivos é o que o relato prova; o readback dos dois passos **não foi visto**.
- Não se sabe se o conteúdo gravado é o texto do v3 do ADR-013 nem o que o plano contém.
- O diagnóstico do script não cobria o v3 nem os planos, e imprimia o dicionário inteiro do próximo item da fila: **corrigido neste mesmo PR** (agora mostra o v3, a contagem de planos e só o `id`).

## Continua aberto

- O resultado do `token privado` (linha `RESULTADO`), sem o token, para saber se o perfil privado confere.
- P4 (escritor), P7, P8 e P9, OPEN-01 e OPEN-02, a S7 e a habilitação da flag, que é PR próprio com aprovação humana.
- Confirmação independente de P1, P3 e do plano, que só vale por leitura autenticada fora do modelo.
