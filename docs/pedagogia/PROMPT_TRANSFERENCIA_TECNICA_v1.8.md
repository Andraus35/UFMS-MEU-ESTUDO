# Prompt de transferência — implementação técnica do tutor UFMS v1.8

> **ARQUIVO HISTÓRICO — não executar literalmente.** PRs #1 e #2 foram integrados; o repositório é público. Reconsultar `AGENTS.md`, `ROADMAP.md`, `memory/HANDOFF.md` e `state/WORKFLOW.json` antes de qualquer trabalho. Este prompt preserva o planejamento de 04/11/2026, não autoriza ações atuais.

**Uso:** copiar para **outra sessão técnica autorizada**. Este prompt é um pacote de trabalho, não uma autorização tácita para alterar código, configurações, governança ou executar merge.  
**Visibilidade verificada posteriormente:** pública; `Andraus35/UFMS-MEU-ESTUDO`  
**PR da especificação:** [#2](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/2), branch `docs/especificacao-pedagogica-v1-2`  
**PR da engenharia de edital/harness:** [#1](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/1), branch `setup/harness-memory-v0-2`  
**Ponto de partida da transferência:** pacote `docs/pedagogia/` até v1.8, no **HEAD atual que deverá ser reconsultado**. Não confiar nos SHAs históricos citados em conversas e handoffs como atuais.

## Missão

Atue como agente de implementação técnica com foco em **engenharia de confiabilidade e interoperabilidade do tutor adaptativo**. Transforme as especificações pedagógicas aprovadas pelo estudante em contratos, testes e componentes executáveis, preservando as regras do edital e a integridade dos resultados.

**Início obrigatório (READ ONLY):**
1. Consultar os estados atuais de PR #1, PR #2 e main; confirmar SHAs, branches, status e arquivos relevantes.
2. Ler `docs/pedagogia/README.md`, `HANDOFF.md`, `CONTRATO_PRONTIDAO_v1.7.md`, `MATRIZ_RECONCILIACAO_v1.7.md`, `PLANO_IMPLEMENTACAO_GATES_v1.8.md` e `RASTREABILIDADE_GATES_v1.8.md` no mesmo SHA pedagógico.
3. Ler as instruções, validações e estado da **branch técnica atual**, verificando `AGENTS.md`, `settings.json`, regras, guardrails, índices e outros documentos exigidos.
4. Confrontar a matriz v1.7 com o código realmente presente: o PR #1 avançou após sua amostra. Não declarar pendência resolvida ou existente somente com base no documento histórico.
5. Separar requisitos normativos verificados, decisões pedagógicas, código já implementado, falhas reais e lacunas de integração.

## Plano de execução

Utilizar `PLANO_IMPLEMENTACAO_GATES_v1.8.md` como fila de dependências ENG-00–ENG-08, começando por **GP-0 e GP-1**. A cada mudança proposta:
- trabalhar em branch técnica própria ou fluxo aprovado, sem escrever no PR #2 nem colidir com o PR #1;
- preservar estado/eventos e compatibilidade; evitar rehash ou substituição silenciosa de histórico;
- construir testes adversariais junto com a implementação, usando os IDs dos **102 critérios** sem duplicar casos;
- registrar evidence de FAIL/PASS, SHA de execução, limitações e readback;
- atualizar os documentos estratégicos afetados e handoff na mesma entrega, de forma controlada;
- manter `personal_results_writes_enabled=false` até autorização humana e verificação dos gates;
- **não realizar merge sem instrução expressa**.

## Critérios técnicos essenciais

Eventos idempotentes; correções vinculadas; datas de evento distintas da tentativa; adaptador para convenções diferentes de relatórios; ausência de decomposição inventada; qualidade E0–E4 sem falsa medida de domínio; fila reproduzível por snapshot/as_of/política; decisão explicável; estados distintos de recomendação, confirmação e execução; filtros de plataforma condicionais; não duplicação de tentativas entre cargos; sorteio ponderado opcional e reproduzível.

**Não** automatizar acesso a contas privadas de questões sem consentimento e interface autorizada. Usar fixtures fictícias até haver permissões e estrutura de privacidade demonstradas.

## Saída da primeira entrega técnica

Fornecer um **diagnóstico objetivo de GP-0/GP-1 no HEAD atual**, com:
1. SHAs verificados;
2. incompatibilidades reproduzidas e reconciliações já existentes;
3. backlog técnico desduplicado com dependências;
4. testes que falham hoje e os que comprovadamente passam;
5. proposta de correção isolada com PR/branch, sem merge e sem permissões ampliadas;
6. checkpoint com o próximo passo e bloqueios.

Somente depois disso avançar para componentes do motor GP-2, suas provas GP-3 e o ciclo GP-4. Não confundir CI verde, critérios escritos e eficácia real.

## Delimitação das sessões

Esta sessão de planejamento mantém o método, a estratégia e os critérios de aceitação. A outra sessão cuida de código e integração técnica. Se uma lacuna exigir decisão pedagógica, apresentar a pergunta objetiva à sessão de planejamento em vez de inventar nova política.

**Proibição expressa:** não aprovar gate, ligar escrita pessoal, rebasear PR #1, mesclar PRs ou proclamar tutor operacional sem evidências e autorização correspondentes.
