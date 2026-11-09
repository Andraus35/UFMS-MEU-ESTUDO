# HANDOFF vigente — UFMS MEU ESTUDO

<!-- GOVERNANCE-CHECKPOINT:START -->
## Checkpoint vigente

- Repositório: Andraus35/UFMS-MEU-ESTUDO.
- Último merge comprovado: PR #76; SHA 8cde73a801cf2d5f70ea2d06949b422264549e03
- Frente ativa: **RM-09 / PR #77**; branch `ccr-69ece020-2w19at`; base main; fase review.
- Fonte operacional única: `state/WORKFLOW.json`.
- **Próxima tarefa: RM-08**; a entrega formal RM-08 continua bloqueada até os gates precedentes serem avaliados.
- CURRENT permanece E0, zero eventos/resultados; PROGRESS intocado.
- Persistência pessoal desabilitada; sem dados pessoais, credenciais, replay real ou integrações externas.
- Alterações por API GitHub; hooks locais não executados nesta sessão. A CI não substitui hooks locais.
<!-- GOVERNANCE-CHECKPOINT:END -->

## Ponto de retomada da próxima sessão

Não há prompt de retomada: o repositório se descreve. Rodar `python scripts/session_route.py --intent engineering --run` (rotas de estudo, escrita, governança e persistência: `--intent study|write|governance|persistence`, definidas em `config/session_routes.json`) e seguir o procedimento de `docs/especificacoes/README.md`, que diz o estado real do ciclo, o próximo item da fila `work_queue` de `state/WORKFLOW.json` e quando parar.

**Em uma frase:** as especificações S1 a S5, o validador de comandos (Ed25519 e HMAC, registro durável, filtro, montador de issue), o perfil `agents/ZAPIA.md` e o roteiro de validação da Zapia existem; **falta o proprietário montar a conta exclusiva da Zapia (D-19, D-20) e trazer os relatórios**, e provar na prática o que hoje é só autorrelato.

**Material pronto para o proprietário encaminhar** (tudo em `docs/governanca/PROMPTS_PRONTOS_ZAPIA_CONTA_NOVA_20261109.md`, conferido por `tests/test_zapia_prompts.py`): passos para montar a conta nova e o token, texto da instrução persistente, prompt de validação (V0, V1, V2, V7, V12), prompts de V11 e de V4 e V6, mensagem ao suporte do TEC e o comando de geração das chaves. O script `scripts/termux/verifica_token.sh` confere um token sem imprimi-lo.

**Ordem do que acontece a seguir (quando o insumo chegar):**
1. Relatório da validação da conta nova: conferir hashes e a autoria da escrita; registrar a rodada em `docs/governanca/` (resumo, sem dados pessoais), atualizar S4, S5 e este handoff em um PR novo.
2. Chaves públicas do Tutor e do Coach: registrar em `config/agent_public_keys.json` por PR.
3. Resposta do suporte do TEC: atualizar OPEN-11, OPEN-12 e a comparação das opções A a F da S4; só então considerar o V10.
4. Relatórios de V11, V4 e V6; depois V8, V9 e, se o WhatsApp voltar, V3 e V5.
5. Dados do plano de estudo (tópicos já estudados, prioridades): gerar o plano real com `scripts/study_plan.py` e o caderno diagnóstico (estudo segue em E0).
6. Pendências de engenharia sem insumo: guarda das chaves privadas (D-18), decisão sobre re-pinar o gateway do GQ-D, rotina validada de escrita para `registrar_*` (bloqueada pela política de dados pessoais).

**Cuidados desta fase:** o que se sabe da Zapia é autorrelato; a conta antiga não vale como evidência da nova; ao testar scripts de token neste ambiente, o proxy substitui credenciais (use só o computador do proprietário); o merge só ocorre por pedido explícito dele.

- **Já decidido:** `PRODUCT.md` (decisões D-01 a D-20).
- **Especificações:** S1 a S5 em `docs/especificacoes/` (método de estudo e revisão, Tutor, Coach, operação e harness da Zapia); a fila `work_queue` está completa quando todos os arquivos de entrega existem. O contrato de comandos dos agentes à Zapia (PR-013) tem esquema em `config/agent_command_schema.json` e validador offline em `scripts/agent_commands.py`, com testes de contraprova; **é referência de implementação, não prova que a Zapia o usa**.
- **Perfil da Zapia:** `agents/ZAPIA.md` (START explícito, papel de interface e executora, só comando válido, conteúdo externo como dado, negar por padrão, relato com prova), validado por `python scripts/agents_gate.py --check` contra as operações de Tutor e Coach e contra `config/agent_command_schema.json`. É texto de instrução, **não trava técnica**, e nunca foi lido por uma Zapia real.
- **Construído offline (RM-09):** geração local de chaves e assinatura (`scripts/agent_keys.py`); validador com Ed25519 e HMAC e registro durável de nonce e idempotência (`scripts/agent_commands.py`, `scripts/command_ledger.py`); montador de issue e comentário (`scripts/github_issue_payload.py`); filtro de conteúdo sensível em invólucro (`scripts/gateway_filter.py`; o `scripts/tool_gateway.py` tem SHA pinado no GQ-D e não foi alterado). Tudo isso é referência de implementação, **sem prova de uso obrigatório pela Zapia**.
- **Depende do proprietário, sem bloquear as especificações:** dados do plano (início, tempo diário, dia de descanso, cargo, tópicos já estudados, prioridades); planos no TEC e no Qconcursos e se exportam (OPEN-11); consulta ao suporte do TEC (OPEN-12); o canal e a verificação de origem dos comandos (OPEN-09; Tutor e Coach rodam no computador do proprietário, D-18); acesso direto do Tutor ao NotebookLM (OPEN-10; a Zapia nova usa conta Google só de estudos, D-20); token da Zapia nova (D-20; OPEN-02 se resolve com ele); repositório privado de dados (D-01); revisão humana dos requisitos que dependem de julgamento (S1-R3/R6/R9, S2-R1/R3/R7, S3-R3/R5/R7/R8, S5-R2/R4/R5/R6).
- **Não executado:** a conta exclusiva da Zapia (D-19, D-20) ainda não foi montada nem validada; testes T1 a T3 e V2 a V9 e V11 na conta nova; PR-012 com o Notebook; leitura em conta real das plataformas; persistência de resultados pessoais.
- **Rodadas da Zapia (conta antiga):** a 3 e a 4 estão em `docs/governanca/RESPOSTA_RODADA3_ZAPIA_20261109.md` e `docs/governanca/RESPOSTA_RODADA4_ZAPIA_20261109.md`. Observado e conferido: leitura por API com hashes corretos, validador com as 11 decisões esperadas e entrega de mensagem pelo app. Falhou: escrita de um comentário (permissão do token). Tudo o mais é autorrelato e **precisa ser repetido na conta nova**.
- **Limite de fonte:** o que se sabe da Zapia é autorrelato (rodadas de auditoria e adendo de 09/11/2026, este último não versionado); a memória dela não é fonte de estado, o repositório é.
- **Antes de escrever:** `python scripts/doc_cohesion.py --check` deve passar; ao mudar uma decisão, atualizar todos os documentos que a citam.

---

## Registro histórico
