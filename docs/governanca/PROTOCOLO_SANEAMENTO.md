# Protocolo de saneamento documental — UFMS MEU ESTUDO

## Fonte de autoridade e escopo

O saneador em scripts/saneamento_documental.py mantém uma camada de estado
corrente identificada por commit, consultada via GitHub autenticado. A main é
a fonte de código integrado; PRs abertos são candidatas, mesmo com CI verde.
Documentos antigos são registros históricos, nunca descartados por inferência.

### Manter integralmente

- A fonte do edital, as 81 unidades recuperáveis e o manifesto de integridade.
- AGENTS, settings, rules, guardrails, estados derivados e contratos da CI.
- A proibição de resultados individuais no repositório público.
- Decisões anteriores e handoffs históricos, inclusive aprovações limitadas.
- A separação entre testes locais, auditoria independente, homologação,
  aprovação de SPEC, implantação e autorização de merge.

### Sanear de maneira mecânica

- Criar docs/governanca/STATUS_VIGENTE.md com estado de PRs (incluindo
  fechado sem merge), SHA de main, visibilidade e bootstrap 9/10.
- Colocar seção delimitada governance-current no início de memory/INDEX.md,
  memory/HANDOFF.md, memory/DECISIONS.md, docs/API_WRITE_GOVERNANCE.md,
  docs/pedagogia/HANDOFF.md e
  docs/pedagogia/PROTOCOLO_ENTREGA_CONTINUIDADE.md.
- Preservar 100% do texto histórico abaixo dos avisos.
- Repetições do mesmo comando são idempotentes para a mesma fotografia.

### Não corrigir automaticamente

- Qualquer aprovação humana, decisão pedagógica, gate de segurança,
  contratos GOV, status de C1–C27 ou política de privacidade.
- Fixação de PR #1 em scripts/api_write_guard.py: requer PR próprio,
  testes adversariais e decisão de autorização de clientes.
- Instalação de Zapia, Gemini Notebook, Calendar/Tasks, Apps GitHub,
  regras administrativas, armazenamento privado e rotina de retificações.
- Integração do ROADMAP PR #9, broker PR #11 ou SPEC PR #5: cada um
  mantém seu próprio gate; o saneador não promove propostas.

## Execução

Pré-requisito: gh autenticado, checkout Git da branch exata, e permissão
para criar PR draft. Nunca executar no branch main.

Auditoria (somente leitura):

    python scripts/saneamento_documental.py --mode audit

Verificar se há divergências geradas (retorna código 2 se faltar sincronizar):

    python scripts/saneamento_documental.py --mode check

Aplicar atualizações documentais, exclusivamente em branch audit/docs/fix
associada a UM PR aberto e draft, após confirmar SHA do HEAD:

    python scripts/saneamento_documental.py --mode apply --expected-head SHA_COMPLETO

O modo apply nunca faz commit, push, merge, altera workflow, envia mensagem,
escreve dados pessoais ou muda regras administrativas. Depois da aplicação,
rodar os testes, conferir diff, fazer commit em PR e CI; atualizar handoff
conforme o contrato vigente.

O snapshot é uma fotografia; exige nova leitura remota antes de autorizar
qualquer ação. main.protected=true não comprova a configuração detalhada.
Uma falha no gh, em identidade, paginação, bootstrap, privacidade, markers,
symlink, estado sujo ou SHA deve interromper a operação.

## Limite operacional da automação

Este script elimina ambiguidade de precedência documental, mas não garante
que todo LLM leia ou obedeça a seus arquivos. O código não modifica a
segurança de clientes com credenciais externas. Não alegar G0/GQ-H,
GQ-D/C/O ou GP aprovado por resultado de sincronização.
