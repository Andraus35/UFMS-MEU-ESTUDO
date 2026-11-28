# E55 — Resumo do canal no START do broker e rodada Tutor–Coach com subagentes reais (28/11/2026)

**Natureza:** registro da decisão do proprietário de 28/11/2026 ("Aprovo", sobre o texto proposto no chat). Altera `scripts/agent_entrypoint.py` (broker do START, somente leitura) e `tests/test_agent_entrypoint.py`. **Não** altera `agents/`, `AGENTS.md`, `PRODUCT.md`, `.claude/`, o esquema de comandos nem o `bootstrap.py`. O merge continua só por pedido dele, citando PR e head.

## Texto aprovado
1. **START:** o recibo do broker ganha, **só se o chamador apontar o clone do `entrada`** (`--entrada` ou `UFMS_ENTRADA_CLONE`; parâmetro `entrada` da classe), o campo `canal`: `parada_ativa`, `aguardando_resposta`, `a_conferir`, `aceitas`, `aceitas_mas_paradas` (id → código) e `recusadas` (id → código), lido por `canal_engenharia.estado()`. **Nunca** o texto das respostas. Sem o clone, o recibo é o de sempre (campo ausente). Falha ao ler vira `disponivel: false`; o START **não** cai.
2. **Rodada Tutor–Coach:** uma rodada **sintética**, sem dado real e sem gravar no `entrada`, com o Tutor e o Coach chamados como **subagentes reais** (somente leitura) a partir de um pacote fechado de `scripts/rodada_tutor_coach.py`; as saídas passam por `validar_saida` e `rodada`.

## Limites
- O resumo vem de um **clone local** do `entrada`, **sem prova do HEAD remoto**: serve de orientação, não de verdade. Resposta `PARADO` ou `RECUSADA` não é resultado (E49).
- O broker **não** garante que um orquestrador o use; não impede quem tem credencial direta (limite fundamental do `AGENTS.md`).
- A rodada sintética prova que o contrato de forma aceita saídas **de modelos reais**; **não** prova qualidade pedagógica nem uso com dado do aluno (estado E0, resultados pessoais desligados).
- Lista limitada a 100 ids por campo.

## Verificação
`tests/test_agent_entrypoint.py` (6 testes novos, `CanalNoStartTests`): recibo sem o campo quando não há clone; só ids e códigos (um segredo plantado numa resposta não aparece); hashes e lista obrigatória inalterados; clone ausente ou registro corrompido não derruba o START; parada ativa aparece e `write` segue bloqueado; limite de 100.
