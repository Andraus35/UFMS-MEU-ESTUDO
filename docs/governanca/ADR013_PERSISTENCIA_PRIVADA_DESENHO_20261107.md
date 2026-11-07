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

## Decisões em aberto (do proprietário)

1. Nome e criação do repositório privado de dados (a criação é ato administrativo seu).
2. Quem opera o escritor confiável (host/cliente) e onde guarda a credencial.
3. Texto e versão do consentimento.
4. Política de retenção e de backup dos dados.

## Próximos passos (cada um em PR próprio, em série)

1. Fixtures e contraprovas P1–P3 e P5–P6 contra um repositório de teste **sintético e privado**.
2. Escritor confiável (P4) reaproveitando `scripts/api_write_transaction.py` e `scripts/api_write_guard.py`.
3. Decisão separada de habilitação (flag), com aprovação humana.

RM-08 formal permanece `bloqueado`. Este ADR é desenho, não homologação de GP-4.
