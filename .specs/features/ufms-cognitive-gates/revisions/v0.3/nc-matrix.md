# Matriz de tratamento — parecer independente PR #4

**Natureza:** proposta do produtor para reauditoria; não é parecer independente nem encerramento das NCs. Objeto de origem congelado: `0db458a50447c2a9f8e7131f402dc3be9c0db313`. GQ-D original = REPROVADA (1 P0, 7 P1, 1 P2).

| Achado | Severidade | Correção documental proposta | Contraprova exigida para encerrar | Status |
|---|---|---|---|---|
| NC-UFMS-GQD-01 | P0 | TC-02, AC13/14/22, D2 — emissores/aprovadores autenticados, JCS e vinculação completa de ferramenta/destino/parâmetros, nonce atômico | AUTH-IND-01 e NEW-02, efeito externo zero para troca tool/recipient | PROPOSTA; NÃO ENCERRADA |
| NC-UFMS-GQD-02 | P1 | TC-06, testes de significado separados do lint estrutural, quatro mutantes M-IND | Quatro mutantes semânticos rejeitados e oráculos humanos auditados | PROPOSTA; NÃO ENCERRADA |
| NC-UFMS-GQD-03 | P1 | `composition-manifest.json` com três SHAs fixos, ordem e FAIL_CLOSED | auditor reconstrói três checkouts imutáveis por SHA; não atribui prova ao HEAD de PR #4 isolado | PROPOSTA; NÃO ENCERRADA |
| NC-UFMS-GQD-04 | P1 | TC-01, AC04/11/25 — cadeia de fontes/fatos e `SOURCE_CONFLICT` | NEW-01 (p.13) + retificação fraudulenta e oráculo com versão | PROPOSTA; NÃO ENCERRADA |
| NC-UFMS-GQD-05 | P1 | TC-03, AC15 — rate limit atômico e contagem de efeito | limiar, janela, simultaneidade e zero chamadas após DENY | PROPOSTA; NÃO ENCERRADA |
| NC-UFMS-GQD-06 | P1 | TC-04, AC18 — pré-execução `DEPENDENCY_FAILED` x `UNCONFIRMED` e exits 0/1/2/3 | runner testa cinco estados de execução, quatro saídas e ausência de retry indevido | PROPOSTA; NÃO ENCERRADA |
| NC-UFMS-GQD-07 | P1 | TC-04, AC20, manifesto e status de aprovação do v0.2 | evidência independente do snapshot original associado ao aceite; receipts com SHA/árvore/dependências/exits | PROPOSTA; vínculo aprovação original NÃO VERIFICADO |
| NC-UFMS-GQD-08 | P1 | TC-05, AC26/D4 — versão de estado/fonte/canal/destinatário na autorização de render | token stale/trocado, bypass e zero publicações | PROPOSTA; NÃO ENCERRADA |
| NC-UFMS-GQD-09 | P2 | seções Flow, Impact, Relations; explicitação da adaptação Spec Lean | validadores oficiais e auditor independente executados sobre novo objeto | PROPOSTA; NÃO ENCERRADA |

**Preservação:** 17 critérios que receberam PASS documental na auditoria permanecem numerados e semanticamente equivalentes; ajustes de TC não dispensam reauditoria dos efeitos cruzados. AC4/11/13/14/15/18/20/22/25/26 foram alterados na v0.3 — **dependem de nova aprovação humana** antes de congelar CHECKS definitivos.
