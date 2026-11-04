# Handoff da sessão de estratégia pedagógica — UFMS

**Checkpoint documental:** 04/11/2026, fuso America/Campo_Grande.  
**Estado:** v1.6 PROPOSTA DE ESPECIFICAÇÃO. **Não** representa motor em produção, integração automática com TEC/Qconcursos ou resultados reais.

## Objeto confirmado no START

- Repositório: `Andraus35/UFMS-MEU-ESTUDO` (privado na consulta).
- PR pedagógico: [#2](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/2), branch `docs/especificacao-pedagogica-v1-2`, aberto em draft e não mesclado.
- HEAD verificado **anterior a esta entrega**: `8cdafc8e5c3840a061016edb3a966acd6a6eb840`. Confirmar o novo HEAD por leitura do GitHub após commit; ele não pode ser inscrito no próprio commit que o cria.
- PR independente de engenharia do edital: [#1](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/1), aberto e não mesclado na consulta. Não houve edição do PR #1 nesta entrega.
- `main` não alterada; sem merge.

## Acervo pedagógico versionado

| Versão | Documento | Escopo |
|---|---|---|
| v1.0 | [METODO_v1.0.md](METODO_v1.0.md) | Modalidades de aprendizagem por questões |
| v1.1 | [PROTOCOLO_DECISAO_v1.1.md](PROTOCOLO_DECISAO_v1.1.md) | Regras determinísticas e decisão adaptativa |
| v1.2 | [MODELO_EVIDENCIAS_v1.2.md](MODELO_EVIDENCIAS_v1.2.md) | Dados, incerteza, retenção e comparabilidade |
| v1.3 | [ESTRATEGIA_COMPETITIVA_v1.3.md](ESTRATEGIA_COMPETITIVA_v1.3.md) | Equilíbrio de cargos 523 e 324 |
| v1.4 | [PROTOCOLO_SIMULADOS_v1.4.md](PROTOCOLO_SIMULADOS_v1.4.md) | Simulados por cargo e combinados |
| v1.4 | [AVALIACAO_EFICACIA_v1.4.md](AVALIACAO_EFICACIA_v1.4.md) | Reavaliação de recomendações e eficácia |
| v1.5 | [FILA_DINAMICA_v1.5.md](FILA_DINAMICA_v1.5.md) | Fila sem calendário e prioridade multicritério |
| **v1.6** | [CADERNOS_RESULTADOS_v1.6.md](CADERNOS_RESULTADOS_v1.6.md) | Prescrição prática e devolução de evidências |

- [CRITERIOS_DE_ACEITACAO.md](CRITERIOS_DE_ACEITACAO.md): **86 cenários documentados**, ainda não executados (PED 20, COMP 12, SIM 10, EFA 8, FIQ 18, CDO 18).
- [PROTOCOLO_ENTREGA_CONTINUIDADE.md](PROTOCOLO_ENTREGA_CONTINUIDADE.md): exige readback remoto, commit por entrega e handoff.
- Edital e retificações verificadas têm primazia. Funcionalidades e exportações de plataformas são condicionais; nesta entrega não se verificou suporte específico de TEC/Qconcursos.

## Entrega v1.6

**Objeto:** estabelecer contrato da recomendação, filtros escalonados, modo de execução, confirmação de criação, máquina de estados de caderno, dados mínimos de retorno, integridade, proveniência, feedback e reapriorização.

**Arquivos previstos no mesmo commit:** `CADERNOS_RESULTADOS_v1.6.md` (novo), `CRITERIOS_DE_ACEITACAO.md`, `README.md`, `HANDOFF.md`. Após a publicação, conferir os quatro arquivos no SHA exato.

**Limitações:** nenhum importador de CSV real, conexão autorizada, teste pedagógico executável ou gravação de resultados pessoais foi criado nesta frente. A CI, se existir, mede apenas o que efetivamente executar.

## Próxima frente objetiva

**v1.7 — Prontidão pedagógica para implementação**: reconciliar todos os contratos v1.0–v1.6, resolver contradições entre especificações, separar invariantes automáticos de hipóteses do agente, definir gates para testes fictícios e piloto com resultados consentidos. Não iniciar implementação nesta sessão sem mudança explícita de escopo.

## Condições de retomada

1. Reabrir PR #2, conferir HEAD e ler `README.md`, este handoff, `PROTOCOLO_ENTREGA_CONTINUIDADE.md` e o documento v1.6 no mesmo SHA.
2. Um commit por entrega substantiva com handoff no mesmo commit, seguido de readback.
3. Sem merge, sem colisão com PR #1 e sem dados pessoais inventados ou armazenados sem autorização.
4. Nunca confundir especificação, implementação, validação com cenários ou validação empírica.
