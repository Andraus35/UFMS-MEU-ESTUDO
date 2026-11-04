# NC-PR9-01 — Âncora de governança fora do GitHub Actions

**STATUS: PROPOSTA CORRIGIDA NO PR #10; NÃO INSTALADA; NÃO HOMOLOGADA.**
Este documento não autoriza merge nem substitui auditoria G0/GQ-H.

## Arquitetura de confiança

O workflow original `pull_request_target` foi **retirado da candidata**.
Uma verificação obrigatória emitida pelo aplicativo genérico GitHub Actions pode
ser confundida com outro job de mesmo nome. Além disso, a política para
`pull_request_target` em repositórios públicos mudará em 02/12/2026.
Nenhuma das duas características é aceitável como âncora autoritativa.

A solução proposta é uma **GitHub App própria e separada**, hospedada em um
checkout congelado e revisado fora das branches candidatas, por exemplo na
Oracle Cloud (conta gratuita, se já disponível).

- `scripts/trusted_governance.py` valida PR, HEAD, base, `changed_files`,
  todas as páginas do diff, nomes atuais e anteriores, comentários de autorização
  Ed25519 e uma segunda leitura da identidade no mesmo HEAD/base.
- `scripts/trusted_app_check.py` autentica-se como a **GitHub App específica**,
  obtém token efêmero limitado ao repositório e publica o check
  `ufms-governance/app-verified` no **commit sintético de merge do PR**,
  após conferir `merge_commit_sha`, `refs/pull/<n>/merge` e os dois pais
  exatos (base, HEAD). Checks não são emitidos apenas no HEAD compartilhável.
  O `app.id` é conferido na resposta da API.
- `--all --once` varre PRs abertos periodicamente, sem webhook, porta de
  entrada pública ou segredo injetado em workflow de PR. Erros levam a falha
  ou ausência de check, **nunca à produção intencional de sucesso**.
- Cada parecer de autoria humana assina, com chave Ed25519 guardada
  **somente no Termux**, a string
  `GOVERNANCE-REVIEWED PR=<numero> HEAD=<sha40> BASE=<sha40>`.
- A chave privada RSA da GitHub App é **outra chave**, separada da Ed25519:
  ela deve ficar somente no host confiável (Oracle), com permissões 0600.
  Nunca levar qualquer chave privada a este chat, ao repositório ou ao LLM.
- `scripts/trusted_governance.py`, `scripts/trusted_app_check.py` e os testes
  de ambos são caminhos LOCKED; alterações futuras exigem processo
  excepcional fora da rotina, nova revisão externa e decisão humana.

**Limites:** uma assinatura prova posse da chave e identidade do objeto, não
a avaliação semântica nem independência humana do auditor. Um administrador
com privilégios completos pode alterar a proteção ou desativar a App; uma
máquina Oracle comprometida pode emitir checks falsos como a App. A aplicação
de check obrigatório, App ID esperado e isolamento de credenciais deve ser
comprovada em ambiente real. **Até lá NC-PR9-01 permanece aberta.**

## Sequência operacional (cada etapa tem gate próprio)

1. **Reauditar o PR #10 corrigido em SHA congelado.** Não instalar código
   de commit mutável nem mesclar candidatos reprovados. Somente após
   autorização humana específica, integrar código revisado na main.
2. **Registrar uma GitHub App** em https://github.com/settings/apps
   com nome único, acesso a **somente** `Andraus35/UFMS-MEU-ESTUDO` e
   permissões repositório: Checks **read/write**, Pull requests **read**,
   Issues **read**, Contents **read**, Metadata **read**. Sem Contents write, Administration
   write, Secrets ou Workflows. Sem webhook (verificador por polling).
   Instalar a App na conta proprietária e gerar uma **chave RSA privada
   da App**, armazenada apenas no Oracle com permissão 0600.
3. **Ativar ambiente independente no Oracle**: sistema Linux com Python 3.11+
   e OpenSSL, cópia isolada do código no **SHA auditado** em diretório
   não gravável por Tutor/Coach, token App guardado só no serviço.
   Variáveis restritas:
   `UFMS_GITHUB_APP_ID` (ID numérico da App),
   `UFMS_GITHUB_APP_KEY_FILE` (caminho da chave RSA),
   `UFMS_APPROVAL_PUBKEY_B64` (chave pública Ed25519 previamente
   gerada no Termux). Não usar o mesmo GitHub token pessoal dos agentes.
4. **Primeiro ensaio manual, sem exigir check ainda**:
   `python scripts/trusted_app_check.py --all --once`.
   Um PR de governança sem assinatura deve receber `failure`, o esperado.
   No GitHub, consultar o check emitido e comprovar `name`,
   `head_sha` **igual ao merge sintético**, `conclusion`, `app.id` e origem da App.
   A saída pode terminar em código 1 enquanto PRs aguardam assinatura.
5. **Automatizar**: executar `--all --once` a cada 2–5 minutos via
   cron ou systemd timer em host Oracle com usuário dedicado, diretório
   de código somente leitura, chaves sem leitura para os LLMs.
   Cada ciclo lê o estado atual e só reutiliza o check se tiver
   exatamente o mesmo PR/HEAD/base/**merge SHA**, resultado e App ID,
   e o resultado anterior tiver no máximo **10 minutos**. Este prazo é
   de renovação local, **não é exigido pelo GitHub** ao permitir merge.
   Testar adição/remoção de assinatura e novo push.
6. **Somente depois do check real e de nova auditoria**, configurar
   branch protection com **dois checks obrigatórios**:
   `validate` da GitHub Actions, App ID 15368;
   `ufms-governance/app-verified`, App ID **da App própria**.
   Usar o PATCH restrito de `required_status_checks`, não substituir
   a regra completa por `scripts/protect_main.py --apply`.
   Ler de volta toda a proteção autenticada e testar PR sem assinatura,
   PR assinado válido, SHA novo, nome duplicado originado em Actions,
   app offline e comportamento após mudança de base.
7. Fazer **reauditoria independente** e autorização humana para cada merge,
   preservando bloqueio de dados individuais e de execuções externas.

## Comandos Termux — somente após App instalada e auditoria aprovada

A chave Ed25519 já foi criada localmente pelo proprietário; **não a recriar**.
O comando abaixo utiliza APENAS a chave pública:

```sh
PUB="$HOME/.config/ufms-governance/public.pem"
test -s "$PUB" || { echo "Chave pública ausente"; exit 1; }
sha256sum "$PUB"
base64 < "$PUB" | tr -d '\n'
```

O resultado de base64 é público e será configurado **no serviço da App no
Oracle**, não em um workflow de PR. A chave `private.pem` NUNCA é transmitida.

Depois de instalada a App e auditado o check, a alteração administrativa
restrita poderá ser feita no Termux, com `APP_ID` verificado na página da
App (não inventar um valor):

```sh
REPO=Andraus35/UFMS-MEU-ESTUDO
APP_ID=<ID_NUMERICO_VERIFICADO>
gh api "repos/$REPO/branches/main/protection/required_status_checks"
# Revisar a configuração antes de QUALQUER PATCH.
# Não executar alteração até haver check real e autorização humana específica.
```

Um PATCH futuro deve preservar `validate` e acrescentar o check da App com
`app_id` específico; fazer readback da configuração integral e testes de
bloqueio antes de declarar ativo.

## Três riscos arquiteturais pendentes da conferência independente

### 1. Mesmo HEAD em dois PRs

O GitHub armazena check runs por **commit**; `external_id` não é um gate
por PR. O código agora confere o commit de teste de merge gerado pelo GitHub,
verifica os pais e **rejeita sucesso se dois PRs abertos compartilham o
HEAD**. A tentativa resulta em `failure` sobre o merge sintético, sem
permitir que uma assinatura emitida ao PR A seja atribuída ao PR B.

**Aceite obrigatório em ambiente real:** abrir dois PRs de teste com HEAD
compartilhado, assinar somente um, e comprovar que o outro NÃO pode ser
mesclado. A proteção nativa do GitHub precisa efetivamente considerar os
checks do merge sintético, não os resultados anteriores do HEAD. Até esse
teste, a mitigação é **verificada localmente**, não homologada no servidor.

### 2. Serviço externo indisponível após sucesso

**RISCO AINDA ABERTO.** A renovação de `success` a cada 10 minutos
evita reutilizar o check antigo enquanto a App opera. No entanto, se a
App parar após publicar `success`, um check anterior pode permanecer
válido para branch protection pelas regras do GitHub (checagens exigidas
precisam ser recentes, em geral dentro de sete dias). **Não existe um
TTL que o GitHub aplique a `external_id` ou ao prazo local do verificador.**

**Consequência:** não ativar esse gate como único controle de autorização
de merge. Para garantia de aprovação por PR vigente, é necessária uma
política nativa complementar (por exemplo, revisão obrigatória de outro
responsável, com descarte de aprovações obsoletas), ou um controle
servidor-side com avaliação síncrona no momento do merge, além de
monitoramento de disponibilidade. **Não prometer bloqueio de merge por
indisponibilidade somente com polling.**

**Aceite real:** emitir `success`, derrubar o serviço de forma controlada,
revogar ou remover a autorização **sem novo commit** e verificar se o merge
ainda é possível. Se for, registrar **FAIL** para garantia de fail-closed na
indisponibilidade e não homologar. Não executar teste real que altere branch
protection ou faça merge em PR de produção.

### 3. HEAD versus commit sintético de merge

O GitHub pode exigir verificações no merge sintético quando existem
checks naquele commit. Por isso o check da App é produzido no merge
sintético; a CI `validate` continua sendo executada no push e no
evento de PR (que pode usar o merge sintético).

**Aceite real:** verificar no servidor que ambos os checks obrigatórios,
`validate` e `ufms-governance/app-verified`, são satisfeitos no commit
correto para PR válido; PR inválido deve continuar bloqueado. Registrar
a SHA sintética, a aplicação emissora, o SHA HEAD e o estado de merge
sem forçar integração real.

### Condições de encerramento

Estas contraprovas são testes de infraestrutura, **não** substituíveis
por mocks de API ou resultados da CI do candidato. A instalação da App,
o check real, a proteção por App ID e o isolamento do executor devem
ser auditados por agente distinto. Sem isso, manter G0/GQ-H e NC-PR9-01
**PENDENTES DE EVIDÊNCIAS**.

## Ensaios aceitos e evidências insuficientes

- **Código:** testes unitários e negativos de renomeação de arquivo LOCKED,
  alteração semântica, paginação incompleta, corrida de HEAD/base,
  assinatura obsoleta, ausência de chave e check de App ID falso.
- **Infraestrutura:** nenhuma execução de GitHub App externa, criação
  de App, instalação administrativa ou required check da App foi realizada
  por esta entrega. A CI `validate` atual é verificação do código candidato.
- **Riscos residuais:** conflito de privilégios do próprio proprietário,
  disponibilidade do Oracle, expiração de tokens, alteração de permissões,
  e checks já emitidos enquanto o serviço está indisponível. Um check antigo
  pode persistir; exigir auditoria operacional de cobertura de eventos antes
  de considerar o ciclo resistente a indisponibilidade.

**NC-PR9-02 separada:** o PR #11 contém apenas broker local sem efeitos;
nenhum Tutor/Coach real está obrigado a usá-lo até restringir todas as
credenciais e implantar o supervisor. A App de governança não substitui essa
restrição de execução.


## Deliberação necessária após última bateria técnica

Existe um documento específico:
`docs/ADR_P0_APP_OUTAGE.md`. Ele registra que o GitHub aceita checks
aprovados por até sete dias, independentemente do TTL interno de dez minutos
e da disponibilidade da App. Uma arquitetura com merge queue por commit de
grupo pode mitigar esse problema, mas exigiria transferir o repositório pessoal
para uma organização GitHub pública, alterar o protocolo App/CI e realizar
testes reais. **Não foi decidido nem executado**.

O PR #10 inclui também:
- `tests/test_trusted_app_real_crypto.py`: fluxo integrado com assinatura
  Ed25519 real, sem simular a verificação OpenSSL; API GitHub simulada.
- `scripts/check_live_governance.py`: ferramenta de leitura administrativa
  para Termux, que falha na ausência da App/check/regras e registra
  explicitamente `merge_authorized: false`. Seu PASS é uma fotografia,
  não uma garantia futura.
- `tests/test_check_live_governance.py`: negativas determinísticas,
  inclusive app_id falsificado, proteção permissiva, check antigo e
  merge SHA incompatível.

**Sem implantação da App e sem prova do cenário offline, GQ-H permanece
PENDENTE DE EVIDÊNCIAS e o merge continua proibido.**
