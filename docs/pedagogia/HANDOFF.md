# Handoff da sessão de estratégia pedagógica — UFMS

**Checkpoint:** 04/11/2026, fuso America/Campo_Grande.  
**Natureza:** especificação pedagógica consolidada v1.7; **não** motor de estudo implementado.

## Identidade da entrega / START verificado

- Repositório: Andraus35/UFMS-MEU-ESTUDO.
- PR pedagógico: [#2](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/2), branch docs/especificacao-pedagogica-v1-2, aberto em draft e não mesclado no início.
- HEAD exato **anterior** a esta entrega: b640eb595273f322fbb1c614f8ae1bf4a853828e; conferir o novo commit no readback remoto do PR.
- PR de engenharia independente: [#1](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/1), aberto em draft na leitura. Amostra técnica usada nesta revisão: 18a81bacd6163e6d510e58c00f2a55e77051b3ca — **não presumir que ainda seja HEAD**.
- Nenhum merge ou modificação de main/PR #1 autorizada por esta entrega.

## Inventário de documentação pedagógica

- v1.0 — [METODO_v1.0.md](METODO_v1.0.md): métodos e modalidades de caderno.
- v1.1 — [PROTOCOLO_DECISAO_v1.1.md](PROTOCOLO_DECISAO_v1.1.md): regras determinísticas e avaliação adaptativa.
- v1.2 — [MODELO_EVIDENCIAS_v1.2.md](MODELO_EVIDENCIAS_v1.2.md): qualidade E0–E4, comparabilidade, retenção.
- v1.3 — [ESTRATEGIA_COMPETITIVA_v1.3.md](ESTRATEGIA_COMPETITIVA_v1.3.md): duas provas e riscos.
- v1.4 — [PROTOCOLO_SIMULADOS_v1.4.md](PROTOCOLO_SIMULADOS_v1.4.md) e [AVALIACAO_EFICACIA_v1.4.md](AVALIACAO_EFICACIA_v1.4.md): simulados e avaliação de recomendações.
- v1.5 — [FILA_DINAMICA_v1.5.md](FILA_DINAMICA_v1.5.md): shortlist adaptativa, eventos e reordenação.
- v1.6 — [CADERNOS_RESULTADOS_v1.6.md](CADERNOS_RESULTADOS_v1.6.md): recomendação, filtros, retorno, validação e feedback.
- **v1.7 — [CONTRATO_PRONTIDAO_v1.7.md](CONTRATO_PRONTIDAO_v1.7.md) e [MATRIZ_RECONCILIACAO_v1.7.md](MATRIZ_RECONCILIACAO_v1.7.md): contrato integrado, 16 pontos de integração, gates GP-0..GP-5.**
- [CRITERIOS_DE_ACEITACAO.md](CRITERIOS_DE_ACEITACAO.md): **102 cenários textuais** (PED 20 + COMP 12 + SIM 10 + EFA 8 + FIQ 18 + CDO 18 + PRD 16). **Não são 102 testes executados**.

## Entrega prevista neste commit

- Criar contrato v1.7 com fronteiras entre fonte, evidência, recomendação e evento, pipeline de decisão, invariantes e gates.
- Criar matriz de compatibilidade baseada na amostra técnica citada; registrar REC-01..REC-16, com ações para a sessão de implementação.
- Acrescentar PRD-01..PRD-16 ao catálogo de cenários.
- Atualizar README e este handoff no **mesmo commit**.

**Verificação pós-commit obrigatória:** conferir HEAD do PR #2, readback dos cinco arquivos e execução de CI se houver. Este arquivo traz HEAD anterior porque não pode afirmar o SHA futuro de seu próprio commit.

## Pendências e próxima frente

- **GP-0:** validar versão vigente do edital/retificações relevantes antes de operar regras normativas.
- **GP-1:** reconciliar contratos de ID, datas, normalização de relatórios, estados e privacidade.
- **GP-2:** implementar motor da fila e evidências; **GP-3:** executar cenários adversariais.
- **GP-4/GP-5:** testar ciclo real autorizado e validar uso/piloto somente após segurança e consentimento.
- A escrita de resultados pessoais continua bloqueada no settings.json técnico observado.
- **Próxima entrega indicada:** plano de transferência pedagógica à engenharia, priorizado por gates e sem abrir merge; alternadamente, iniciar estudo real por cadernos apenas em fluxo separado e autorizado.

## Retomada anti-alucinação

1. Conferir SHA atual do PR #2, ler [README.md](README.md), [PROTOCOLO_ENTREGA_CONTINUIDADE.md](PROTOCOLO_ENTREGA_CONTINUIDADE.md), este arquivo e documentos v1.7 no mesmo commit.
2. A cada entrega substantiva, criar commit e atualizar handoff; reler remotamente antes de declarar sucesso.
3. Não tocar PR #1 nesta sessão, não inventar dados de estudo, não presumir funcionalidades de plataformas nem aprovação de CI.
4. Não fazer merge sem autorização humana expressa; documentação não é software funcional.
