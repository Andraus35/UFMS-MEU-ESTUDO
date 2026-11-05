# API preflight corrigido — PRs draft atuais

Estado: proposta sensível em PR independente; não homologado nem mesclado.

O guard legado aceitou apenas o PR #1, que já foi mesclado. A correção
suporta qualquer PR com número inteiro positivo, mas continua recusando
repositório, branch, estado, arquivos e SHA inválidos. O PR deve permanecer
aberto e draft, sempre sobre main.

Duas etapas distintas:

1. check_proposal: valida apenas a estrutura declarada pelo chamador;
   não autentica os dados do LLM.
2. check_authenticated_proposal: usa leitor confiável da API GitHub,
   por padrão gh api -i no host autenticado. Confere identidade do PR,
   repositório, base, branch, SHA atual e blob de cada arquivo. Um create
   somente passa quando o servidor responde 404 para o caminho no HEAD;
   update exige blob e tipo file idênticos. 403, 429, ausência de dados,
   branch alterada e base desatualizada reprovam.

Os bloqueios de AGENTS, settings, rules, guardrails, edital, state,
segredos, scripts de política e workflows não são enfraquecidos. Mudança
de política não pode usar este preflight rotineiro.

A verificação é uma fotografia e não uma transação atômica. O cliente
ainda precisa usar CAS ou lease no write, reler HEAD e CI depois. Um
cliente com token direto pode ignorar o script, portanto não é um
controle universal de servidor nem concede autorização de merge.

O PR #9 (ROADMAP), PR #11 (broker), PR #12 (saneamento) e PR #5
(especificação) permanecem independentes e sujeitos aos seus próprios
gates. A mudança do próprio script de segurança precisa de revisão
humana e auditoria separada antes de integrar à main.


## Revisão adicional: alegações locais versus evidência remota

NC-13-01 (P1): check_readback aceitava SHA e estado da CI fornecidos
pelo próprio chamador, mas devolvia ci=success, confundindo alegação
com comprovação. O retorno agora declara claimed_ci=success_unverified,
readback=caller_asserted_only, ci_verified=false e
authenticated_remote_read=false. Não autoriza merge.

Nova check_authenticated_commit_readback exige GitHub autenticado
pós-commit, PR ainda draft, base/branch coerentes, HEAD efetivamente
avançado e pai imediato igual ao SHA anteriormente conferido.
Reprova troca de base, rebase, merge commit, PR fechado, branch
concorrente e ausência de prova. Ela NÃO atesta CI, permissões
administrativas, implantação de serviços ou autorização de merge.
