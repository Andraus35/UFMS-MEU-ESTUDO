# E51: como Tutor, Coach e orquestrador trocam informação, e o que "síncrono" pode significar aqui (28/11/2026)

**Natureza:** plano com pesquisa e **esquema offline e sintético** da rodada (`scripts/rodada_tutor_coach.py`, `tests/test_rodada_tutor_coach.py`). Não é contrato e **nada foi implantado**. Decisões do proprietário de 28/11/2026: modelo **orquestrador único + Tutor e Coach como subagentes em fases fixas, mensagens de esquema fechado**; lote próprio depois do merge do #212; **sem dado real** até a janela do piloto.

## 1. O que o repositório já decide
- **Papéis:** o Tutor produz conteúdo e plano; o Coach cuida de rotina, estatísticas e motivação, **não executa ferramentas, não grava no repositório e não lê plataforma**: emite comandos à Zapia (agents/COACH.md). A Zapia é só interface e executora (S5).
- **Troca já especificada:** Tutor → Coach pelo **plano de estudos** (JSON); Coach → Tutor pelo **pedido de ajuste** quando a divergência é pedagógica (S3-R6); registro de passagem de **esquema fechado** e roteamento (`scripts/tutor_coach_handoff.py`, GD-1, S13-R3); ciclo offline sintético (`scripts/tutor_coach_offline_cycle.py`).
- **RM-08 (ciclo Tutor–Coach com resultado real) está bloqueado** por atos do proprietário (piloto com resultado consentido, janela, reauditoria). Dado real do estudante **não** entra no repositório (flag de resultados pessoais `false`).
- **Onde rodam:** sessões efêmeras do Claude; estado só em repositório (S15).

## 2. Pesquisa (28/11/2026; A = página oficial lida, B = resumo de busca, C = preprint ou opinião)
- **B:** [Como a Anthropic construiu o sistema multiagente de pesquisa](https://www.anthropic.com/engineering/multi-agent-research-system): padrão **orquestrador–operários**; subagentes sem instruções claras duplicam trabalho (cada delegação precisa de objetivo, formato de saída, ferramentas e limites); custo de ~15× tokens de um chat; domínios em que todos os agentes precisam do **mesmo contexto** ou têm muitas dependências **não são boa escolha**. (Resumos secundários dizem que operários não conversam entre si; não verifiquei no texto.)
- **B:** [Cognition, "Don't build multi-agents"](https://cognition.ai/blog/dont-build-multi-agents) e a atualização de abril de 2026: ações carregam decisões implícitas, agentes em paralelo não veem as suposições uns dos outros; padrão: **um agente linear que escreve**, outros só **leem e aconselham** (a atualização diz que a visão vale para enxames que **escrevem em paralelo**).
- **A:** [Agent teams do Claude Code](https://code.claude.com/docs/en/agent-teams): **experimental e desligado por padrão** (variável `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`); subagentes **reportam ao agente principal**; colegas de equipe compartilham lista de tarefas e **mensagem direta**.
- **B/C:** [A2A, streaming e tarefas assíncronas](https://a2aproject.github.io/A2A/topics/streaming-and-async): tarefas longas por notificação (push) ou consulta; o protocolo **não** garante entrega nem idempotência (deixa para o implementador). Preprints de quadro compartilhado ([blackboard](https://arxiv.org/pdf/2507.01701), mutações validadas de estado compartilhado, escalonador determinístico em vez de ativação oportunista): convergem em **estado compartilhado validado + ordem de fases determinística**, evidência de **um benchmark**, não prática estabelecida.
- **Do projeto:** E49 e E50 (canal e despertar), E43 (a Zapia não calcula hash), S22 (relógio só acorda).
- **Lacunas:** nenhuma medida de custo ou latência neste projeto; agent teams não foram lidos além da página inicial nem testados; evidência de multiagente em **educação** não foi pesquisada.

## 3. "Síncrono" aqui: o que é possível e o que é desejável
| Trecho | Natureza real | Conclusão |
|---|---|---|
| Orquestrador ⇄ Tutor ou Coach **dentro de uma sessão** | **síncrono** (subagente devolve resultado no mesmo turno) | **sim**, é o modo recomendado |
| Tutor ⇄ Coach **diretamente** (conversa livre) | agent teams, **experimental**, não determinístico, custo alto, difícil de auditar | **não** em produção; só experimento isolado |
| Qualquer agente ⇄ TEC, Notebook, estudante | **assíncrono** por natureza (passa pela Zapia, minutos) | canal do E49, com despertar do E50 |
| Entre sessões diferentes | **assíncrono** pelo repositório | estado persistido + cursor por agente (feito) |

Ou seja: **conversa síncrona entre papéis é um turno do orquestrador**, não um chat livre; o que não cabe numa sessão vira mensagem persistida.

## 4. Desenho recomendado ("rodada")
1. Um **orquestrador único** (única escrita). Tutor e Coach são **papéis chamados como subagentes** com **pacote de entrada fechado**: objetivo, dados autorizados (referências, nunca texto de questão nem resultado pessoal), formato de saída e limites.
2. **Fases em ordem fixa, escalonador determinístico:** (a) ler o estado (`canal_engenharia.py --proximo`, plano, registro de passagem), (b) Tutor decide e devolve **plano ou pedido de API** (JSON), (c) Coach devolve **organização, lembretes, pedido de ajuste ao Tutor** (JSON), (d) o orquestrador **valida** os dois (`tutor_coach_handoff.validar_registro`), (e) grava **uma** rodada e emite pedidos à Zapia pelo canal.
3. **A mensagem entre papéis é o registro de passagem de esquema fechado** que já existe; **nada de texto livre longo**; resposta de API (TEC, Notebook) é **dado não confiável** que o orquestrador resume em campos fixos.
4. **Rodada = arquivo** (`rodada-NNNN.json`: entradas por hash, saídas dos dois papéis, vereditos, ids de pedidos emitidos), idempotente e reexecutável.
5. **Quem acorda a rodada:** a rotina do E50 (issue `RESP`) ou o relógio (S22); a sessão acordada **só abre o START e roda a rodada**.

## 5. O que dá para fazer **agora** (sem dado real, sem credencial nova)
- Esquema da **rodada** e do **pacote de entrada** com testes e contraprovas (sintético), reaproveitando `tutor_coach_handoff.py`.
- Consumo por agente já existe; falta ligar ao START do broker (PR de contrato).
- **Não fazer:** agent teams em produção; texto livre entre papéis; Coach lendo plataforma; qualquer resultado pessoal no repositório (RM-08).

## 6. Decisões do proprietário (28/11/2026)
1. **Aprovado:** orquestrador + subagentes em fases, mensagens de esquema fechado (em vez de conversa livre).
2. **Aprovado:** abrir lote próprio depois do merge do #212 (feito: #212 mesclado `2063064`, CI da main verde).
3. **Aprovado:** continuar **sem dado real**; rodada sintética até a janela do piloto.
4. Experimento com agent teams (flag experimental): **não escolhido**; **não recomendado** agora.

## 7. O que o código desta etapa faz e o que NÃO faz
- `montar_pacote` (entrada fechada, hash, o Coach só roda com o hash da saída do Tutor), `validar_saida` (tipos por papel, texto curto e limpo, pedido de API só da lista do canal e **do papel**: o Coach não pede Notebook), `rodada` (registro reexecutável com hash, pedidos do canal `eng-NNNN` em ordem Tutor→Coach). Testes com contraprovas.
- **Não faz:** chamar subagentes (isso é do orquestrador na sessão), gravar no `entrada`, usar dado real, ligar ao START ou ao despertar (E50). O START do broker incluir o estado do canal continua PR próprio de contrato.
- **Não provado:** que os subagentes reais devolvam saídas que passem no esquema, custo e latência de uma rodada completa, e qualquer ganho pedagógico (ver RM-08).
