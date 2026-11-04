# Checagem oficial Spec Lean como CI documental (PR #5)

Objeto esperado: `Andraus35/UFMS-MEU-ESTUDO` PR #5, HEAD pai `99df236251bbaad83033c996f34f8d2c4cc9ccc2`. A workflow adicionada usa apenas permissões `contents: read`, sem credenciais de LLM, sem ferramenta de Calendar/Telegram e sem persistência de resultados pessoais.

O commit TLC público é fixado em `1da2195067c14ae5d44dc615b31cb26f50ebeb91`, com os quatro hashes Git blob dos scripts oficiais conferidos antes de execução. O resultado é publicado como logs/artifact em GitHub Actions, não como homologação do produto.

**Duas visões diferenciadas:** no objeto canônico, `plan.md` e `checks.md` têm seus SHA-256 recalculados a partir do recibo de aprovação. Uma cópia efêmera recebe a linha `**Approved**: 2026-11-04 - user: "APROVO"` exigida pela Tech Leads Club, sem escrita no arquivo aprovado. Ambas são validadas e seus códigos de saída registrados. Um PASS da cópia efêmera é limitado à compatibilidade formal; não autoriza declarar que os bytes canônicos passaram nem que o harness funciona.

**Limites:** `validate_checks.py --execute` NÃO é acionado, pois os comandos Build citam o PR técnico #1 em outro SHA; `validate_verification.py` não é tratado como passável sem provas funcionais. Não encerra as nove NCs, não substitui reauditoria independente, não executa VERIFY-C/O e não autoriza merge/deploy.

Se o runner não for disparado, registrar `CI NOT_RUN`. Se houver falha, preservar os logs e reportar o erro real — sem alterar PLAN/CHECKS normativos para produzir verde.
