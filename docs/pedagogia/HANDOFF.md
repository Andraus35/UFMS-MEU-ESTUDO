# Handoff da sessão de estratégia pedagógica — UFMS

**Data do checkpoint:** 04/11/2026 (America/Campo_Grande).  
**Natureza:** documentação pedagógica — **não** é motor adaptativo já em funcionamento.

## Identidade verificada no START desta entrega

- Repositório privado: `Andraus35/UFMS-MEU-ESTUDO`.
- PR pedagógico: [#2](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/2), branch `docs/especificacao-pedagogica-v1-2`, **aberto em draft, sem merge**.
- HEAD **anterior a este commit de protocolo**, efetivamente conferido: `3448c0650abb4378ee9a6268c3113e4008bc632c`.
- Frente independente de engenharia documental: [PR #1](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/1), também aberto e não mesclado no momento da consulta. **Seu HEAD muda independentemente; reconferir.**
- A identidade do commit que publica **este** checkpoint deve ser obtida por readback do branch/PR no GitHub; um arquivo não pode conter com segurança seu próprio futuro SHA.

## Estado pedagógico consolidado (propostas)

| Versão | Documento | Estado |
|---|---|---|
| v1.0 | [METODO_v1.0.md](METODO_v1.0.md) | Método de aprendizagem por questões, modalidades não rígidas |
| v1.1 | [PROTOCOLO_DECISAO_v1.1.md](PROTOCOLO_DECISAO_v1.1.md) | Invariantes determinísticos e decisão adaptativa |
| v1.2 | [MODELO_EVIDENCIAS_v1.2.md](MODELO_EVIDENCIAS_v1.2.md) | Resultados, incerteza, retenção e comparabilidade |
| v1.3 | [ESTRATEGIA_COMPETITIVA_v1.3.md](ESTRATEGIA_COMPETITIVA_v1.3.md) | Equilíbrio de cargos 523 e 324 e riscos |
| v1.4 | [PROTOCOLO_SIMULADOS_v1.4.md](PROTOCOLO_SIMULADOS_v1.4.md) | Simulados por cargo e ensaio combinado |
| v1.4 | [AVALIACAO_EFICACIA_v1.4.md](AVALIACAO_EFICACIA_v1.4.md) | Sinais de eficácia e custo de oportunidade |

- [CRITERIOS_DE_ACEITACAO.md](CRITERIOS_DE_ACEITACAO.md): **50 cenários documentados** (PED-01–20, COMP-01–12, SIM-01–10 e EFA-01–08), ainda **não executados como testes pedagógicos**.
- `docs/pedagogia/PROTOCOLO_ENTREGA_CONTINUIDADE.md`: regra START/DELIVERY instituída pelo estudante para cada entrega relevante.
- Os arquivos de regras do harness, scripts de decisão, integração TEC/Qconcursos e gravação de resultados são responsabilidade de implementação técnica futura; **não presumir ativação**.
- Este commit de governança não modifica o edital, a indexação ou código.

## Entrega desta vez

**Objetivo:** impedir perdas de contexto e afirmações não verificadas por meio de commit por entrega, atualização de handoff no mesmo commit e readback remoto antes de alegar sucesso.

**Arquivos previstos nesta transação:** `PROTOCOLO_ENTREGA_CONTINUIDADE.md`, `HANDOFF.md` e `README.md` da pasta pedagógica. Conferir no HEAD remoto após a publicação.

## Próxima frente pedagógica

**v1.5 — Fila dinâmica de aprendizagem**, integrando prioridades de conteúdos comuns e específicos, riscos eliminatórios, evidência E0–E4, revisões e recomendações de cadernos. **Sem** planograma fixo, sem implementação técnica nesta sessão a menos que solicitada e sem atualizar PR #1.

## Condições para retomar

1. Ler [README.md](README.md), [PROTOCOLO_ENTREGA_CONTINUIDADE.md](PROTOCOLO_ENTREGA_CONTINUIDADE.md) e este handoff.
2. Confirmar HEAD atual do PR #2; não confiar apenas no SHA acima, que é **anterior** à entrega atual.
3. Conferir artefatos e pendências; preparar **um commit novo** por entrega futura com este handoff atualizado.
4. Verificar CI quando aplicável; documentação versionada não é prova de eficácia pedagógica.
5. **Sem merge**, sem escrever dados de desempenho não autorizados e sem colisão com PR #1.
