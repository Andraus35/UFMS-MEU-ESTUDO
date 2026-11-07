# Índice pedagógico — UFMS MEU ESTUDO

**Versão de referência:** v1.8 + verificação GP-0/GP-1 — 04/11/2026  
**Estado do pacote:** especificação e evidências documentais; não equivale a tutor operacional, eficácia validada ou homologação de GP-1.  
**Escopo:** preparação adaptativa por questões para os cargos UFMS 523 e 324.

> **Regra de leitura:** este diretório é consultado sob demanda. O estado operacional atual está em `/ROADMAP.md`, `/memory/HANDOFF.md` e `/state/WORKFLOW.json`. Relatórios datados, handoffs antigos e prompts de transferência são snapshots históricos, não autoridade de execução.

## 1. Especificações metodológicas de referência

1. [Método de aprendizagem v1.0](METODO_v1.0.md): objetivos, princípios, modalidades de caderno e interação com plataformas.
2. [Protocolo de decisão v1.1](PROTOCOLO_DECISAO_v1.1.md): prioridades por assunto, concorrência entre cargos, camadas determinística e adaptativa.
3. [Modelo de evidências v1.2](MODELO_EVIDENCIAS_v1.2.md): resultados, incerteza, proveniência, retenção e comparação.
4. [Estratégia competitiva v1.3](ESTRATEGIA_COMPETITIVA_v1.3.md): dois cargos, riscos eliminatórios, matriz de prioridades, prova em dois turnos e cenários.
5. [Protocolo de simulados v1.4](PROTOCOLO_SIMULADOS_v1.4.md): composição, dois turnos, pontuação válida e comparabilidade.
6. [Avaliação da eficácia v1.4](AVALIACAO_EFICACIA_v1.4.md): sinais de aprendizagem, acompanhamento das recomendações e adaptação verificável.
7. [Fila dinâmica de aprendizagem v1.5](FILA_DINAMICA_v1.5.md): geração de candidatos, elegibilidade, reordenação, equilíbrio 523/324 e decisões justificadas.
8. [Cadernos e resultados v1.6](CADERNOS_RESULTADOS_v1.6.md): prescrições, filtros escalonados, devolução mínima, validação e feedback.
9. [Contrato integrado de prontidão v1.7](CONTRATO_PRONTIDAO_v1.7.md): arquitetura única de decisão, evidência, persistência e gates.
10. [Matriz de reconciliação v1.7](MATRIZ_RECONCILIACAO_v1.7.md): diferenças entre especificações e harness, bloqueadores e encaminhamentos.
11. [Plano técnico por gates v1.8](PLANO_IMPLEMENTACAO_GATES_v1.8.md): pacotes ENG-00–ENG-08, dependências, entregas e critérios de pronto.
12. [Rastreabilidade de testes v1.8](RASTREABILIDADE_GATES_v1.8.md): 102 cenários vinculados a GP-0..GP-5.

## 2. Evidências e relatórios históricos — consultar sob demanda

13. [Verificação parcial GP-0/GP-1](VERIFICACAO_GP0_GP1_2026-11-04.md): fontes UFMS/FAPEC, cronograma original, anomalias documentais e contratos técnicos no SHA observado.
14. [Cotejo dos específicos 523/324](COTEJO_ESPECIFICOS_523_324_2026-11-04.md): interseções textuais confirmadas no edital original e recortes não compartilháveis.
15. [Contraprovas de compartilhamento](CONTRAPROVAS_CADERNOS_523_324_2026-11-04.md): 13 verificações positivas/negativas e quatro cadernos-modelo, sem criar objetos reais.
16. [Reauditoria GP-0/GP-1, ciclo 3](REAUDITORIA_GP0_GP1_CICLO3_2026-11-04.md): mudanças verificadas no HEAD técnico, CI e pendências de fonte.
17. [Contrato de ingestão GP-1](CONTRATO_INGESTAO_GP1_2026-11-04.md): correspondência entre resultados, cadernos, eventos, tentativas e tempos.
18. [Fixtures sintéticas GP-1](FIXTURES_INGESTAO_GP1_2026-11-04.json): 14 casos de compatibilidade, sem dados pessoais.
19. [Execução isolada das fixtures GP-1](EXECUCAO_FIXTURES_GP1_2026-11-04.md): resultados dos 11 casos executáveis e três lacunas no ciclo registrado.
20. [Resultado estruturado da execução](RESULTADOS_EXECUCAO_GP1_2026-11-04.json): status por IGP, proveniência e limites.
21. [Contraprovas IGP-12–14, ciclo 6](CONTRAPROVAS_INGESTAO_GP1_CICLO6_2026-11-04.md): lacunas verificadas no código técnico observado e critérios de implementação.
22. [Contraprovas executadas IGP-12–14](EXECUCAO_NEGATIVA_GP1_CICLO7_2026-11-04.md): três lacunas reproduzidas e HEAD técnico do ciclo.
23. [Recibo de execução negativa](RESULTADOS_NEGATIVOS_GP1_CICLO7_2026-11-04.json): observações e hashes dos insumos.
24. [Referência isolada GP-1, ciclo 8](REFERENCIA_GP1_CICLO8_2026-11-04.md): protótipo local com 15 testes verdes e limites de integração.
25. [Recibo da referência GP-1](RECIBO_REFERENCIA_GP1_CICLO8_2026-11-04.json): hashes e contagens verificadas.

## 3. Critérios e continuidade documental

26. [Critérios de aceitação](CRITERIOS_DE_ACEITACAO.md): cenários documentados para implementação posterior.
27. [Protocolo START/DELIVERY](PROTOCOLO_ENTREGA_CONTINUIDADE.md): commit, readback e handoff a cada entrega relevante.
28. [Handoff pedagógico — histórico](HANDOFF.md): checkpoint do ciclo 8, 04/11/2026; não usar como handoff operacional atual.
29. [Prompt de transferência técnica v1.8 — histórico](PROMPT_TRANSFERENCIA_TECNICA_v1.8.md): pacote de planejamento antigo; PRs #1/#2 já foram integrados e instruções de estado devem ser revalidadas. **Substituído como porta de entrada de construção por `/PRODUCT.md` (raiz do repositório).**

## Hierarquia e limites

- O edital PROGEP/UFMS 152/2026 e retificações verificadas determinam conteúdo, requisitos e regras da prova; a pedagogia não pode reescrevê-los.
- Este pacote especifica comportamento pedagógico; não altera por si só scripts, permissões, conectores ou runtime.
- Um resultado do estudante é evidência observada, não domínio presumido. O tutor não inventa cadernos, IDs de questões, pontuações por subtópico ou acesso a contas privadas.
- Não há cronograma obrigatório, número fixo universal de questões, percentuais rígidos de domínio ou intervalos universais de revisão.
- Regras determinísticas devem impedir incoerência; a IA escolhe intervenções adaptativamente dentro dessas regras.
- A interação com TEC Concursos e Qconcursos depende de ações do estudante e dos dados legitimamente disponibilizados.
- Nenhuma gravação de resultados individuais foi habilitada; não declarar memória operacional testada.

## Autoridade operacional

Para trabalho ativo, começar por `AGENTS.md`, `ROADMAP.md`, `memory/HANDOFF.md` e `state/CURRENT.json`, respeitando `state/WORKFLOW.json`. Abrir este diretório apenas quando a tarefa exigir a regra pedagógica, evidência ou critério específico. Nenhum arquivo deste índice foi apagado ou movido nesta organização.
