# HANDOFF — Reauditoria GQ-D r2 reprovada → proposta corretiva r3

**Audit source:** `auditoria-independente-recebida.txt` (user supplied), target PR #5 `652634b70a411ed4641cb7a202b0ae2f9a19ed1b`, GQ-D **REPROVADA**.
**Baseline technical:** `main` já contém PR #1 e #2 mesclados; commit/árvore congelados em `composition-lock.json`. O próprio PR #5 continua draft.
**Source approval:** r2 aprovada em 04/11/2026, bytes de `approved-r2/plan.md` e CHECKS imutados. Status de aprovação resolvido por evidências, não reescrito no PLAN original.
**Candidate:** `proposals/r3/plan.md` e `checks-preview.md` **NÃO APROVADOS**, não promover a r2 automaticamente.
**Changes:** distinção AC13/14 no Observable; contrato de emissão/consumo atômico e revogação do renderer TC05/AC26; AC20/21 com SHA/escopo/âncora e mutação semântica; manifesto atualizado; auditor do recibo reforçado.
**Tests local:** 16/16 PASS, incluindo três mutantes independentes originais que escapavam. Somente inspeção documental/estrutural; a auditoria GQ-D independente continua reprovada até nova revisão.
**Expected official CI:** validadores formais de PLAN r3 (sem marcador Approved); CHECKS r3 deve falhar só pela ausência de aprovação humana, caso não haja outro problema. `--execute`, GQ-C e GQ-O continuam não executados.
**Next:** após publicação, conferir SHA/tree e a CI oficial. Submeter PLAN r3 à aprovação humana **separada**; somente então congelar CHECKS r3 e pedir reauditoria GQ-D independente.
**Never:** merge, habilitar dados pessoais, deploy, credenciais, Telegram ou Calendar sem gates específicos.
