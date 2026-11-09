# HANDOFF vigente — UFMS MEU ESTUDO

<!-- GOVERNANCE-CHECKPOINT:START -->
## Checkpoint vigente

- Repositório: Andraus35/UFMS-MEU-ESTUDO.
- Último merge comprovado: PR #72; SHA 738947924e465d56744dbf27b5acda90d0eeb23e
- Frente ativa: **RM-09 / PR #73**; branch `ccr-69ece020-2w19at`; base main; fase review.
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
- **Próxima tarefa de construção (RM-09, offline e sem conta real; começa em novo PR draft, depois de registrar o recibo do último merge com `record_merge_receipt.py`):** assinatura gerada por código local fora do modelo; filtro de conteúdo pessoal também no gateway; registro durável de nonce e idempotência. Depois, o protocolo de teste T1 a T3 e PR-012 para o proprietário autorizar (inclui verificar se a Zapia segue o perfil). Parar no pedido de merge ao proprietário.
- **Depende do proprietário, sem bloquear as especificações:** dados do plano (início, tempo diário, dia de descanso, cargo, tópicos já estudados, prioridades); planos no TEC e no Qconcursos e se exportam (OPEN-11); consulta ao suporte do TEC (OPEN-12); onde Tutor e Coach rodam (OPEN-09); acesso ao NotebookLM (OPEN-10); token da Zapia restrito a este repositório (OPEN-02); repositório privado de dados (D-01); revisão humana dos requisitos que dependem de julgamento (S1-R3/R6/R9, S2-R1/R3/R7, S3-R3/R5/R7/R8, S5-R2/R4/R5/R6).
- **Não executado:** leitura do perfil por uma Zapia real, testes T1 a T3 da Zapia (exigem autorização literal), prova de assinatura do lado da Zapia, PR-012 com o Notebook, leitura em conta real das plataformas, persistência de resultados pessoais.
- **Limite de fonte:** o que se sabe da Zapia é autorrelato (rodadas de auditoria e adendo de 09/11/2026, este último não versionado); a memória dela não é fonte de estado, o repositório é.
- **Antes de escrever:** `python scripts/doc_cohesion.py --check` deve passar; ao mudar uma decisão, atualizar todos os documentos que a citam.

---

## Registro histórico
