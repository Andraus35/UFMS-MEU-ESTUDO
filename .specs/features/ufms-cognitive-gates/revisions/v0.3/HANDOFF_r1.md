# HANDOFF — proposta corretiva v0.3-r1

**Estado:** PLAN v0.3-r1 NÃO APROVADO; CHECKS são PREVIEW, não congelados.
**Baseline congelada:** PR #5 pai 565c1f8ea61eb099d7875d83ed27ffb569fadf67; PR #4 reprovado 0db458a50447c2a9f8e7131f402dc3be9c0db313; PRs #1/#2 não editados.
**Escopo:** publicação documental de pré-aprovação; NÃO iniciar BUILD, GQ-C/GQ-O, merge, escrita de resultados pessoais, segredos, Calendar ou Telegram.

## Evidências locais, não operacionais

- PLAN v0.3-r1: 27/27 critérios EARS preservados da proposta corretiva v0.3; Observable com 16 estados vinculados a AC; quatro superfícies com aliases numéricos documentais.
- CHECKS-preview: 27 checks e dez deltas específicos, não são provas funcionais.
- Suíte r1 `python -m unittest -v test_local_validate.py`: 10/10 PASS em workspace local.
- Regressão da candidata original com PLAN/CHECKS r1: `python -m unittest discover -s tests -v`: 17/17 PASS após correção de falso positivo para sufixo r1.
- Os novos testes do verificador continuam reprovando falsa aprovação e ausência do estado de aprovação pendente.
- Tech Leads Club validate_plan.py / validate_checks.py / validate_verification.py oficiais: NOT_RUN; DNS do ambiente impede instalação/npm.
- Auditoria independente GQ-D: REPROVADA no objeto original. NC01–NC09 continuam ABERTAS nesta candidata até reauditoria independente; GQ-C NOT_RUN; GQ-O BLOCKED.

## Nota de integridade e provenance

Os arquivos `README_r1_local_snapshot.md` e `receipt_r1_local.json` preservam literalmente a situação **antes da publicação**; campos como `remote_written=false` são estado histórico do arquivo local e não equivalem ao estado desta branch depois do commit. O STATUS remoto deve ser comprovado por readback do SHA exato.
O original v0.3 permanece recuperável pelo commit pai. O PLAN v0.2 aprovado e o PR #4 auditado não são alterados.
A próxima decisão humana é ACEITE EXPRESSO do PLAN v0.3-r1; só então gerar/congelar CHECKS e encaminhar à reauditoria.
