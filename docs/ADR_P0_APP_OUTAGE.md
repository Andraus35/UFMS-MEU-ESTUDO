# ADR-P0-APP-001 — Ausência da GitHub App e check verde obsoleto

**Estado: proposta, sem aprovação humana, nenhuma infraestrutura instalada.**
**Referência:** auditorias independentes PR #10, G0/GQ-H PENDENTES. Esta
decisão é registro técnico de alternativas; não autoriza merge nem transfer.

## Problema demonstrado

O GitHub aceita checks obrigatórios concluídos com sucesso dentro de até
**sete dias**. O publicador `scripts/trusted_app_check.py` revalida a
política a cada varredura e limita a reutilização a 10 minutos, mas esse
limite **não é aplicado pelo GitHub**.

Se o serviço para depois de emitir verde e alguém revoga um comentário de
autorização sem alterar HEAD/base, o último verde pode continuar suficiente
para a proteção nativa. A suíte real-crypto reproduz a **persistência da
aprovação no backend simulado** quando nenhuma nova verificação é feita.
Isso confirma uma limitação do desenho, não prova que a proteção remota
seja resistente a bypass.

## Conclusão arquitetural

**Impossível garantir revogação imediata durante indisponibilidade
usando apenas um check assíncrono no mesmo commit imutável.**
Mais testes do mesmo checker não mudam a regra do GitHub.

Há duas vias de decisão, sem ativação automática:

### Opção A — Conservar repositório pessoal e operação manual bloqueada

- Manter PRs em draft; merge proibido até auditoria externa e aceite humano.
- Exigir revisão humana de colaborador distinto, com descarte de aprovações
  obsoletas e proteção sem bypass administrativo, depois de confirmação pelo
  proprietário. A simples revisão humana NÃO torna o check de 10 minutos uma
  restrição imposta pelo GitHub.
- Fazer revalidação síncrona no momento da decisão humana e não permitir
  agentes com permissão para mesclar diretamente.
- **Limite:** enquanto o dono tiver permissão para mesclar e existir verde
  antigo, um comando de merge fora desse processo ainda pode contornar a
  revalidação. Portanto, **não homologar como fail-closed universal**.

### Opção B — Migrar para organização GitHub Free pública e usar merge queue

O GitHub oferece merge queue para **repositórios públicos pertencentes
a organizações**, inclusive no modelo gratuito. Também há restrições de
push por ator/App para repositórios públicos de organizações elegíveis.

Arquitetura-alvo (ainda não desenvolvida ou ensaiada):

1. Criar organização GitHub Free, com governança e responsáveis distintos.
   Transferir o repositório **somente sob autorização expressa**; revisar
   todas as integrações, branches, permissões, URLs e invariantes de identidade.
2. Exigir PR, revisão independente, sem bypass de admins, verificação
   `validate` e `ufms-governance/app-verified` de App ID específico,
   e **merge queue**; restringir push à `main` conforme recursos disponíveis
   na organização.
3. Adaptar `validate.yml` ao evento `merge_group` e o verificador App à
   verificação assinada de **cada SHA de merge group recém-criado**,
   incluindo PRs incorporados, base e autorizações exatas. O código de
   `verify_one()` atual, atrelado a `refs/pull/<n>/merge`, **não serve
   diretamente para merge queue**.
4. Se a App estiver indisponível quando o merge group nascer, o novo SHA
   não deverá receber o check requerido e a fila deverá permanecer bloqueada.
   Demonstrar com E2E real e casos adversariais, sem presumir comportamento.
5. Verificar que nenhum ator ou token de agente consegue empurrar commits à
   `main` contornando a fila, e que o proprietário permanece sujeito à
   proteção; auditoria administrativa independente obrigatória.

**Atenção:** a migração/merge queue não é uma alteração já implementada;
é uma possível via para exigir **novo check por tentativa de integração**,
em vez de reutilizar aprovação do mesmo commit por sete dias. Exige
engenharia adicional e ensaios reais.

## Gates objetivos para homologar

- GitHub App registrada, instalada e executando em host confiável com
  chave RSA inacessível aos agentes e public key Ed25519 verificada.
- Checks reais vinculados à identidade de App e requeridos pela branch.
- Teste de dois PRs compartilhando HEAD com a assinatura de um só.
- Teste de revogação de assinatura + serviço fora do ar após check verde,
  **bloqueando integração por controle nativo, não por convenção**.
- Teste de HEAD/merge sintético ou merge group, conforme arquitetura
  definitiva, com prova de impossibilidade de bypass por push ou merge.
- Readback autenticado de proteção e de regras adicionais, com
  `required_status_checks`, `enforce_admins`, regras de revisão,
  bypass, force push/deletion e identidade do check.
- Reauditoria externa G0/GQ-H do SHA congelado e aceite humano.

## Referências

- GitHub Docs — Troubleshooting required status checks:
  https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- GitHub Docs — Managing a merge queue:
  https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- GitHub Docs — Managing a branch protection rule:
  https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule

## Limite adicional de uma merge queue

A fila cria um novo SHA para o grupo no momento do enfileiramento e pode evitar
que um check antigo do HEAD autorize outro objeto de integração. **Não fornece
revogação instantânea depois de um check verde no próprio merge-group**: uma
autorização revogada entre a aprovação do grupo e a integração continua
sujeita às regras nativas de validade de checks. Assim, migração sem um
protocolo de autorização e ensaio E2E não encerra a não conformidade.

A CI atual é executada com o código do merge sintético, mas seu check
`validate` aparece no HEAD. Uma App que emitir check no sintético poderá
mudar o SHA utilizado pelo GitHub para os checks obrigatórios. Não ativar a
proteção proposta até reconciliar todos os checks obrigatórios no mesmo
commit verificado no servidor.
