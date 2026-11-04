# Aplicação administrativa da proteção da main

**Estado de referência:** a API do GitHub informou `main.protected=false` e zero rulesets em 04/11/2026. Reconsultar ao executar. A CI do PR #9 teve duas execuções `validate` com sucesso para o commit `3106819840d4ebfe1dcc27736009b4af48f44341`, mas ainda não é requisito obrigatório de merge.

## Uma operação administrativa necessária

O conector GitHub utilizado pelos agentes permite leitura de proteções, mas **não oferece escrita nas configurações administrativas**. A proteção tem de ser aplicada pelo proprietário com `gh` autenticado no computador ou pela interface do GitHub. O comando abaixo executa **PUT** na API, depois **GET** e falha se o readback não corresponder. Não envolve segredos no repositório:

```powershell
gh auth status
python scripts/protect_main.py --plan
python scripts/protect_main.py --apply --confirm Andraus35/UFMS-MEU-ESTUDO
python scripts/protect_main.py --check
```

Executar em checkout do **PR #9 depois de revisar os arquivos**, ou após merge devidamente autorizado. A aplicação sobre `main` não exige merge prévio, mas o script deve ser executado a partir de código revisado.

## Política aplicada por padrão

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
