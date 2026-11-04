# Pré-aprovação v0.3-r1 — Spec Lean UFMS

**Objeto:** revisão local, NÃO publicada no GitHub, do PLAN v0.3 contido no PR #5 SHA `565c1f8ea61eb099d7875d83ed27ffb569fadf67`. O PLAN v0.2 previamente aprovado e os PRs #1/#2/#4 permanecem intocados.

## Resultado

- Corrigida ausência da seção obrigatória **Observable**, agora 16 decisões observáveis em quatro superfícies, todas vinculadas a ACs.
- Adicionados aliases documentais de três dígitos para as quatro superfícies em `Surface`, preservando os estados semânticos e exit codes CLI originais.
- Corrigida referência incorreta do CHECKS-preview v0.3 para o PLAN v0.2; `Plan:` agora aponta explicitamente para a candidata v0.3.
- **27/27 critérios EARS textualmente idênticos** à proposta remota anterior. Nenhum requisito novo de segurança foi implicitamente aprovado.
- Verificador auxiliar local: **10/10 testes PASS**, incluindo nove tentativas de enfraquecer estrutura. Não é o validador oficial da TLC nem auditoria independente.
- **GQ-D REPROVADA**, todas as 9 NC ainda abertas; GQ-C NOT_RUN; GQ-O BLOCKED. Novo PLAN **AGUARDA APROVAÇÃO HUMANA**.

## Próximo gate

Submeter o PLAN corrigido à revisão humana. Não congelar CHECKS ou homologar antes do aceite. Validadores oficiais não executados por DNS bloqueado; a estrutura foi conferida mediante regras públicas de `validate_plan.py` consultadas em 04/11/2026, **não execução literal** desse script.

Referência: https://agent-skills.techleads.club/skills/tlc-spec-lean/
