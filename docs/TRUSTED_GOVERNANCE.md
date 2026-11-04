# RM-00 — Âncora independente para governança

**PROPOSTO:** este controle está em um PR próprio. Ainda não está na main, não é required check e não homologa o PR #9.

## Propriedades

- Workflow \`.github/workflows/trusted-governance.yml\` usa \`pull_request_target\`, faz checkout **somente da base protegida**, nunca do código do PR, e usa token de leitura. Analisa diff/identidade/comentários obtidos pelo GitHub REST, sem executar qualquer código candidato.
- Arquivos estratégicos (\`ROADMAP.md\`, \`AGENTS.md\`, settings, rules/guardrails, hooks, CI e validadores) exigem assinatura **Ed25519** de uma mensagem contendo PR, HEAD e base exatos.
- A chave **privada** deve existir somente no Termux do proprietário. O GitHub guarda apenas a chave **pública** na variável administrativa de Actions \`UFMS_APPROVAL_PUBKEY_B64\`. Comentário GitHub sem assinatura não serve como autorização.
- O próprio gate (\`scripts/trusted_governance.py\`, workflow e teste) não pode ser alterado por PR ordinário, mesmo com assinatura. Manutenção exige operação administrativa excepcional, auditoria distinta e autorização humana.
- A assinatura atesta uma decisão humana identificada, **não** correção semântica do roadmap, auditoria independente ou autorização de merge.

## Implantação em etapas

1. Auditar independentemente **este PR de âncora**, aprovar e somente então integrá-lo à main por decisão humana expressa. Manter \`validate\` obrigatório.
2. Gerar chave exclusiva no Termux (não compartilhar \`private.pem\` com agentes, GitHub ou chat):

   \`\`\`sh
   pkg install -y openssl
   mkdir -p "$HOME/.config/ufms-governance"
   chmod 700 "$HOME/.config/ufms-governance"
   openssl genpkey -algorithm Ed25519 -out "$HOME/.config/ufms-governance/private.pem"
   chmod 600 "$HOME/.config/ufms-governance/private.pem"
   openssl pkey -in "$HOME/.config/ufms-governance/private.pem" -pubout -out "$HOME/.config/ufms-governance/public.pem"
   gh variable set UFMS_APPROVAL_PUBKEY_B64 -R Andraus35/UFMS-MEU-ESTUDO -b "$(base64 < "$HOME/.config/ufms-governance/public.pem" | tr -d '\n')"
   \`\`\`

   Fazer backup offline protegido. A perda da chave exige processo administrativo auditado para substituí-la.
3. Reacionar o PR #9 (editar a descrição) e confirmar que o check \`trusted-governance\` é produzido pela branch-base, **falhando por falta de assinatura**.
4. Somente após essa prova, o proprietário adiciona \`trusted-governance\` à proteção da main como check obrigatório **além de \`validate\`**, sem remover proteções existentes. Confirmar por leitura autenticada. **Não usar** \`scripts/protect_main.py --apply\` sem revisar: ele substitui a lista de checks existente.
5. Manter o PR #9 draft. Somente após **reauditoria independente APROVADA** e autorização humana específica, assinar o seu SHA exato.

## Assinatura no Termux após auditoria APROVADA

A mensagem deve ser exatamente \`GOVERNANCE-REVIEWED PR=<numero> HEAD=<sha40> BASE=<sha40>\`.

   \`\`\`sh
   REPO=Andraus35/UFMS-MEU-ESTUDO
   PR=9
   HEAD=$(gh pr view "$PR" -R "$REPO" --json headRefOid --jq .headRefOid)
   BASE=$(gh api "repos/$REPO/pulls/$PR" --jq .base.sha)
   gh pr diff "$PR" -R "$REPO"
   MSG="GOVERNANCE-REVIEWED PR=$PR HEAD=$HEAD BASE=$BASE"
   MSGFILE=$(mktemp); SIGFILE=$(mktemp)
   printf %s "$MSG" > "$MSGFILE"
   openssl pkeyutl -sign -rawin -inkey "$HOME/.config/ufms-governance/private.pem" -in "$MSGFILE" -out "$SIGFILE"
   SIGNATURE=$(base64 < "$SIGFILE" | tr -d '\n')
   rm -f "$MSGFILE" "$SIGFILE"
   gh pr comment "$PR" -R "$REPO" --body "$MSG SIG=$SIGNATURE"
   \`\`\`

A assinatura e o comentário são públicos; nunca publicar a chave privada. Qualquer novo HEAD/base exige outra assinatura.

## Riscos não resolvidos

- **NC-PR9-02:** sem Tutor/Coach operacionais e um broker central com tokens exclusivos, não há garantia de START universal. Restringir agentes consultivos a somente leitura, bloquear rotas diretas de escrita, impor bootstrap/recibo no executor e testar ações recusadas.
- **NC-PR9-03 a 06:** modelo de transições, sincronização estratégica, preflight API e prova administrativa completa seguem pendentes.
- A política de \`pull_request_target\` em repositórios públicos está sujeita a restrições anunciadas pelo GitHub para **02/12/2026**. Verificar se o workflow efetivamente roda **antes de torná-lo required**, e migrar a App externa confiável se necessário.


## Riscos adicionais identificados na revisão do mecanismo

**NÃO declarar este workflow uma âncora infalsificável.** Um check de GitHub Actions exigido apenas por nome e pelo aplicativo GitHub Actions pode, conforme configuração do repositório, ser confundido com outro job de nome idêntico introduzido pelo autor do PR. Portanto, a instalação deste workflow por si só **não encerra NC-PR9-01**. Uma implementação de produção exige confirmar o vínculo do check ao workflow confiável e evitar duplicidade/spoof de contexto, preferencialmente mediante **GitHub App verificadora distinta, com identidade própria e permissões mínimas**, ou uma política de workflow obrigatório aplicada fora do PR. Enquanto isso não for demonstrado, manter revisão independente e não homologar.

**A chave pública em variável do Actions não é secreta, mas sua substituição administrativa é um risco:** a chave deve ser revisada por outro canal e gerenciada separadamente das credenciais dos agentes. Os agentes de IA jamais recebem a chave privada do Termux ou permissão administrativa de substituir o check e sua origem.

**Prazo de execução:** a política padrão do GitHub para \`pull_request_target\` em repositórios públicos será aplicada a partir de **02/12/2026**, com testes de bloqueio em novembro de 2026. Verificar e autorizar estritamente o evento no painel de Actions Policies quando apropriado. Não tornar o workflow um check obrigatório antes de comprovar que continuará sendo executado.

**Estado preciso:** CI do PR significa apenas testes no código candidato. Instalação do workflow, assinatura administrativa e bloqueio efetivo de mutantes coordenados são etapas distintas e **ainda não realizadas**.
