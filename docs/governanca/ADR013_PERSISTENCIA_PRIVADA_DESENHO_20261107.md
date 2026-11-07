# ADR-013 — Persistência privada de resultados pessoais (desenho, sem implementação)

**Data:** 07/11/2026 · **Estado:** decisão de desenho aprovada pelo proprietário; **implementação e habilitação NÃO autorizadas**.
**Relaciona:** RM-08 (critérios 5–7 da baseline), RM-10, ADR-004, ADR-009, `docs/pedagogia/RM08_BASELINE_FORMAL_20261107.md`.

## Decisão

Resultados pessoais de estudo, quando habilitados, serão gravados em um **repositório GitHub privado, separado** deste repositório público. Este repositório (`UFMS-MEU-ESTUDO`, público) continua sem dados pessoais: `state/events/`, `state/CURRENT.json` e `state/PROGRESS.csv` permanecem projeções sintéticas/vazias e `settings.json` mantém `personal_results_writes_enabled=false`.

Este ADR **não altera** `settings.json`, regras ou guardrails e **não habilita** nenhuma gravação. Habilitar exige PR próprio, aprovação humana expressa (rules §5 e §14) e os gates abaixo.

## O que pode e o que não pode ser persistido

- **Pode (no repositório privado):** eventos append-only no schema já validado (`validate_attempt_events`), com `event_id`, data, caderno/recomendação relacionados, convenção de contagem e totais por tópico quando informados.
- **Nunca (nem no privado):** CPF e documentos, credenciais e tokens, exports brutos da plataforma, capturas de tela, texto de questões, comentários de professores.
- **Nunca no público:** qualquer resultado individual, mesmo agregado, enquanto o repositório for público.

## Controles obrigatórios (critérios de entrada para implementar)

| # | Controle | Prova exigida |
|---|---|---|
| P1 | **Visibilidade verificada a cada escrita:** leitura autenticada do repositório de destino com `private=true` imediatamente antes de gravar; qualquer outro valor, erro ou leitura indisponível bloqueia. | teste negativo: público, 404, 403, timeout e resposta malformada → nenhuma escrita |
| P2 | **Destino fixo:** o escritor só aceita o repositório privado configurado; nunca o repositório público. | teste negativo: alvo = repositório público → recusa |
| P3 | **Consentimento explícito e versionado** (data, escopo, versão do texto) gravado antes do primeiro evento; ausência ou revogação bloqueia. | teste negativo: sem consentimento / revogado → recusa |
| P4 | **Token fora do LLM:** a gravação roda em host/cliente confiável com credencial segregada e `UFMS_ENABLE_GITHUB_WRITE=1` (ADR-009); o modelo não recebe o token. | revisão do desenho de implantação; sem token em logs/prompt |
| P5 | **Idempotência e concorrência:** `event_id` único, escrita condicional por HEAD esperado (CAS), sem force-push. | testes de duplicidade, 409 e HEAD divergente |
| P6 | **Readback:** após cada escrita, confirmar SHA do commit e conteúdo; sem readback, a escrita é tratada como pendente. | teste de readback divergente → pendente, não "confirmado" |
| P7 | **Replay/recuperação:** reconstrução determinística de `CURRENT`/`PROGRESS` a partir dos eventos privados, em nova sessão. | teste de rebuild idempotente e de interrupção parcial |
| P8 | **Revogação:** procedimento documentado para suspender novas gravações e apagar dados. | ver limite abaixo |
| P9 | **Privacidade negativa geral:** corrupção, divergência de identidade ou resultado inconsistente não geram persistência nem efeito externo. | testes adversariais |

## Limites e riscos conhecidos

- **Histórico Git é permanente:** apagar um arquivo não remove o dado dos commits. Revogação efetiva de dados já gravados exige **apagar o repositório privado** (ou reescrever o histórico), o que é irreversível. Por isso a minimização (não gravar o desnecessário) vale mais que a revogação.
- **Plano GitHub:** proteção de branch e rulesets em repositório privado dependem do plano; não assumir. Verificar por readback antes de confiar.
- **Acesso do app Claude:** incluir o repositório privado na instalação do app só quando houver implementação aprovada, com a menor permissão possível. Nesta etapa **o app não deve ter acesso ao repositório privado**.
- **CI não prova privacidade:** a CI do repositório público valida código e testes sintéticos; não comprova a visibilidade nem os controles do repositório privado.
- **Interface Zapia/Telegram** não está implantada; este desenho não depende dela.

## Decisões do proprietário (07/11/2026)

1. **Repositório privado de dados:** `Andraus35/ufms-meu-estudo-dados`, criado como **privado desde o início**. A criação é ato administrativo do proprietário; **ainda não foi criado** (nem verificado) por este ADR.
2. **Escritor (P4), revisado em 07/11/2026:** a **Zapia grava desde o início, pela API REST do GitHub com credencial própria dela** (decisão D-02 do `PRODUCT.md`; não há conector nem MCP de GitHub, segundo o autorrelato de 07/11/2026). Isso **substitui** a decisão anterior, de que o proprietário gravaria manualmente pelo Termux. Condições mantidas: controles P1 a P9, flag `false` até PR próprio com aprovação humana, e resolução de OPEN-01 e OPEN-02 do `PRODUCT.md`. A Zapia informou que **não há trava técnica** para P1 nem para a confirmação antes de escrever (só protocolo), e que o escopo do token atual não foi verificado; por isso o PR-003 está bloqueado até a credencial de escopo único (PR-010). Agentes construtores continuam sem credencial de escrita pessoal.
3. **Retenção e revogação:** dados mantidos **até a prova (17/01/2027) mais 30 dias** (janela curta definida pelo proprietário em 07/11/2026), e a **revogação efetiva é apagar o repositório privado inteiro** (o histórico Git é permanente; apagar arquivo não basta). Sem reescrita de histórico.
4. **Backup:** não decidido; por padrão, **sem backup externo** do dado pessoal.

## Ainda em aberto

- **Criação do repositório privado** pelo proprietário e verificação de `private=true` por leitura autenticada.
- **Registro formal do consentimento** (data, versão e escopo) no repositório privado, antes do primeiro evento (P3). A aprovação do texto abaixo não grava consentimento: ela só fixa a versão.

## Texto de consentimento v1 (APROVADO pelo proprietário em 07/11/2026, sem ajustes)

> Autorizo o registro, no repositório privado `ufms-meu-estudo-dados`, dos resultados dos meus cadernos e simulados de estudo (data, caderno relacionado, convenção de contagem e totais por tópico quando eu informar), exclusivamente para orientar meus estudos para os cargos UFMS 523 e 324. Não autorizo registrar CPF, documentos, credenciais, exports brutos, capturas de tela nem texto de questões. Os dados serão mantidos até 17/01/2027 mais 30 dias, e posso revogar este consentimento a qualquer momento, o que suspende novas gravações e leva ao apagamento do repositório privado. Versão: v1.

## Próximos passos (cada um em PR próprio, em série)

1. (Depende da criação do repositório privado) Fixtures e contraprovas P1–P3 e P5–P6. **Parcial (07/11/2026):** `scripts/private_persistence_guard.py` e `tests/test_private_persistence_guard.py` cobrem esses controles com leitor de visibilidade injetado (fakes), sem rede e sem gravar. **Falta** a prova contra um repositório privado real de teste, que depende da criação desse repositório pelo proprietário.
2. Escritor (P4): reaproveitar `scripts/api_write_transaction.py` e `scripts/api_write_guard.py` onde servirem ao fluxo do conector da Zapia (depende de OPEN-01 e OPEN-02).
3. Decisão separada de habilitação (flag), com aprovação humana.

RM-08 formal permanece `bloqueado`. Este ADR é desenho, não homologação de GP-4.
