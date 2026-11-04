# Handoff da sessão de estratégia pedagógica — UFMS

**Checkpoint:** 04/11/2026, fuso America/Campo_Grande.  
**Status:** pacote pedagógico de transferência à engenharia v1.8 documentado; não significa tutor implementado.

## START desta entrega (objetos consultados)

- Repositório: `Andraus35/UFMS-MEU-ESTUDO`.
- PR pedagógico [#2](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/2), branch `docs/especificacao-pedagogica-v1-2`, aberto em draft e não mesclado.
- HEAD **anterior** à entrega: `7c4c346426ffadc73deb535eb772701422b3c93b`. O SHA novo deve ser obtido pelo readback do PR/commit; este documento não pode incluir seu próprio SHA futuro.
- PR técnico [#1](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/1), aberto e não mesclado no início. HEAD observado: `4317103ab91fae43c7e07cf5527d6ecbcc5681d7`, sujeito a alterações posteriores.
- A matriz de reconciliação v1.7 baseou-se em HEAD técnico histórico `18a81bacd6163e6d510e58c00f2a55e77051b3ca`; **não** considerar essa fotografia como estado atual.
- Sem merge, sem alteração da main ou do PR #1 nesta entrega.

## Especificação consolidada

- v1.0 [Método](METODO_v1.0.md); v1.1 [Decisão](PROTOCOLO_DECISAO_v1.1.md); v1.2 [Evidências](MODELO_EVIDENCIAS_v1.2.md); v1.3 [Competitiva](ESTRATEGIA_COMPETITIVA_v1.3.md).
- v1.4 [Simulados](PROTOCOLO_SIMULADOS_v1.4.md) e [Eficácia](AVALIACAO_EFICACIA_v1.4.md).
- v1.5 [Fila](FILA_DINAMICA_v1.5.md); v1.6 [Cadernos/resultados](CADERNOS_RESULTADOS_v1.6.md).
- v1.7 [Contrato](CONTRATO_PRONTIDAO_v1.7.md) e [Reconciliação](MATRIZ_RECONCILIACAO_v1.7.md).
- **v1.8 [Plano de implementação](PLANO_IMPLEMENTACAO_GATES_v1.8.md), [Rastreabilidade](RASTREABILIDADE_GATES_v1.8.md) e [Prompt técnico](PROMPT_TRANSFERENCIA_TECNICA_v1.8.md).**
- [CRITERIOS_DE_ACEITACAO.md](CRITERIOS_DE_ACEITACAO.md): **102 cenários documentados**, não executados como suíte pedagógica; GP-0..GP-5 ainda não homologados.

## Entrega deste commit

Acrescentar os três documentos v1.8, atualizar README e este handoff **no mesmo commit**, mantendo `CRITERIOS_DE_ACEITACAO.md` sem novos casos (o pacote mapeia casos existentes para evitar duplicações).

**Evidência pendente até readback:** confirmar o SHA final, os cinco blobs e a situação de CI. Não interpretar uma simples lista de requisitos como testes executados.

## Estado e bloqueios

- As decisões pedagógicas estão documentadas, mas o motor operacional não foi demonstrado.
- Escopo normativo/retificações: requer conferência oficial antes de uso final (GP-0).
- Mapeamento técnico de IDs, datas, estados, convenções e permissão de escrita: GP-1 pendente.
- GP-2 e GP-3: motor e suíte adversarial por implementar/verificar; GP-4/5: ciclo/piloto não realizados.
- Não habilitar gravação pessoal, criar contas, acessar bancos privados por scraping ou concluir merge por inferência.

## Próximo passo

**Outra sessão técnica:** seguir [PROMPT_TRANSFERENCIA_TECNICA_v1.8.md](PROMPT_TRANSFERENCIA_TECNICA_v1.8.md), ler HEADs atuais, auditar GP-0/GP-1 e decidir proposta de implementação isolada.

**Esta sessão pedagógica:** evitar proliferar novos métodos sem evidência. Revisar decisões de implementação somente se surgirem divergências concretas e começar estudos por questões com devoluções humanas quando operacionalmente autorizadas.

## Retomada

Consultar o HEAD atual do PR #2 e o índice pedagógico, este handoff e o protocolo START/DELIVERY no mesmo SHA. Cada nova entrega substantiva mantém commit próprio + atualização de handoff + readback. Não misturar trabalho pedagógico com edição técnica do PR #1 e não realizar merge sem ordem expressa.
