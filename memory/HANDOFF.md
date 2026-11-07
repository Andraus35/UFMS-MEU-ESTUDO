# HANDOFF vigente — UFMS MEU ESTUDO

<!-- GOVERNANCE-CHECKPOINT:START -->
## Checkpoint vigente

- Repositório: Andraus35/UFMS-MEU-ESTUDO.
- Último merge comprovado: PR #68; SHA 9fb61864d463b9ca0dcb30fc47406fe1446a192d
- Frente ativa: **RM-09 / PR #69**; branch `feat/rm09-pesquisa-obrigatoria-spec-20261107`; base main; fase review.
- Fonte operacional única: `state/WORKFLOW.json`.
- **Próxima tarefa: RM-10**; a entrega formal RM-08 continua bloqueada até os gates precedentes serem avaliados.
- CURRENT permanece E0, zero eventos/resultados; PROGRESS intocado.
- Persistência pessoal desabilitada; sem dados pessoais, credenciais, replay real ou integrações externas.
- Alterações por API GitHub; hooks locais não executados nesta sessão. A CI não substitui hooks locais.
<!-- GOVERNANCE-CHECKPOINT:END -->

## Ponto de retomada da próxima sessão

1. **Conferir o estado:** `python scripts/bootstrap.py --mode engineering` (inclui `scripts/doc_cohesion.py`) e `python scripts/single_flow_gate.py --check`; depois confirmar no GitHub o PR indicado em `state/WORKFLOW.json`, sua CI e o merge.
2. **Já decidido (`PRODUCT.md`):** agentes Tutor e Coach (D-12), plano 4.2 com revisão 7, 15 e 30 (D-11), especificações enxutas S1 a S4 (D-13) com pesquisa obrigatória de estado da arte, benchmarks em repositórios e sites de estudo para concursos (D-16, `docs/especificacoes/README.md`), acesso direto às plataformas como primeira opção (D-14) e escolha do mecanismo só depois de testar todas as possibilidades (D-15).
3. **Próximo trabalho útil:** especificações S1 a S4, uma por vez, começando pela S1; na S4, executar os testes das opções A a F de `docs/PLATFORMS.md` (a pesquisa de cada especificação é obrigatória e entra na seção `## Pesquisa`).
4. **Depende do proprietário:** dados do plano (início, tempo diário, dia de descanso, cargo, tópicos já estudados, prioridades); planos no TEC e no Qconcursos e se há exportação; consulta ao suporte do TEC (OPEN-12); onde Tutor e Coach rodam (OPEN-09); token da Zapia restrito a este repositório (OPEN-02); repositório privado de dados (D-01).
5. **Não executado:** testes T1 a T3 da Zapia (exigem autorização literal), leitura em conta real das plataformas, persistência de resultados pessoais.
6. **Antes de escrever:** `python scripts/doc_cohesion.py --check` deve passar; ao mudar uma decisão, atualizar todos os documentos que a citam (o script acusa os que sobrarem).

---

## Registro histórico
