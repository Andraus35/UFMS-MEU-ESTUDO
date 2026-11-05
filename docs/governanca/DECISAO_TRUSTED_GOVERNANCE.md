# SIM-07 — decisão sobre a proposta Trusted Governance / GitHub App

**Origem:** branch histórica `audit/trusted-governance-p0-20261104`, SHA `9e928a31d626c174a813e54461d408271d531c65` (44 commits exclusivos no inventário original). PR #10 foi encerrado sem merge. Esta nota registra auditoria e decisão, não instala serviço.

## O que a proposta exige

- GitHub App própria, instalada apenas no repositório, com permissões específicas de Checks e leitura de PRs/Contents.
- Host externo confiável (proposta Oracle), execução agendada, token de instalação efêmero e chave RSA privada da App fora do repositório.
- Chave Ed25519 separada, guardada no Termux, para assinar a aprovação humana exata de PR/HEAD/BASE.
- Scripts de leitura/validação e publicação de check próprio da App, workflows e testes adversariais.

## Limitações documentadas pela própria proposta

1. A App não foi registrada/instalada e o host Oracle não foi implantado nem ensaiado. Os testes usam backend simulado; não comprovam proteção remota.
2. Um check verde pode permanecer válido no GitHub por até sete dias. A janela local de 10 minutos do publisher **não é lease aplicada pelo GitHub**; não garante revogação imediata quando o serviço fica indisponível.
3. A própria ADR-P0-APP-001 conclui que revogação imediata durante indisponibilidade é impossível usando apenas check assíncrono no mesmo commit imutável.
4. A alternativa de transferir o repositório para organização e usar merge queue é outra migração administrativa, ainda não desenvolvida, com impacto em identidade, permissões e integrações.
5. A assinatura prova posse da chave e vínculo ao objeto; não prova avaliação semântica independente. Administrador ou host comprometido ainda pode desativar ou falsificar a barreira.

## Decisão para o projeto pessoal

**Não integrar** `scripts/trusted_governance.py`, `scripts/trusted_app_check.py`, workflows, chaves, permissões ou a infraestrutura Oracle. O projeto já possui branch protection `validate`, PR serial, CI, revisão e gates de privacidade proporcionais. A proposta externa adiciona operação e segredos sem eliminar o risco estrutural de check verde obsoleto.

A branch histórica permanece preservada para consulta; não apagar commits exclusivos. A decisão não impede reavaliação se o projeto migrar para colaboração multiusuário ou precisar de uma âncora externa comprovável. Nesse caso, exigir primeiro ensaio E2E com App real, indisponibilidade, revogação, branch protection sem bypass e merge queue; caso não se consiga provar a revogação requerida, não afirmar fail-closed universal.

## Estado operacional

- Nenhuma GitHub App nova instalada; nenhum host Oracle configurado.
- Nenhuma chave privada, token ou segredo criado/importado.
- Nenhuma nova check requerida ou workflow confiável adicionado.
- A branch protection e o check `validate` continuam sendo a proteção confirmada; não confundir CI com barreira administrativa inviolável.
