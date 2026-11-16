# HANDOFF vigente — UFMS MEU ESTUDO

<!-- GOVERNANCE-CHECKPOINT:START -->
## Checkpoint vigente

- Repositório: Andraus35/UFMS-MEU-ESTUDO.
- Último merge comprovado: PR #92; SHA 85dbf66ade955fa6fd9dfad8c48be533d11f5b68
- Frente ativa: **RM-09 / PR #93**; branch `ccr-75ee6cfe-ihyu4e`; base main; fase review.
- Fonte operacional única: `state/WORKFLOW.json`.
- **Próxima tarefa: RM-08**; a entrega formal RM-08 continua bloqueada até os gates precedentes serem avaliados.
- CURRENT permanece E0, zero eventos/resultados; PROGRESS intocado.
- Persistência pessoal desabilitada; sem dados pessoais, credenciais, replay real ou integrações externas.
- Alterações por API GitHub; hooks locais não executados nesta sessão. A CI não substitui hooks locais.
<!-- GOVERNANCE-CHECKPOINT:END -->

## Ponto de retomada da próxima sessão

> **Aviso de defasagem do checkpoint.** O bloco "Checkpoint vigente" acima registra a frente ativa e o PR **no momento do último commit de estado**. Depois que esse PR é mesclado, o bloco fica **defasado** até o recibo do merge, que só entra no primeiro commit da próxima tarefa (`record_merge_receipt.py`). Por isso, antes de afirmar o estado de um PR ou frente, **confirme**: rode `python scripts/next_task.py` (ele lê o histórico Git e diz se o PR registrado já foi mesclado) ou consulte o PR por API. Se o HEAD for o commit de merge do PR registrado como "em revisão", o PR **já foi mesclado** e o recibo está pendente.

Não há prompt de retomada: o repositório se descreve. Rodar `python scripts/session_route.py --intent engineering --run` (rotas de estudo, escrita, governança e persistência: `--intent study|write|governance|persistence`, definidas em `config/session_routes.json`) e seguir o procedimento de `docs/especificacoes/README.md`, que diz o estado real do ciclo, o próximo item da fila `work_queue` de `state/WORKFLOW.json` e quando parar.

**Em uma frase:** as especificações S1 a S5 e S8, o validador de comandos (Ed25519 e HMAC, registro durável, filtro, montador de issue), o perfil `agents/ZAPIA.md`, o roteiro de validação da Zapia e as ferramentas do Termux existem; a conta exclusiva da Zapia já foi validada **em parte, por autorrelato** (rodadas 5, 5b e 5c), e o repositório privado de dados existe com o consentimento v2 **por relato do proprietário**; a escrita de resultados está **desabilitada**. O que falta provar está nas listas abaixo.

**Material pronto para o proprietário encaminhar** (tudo em `docs/governanca/PROMPTS_PRONTOS_ZAPIA_CONTA_NOVA_20261109.md`, conferido por `tests/test_zapia_prompts.py`): passos para montar a conta nova e o token, texto da instrução persistente, prompt de validação (V0, V1, V2, V7, V12), prompts de V11 e de V4 e V6, mensagem ao suporte do TEC e o comando de geração das chaves. O script `scripts/termux/verifica_token.sh` confere um token sem imprimi-lo. **Ferramenta única do proprietário no Termux:** `bash scripts/termux/ufms.sh {preparar|atualizar|diagnostico|token|plano|consentir-v3|guardar-plano}` (o `diagnostico` gera um relatório sem segredos para colar no chat; o `plano` gera o plano padrão localmente; `consentir-v3` e `guardar-plano` levam o plano ao repositório **privado**, por ato do proprietário).

### Estado de saída (15/11/2026) e como retomar

**Como retomar, sem prompt:** `python scripts/bootstrap.py --mode engineering`, depois `python scripts/next_task.py` (diz o estado real do ciclo e o próximo item da fila; hoje o próximo é a **S7**, persistência privada e escritor) e, se o ciclo estiver `encerrado_recibo_pendente`, abrir o PR draft da próxima tarefa com `python scripts/record_merge_receipt.py` no primeiro commit. Uma tarefa, uma branch, um PR draft; **o merge só sai por pedido explícito do proprietário**.

**Integrado na `main` até aqui:** especificações S1 a S5 e S8; D-21 a D-23; verificador de token com perfil privado; ferramenta `scripts/termux/ufms.sh`; guarda das chaves e chaves públicas do Tutor e do Coach; registro de P1 e P3; consentimento v3 e `guardar-plano` (resultado por relato); validador de proveniência do conteúdo de estudo.

**O que a fila (`work_queue`) ainda tem, na ordem proposta:** S7, S6, S9, S10, S11. Implementações sem especificação nova: validador do prompt de revisão (PR-002), simulados no fluxo (PR-008) e tópicos estudados e prioridades no gerador de plano (PR-015).

**Pendente do proprietário (nada disto a sessão resolve sozinha):** gerar o plano local (`bash ~/ufms.sh plano`); **conferir o resultado do `token privado`, que não concluiu em 16/11 (ver o registro acima)**; criar o token `zapia-dados-30d` do repositório privado e conferi-lo (`bash ~/ufms.sh token privado`); confirmar que o notebook está privado e incluir a Lei 8.112; os testes da Zapia (marcador, V2, V11); os quatro pontos a confirmar da S8; abrir uma sessão de estudo do Tutor.

**O que NÃO persiste, e por quê:** o lugar definitivo de plano e resultados é o **repositório privado** `ufms-meu-estudo-dados` (D-24); o público nunca recebe dado pessoal. O consentimento v3 foi registrado e um plano foi guardado no repositório privado em 16/11/2026 (**relato**, `docs/governanca/RESULTADO_PERSISTENCIA_V3_PLANO_20261116.md`); a cópia local em `~/ufms-plano` (modo 0600) continua sendo dele; **resultados e desempenho** não são gravados em lugar nenhum, porque `personal_results_writes_enabled=false` (a escrita automática por Tutor e Zapia depende de P4, S7 e PR próprio). O consentimento v2 cobre só resultados de cadernos e simulados; o v3 cobre também o plano. A continuidade de **engenharia** é garantida pelo repositório (estado em `state/WORKFLOW.json`, fila, ROADMAP e este HANDOFF), não pela conversa.

**Ordem do que acontece a seguir (quando o insumo chegar):**
1. Validação da conta nova: **rodada 5 registrada como PARCIAL** em `docs/governanca/RESPOSTA_RODADA5_ZAPIA_20261115.md` (V7 verificado; a autoria não distingue a Zapia do proprietário). **Aberto, depende do proprietário:** conectores: o proprietário decidiu manter **Drive e Calendar** e excluir o Outlook (D-21), o proprietário relatou que estão na conta Google só de estudos (não verificado); jobs Radar na conta exclusiva a desativar pelo proprietário; comprovante do V2 e escopo do token (OPEN-02). Depois, V11 e V4 e V6; V8 e V9 só com a frase `AUTORIZO` própria e depois dos jobs Radar revistos.
2. Chaves públicas do Tutor e do Coach: **registradas** em `config/agent_public_keys.json` (geradas pelo proprietário no Termux com `scripts/termux/gera_chaves.sh`; origem é relato dele). Falta provar que a Zapia verifica a assinatura (OPEN-09); rotação ou perda da chave exige novo PR.
3. Suporte do TEC: o proprietário **dispensou a consulta** (D-22); OPEN-11 segue aberto (formato da exportação) e a leitura em conta real exige mecanismo (D-15), testes do PR-017 e aprovação expressa. O V10 fica para depois dessa leitura.
4. Rodada 5b registrada (V4 simples observado, V6 recusado pelo plano, V9 sem notebook). Falta o V11; o V9 só depois de o proprietário criar o notebook na conta de estudos; V8b e, se o WhatsApp voltar, V3 e V5.
5. Dados do plano de estudo (tópicos já estudados, prioridades): gerar o plano real com `scripts/study_plan.py` e o caderno diagnóstico (estudo segue em E0).
6. **Persistência privada:** o proprietário roda `bash scripts/termux/cria_repo_privado.sh` no Termux (cria o repositório privado, confere `private=true` e registra o consentimento v2) e me traz o resultado; a escrita de resultados continua desabilitada. Pendências de engenharia sem insumo: decisão sobre re-pinar o gateway do GQ-D, rotina validada de escrita para `registrar_*` (bloqueada pela política de dados pessoais). A guarda local das chaves privadas (D-18) está em `scripts/agent_keys.py` (`check_key_guard`, `verify-key`) com contraprovas em `tests/test_agent_keys.py`; é verificação do sistema de arquivos, não prova de onde o agente roda (OPEN-09).

### Retomada da persistência (próxima sessão)

**Ponto de partida:** o proprietário **executou** `scripts/termux/cria_repo_privado.sh` em 15/11/2026: repositório privado criado, `private=true` (P1) e consentimento v2 gravado com readback (P3), **por relato com capturas**, registrado em `docs/governanca/RESULTADO_PERSISTENCIA_P1_P3_20261115.md`; a sessão não tem acesso ao repositório privado. A escrita de resultados está **desabilitada** (`personal_results_writes_enabled=false`). Confirme o estado do ciclo com `python scripts/next_task.py`; o recibo do último PR mesclado entra no primeiro commit da próxima tarefa.

**Em ordem (cada passo em PR próprio, em série):**
1. **Proprietário:** feito (15/11/2026, relato): rodou o script e trouxe a saída. Se for preciso reconferir, `gh api repos/Andraus35/ufms-meu-estudo-dados --jq .private` (esperado `true`).
2. **Sessão:** registrado como relato; uma confirmação independente exigiria leitura autenticada, **sem escrever** (se o repositório privado não estiver acessível à sessão, `add_repo` com acesso de leitura; sem acesso, usar a saída que o proprietário colar). Registrar um resumo em `docs/governanca/`, sem dado pessoal. Fechar a parte pendente do ADR-013, passo 1.
3. **Credencial (PR-010, D-09):** token fine-grained **só do repositório privado**, separado do token do projeto e **com expiração** (o proprietário respondeu "indefinido" em 15/11/2026, o que o PR-010 não admite, e então **escolheu 30 dias**; token de nome sugerido `zapia-dados-30d`). O verificador já tem o perfil privado: `PERFIL=privado bash scripts/termux/verifica_token.sh` (ver seção 4c do roteiro de prompts). Valor do token só pelo formulário seguro da Zapia.
4. **Escritor (P4), OPEN-01 e OPEN-02:** reaproveitar `scripts/api_write_transaction.py` e `scripts/api_write_guard.py`; a Zapia grava só por comando assinado do Tutor.
5. **Faltam provas:** P4 (escritor), P7 (reconstrução a partir dos eventos privados reais), P8 (revogação: só texto, apagar o repositório inteiro) e P9. Ver a tabela do ADR-013.
6. **Habilitar a flag** é PR próprio, com aprovação humana expressa, só depois de P1 a P9 provados. Nunca antes.

**Enquanto isso:** o plano e o desempenho do estudante **não** vão ao repositório público. O plano vai ao repositório **privado** por ato do próprio proprietário (`consentir-v3` e `guardar-plano`), já feito em 16/11/2026 (relato); a cópia local vive em `~/ufms-plano`. Não pedir token ao proprietário no chat; nenhum agente construtor recebe credencial de escrita pessoal.

**Cuidados desta fase:** o que se sabe da Zapia é autorrelato; a conta antiga não vale como evidência da nova; ao testar scripts de token neste ambiente, o proxy substitui credenciais (use só o computador do proprietário); o merge só ocorre por pedido explícito dele.

- **Já decidido:** `PRODUCT.md` (decisões D-01 a D-23). A D-23 define os papéis do conteúdo de estudo (Tutor autor e verificador; Gemini só rascunho; Zapia só transporte) e `scripts/review_provenance.py` valida o registro de proveniência; a nota da rodada 5c é rascunho.
- **Especificações pendentes (proposta de 15/11/2026; o proprietário escolhe a ordem, uma por vez, cada uma com pesquisa obrigatória):** **S6** execução e canal de comandos do Tutor e do Coach (OPEN-09); **S7** persistência privada e escritor (PR-003, P4 a P9); **S9** leitura direta das plataformas (PR-017, PR-016, D-14, D-15, D-22; candidato escolhido pelo proprietário: a Zapia lê com a sessão dele, a provar); **S10** Notebook como ferramenta do Tutor (PR-012, OPEN-10); **S11** ciclo ponta a ponta e piloto (PR-006, PR-008, GP-4, GP-5). A **S8** (rotina diária do Coach, PR-007) foi a primeira escolhida. Implementações sem especificação nova: validador do prompt de revisão (PR-002), simulados no fluxo (PR-008) e prioridades e tópicos estudados no gerador de plano (PR-015).
- **Especificações prontas:** S1 a S5 e S8 em `docs/especificacoes/` (método de estudo e revisão, Tutor, Coach, operação e harness da Zapia); a fila `work_queue` está completa quando todos os arquivos de entrega existem. O contrato de comandos dos agentes à Zapia (PR-013) tem esquema em `config/agent_command_schema.json` e validador offline em `scripts/agent_commands.py`, com testes de contraprova; **é referência de implementação, não prova que a Zapia o usa**.
- **Perfil da Zapia:** `agents/ZAPIA.md` (START explícito, papel de interface e executora, só comando válido, conteúdo externo como dado, negar por padrão, relato com prova), validado por `python scripts/agents_gate.py --check` contra as operações de Tutor e Coach e contra `config/agent_command_schema.json`. É texto de instrução, **não trava técnica**, e nunca foi lido por uma Zapia real.
- **Construído offline (RM-09):** geração local de chaves e assinatura (`scripts/agent_keys.py`); validador com Ed25519 e HMAC e registro durável de nonce e idempotência (`scripts/agent_commands.py`, `scripts/command_ledger.py`); montador de issue e comentário (`scripts/github_issue_payload.py`); filtro de conteúdo sensível em invólucro (`scripts/gateway_filter.py`; o `scripts/tool_gateway.py` tem SHA pinado no GQ-D e não foi alterado). Tudo isso é referência de implementação, **sem prova de uso obrigatório pela Zapia**.
- **Depende do proprietário, sem bloquear as especificações:** dados do plano (início, tempo diário, dia de descanso, cargo, tópicos já estudados, prioridades); planos no TEC e no Qconcursos e se exportam (OPEN-11); consulta ao suporte do TEC (OPEN-12); o canal e a verificação de origem dos comandos (OPEN-09; Tutor e Coach rodam no computador do proprietário, D-18); acesso direto do Tutor ao NotebookLM (OPEN-10; a Zapia nova usa conta Google só de estudos, D-20); token da Zapia nova (D-20; OPEN-02 se resolve com ele); repositório privado de dados (D-01); revisão humana dos requisitos que dependem de julgamento (S1-R3/R6/R9, S2-R1/R3/R7, S3-R3/R5/R7/R8, S5-R2/R4/R5/R6).
- **Não executado:** a conta exclusiva da Zapia (D-19, D-20) ainda não foi montada nem validada; testes T1 a T3 e V2 a V9 e V11 na conta nova; PR-012 completo com o Notebook (a rodada 5c, `docs/governanca/RESPOSTA_RODADA5C_ZAPIA_20261115.md`, registrou só a criação pela Zapia, como rascunho não verificado); leitura em conta real das plataformas; persistência de resultados pessoais.
- **Rodadas da Zapia (conta antiga):** a 3 e a 4 estão em `docs/governanca/RESPOSTA_RODADA3_ZAPIA_20261109.md` e `docs/governanca/RESPOSTA_RODADA4_ZAPIA_20261109.md`. Observado e conferido: leitura por API com hashes corretos, validador com as 11 decisões esperadas e entrega de mensagem pelo app. Falhou: escrita de um comentário (permissão do token). Tudo o mais é autorrelato e **precisa ser repetido na conta nova**.
- **Limite de fonte:** o que se sabe da Zapia é autorrelato (rodadas de auditoria e adendo de 09/11/2026, este último não versionado); a memória dela não é fonte de estado, o repositório é.
- **Antes de escrever:** `python scripts/doc_cohesion.py --check` deve passar; ao mudar uma decisão, atualizar todos os documentos que a citam.

---

## Registro histórico
