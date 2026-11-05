# Revisão técnica adversarial — PR #9 / ROADMAP e START

**Data:** 04/11/2026 — America/Campo_Grande  
**Repositório:** [Andraus35/UFMS-MEU-ESTUDO](https://github.com/Andraus35/UFMS-MEU-ESTUDO)  
**Candidata:** [PR #9](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/9), branch `docs/roadmap-required-bootstrap-20261104`  
**Base `main` observada:** `676dd5d3259c66ba97c3e7e3338451cfc4e5cd68`.  
**Referência da revisão inicial:** `f77ceb9c34625200b1a0e9fd99f309bbac9902e9`.  
**Escopo:** integridade do roadmap, enforcement de START/DELIVERY, CI, proteção administrativa de `main` e agentes externos.  
**Modalidade:** revisão adversarial **do próprio agente implementador**, sem independência de autoria. **Não constitui homologação G0/GQ-H ou autorização de merge.**

## Evidências confirmadas

- Na revisão inicial, duas execuções do workflow `validate` no commit `f77ceb9...` terminaram `success`; log indicou 175 testes. O HEAD atual depois das correções exige nova CI específica; não herdar CI anterior.
- Em 04/11/2026, a API GitHub retornou `main.protected=true`, check obrigatório `validate` com `enforcement_level=everyone`. A consulta detalhada `GET /branches/main/protection` retornou 403 à integração (falta permissão de administração dessa credencial); o proprietário relatou `python scripts/protect_main.py --check` OK com autenticação no Termux.
- O PR #9 permanece draft e aberto. `main` segue no SHA de base sem o `ROADMAP.md`; as regras novas funcionam na candidata até merge autorizado.
- `settings.json` inclui `ROADMAP.md` como segunda leitura obrigatória; `scripts/agent_gates.py` calcula hashes e rejeita arquivos ausentes e inconsistências; `scripts/roadmap_gate.py` executado pelo workflow verifica referências. Scripts não atestam interpretação cognitiva por LLM.

## Matriz de não conformidades e riscos

| ID | Severidade | Condição adversarial | Resultado / ação |
|---|---|---|---|
| AR-09-01 | M | `docs/OPERACAO.md` citava nove arquivos apesar do bootstrap de dez | **Corrigido na candidata**; teste de regressão `test_nove_arquivos_reprova_contrato`; confirmar CI do HEAD final |
| AR-09-02 | A | Um `ROADMAP.md` contendo só cabeçalhos podia passar sem conter RM-00–10 | **Corrigido na candidata**: conteúdo mínimo, 11 itens ordenados, IDs únicos, prioridade, status e critério; mutantes testados |
| AR-09-03 | M | Handoff, README e docs de governança ainda afirmavam que PR #1 era draft ou `main` desprotegida | **Corrigido por atualização do estado vigente**, preservando histórico; revalidar com GitHub antes de cada sessão |
| AR-09-04 | A | `scripts/api_write_guard.py` aceita apenas PR #1 e bloqueia arquivos de governança; não atesta o PR #9 | **Pendente, explicitado** em `docs/API_WRITE_GOVERNANCE.md`. Este PR segue caminho estrutural sensível com revisão humana; não declarar cumprimento do adaptador legado, nem afrouxá-lo sem auditoria |
| AR-09-05 | A | Mesmo exigindo o check `validate`, o autor pode propor alterações simultâneas no workflow e em seus validadores | **Risco residual**; a proteção `main` não garante um validador imutável. Exigir verificador de fonte confiável, separado do HEAD candidato, ou revisão independente efetiva antes de merge |
| AR-09-06 | A | Um agente externo/API pode ignorar bootstrap; um LLM pode ler bytes sem interpretar o documento | **Risco residual**. Exigir enforcement no entrypoint do Tutor/Coach e credenciais de menor privilégio. Copilot recebe instruções consultivas; isso não constitui prova de execução |
| AR-09-07 | M | O auditor via conector não consegue observar todos os campos da proteção GitHub (403) | **Evidência parcial**: branch `protected=true`, check `validate` obrigatório, verificação administrativa relatada pelo proprietário. Para fechamento independente, conferir dump sanitizado de `gh api repos/Andraus35/UFMS-MEU-ESTUDO/branches/main/protection` com permissão adequada |
| AR-09-08 | A | O mesmo agente implementou e revisou a candidata | **Bloqueio de independência**. Auditor distinto deve congelar HEAD/base, examinar mutantes e dar parecer próprio; CI verde não substitui parecer |

**Severidade:** A = alta, M = média. Correção na candidata não significa correção integrada à main.

## Limites e contraprovas

1. Testar remoção do roadmap, arquivo vazio, UTF-8 inválido, seções ausentes, truncamento e IDs duplicados/ausentes. Exigir falha da CI e scripts, não apenas saída textual favorável.
2. Trocar dez por nove no contrato operacional e verificar `scripts/roadmap_gate.py --check` rejeitando. Trocar ordem no `settings.json` e verificar `check_bootstrap` rejeitando.
3. Retirar `python scripts/roadmap_gate.py --check` do workflow e comprovar que `scripts/ci_gate_contract.py` reprova **se preservado**; reportar que um atacante com permissão para alterar também esse próprio verificador ainda tem bypass.
4. Com CI verde, checar se PR draft ainda não foi mesclado, SHA exato do check, branch protection `protected=true` e status obrigatório. Nunca derivar aprovação humana do campo `mergeable=true`.
5. Usar resultados sintéticos e somente testes que não escrevam estado pessoal; flags de resultados individuais e `state/events/` permanecem bloqueados.

## Veredito limitado

**Conformidade local estrutural: condicionada à CI do HEAD final.**  
**Garantia universal de leitura antes de qualquer trabalho: NÃO DEMONSTRADA.**  
**Auditoria independente: NÃO EXECUTADA.**  
**Merge/implantação na main: NÃO AUTORIZADOS.**

Próxima etapa: congelar a SHA final candidata, fazer auditoria verdadeiramente independente, fechar ou aceitar formalmente os riscos AR-09-04/05/06/07/08 e registrar decisão humana específica para merge. A ausência de um sistema central de supervisão dos agentes é um impedimento arquitetural, não algo que se resolva declarando sucesso no README.
