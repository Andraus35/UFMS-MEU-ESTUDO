# Especificação pedagógica — UFMS MEU ESTUDO

**Versão de referência:** v1.3 — 04/11/2026  
**Estado:** PROPOSTA DOCUMENTAL; não equivale a implementação, aprovação do método ou operação autônoma do tutor.  
**Escopo:** preparação adaptativa por questões para os cargos UFMS 523 e 324.

## Documentos desta entrega

1. [Método de aprendizagem v1.0](METODO_v1.0.md): objetivos, princípios, modalidades de caderno e interação com plataformas.
2. [Protocolo de decisão v1.1](PROTOCOLO_DECISAO_v1.1.md): prioridades por assunto, concorrência entre cargos, camadas determinística e adaptativa.
3. [Modelo de evidências v1.2](MODELO_EVIDENCIAS_v1.2.md): resultados, incerteza, proveniência, retenção e comparação.
4. [Estratégia competitiva v1.3](ESTRATEGIA_COMPETITIVA_v1.3.md): dois cargos, riscos eliminatórios, matriz de prioridades, prova em dois turnos e cenários.
5. [Critérios de aceitação](CRITERIOS_DE_ACEITACAO.md): testes de cenário para implementação posterior.

## Hierarquia e limites

- O edital PROGEP/UFMS 152/2026 e retificações verificadas determinam conteúdo, requisitos e regras da prova; a pedagogia não pode reescrevê-los.
- O harness de engenharia, atualmente proposto no PR #1, é responsável por validação, persistência, estado e recuperação. Este pacote especifica **comportamento pedagógico**, não altera scripts nem permissões.
- Um resultado do estudante é evidência observada, não domínio presumido. O tutor jamais inventa cadernos, IDs de questões, pontuações por subtópico ou acesso às contas privadas.
- Sem cronograma obrigatório, número fixo universal de questões, percentuais rígidos de domínio ou intervalos universais de revisão.
- Regras determinísticas devem impedir incoerência; a IA deve escolher intervenções adaptativamente dentro dessas regras.
- A interação com TEC Concursos e Qconcursos depende de ações do estudante e dos dados legitimamente disponibilizados.
- Nenhuma gravação de resultados individuais foi habilitada nesta entrega; não declarar memória operacional testada.

## Para a sessão de implementação

Converter as seções e os critérios de aceitação em decisões rastreáveis, schemas, validações e testes sobre históricos fictícios **sem alterar o comportamento pedagógico por conveniência técnica**. Preservar AGENTS.md, rules, guardrails e o trabalho de chunks em PR próprio. Qualquer alteração estrutural deve passar por revisão humana. Não realizar merge automático.

**Proveniência:** formalização das decisões pedagógicas discutidas com o usuário nesta conversa. São propostas metodológicas, não resultados experimentais ou validação empírica da eficácia.
