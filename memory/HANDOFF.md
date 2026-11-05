# HANDOFF vigente — UFMS MEU ESTUDO

**Data:** 05/11/2026. Conferir SHA e estado remoto no GitHub antes de toda operação. Este resumo indica a próxima tarefa; não substitui validação do commit/CI.

## Estado

- **Fonte da verdade:** `Andraus35/UFMS-MEU-ESTUDO`; a `main` estava em `676dd5d3259c66ba97c3e7e3338451cfc4e5cd68` na leitura inicial, protegida pelo check `validate`. A reforma SIM está no **PR #9 draft**, ainda não mesclada.
- **Privacidade:** repositório **público**; nunca armazenar desempenho individual, CPF, relatórios reais ou credenciais. A flag `personal_results_writes_enabled` continua `false`.
- **Estudo:** cargos 523 (manhã) e 324 (tarde), prova prevista 17/01/2027, sujeito a retificações oficiais. `state/CURRENT.json` informa 0 eventos e 0 resultados no estado inicial; reler sempre no HEAD atual.
- **Edital:** transcrição integral, manifesto, índices e 81 chunks preservados; consultar somente os recortes pertinentes. A página 13 contém divergência cronológica a acompanhar. Não substituir edital original silenciosamente.
- **Integrações:** Tutor/Coach podem recomendar livremente, mas não afirmar Zapia/agenda/Oracle/Gemini operacionais sem testes E2E. PR #5 tem especificação não homologada.

## Como retomar — sequência fixa

1. Ler `AGENTS.md`, `ROADMAP.md` (especialmente fila **SIM**), este `memory/HANDOFF.md` e `state/CURRENT.json` do **mesmo HEAD**. Recuperar outros arquivos apenas conforme a tarefa.
2. **Próximo: SIM-01 — ALTA, em andamento.** Verificar visibilidade pública atual e rejeição de dados pessoais (incluindo tentativa de liberar a flag). Reconciliar documentos com estado real; executar testes negativos e CI.
3. Continuar **SIM-02** (cadeia de escrita por API PR #13→#17→#18 e ACK perdido) e **SIM-03** (monitorar FAPEC/UFMS e alerta do edital) antes das médias.
4. **SIM-04 a SIM-08 — MEDIA:** consolidar PRs sem perder funcionalidades, validar START de quatro arquivos (SIM-05 candidata já neste PR), higienizar handoff, separar cognição de efeitos e eliminar gates duplicados com testes.
5. **SIM-09/10 — BAIXA:** inventariar branches e documentos antigos; registrar riscos aceitos sem interromper o estudo.

## Regras de entrega e rastreabilidade

- Para ALTA/MEDIA: identificar causa, correção, contraprovas negativas reais, regressão, HEAD/CI e riscos remanescentes. Uma referência a teste não demonstra que ele foi executado. Não promover status antes de comprovação.
- Evitar novo PR de saneamento enquanto **PR #9** puder acomodar mudanças. Cadeias empilhadas #9→#14→#15 e #13→#17→#18 precisam ser reconciliadas, não mescladas às cegas; PR #12 pode estar incorporado em #14, mas não deve ser descartado sem verificar equivalência final.
- Não mesclar nem deletar branches por inferência; manter `main` sem alterações até a integração explicitamente autorizada. Atualizar o topo deste handoff a cada nova entrega, preservando histórico no arquivo de referência.

## Histórico preservado

O conteúdo anterior completo (sem apagamentos) está em `memory/HANDOFF_ARCHIVE_2026-11-05.md`. Decisões em `memory/DECISIONS.md`; prova independente e detalhes históricos devem ser buscados apenas sob demanda.
