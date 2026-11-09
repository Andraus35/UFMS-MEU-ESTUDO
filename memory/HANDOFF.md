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

- **Já decidido:** `PRODUCT.md` (decisões D-01 a D-17).
- **Especificações:** S1 a S5 em `docs/especificacoes/` (método de estudo e revisão, Tutor, Coach, operação e harness da Zapia); a fila `work_queue` está completa quando todos os arquivos de entrega existem. O contrato de comandos dos agentes à Zapia (PR-013) tem esquema em `config/agent_command_schema.json` e validador offline em `scripts/agent_commands.py`, com testes de contraprova; **é referência de implementação, não prova que a Zapia o usa**.
- **Perfil da Zapia:** `agents/ZAPIA.md` (START explícito, papel de interface e executora, só comando válido, conteúdo externo como dado, negar por padrão, relato com prova), validado por `python scripts/agents_gate.py --check` contra as operações de Tutor e Coach e contra `config/agent_command_schema.json`. É texto de instrução, **não trava técnica**, e nunca foi lido por uma Zapia real.
- **Próxima tarefa de construção (RM-09, offline e sem conta real; começa em novo PR draft, depois de registrar o recibo do último merge com `record_merge_receipt.py`):** a geração local de chaves e a assinatura já existem em `scripts/agent_keys.py`; falta o proprietário gerar o par de cada agente, registrar só a pública em `config/agent_public_keys.json` por PR e guardar a privada no computador dele, em arquivo 0600 (D-18); o validador já verifica Ed25519 e HMAC, com registro durável de nonce e idempotência em `scripts/command_ledger.py`); rotina validada de escrita no GitHub para os comandos `registrar_*` (para issue e comentário já existe `scripts/github_issue_payload.py`); o filtro de conteúdo pessoal já está no validador (`scripts/agent_commands.py`) e em `scripts/gateway_filter.py`, invólucro que recusa parâmetros sensíveis antes de o `scripts/tool_gateway.py` ver o token (o gateway tem SHA pinado no GQ-D e não foi alterado; só protege quem chamar pelo invólucro). Depois, o protocolo de teste T1 a T3 e PR-012 para o proprietário autorizar (inclui verificar se a Zapia segue o perfil). Parar no pedido de merge ao proprietário.
- **Depende do proprietário, sem bloquear as especificações:** dados do plano (início, tempo diário, dia de descanso, cargo, tópicos já estudados, prioridades); planos no TEC e no Qconcursos e se exportam (OPEN-11); consulta ao suporte do TEC (OPEN-12); o canal e a verificação de origem dos comandos (OPEN-09; Tutor e Coach rodam no computador do proprietário, D-18); acesso ao NotebookLM (OPEN-10); token da Zapia restrito a este repositório (OPEN-02); repositório privado de dados (D-01); revisão humana dos requisitos que dependem de julgamento (S1-R3/R6/R9, S2-R1/R3/R7, S3-R3/R5/R7/R8, S5-R2/R4/R5/R6).
- **Não executado:** leitura do perfil por uma Zapia real, testes T1 a T3 da Zapia (exigem autorização literal), prova de assinatura do lado da Zapia, PR-012 com o Notebook, leitura em conta real das plataformas, persistência de resultados pessoais.
- **Rodada 3 da Zapia:** respondida (`docs/governanca/RESPOSTA_RODADA3_ZAPIA_20261109.md`); decisões que dela decorrem e ainda faltam implementar: rotina validada para escrita no GitHub e orquestrador que imponha o START (a verificação Ed25519 já existe no validador). Autorrelato; Q26 a Q30 e a Parte 2 não foram executadas.
- **Rodada 4 da Zapia:** V1 observado e conferido (11 decisões do validador coincidem) e V7 falhou por permissão do token (`docs/governanca/RESPOSTA_RODADA4_ZAPIA_20261109.md`); V2 a V6, V8, V9 e V11 aguardam autorização literal, V10 aguarda a resposta do suporte do TEC. O proprietário precisa conferir no GitHub o tipo, o repositório, as permissões e a validade do token da Zapia (OPEN-02).
- **Conta exclusiva da Zapia (D-19, D-20), checklist de configuração:** (1) criar a conta Zapia nova e uma conta Google nova só de estudos; (2) criar no GitHub um token fine-grained só deste repositório (Contents: leitura; Issues: leitura e escrita; validade de 30 dias), conferi-lo com `verifica_token.sh` no Termux e cadastrá-lo pelo formulário seguro da Zapia; (3) colar na conta nova a instrução persistente curta do perfil, sem memória pessoal e sem hooks ou jobs de fora do projeto; (4) conectar somente o app como canal; (5) repetir V0, V1, V2 e V7 do roteiro da rodada 4 na conta nova e trazer o relatório; (6) depois, revogar o token do projeto na conta antiga. Nada disso foi feito ainda.
- **Limite de fonte:** o que se sabe da Zapia é autorrelato (rodadas de auditoria e adendo de 09/11/2026, este último não versionado); a memória dela não é fonte de estado, o repositório é.
- **Antes de escrever:** `python scripts/doc_cohesion.py --check` deve passar; ao mudar uma decisão, atualizar todos os documentos que a citam.

---

## Registro histórico
