# Handoff da sessão de estratégia pedagógica — UFMS

**Checkpoint:** 04/11/2026, fuso America/Campo_Grande.  
**Estado da entrega:** especificação pedagógica v1.5 redigida para commit no PR #2. O SHA desta transação deve ser obtido por readback remoto — **não pode constar do próprio arquivo antes de sua criação**.

## Identidade observada no START

- Repositório privado: `Andraus35/UFMS-MEU-ESTUDO`.
- PR pedagógico: [#2](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/2), branch `docs/especificacao-pedagogica-v1-2`, aberto em draft e não mesclado na consulta.
- HEAD **antes** desta entrega: `5d98b6f2a043193ae552e12759030deded2bbf01`.
- Frente independente do edital/harness: [PR #1](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/1), aberto e não mesclado na consulta. Seu HEAD muda independentemente; reconsultar.
- A `main` não é atualizada por esta transação. Sem merge.

## Documentação pedagógica disponível

| Versão | Caminho | Estado |
|---|---|---|
| v1.0 | [METODO_v1.0.md](METODO_v1.0.md) | Princípios e modalidades de aprendizagem por questões: proposta |
| v1.1 | [PROTOCOLO_DECISAO_v1.1.md](PROTOCOLO_DECISAO_v1.1.md) | Regras determinísticas e decisões adaptativas: proposta |
| v1.2 | [MODELO_EVIDENCIAS_v1.2.md](MODELO_EVIDENCIAS_v1.2.md) | Resultados, incerteza e retenção: proposta |
| v1.3 | [ESTRATEGIA_COMPETITIVA_v1.3.md](ESTRATEGIA_COMPETITIVA_v1.3.md) | Equilíbrio 523/324: proposta |
| v1.4 | [PROTOCOLO_SIMULADOS_v1.4.md](PROTOCOLO_SIMULADOS_v1.4.md) | Simulados e ensaio em dois turnos: proposta |
| v1.4 | [AVALIACAO_EFICACIA_v1.4.md](AVALIACAO_EFICACIA_v1.4.md) | Avaliação de recomendações: proposta |
| **v1.5** | [FILA_DINAMICA_v1.5.md](FILA_DINAMICA_v1.5.md) | Geração, priorização e reordenação da fila: proposta desta entrega |

- [CRITERIOS_DE_ACEITACAO.md](CRITERIOS_DE_ACEITACAO.md): **68 cenários documentados** (PED 20 + COMP 12 + SIM 10 + EFA 8 + FIQ 18). Não confundir com 68 testes executados.
- [PROTOCOLO_ENTREGA_CONTINUIDADE.md](PROTOCOLO_ENTREGA_CONTINUIDADE.md): regra de commit + handoff por entrega substantiva, readback e verificação do HEAD.
- Não há motor adaptativo, probabilidade calibrada, integração automática com TEC/Qconcursos ou habilitação de gravação de resultados nesta entrega. Nenhum desempenho individual foi incorporado.

## Alterações previstas neste commit

- Novo `FILA_DINAMICA_v1.5.md`: modelo lógico da fila, estados de elegibilidade, geração de candidatas, filtros determinísticos, comparação multicritério, desempate, reordenação, reproducibilidade, exemplos.
- `CRITERIOS_DE_ACEITACAO.md`: acrescentar FIQ-01–18.
- `README.md`: versão de referência v1.5 e entrada no índice.
- `HANDOFF.md`: este ponto de retomada.

**Verificação necessária após commit:** HEAD do PR #2, blobs dos quatro arquivos, conteúdo e estado da CI. Arquivos nesta seção são declarados como previstos até readback confirmado. Não alegar que motores ou testes pedagógicos foram implementados.

## Próxima frente objetiva

**v1.6 — Protocolo operacional do caderno e devolução de resultados**: como transformar uma decisão da fila em instruções aplicáveis no TEC/Qconcursos, receber dados de granularidade variada, detectar disponibilidade insuficiente e fazer um feedback enxuto ao estudante, sem scraping ou acesso presumido.

## Regras de retomada

1. Ler [README.md](README.md), [PROTOCOLO_ENTREGA_CONTINUIDADE.md](PROTOCOLO_ENTREGA_CONTINUIDADE.md), este handoff e o documento v1.5 a partir do mesmo HEAD confirmado.
2. Reconsultar PR #2 para identificar o SHA atual antes de qualquer escrita; não reutilizar o SHA anterior deste arquivo como estado vigente.
3. Trabalhar apenas em `docs/pedagogia/`, com commit por entrega, checkpoint no mesmo commit e readback.
4. Proteger PR #1; não alterar seus chunks do edital nem scripts.
5. Não mesclar sem autorização humana, não criar dados do aluno e não afirmar implementação só porque a documentação está versionada.
