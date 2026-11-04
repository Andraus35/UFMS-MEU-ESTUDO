# Instruções de reauditoria GQ-D — PR #5

**Papel:** auditor independente/adversarial, READ ONLY. Não herdar veredito do produtor nem usar testes locais como prova funcional.

1. Consultar `Andraus35/UFMS-MEU-ESTUDO` PR #5. **Congelar o SHA exato atual e sua árvore** no início da sessão, e registrar base, estado e commits. Comparar com snapshot de referência `64a0a66d290f6fc7d01318403b6948f43adbe385`; documentos de gate podem ter sido acrescidos depois sem alterar o PLAN/CHECKS.
2. Ler o PLAN aprovado, CHECKS C1–C27, `APPROVAL_v0.3-r1.md`, `approval-receipt.json`, manifesto de composição, a auditoria prévia do PR #4 e o diagnóstico `VALIDACAO_PRE_GATE_TLC_2026-11-04.md`.
3. Reexecutar/confirmar independentemente hashes e convenção formal `plan_approved()` da Tech Leads Club. Se a metodologia oficial não puder ser executada, marcar `NOT_VERIFIABLE`, não `PASS`.
4. Tentar refutar as nove NCs do parecer anterior (AUTH-IND-01, CITE-IND-01, NEW-01/NEW-02, M-IND-01..04). Usar pelo menos três novos mutantes sem repetir os anteriores e duas contraprovas novas.
5. Exigir comparação semântica AC↔CHECKS, incluindo a independência do oráculo de fontes oficiais, token de ferramenta/destinatário e garantia de zero efeito antes de `DENY`.
6. Separar `GQ-D` documental dos estados de comportamento de LLM `GQ-C` e operação externa `GQ-O`.
7. Relatar cada NC como corrigida documentalmente, reprovada ou não verificável. Não encerrar com afirmação de segurança operacional sem executor real.

**Restrições:** nenhuma alteração, commit, merge, deploy, credencial ou persistência de dados pessoais. O PLAN aprovado conserva SHA-256 `fa37d9c5cc2fb4288c477c4b175c8ec923ebb419be2aa9e785b32471b850c70c`.
