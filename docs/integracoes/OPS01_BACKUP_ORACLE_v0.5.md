# OPS-01 — Backup, restauração e segredos na Oracle (v0.5)

Data: 04/11/2026  
**Estado:** protótipo técnico com CI; não há implantação Oracle nem backup real.
**Conservação:** PR #3 separado dos PRs #1/#2. Sem merge sem aceite humano.

## Ameaças mitigadas no código

| Falha | Mecanismo |
| --- | --- |
| Cópia SQLite inconsistente durante escrita | \`sqlite3.Connection.backup()\`, não \`cp\` de arquivo ativo |
| Cópia recuperável em claro no armazenamento de backup | \`age -r\` com recipient público; \`/tmp\` deve estar em tmpfs |
| Arquivo de backup parcial ou substituído | nome aleatório parcial + hardlink atômico sem overwrite |
| Corrupção ou restauração do banco errado | \`PRAGMA integrity_check\`, \`foreign_key_check\` e tabelas obrigatórias |
| Restauração durante a operação dos bots | lock \`.runtime.lock\` do gateway, exigido no restore |
| Restauração acidental destrutiva | confirmação obrigatória e sinal adicional para substituir arquivo existente |
| Informações privadas no retorno | apenas resultado, nome de arquivo, tamanho cifrado; erros genéricos |

## Preparação pelo operador (fora do GitHub)

1. Criar instância Oracle Compute Linux com volume criptografado, usuário
   restrito, atualizações de segurança, SSH com chave e portas públicas
   mínimas. Esta ponte usa **long polling Telegram**; não necessita
   de porta HTTP aberta para webhook.
2. Configurar Docker rootful/rootless conforme governança da instância,
   controles de volumes, limites de CPU/memória e logs mínimos. O processo
   da aplicação roda como usuário não-root no contêiner.
3. Preparar dois tokens BotFather, usuário Telegram autorizado, credenciais
   OAuth Google (se desejado), e chave da API LLM (se habilitada). Armazenar
   em OCI Vault ou mecanismo equivalente de segredos; nunca enviar ao
   chat, PR, logs, scripts versionados ou imagem.
4. Preparar chave age **fora** da VM Oracle, em máquina do operador:
   \`age-keygen -o ufms-recovery-key.txt\` e derivar recipient público com
   \`age-keygen -y ufms-recovery-key.txt\`. Proteger a identidade com
   permissão 0600 em armazenamento separado e cópia protegida.
   Disponibilizar somente o recipient \`age1...\` ao fluxo de backup.
5. Preparar pasta privada de backup sob responsabilidade do operador,
   montada no contêiner como \`/backups\` e com modo 0700/owner compatível.
   Snapshot temporário será gravado no tmpfs \`/tmp\`. Dimensionar espaço
   para o banco completo (e memória/tmpfs); não presumir capacidade ilimitada.

## Exemplo de execução de backup (após VM autorizada)

\`\`\`bash
# Exemplo conceitual: adequar paths, uid e montagem ao ambiente real.
docker compose run --rm --no-deps -v /srv/ufms/encrypted-backups:/backups \
  --entrypoint python ufms-bridge -m bridge.ops_backup backup \
  --db /data/ufms-bridge.sqlite3 \
  --output /backups/ufms-$(date -u +%Y%m%dT%H%M%SZ).sqlite3.age \
  --recipient 'age1CHAVE_PUBLICA_REAL'
\`\`\`

O \`recipient\` **não é secreto**; nunca colocar \`AGE-SECRET-KEY-...\` na
variável. O backup não inicia automaticamente nem é enviado à nuvem.
Agendar apenas após verificar backup, restauração e orçamento/quotas OCI.

## Verificação e restauração (manutenção aprovada, offline)

1. Fazer backup criptografado atual antes de restaurar sobre banco existente.
2. Desligar processo ativo: \`docker compose stop ufms-bridge\`.
3. Confirmar com segurança a origem do arquivo cifrado e dispor da identidade
   privada **somente na sessão operacional de recuperação**. Montar o
   caminho da identidade dentro de um contêiner efêmero, readonly, com
   permissões 0600 para o usuário do processo. Não montar no daemon ativo.
4. Verificar primeiro com \`python -m bridge.ops_backup verify\` e o
   \`--identity\`. Nenhum dado real foi recuperado nesta sessão.
5. Usar \`restore --confirm-restore --replace-existing\` **apenas** depois
   de confirmar banco de destino, serviço parado e backup do banco atual.
   O módulo recusa arquivos \`-wal\`/\`-shm\` remanescentes: tratar offline.
6. Iniciar com \`docker compose up -d\` e validar offsets Telegram, alertas
   \`sending/uncertain\`, consentimentos, relógio e idempotência. Restaurar
   um snapshot antigo **pode reprocessar updates Telegram**: reconciliar antes
   de permitir polling/envios.

## Controles pendentes, externos ao protótipo

- Backup periódico, cópia off-host, retenção por período e expurgo do object
  storage sob política explícita (incluindo snapshots OCI).
- OCI Object Storage com políticas IAM mínimas e instance principal
  se usado; credenciais de acesso à nuvem fora do repositório.
- Recuperação a partir de cópia externa e testes de restauração isolados
  com dados sintéticos + piloto com autorização humana.
- Verificação de dependências e CVEs das imagens e do pacote age.
- Não há garantia de zero tempo de inatividade nem RPO/RTO homologados.

## Critérios de aceite

- Teste real de criptografia \`age\` dentro da imagem construída pela CI.
- Backup de SQLite consistente e verificação sem revelar plaintext.
- Restore de base sintética válido, sem symlink, sem escrita no banco vivo.
- Fail-closed para archive inválido, credencial insegura, restore sem aceite,
  sidecars WAL e pasta de backup permissiva.
- Gate G0/GQ-H independente e autorização de implantação antes da produção.
