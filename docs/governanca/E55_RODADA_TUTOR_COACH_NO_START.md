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

## Rodada sintética com subagentes reais (28/11/2026, `Explore`, somente leitura, uma execução cada)
- **Tutor:** pacote `b1a86437…`; saída `plano` com resumo de 111 caracteres e duas `refs`; **aceita** por `validar_saida`. O resumo cita revisões em 7, 15 e 30 dias (padrão do `AGENTS.md`).
- **Coach:** pacote `9488c047…` com o hash da saída do Tutor (`41370184…`); a saída **crua foi RECUSADA com `REFS`**: o subagente acrescentou a referência `tutor_sha256:<64 hex>` (77 caracteres, acima do limite de 64). **O contrato de forma funcionou como previsto.**
- **Correção minha, não do modelo:** removi só essa referência extra para montar o registro (`rodada-0001`, hash `63197a2c…`). O registro foi montado **só para esta verificação** e **não foi gravado** no `entrada` nem no repositório. Com isso, `viu_tutor_sha256` do Coach igualou o hash da saída do Tutor e nenhum pedido de API foi emitido.
- **Leitura honesta:** são duas chamadas, sem repetição; **não** prova estabilidade do formato nem qualidade pedagógica. A saída crua do Coach mostra que um subagente real tende a "ajudar" com campos que o esquema não pede; a recusa em código é o que protege.
