# Estado de governança — fotografia verificável

**Aviso:** este arquivo é um snapshot de leitura autenticada. NÃO substitui consulta ao GitHub na hora de autorizar ações, não altera aprovações, nem representa revisão administrativa completa.

- Repositório: Andraus35/UFMS-MEU-ESTUDO
- Main (HEAD confirmado): 676dd5d3259c66ba97c3e7e3338451cfc4e5cd68
- Branch desta leitura: audit/governance-document-reconciliation-20261104 (HEAD próprio omitido para evitar autorreferência)
- Visibilidade: public
- Campo main.protected: true (não comprova detalhes de rulesets/bypass)
- Bootstrap desta revisão: 9 documentos; ROADMAP incluído: false
- Personal-result writes: BLOQUEADO (invariante local verificada)

## Pull requests observados

| PR | Estado | HEAD | Base |
|---|---|---|---|
| #1 | MERGED | 1079d7aa2cadb97d099d1e478f9e83b36180a624 | main |
| #2 | MERGED | 6e1fa661a33565d580f99962c3510d5361decbe6 | main |
| #3 | CLOSED_UNMERGED | 757e61c7e880fb8b38c4b215eb063c6c9f1e7cbe | main |
| #4 | CLOSED_UNMERGED | 0db458a50447c2a9f8e7131f402dc3be9c0db313 | main |
| #5 | OPEN_DRAFT | 9f1b347e755c82f15089470749d9d33524167c1f | main |
| #6 | MERGED | 03f1a4e4c615ba9f92b0466c8dacf27f527e182f | main |
| #7 | MERGED | 29a071ba7aec936930609cb952661b42f97919e2 | main |
| #8 | MERGED | 19f0a09207a21459d163807e7833af9eeb98603a | main |
| #9 | OPEN_DRAFT | 4d2909eb6085926fbe4482f664ab2f62bcd61385 | main |
| #10 | CLOSED_UNMERGED | 9e928a31d626c174a813e54461d408271d531c65 | main |
| #11 | OPEN_DRAFT | c7213f1ac512ede8760f8025a0f5d3db4aa7c288 | docs/roadmap-required-bootstrap-20261104 |
| #12 | OPEN_DRAFT | SELF_CANDIDATE | main |

## Regras de interpretação

1. Um PR fechado sem merge continua HISTÓRICO, não normativo.
2. Um PR draft não integra a main nem homologa funcionalidade.
3. Aprovação de especificação não é aprovação de implementação, operação ou CI independente.
4. Main protegida em resumo não comprova detalhes de política; readback administrativo permanece separado.
5. Preferir decisões vigentes e checkpoints mais recentes do mesmo HEAD; blocos históricos abaixo não podem ser usados como instruções atuais sem revalidação.

## Pendências que este saneador não pode decidir

- P0 AUD-01: Executor/broker de agentes não instalado: scripts e hooks locais não impõem START a clientes externos.
- P0 AUD-02: Proteção administrativa e origem independente dos checks não homologadas; nenhum check pode ser promovido por esta rotina.
- P1 AUD-03: scripts/api_write_guard.py continua fixo no PR #1 mesclado; exige revisão específica de segurança antes de generalizar.
- P1 AUD-07: Tutor/Coach, comunicação e armazenamento individual não foram homologados pelo saneamento documental.
- P1 AUD-09: Monitoramento de retificações requer executor, recibos e teste operacional próprios.
- P2 AUD-15: Provas isoladas do PR #5 não equivalem a homologação integrada de C1–C27.

## Proveniência

Fonte: GET autenticado via gh api de repositório, branch main e listagem paginada de PRs. Nenhum endpoint administrativo de proteção detalhada foi aceito como substituto da evidência ausente.
