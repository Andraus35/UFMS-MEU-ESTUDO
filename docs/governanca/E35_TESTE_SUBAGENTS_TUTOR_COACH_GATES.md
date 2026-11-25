# E35: teste dos subagents Tutor e Coach pelos gates da caixa (lote 2, ZAPIA-SUBAGENTS)

**Natureza:** registro e **harness offline**. Sem Zapia, sem `entrada`, sem rede, sem escrita. Nada aqui liga flag, cria hook ou grava resultado pessoal.

## O que foi entregue

- `scripts/subagent_harness.py`: recebe uma **proposta de comando** (JSON de um subagent ou cenário fixo; o texto é **dado não confiável**, nunca executado) e a passa por `command_box.validar`, que reúne esquema, tabela de operações por origem, destino, janela, chave e nonce, filtro de dado pessoal, URL e instrução embutida, validador do prompt do Notebook, `agendar_rotina` e idempotência. Monta a **matriz** de recusas por etapa.
- `tests/test_subagent_harness.py`: contraprovas (com mutações) e propostas ruins.
- CLI: `python scripts/subagent_harness.py --matriz` e `--propostas arquivo.json` (avalia propostas reais de subagent, sem eco do conteúdo).

## Matriz (cenários sintéticos, relógio e contexto fixos)

**21 de 21 cenários batem com o esperado.** Positivos devem ser promovidos; contraprovas devem ser recusadas **na etapa e com o código** indicados.

| Cenário | Perfil | Operação | Tipo | Resultado | Etapa | Código |
|---|---|---|---|---|---|---|
| T-OK-MSG | tutor | `enviar_mensagem` | positivo | PROMOVER | idempotencia | `OK` |
| T-OK-LER | tutor | `ler_arquivo_repositorio` | positivo | PROMOVER | idempotencia | `OK` |
| T-OK-NOTEBOOK | tutor | `enviar_prompt_notebook` | positivo | PROMOVER | idempotencia | `OK` |
| C-OK-MSG | coach | `enviar_mensagem` | positivo | PROMOVER | idempotencia | `OK` |
| C-OK-LEMBRETE | coach | `criar_lembrete` | positivo | PROMOVER | idempotencia | `OK` |
| X-TUTOR-OP-DO-COACH | tutor | `criar_lembrete` | contraprova | DENIED | operacao | `OPERACAO_FORA_DA_TABELA_DA_ORIGEM` |
| X-COACH-OP-DO-TUTOR | coach | `enviar_prompt_notebook` | contraprova | DENIED | operacao | `OPERACAO_FORA_DA_TABELA_DA_ORIGEM` |
| X-ORIGEM-FORJADA | tutor | `enviar_mensagem` | contraprova | DENIED | origem | `ORIGEM_DESCONHECIDA` |
| X-REGISTRAR-RESULTADO | tutor | `registrar_resultado` | contraprova | DENIED | operacao | `REGISTRAR_FORA_DA_CAIXA` |
| X-REGISTRAR-ACOMPANHAMENTO | coach | `registrar_acompanhamento` | contraprova | DENIED | operacao | `REGISTRAR_FORA_DA_CAIXA` |
| X-OPERACAO-INVENTADA | tutor | `apagar_tudo` | contraprova | DENIED | operacao | `OPERACAO_FORA_DA_LISTA` |
| X-DESTINO-ERRADO | tutor | `enviar_mensagem` | contraprova | DENIED | destino | `DESTINO_NAO_DESIGNADO` |
| X-ASSINATURA-FORJADA | tutor | `enviar_mensagem` | contraprova | DENIED | campos | `CAMPOS_FORA_DO_ESQUEMA` |
| X-VERSAO-VELHA | tutor | `enviar_mensagem` | contraprova | DENIED | campos | `VERSAO_DESCONHECIDA` |
| X-COMANDO-VELHO | tutor | `enviar_mensagem` | contraprova | DENIED | chaves | `FORA_DA_JANELA` |
| X-CHAVE-INVALIDA | tutor | `enviar_mensagem` | contraprova | DENIED | chaves | `CHAVE_IDEMPOTENCIA_INVALIDA` |
| X-NONCE-INVALIDO | tutor | `enviar_mensagem` | contraprova | DENIED | chaves | `NONCE_INVALIDO` |
| X-URL-NO-TEXTO | tutor | `enviar_mensagem` | contraprova | DENIED | parametros | `PARAMS_URL` |
| X-LER-FORA-DA-LISTA | tutor | `ler_arquivo_repositorio` | contraprova | DENIED | parametros | `PARAMS_CAMINHO_INVALIDO` |
| X-LEMBRETE-SEM-HASH | coach | `criar_lembrete` | contraprova | DENIED | parametros | `PARAMS_CAMPO_OBRIGATORIO_AUSENTE` |
| X-PROMPT-NOTEBOOK-LIVRE | tutor | `enviar_prompt_notebook` | contraprova | DENIED | parametros | `PROMPT_PARAMS_FORA_DO_CONTRATO` |

Recusas por etapa: `operacao` (5), `origem` (1), `destino` (1), `campos` (2), `chaves` (3), `parametros` (4). Estado: nonce repetido vira `NONCE_REPETIDO` e repetição idêntica vira `DUPLICADO` (teste com ledger).

## O que NÃO é gateável por código (não vira "enforçado")

- compreensão semântica do START (bootstrap confere bytes e hash, não entendimento do modelo)
- instrução embutida em prosa sem URL nem marca de instrução (o filtro é heurístico; o texto do comando é dado)
- qualidade pedagógica e verdade do conteúdo da mensagem
- origem real do comando na nuvem (S6-R7: a origem é só informativa; a defesa é o escopo dos tokens)
- que a Zapia execute só o que a caixa promoveu (autorrelato; recibo e escopo do token)

## O que este lote ainda NÃO cobre

- **Subagents reais (LLM):** o harness aceita as propostas, mas **nenhum subagent foi executado** nesta entrega. Criar os dois subagents somente leitura exige pedido expresso do proprietário; as propostas viriam em `--propostas` e passariam pelos mesmos gates.
- **Outros gates**, que têm testes próprios e **não** passam por este harness: `agents_gate` (perfis), `promotion_gate` e `registrar_*` (flag falsa), `delivery_gate`, `delivery_receipt_binding` e `start_receipt`, `delivery_eval` e `audit_sample`, `session_read_guard` e `projection_generator`, `platform_read_guard`, `gates_mot`. A matriz completa operação × gate do E33 fica para uma segunda rodada deste lote.
- **Prova real:** o fluxo promovendo, a campainha e o hook de Gmail só no lote 3 (`ZAPIA-LIGAR`), na janela do piloto.

## Registro lateral: reinstalação do fluxo no `entrada` (25/11/2026)

Por pedido do proprietário ("faça você mesmo"), a sessão gravou **só** `.github/workflows/promover.yml` no `entrada` (commit `079e694`), gerado do modelo no SHA `a4f8084` (hash do fluxo `0b08e17b5bbe700a653fb9fed4b4fb3d6d0c93df77a6960f240ebeb1b465897d`; blob conferido por leitura de volta). **Pendente, ato do proprietário:** a variável do repositório `FLUXO_SHA256` precisa receber esse hash (a sessão não tem ferramenta para variáveis); sem ela o passo de conferência do fluxo **falha fechado**. A flag do fluxo segue falsa; nada é promovido.
