# Auditoria administrativa de aceitação — PR #10

O **check operacional real** só existe quando uma GitHub App separada publicar
`ufms-governance/app-verified` com `app_id` próprio e esse check for
exigido por branch protection, além de `validate`.

## Em que pé está

**Ainda não instalado.** PR #10 está em draft, nenhum merge foi autorizado,
a `main` mantém somente `validate`. O presente diagnóstico é uma prova
read-only, e NÃO concede homologação G0/GQ-H.

## Procedimento seguro no Termux (não altera nada)

Após cadastrar/instalar a GitHub App, publicar um check real e atualizar a
proteção com autorização humana, executar:

```bash
pkg install -y gh python
gh auth status
cd ~/UFMS-MEU-ESTUDO
git fetch origin
git checkout <SHA_AUDITADO_APROVADO>
# Não usar um commit novo ou branch não auditada para o verificador.
REPO=Andraus35/UFMS-MEU-ESTUDO
PR=10
HEAD=$(gh pr view "$PR" -R "$REPO" --json headRefOid --jq .headRefOid)
BASE=$(gh api "repos/$REPO/pulls/$PR" --jq .base.sha)
APP_ID=<ID_DA_APP_PROPRIA_CONFERIDO_NO_GITHUB>
python scripts/check_live_governance.py \
  --pr "$PR" --head "$HEAD" --base "$BASE" --app-id "$APP_ID"
```

O script exige os dois checks emitidos pelas Apps esperadas sobre o commit de
teste de merge, a cadeia de pais, a identidade PR/HEAD/base, proteção de admins,
revisão de terceiros com aprovação obsoleta descartada, ausência de force-push,
proibição de exclusão, e readback da base. Falha com exit code 1 em qualquer
insuficiência, inclusive 403. **Não usar resultado como permissão de merge**:
o estado observado vale apenas naquele instante.

## Três contraprovas de infraestrutura (ainda NOT_RUN)

1. Abrir dois PRs de ensaio com HEAD idêntico e comprovar bloqueio cruzado.
2. Publicar check verde com App viva, parar o processo, retirar autorização
   sem novo commit e demonstrar que a integração permanece bloqueada.
3. Verificar checks simultâneos `validate` e `ufms-governance/app-verified`,
   com `app_id` específico, no SHA exigido pelo GitHub.

**Limitação estrutural:** o GitHub aceita checks bem-sucedidos dentro de
uma janela de até sete dias. O prazo de dez minutos usado pelo publicador e
pela sondagem read-only **não é regra de proteção no GitHub**. Ao cair a App
após sucesso, não é possível garantir bloqueio automático por ela sozinha.
Exigir política nativa complementar de revisores independentes e nenhum bypass
administrativo, além de controle operacional ou redesenho da autorização.

**Não foi configurada GitHub App, Oracle Cloud ou Branch Protection nesta
entrega.** A chave privada Ed25519 fica somente no Termux do proprietário; a
chave RSA da App, somente no host do serviço. Nunca expor ambas ao ChatGPT.
