# Protocolo START/DELIVERY e continuidade pedagógica

<!-- governance-current:start -->
**Situação vigente (readback autenticado):** main 676dd5d3259c66ba97c3e7e3338451cfc4e5cd68; PRs mesclados: #1, #2, #6, #7, #8; fechados sem merge: #3, #4, #10. O texto original a seguir é histórico quando mencionar PRs antigos; rever o estado atual antes de cada operação. PRs #1/#2 foram mesclados; nenhum motor Tutor/Coach é homologado por essa mudança documental. Consultar [docs/governanca/STATUS_VIGENTE.md](../governanca/STATUS_VIGENTE.md).
<!-- governance-current:end -->

**Status:** regra operacional de trabalho solicitada pelo estudante em 04/11/2026. **Aplicação:** entregas substantivas desta sessão sobre estratégia de estudos, registradas no PR pedagógico #2. Não é um hook automático executado pelo ChatGPT, e não substitui instruções de maior prioridade.

## Objetivo

Evitar perda de contexto, falsa memória, repetição, deriva da estratégia e declarações de êxito sem evidência. O repositório é a fonte de verdade versionada para entregas **realmente confirmadas**; a conversa é o ambiente de elaboração.

## START obrigatório antes de toda nova entrega

1. Consultar o [índice pedagógico](README.md) e o [handoff atual](HANDOFF.md) do mesmo commit.
2. Reconferir via GitHub o estado **atual** do PR #2, branch, HEAD e base. Nunca reutilizar SHA de um resumo como prova de atualidade.
3. Verificar quais versões v1.0–v1.4 (e posteriores) já estão gravadas. Não sobrescrever nem criar duplicações sem justificar.
4. Considerar o PR #1 como frente técnica independente de edital/chunks/harness; não incorporar suas mudanças tacitamente nem editar arquivos fora da pasta pedagógica sem autorização de escopo.
5. Verificar o que já foi **especificado** versus **implementado** versus **testado em cenário** versus **testado com resultados reais**.
6. Identificar próxima pendência objetiva, dependências e critérios de aceitação. O handoff não substitui a leitura da fonte pertinente.

## DELIVERY obrigatório para cada entrega substantiva

- Consolidar os artefatos pedagógicos completos, com título, versão, data, objetivo, status, fontes e limitações.
- Acrescentar critérios de aceitação quando houver nova decisão, hipótese ou comportamento a implementar.
- Atualizar o [handoff](HANDOFF.md) **no mesmo commit** com estado conhecido, arquivos alterados, decisões, pendências, próxima ação, limites e a identidade do commit **anterior** que foi verificado no início.
- Criar **um novo commit por entrega** na branch pedagógica apropriada. Não misturar entregas independentes, não fazer commits vazios para simular progresso.
- Atualizar o ref de forma condicional usando HEAD esperado; se houver divergência, parar, reler e reconciliar antes de repetir a escrita. Não usar force push para contornar conflito.
- Executar validação apropriada para o que foi alterado: checar existência, integridade, links/consistência documental; executar testes/CI só quando existirem e forem aplicáveis. **Não chamar documentação aprovada de motor implementado.**
- Fazer **readback remoto** após o commit: confirmar PR aberto, HEAD exato, arquivos e novo conteúdo, registrar SHA e situação real da CI.
- Responder ao estudante com link do commit/PR, caminho dos artefatos, evidências verificadas e pendências. Se a escrita ou o readback falhar, comunicar a falha e **não afirmar que o commit aconteceu**.

## Política de contexto e anti-alucinação

- Toda afirmação de versão, arquivo, status de PR, testes, CI, integração, merge e persistência deve ser baseada em observação verificável **do HEAD atual**, ou identificada como informação histórica/informada pelo estudante.
- Não afirmar que o agente leu todos os arquivos ou implementou funções que apenas descreveu.
- Não afirmar teste real de aprendizagem quando somente há critérios de teste documentados.
- Não inferir desempenho, conhecimentos, tempo disponível ou outras condições do estudante quando não informados.
- Não inventar links, bibliografia normativa, gabaritos, cadernos, quantidades disponíveis ou percentuais de domínio.
- Preferir handoffs concisos, com referências por arquivo, a resumos enormes que aumentem custo de contexto.
- Persistir marcos e decisões do projeto; não copiar a íntegra das conversas nem informação pessoal desnecessária.
- Se a sessão não tiver acesso ou capacidade de escrita, produzir um patch/artefato pendente e explicitar que **não foi persistido**.
- Não realizar merge sem autorização humana expressa; o PR #1 não deve ser perturbado.

## Formato mínimo do handoff

| Campo | Conteúdo esperado |
|---|---|
| Identidade do objeto | Repositório, PR, branch, commit anterior lido |
| Entrega | Versão, objetivo, arquivos realmente confirmados |
| Evidências | O que foi validado, com limitação da verificação |
| Estado | Documentado / implementado / testado / pendente |
| Próxima ação | Uma próxima frente concreta, sem abrir escopo |
| Guardrails | Sem merge, sem dados inventados, sem colisão com PR #1 |

**Limite de garantia:** essas regras são um compromisso operacional instruído ao agente que as consulta. O documento isolado não obriga automaticamente toda futura instância de IA a ler, gravar ou executar hooks. A existência de commit confirma apenas conteúdo versionado, não elimina o risco de alucinação.
