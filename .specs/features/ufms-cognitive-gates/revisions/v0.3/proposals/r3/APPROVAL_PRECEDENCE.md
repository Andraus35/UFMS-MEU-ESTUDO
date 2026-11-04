# Estado efetivo e precedência de aprovação — regra documental (sem alterar PLAN r2)

**Objeto de auditoria:** PR #5 SHA `652634b70a411ed4641cb7a202b0ae2f9a19ed1b`, fonte r2 aprovada por mensagem literal “APROVO”. **GQ-D REPROVADA** no parecer recebido. Isto não revoga a aprovação humana da especificação; apenas impede homologação.

1. O texto “NOVA PROPOSTA — NÃO APROVADA” nas primeiras linhas do `proposals/r2/plan.md` descreve o **estado histórico no momento da autoria do snapshot**, e foi preservado por integridade. Não é uma decisão de aprovação posterior.
2. O **estado efetivo** da versão é determinado por `CURRENT.md`, `APPROVAL_v0.3-r2.md` e `approval-receipt.json` **somente após** o leitor conferir compromisso de commit, SHA-256, blob Git original, escopo literal e proveniência contra âncoras independentes; não confiar em metadados desacoplados.
3. Aceite do PLAN r2 significa **somente** aprovação normativa para derivar CHECKS. **NÃO** concede autorização de deploy, merge, escrita pessoal, Telegram/Calendar, GQ-D/GQ-C/GQ-O ou alteração de requisitos.
4. O PLAN v0.3-r3 em `proposals/r3/plan.md` é **NÃO APROVADO**. O registro r2 não pode ser reutilizado para promovê-lo. O texto do PLAN r2 aprovado permanece imutado.
5. Se qualquer identidade for conflitante, o status é `NOT_VERIFIABLE`, com operação proibida; não corrigir o conflito pela opinião do LLM.

**Limite:** a checagem local é documental e não autentica identidade do aprovador em produção. A fonte externa de confiança é a consulta autenticada aos commits/árvores do GitHub e o histórico real da aprovação humana; recibo e script não podem servir de autoridade exclusiva um do outro.
