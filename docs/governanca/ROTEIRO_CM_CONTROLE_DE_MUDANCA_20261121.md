# Roteiro CM — identidade própria do agente e `CODEOWNERS` ativo (decisão e ato do proprietário)

**Natureza:** passo a passo para **você** decidir e executar no GitHub; **a sessão não altera a proteção da `main`, não cria conta nem token e não executa nada**. Base: `docs/especificacoes/S14_RUNTIME_OPERACIONAL.md` (S14-R18), `.github/CODEOWNERS`, `scripts/protect_main.py`. Item **CM** da fila (depende da **RT**, que depende da **PJ**); este roteiro só **prepara a decisão**.

## Por que existe

Hoje o agente comita **com o seu usuário**: a autoria é **indistinguível** da sua, e o gate pode ser alterado **no mesmo PR** que a mudança. O **seu merge** é o único controle sobre `AGENTS.md`, `PRODUCT.md`, `agents/`, `.claude/`, `.github/` e o gateway. Sem isso a S14 declara a produção **"sem controle de mudança"**.

## Estado lido em 19/11/2026 (por leitura da API; reconferir)

`main` protegida: PR e check `validate` exigidos (strict), vale para administrador, sem force-push, conversas resolvidas; **0 aprovações exigidas** e **`require_code_owner_reviews` falso**. O `.github/CODEOWNERS` já lista os caminhos de contrato, mas **só vale como exigência** quando você ligar a opção na proteção da `main`.

## O impasse que a identidade resolve

Ligar "Require review from Code Owners" **sem** identidade própria do agente **trava o fluxo**: o autor do PR (o agente, que comita como você) **não pode aprovar o próprio PR**, e você é o único dono. Por isso o texto da S14 pede as duas coisas **juntas**.

## Decisões suas (uma de cada vez)

| # | Decisão | Opções | Minha recomendação, com o limite dela |
|---|---|---|---|
| D1 | Qual identidade o agente usa no GitHub | (a) **usuário-máquina**: conta GitHub separada, só para o agente, com acesso de escrita só a este repositório; (b) **GitHub App** instalado só neste repositório | **(a)** é a mais simples para um repositório pessoal e deixa a autoria distinguível. O App dá token curto e permissões finas, mas exige hospedar a lógica de emissão de token, o que o projeto já avaliou e **descartou como pré-requisito** (PR #10, histórico). **Não sei** como a sessão em nuvem passa a comitar com outra identidade: isso depende da configuração da conta/ambiente do Claude e **precisa ser verificado por você antes** |
| D2 | Quantas aprovações exigir | 0 ou 1 | Manter **0 aprovações gerais** e ligar **só** a revisão de dono do código: o PR comum não pede revisão, o de contrato pede a **sua** |
| D3 | O check de CI que reprova alteração de contrato sem aprovação do dono | fazer ou não | **Fazer**, em PR próprio com teste de fixture (altera `.github/`, então exige a sua aprovação expressa); a revisão de dono ativa cobre o caso comum, o check cobre a tentativa de alterar o gate junto |

## Passo a passo do ato (só depois de D1 e da verificação da identidade)

1. **Criar a identidade** conforme D1 (conta separada, 2FA ligado, sem permissão de administração, acesso de escrita **só** a `Andraus35/UFMS-MEU-ESTUDO`). Credencial **fine-grained** com expiração; **nunca** no chat nem no repositório.
2. **Conferir o `.github/CODEOWNERS`**: os caminhos de contrato apontam para **você**, e a identidade do agente **não** é dona de nenhum deles.
3. **Ligar** em Settings → Branches → regra da `main` → *Require review from Code Owners* (mantendo PR, `validate` estrito e as demais proteções que já estão). Não aplique o `scripts/protect_main.py --apply` sem revisar o plano: `python scripts/protect_main.py --plan` mostra o que seria enviado, e a aplicação **sobrescreve** a política inteira.
4. **Provar com um PR inofensivo** do agente que toque, por exemplo, uma linha de `agents/` em branch descartável: o GitHub deve pedir **sua** revisão e **bloquear** o merge sem ela. Feche o PR de teste sem mesclar.
5. **Relatar à sessão**, sem credencial: o nome da identidade, o que o passo 4 mostrou (com captura) e a leitura da proteção (`python scripts/protect_main.py --check`, que **lê** a política com o seu `gh`). A sessão só marca **feito** pelo seu relato (nunca por inferência) e abre o PR do **E9** com o check de CI.

## Frases literais

- Decisão: `CM: usar <usuário-máquina | GitHub App> como identidade do agente; revisão de dono ligada na main; 0 aprovações gerais.`
- Relato: `CM feito: identidade <nome>; Require review from Code Owners ligado; PR de teste bloqueado sem a minha revisão.`
- Aprovação do PR do check de CI (altera `.github/`): `Aprovo o texto e o merge do PR #<n>, head <sha completo>.`

## Limites

Sem a leitura autenticada da proteção pela sessão (a API devolve 403 à integração), a verificação é **relato seu**. A identidade separada **limita** o dano e **distingue** a autoria; **não** impede quem tem a sua credencial de alterar o gate. O CODEOWNERS **não** protege o que ele não lista.
