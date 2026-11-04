# Aplicação administrativa da proteção da main

**Estado observado em 04/11/2026:** após aplicação pelo proprietário no Termux, a API autenticada confirmou `main.protected=true` e `validate` obrigatório para todos. O usuário informou `python scripts/protect_main.py --check` com resultado OK. A conexão do agente recebe 403 no endpoint detalhado, portanto não se afirma reauditoria independente da configuração completa. O PR #9 permanece draft sem merge.

## Conferência periódica e reaplicação excepcional

O conector GitHub utilizado pelos agentes permite leitura de proteções, mas **não oferece escrita nas configurações administrativas**. A proteção **já foi aplicada pelo proprietário**. Para verificar via `gh` autenticado no Termux, executar apenas `--check` (GET, sem escrita). Não envolve segredos no repositório:

```powershell
gh auth status
python scripts/protect_main.py --check
```

Reaplicar somente quando uma alteração administrativa for deliberadamente autorizada; `--apply --confirm Andraus35/UFMS-MEU-ESTUDO` envia PUT e **substitui** regras já existentes. Antes de uma reaplicação, verificar a política atual e revisar o código no checkout do PR. A verificação não realiza merge.

## Política que o script verifica

- Branch alvo: `main`; PR obrigatório, sem push direto para `main`.
- `validate` obrigatório e estrito (branch atualizada em relação à base).
- Aplicação também a administradores; sem force-push e sem exclusão.
- Conversas de revisão devem ser resolvidas.
- **Zero aprovações formais obrigatórias**, evitando bloqueio em repositório de mantenedor único: o autor de um PR não pode aprová-lo. O processo do projeto **continua exigindo autorização humana explícita antes do merge**, mas esta autorização não fica provada automaticamente por zero revisões.
- Se existir um segundo revisor GitHub independente com permissão adequada, preferir `--approvals 1` para impor aprovação formal de servidor; não habilitar sem verificar que há revisor possível.

Se uma proteção já existir, revisar a política atual antes de aplicar: a operação PUT **substitui** a configuração existente. Não executar comando administrativo de origem não revisada.

## Alternativa pela interface

Abrir [Settings → Branches](https://github.com/Andraus35/UFMS-MEU-ESTUDO/settings/branches) no repositório, adicionar regra para `main`: Require a pull request before merging, Require status checks to pass before merging (**validate**, strict), Require conversation resolution, Do not allow bypassing / Include administrators, bloquear force push e deletion. A nomenclatura varia segundo a interface/plano. Consultar a [documentação oficial do GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule).

## Testes de aceite (não presumir)

1. `python scripts/protect_main.py --check` retorna OK com autenticação administrativa.
2. GET autenticado para `repos/Andraus35/UFMS-MEU-ESTUDO/branches/main` indica `protected=true`.
3. PR de contraprova com CI vermelha **não pode ser mesclado**; evitar tentativas de push direto apenas para testes quando houver risco de escrita inadvertida.
4. Merge do PR #9 somente com autorização humana explícita. A existência da regra não comprova que todo LLM leu ou interpretou o roadmap.

**Limite de enforcement:** GitHub protege integração à `main`, não a etapa de raciocínio privado dos modelos, consultas ou operações fora do GitHub. Agentes externos devem utilizar o bootstrap do repositório e ser restringidos a PRs; revogar credenciais de escrita direta que escapem desse fluxo quando houver controle administrativo.
