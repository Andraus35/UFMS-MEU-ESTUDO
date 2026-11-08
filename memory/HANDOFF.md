# HANDOFF vigente — UFMS MEU ESTUDO

<!-- GOVERNANCE-CHECKPOINT:START -->
## Checkpoint vigente

- Repositório: Andraus35/UFMS-MEU-ESTUDO.
- Último merge comprovado: PR #71; SHA 2440a82cd4d0c66abf7170c32ad4470a8ff4effa
- Frente ativa: **RM-09 / PR #72**; branch `ccr-69ece020-2w19at`; base main; fase review.
- Fonte operacional única: `state/WORKFLOW.json`.
- **Próxima tarefa: RM-08**; a entrega formal RM-08 continua bloqueada até os gates precedentes serem avaliados.
- CURRENT permanece E0, zero eventos/resultados; PROGRESS intocado.
- Persistência pessoal desabilitada; sem dados pessoais, credenciais, replay real ou integrações externas.
- Alterações por API GitHub; hooks locais não executados nesta sessão. A CI não substitui hooks locais.
<!-- GOVERNANCE-CHECKPOINT:END -->

## Ponto de retomada da próxima sessão

Não há prompt de retomada: o repositório se descreve. Rodar `python scripts/session_route.py --intent engineering --run` (rotas de estudo, escrita, governança e persistência: `--intent study|write|governance|persistence`, definidas em `config/session_routes.json`) e seguir o procedimento de `docs/especificacoes/README.md`, que diz o estado real do ciclo, o próximo item da fila `work_queue` de `state/WORKFLOW.json` e quando parar.

- **Já decidido:** `PRODUCT.md` (decisões D-01 a D-16).
- **Depende do proprietário, sem bloquear as especificações:** dados do plano (início, tempo diário, dia de descanso, cargo, tópicos já estudados, prioridades); planos no TEC e no Qconcursos e se exportam; consulta ao suporte do TEC (OPEN-12); onde Tutor e Coach rodam (OPEN-09); token da Zapia restrito a este repositório (OPEN-02); repositório privado de dados (D-01).
- **Não executado:** testes T1 a T3 da Zapia (exigem autorização literal), leitura em conta real das plataformas, persistência de resultados pessoais.
- **Antes de escrever:** `python scripts/doc_cohesion.py --check` deve passar; ao mudar uma decisão, atualizar todos os documentos que a citam.

---

## Registro histórico
