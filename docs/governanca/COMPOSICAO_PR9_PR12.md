# Composição controlada: PR #9 + PR #12

**Objeto:** candidata PR #14 empilhada sobre PR #9, sem merge na `main`.

- PR #9 HEAD de base: `4d2909eb6085926fbe4482f664ab2f62bcd61385`; inclui bootstrap de dez arquivos, roadmap e autonomia cognitiva.
- PR #12 HEAD de referência: `36e81390d8b41cf5c62a071e067779d2aed1d805`; saneador e testes preservados com correção de prefácios.
- O handoff do PR #9 começa com notas históricas antes do título; a nova implementação insere aviso sem sobrescrever esse prefácio.
- A geração mantém em `docs/governanca/STATUS_VIGENTE.md` o estado autenticado dos PRs; usa `SELF_CANDIDATE` para impedir SHA autorreferente da própria proposta.
- Conteúdo de `AGENTS.md`, `ROADMAP.md`, `settings.json`, `rules/`, `guardrails/`, `state/`, edital e CI do PR #9 não é alterado nesta composição.
- Sem teste funcional Tutor/Coach, sem habilitar resultados pessoais, sem credenciais externas, sem merge.
- G0/GQ-H independente do PR #9 permanece pendente; CI composta é somente evidência técnica.
