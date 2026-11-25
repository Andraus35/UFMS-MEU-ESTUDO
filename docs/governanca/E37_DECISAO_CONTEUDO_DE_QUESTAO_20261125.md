# E37: decisão do proprietário sobre conteúdo de questão na entrega da Zapia (25/11/2026)

**Natureza:** **registro de decisão**, não contrato. Nada foi aplicado em `agents/`, `AGENTS.md`, `PRODUCT.md`, `config/agent_command_schema.json`, `scripts/agents_gate.py` nem nos filtros em código. A aplicação exige aprovação expressa do texto e do merge, **depois da janela do piloto** (E3, D-27).

## Decisão C1 (25/11/2026, mantida e mandada persistir pelo proprietário)

1. O conteúdo das questões é **público**, obtido em sites de bancas de concursos. **Deixa de ser proibido** que a Zapia traga **enunciado e gabarito** na entrega.
2. O motivo: o Tutor precisa saber **o que o aluno acertou ou errou** ao confrontar com o relatório de desempenho das resoluções.
3. **Continua proibido:** o **comentário do professor** e os **recursos do TEC** (expertise da empresa), além de identificador de conta, HTML bruto, captura, credencial e dado pessoal.

## Como a sessão entende a aplicação (proposta, a aprovar)

- **Campos estruturados e separados** (`enunciado`, `gabarito`, `caderno_id`, `questao_id`, resposta marcada pelo aluno). Um filtro não separa com segurança "enunciado da banca" de "comentário do professor"; o que ficar fora dos campos é recusado (esquema fechado).
- **Só no repositório privado** (`entrada` e `dados`), pela fila e pelo portão, com a flag falsa. Nunca no público.
- Texto da questão e instrução embutida seguem como **dado não confiável** (S5-R4).
- **Teto de volume** por entrega, a definir na aplicação, para o arquivo não crescer sem limite.
- **Decidido pelo proprietário (25/11/2026):** o gabarito oficial e a resposta marcada pelo aluno vêm em **campos separados** (`gabarito` e `resposta_do_aluno`, mais `questao_id`); a Zapia não interpreta acerto ou erro, quem compara é o Tutor, por código. Registro em `docs/governanca/E38_REGISTRO_DE_APROVACOES_E3_E_FRASE_20261125.md`.

## O que este lote muda e o que não muda

| Muda (texto) | Não muda (aplicação futura) |
|---|---|
| E3, linhas de proibições e a seção "Decisão C1" | `config/agent_command_schema.json` ainda lista `enunciado` em `forbidden_param_keys` |
| S9, emenda E37 sobre a S9-R5 | `scripts/content_filters.py`, `delivery_gate.py`, `session_read_guard.py`, `platform_read_guard.py`, `notebook_prompt_validator.py` |
| Este registro e a nota no HANDOFF | `agents/` e o esquema de eventos |

## Limites

- Regra vigente **em código** segue sendo a antiga até a aplicação aprovada.
- Não há prova de que a Zapia consiga trazer enunciado e gabarito sem trazer comentário do professor; isso depende de teste real na janela do piloto.
- Direito autoral: o proprietário afirma que o conteúdo é público das bancas; a sessão não verificou a situação jurídica da cópia que o TEC exibe.
