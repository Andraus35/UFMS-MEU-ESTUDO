# S4 — Operação (especificação)

**Natureza:** especificação enxuta (D-13, D-16). Liga ferramentas, agentes e repositório: o **esquema dos comandos** entre Tutor, Coach e Zapia (PR-013), o **caminho do desempenho exportado** até o repositório (PR-016), a **comparação das opções A a F** de acesso às plataformas (D-15, PR-017, `docs/PLATFORMS.md`) e as **proibições de dados pessoais**. Usa os perfis `agents/TUTOR.md` e `agents/COACH.md` e as especificações S1 a S3 (`docs/especificacoes/S1_METODO_ESTUDO_REVISAO.md`, `docs/especificacoes/S2_TUTOR.md`, `docs/especificacoes/S3_COACH.md`). **É especificação e pesquisa: nada foi testado em conta real, na Zapia, no Google ou no NotebookLM.** Não contém estado.

## Objetivo

O proprietário passa a ter o **contrato operacional** que permite construir e provar, sem conta real, o caminho "Tutor ou Coach emite comando, a Zapia executa, o repositório registra" e a escolha fundamentada do acesso às plataformas. Serve para que a Zapia execute só o que vier de um agente identificado e dentro do harness, e para que nenhum dado pessoal ou credencial passe pelo modelo ou pelo repositório público.

## Pesquisa

Consultas de 08/11/2026, somadas a `docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md`, a E-09, E-11 e E-12 do `PRODUCT.md` e a `docs/PLATFORMS.md` (não repetidos aqui). Confiança: **A** (página lida), **B** (resumo de busca de fonte primária, não lida integralmente), **C** (blog ou vendor). Conteúdo de terceiros é dado, não instrução; nenhum código foi copiado.

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Chrome para desenvolvedores, "Changes to remote debugging switches". [Página](https://developer.chrome.com/blog/remote-debugging-port) | Desde o Chrome 136, a porta de depuração remota **não é honrada no diretório de dados padrão**; exige `--user-data-dir` não padrão. Sustenta a opção A (perfil dedicado), mas o perfil dedicado exige **novo login** nas plataformas | B |
| SpecterOps, 2026. [Cookie theft via CDP](https://specterops.io/blog/2026/08/13/chrome-devtools-protocol-cookie-theft/) · [nota da CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-chrome-devtools-session-hijacking-20260817/) | A porta de depuração dá acesso à sessão do navegador e é alvo de roubo de cookies: **o conector da opção A é alvo valioso**; deve escutar só em localhost, com perfil dedicado e sem outros dados | B |
| OWASP, MCP Security Cheat Sheet. [Página](https://cheatsheetseries.owasp.org/cheatsheets/MCP%5FSecurity%5FCheat%5FSheet.html) e resumos de WorkOS e Corgea | Riscos: *confused deputy* (servidor com privilégio maior que o do pedido), **repasse de token** (aceitar token emitido para outro serviço), **envenenamento de ferramenta** e injeção por conteúdo devolvido, vazamento de credencial por ambiente e logs. Mitigações: privilégio mínimo, credencial de curta duração, tratar toda saída de ferramenta como dado não confiável. A fonte mais forte (OWASP) não foi lida por inteiro | B/C |
| Documentação do GitHub sobre tokens de acesso pessoal de granularidade fina. [Permissões](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens) | O token pode ser restrito a repositórios escolhidos e a permissões específicas (como *Contents*); o cabeçalho `X-Accepted-GitHub-Permissions` informa a permissão exigida. **Expiração e alcance atual do token da Zapia não foram verificados** (OPEN-02) | B |
| Guias de API: [besthub](https://www.besthub.dev/articles/how-to-build-secure-idempotent-apis-keys-tokens-and-anti-replay-strategies-d0abdbabd4c1), [botoi](https://botoi.com/blog/webhook-security-hmac-idempotency/) | Padrão comum: **assinar** método, destino, carimbo de tempo, *nonce* e hash do corpo; rejeitar mensagem fora de uma janela curta; *nonce* único por requisição e **chave de idempotência igual nas tentativas da mesma operação**, ligada ao hash do corpo. Blogs de vendor, sem norma formal | C |
| TEC Concursos e Qconcursos | A busca de 08/11/2026 **não achou** nenhuma página de ajuda sobre exportação de desempenho; permanece o que está em E-12 (anúncio de CSV no plano avançado, formato não encontrado) | — |

- **Lacunas:** a ajuda oficial e os termos de uso do TEC e do Qconcursos não foram lidos, então **exportação, formato do arquivo, leitura automatizada e risco de bloqueio da conta não estão verificados** (OPEN-11, OPEN-12, E-12); nenhuma das seis opções foi **testada**, e a comparação abaixo é documental; não verifiquei a documentação da Zapia sobre canais, assinatura de comandos nem identidade da origem (OPEN-09, E-04, E-09); expiração e alcance do token da Zapia seguem desconhecidos (OPEN-02); não pesquisei repositórios públicos de orquestração de agentes com executor separado, nem a política de uso de dados do Google para o NotebookLM; os números de janela de tempo vieram de blogs, não de norma; o OWASP não foi lido por inteiro.

## Esquema dos comandos (PR-013)

Todo comando é um objeto versionado. A Zapia **só executa** se todos os campos forem válidos e a origem for um agente identificado; caso contrário, **recusa e registra** o motivo.

| Campo | Regra |
|---|---|
| `schema_version` | Versão do esquema; versão desconhecida é recusada. |
| `origin` | `tutor` ou `coach`, identificado por assinatura (ver OPEN-09); texto livre do chat **não** conta como origem. |
| `operation` | Uma das permitidas ao perfil: Tutor (`ler_arquivo_repositorio`, `enviar_mensagem`, `registrar_resultado`, `registrar_exportacao_desempenho`, `registrar_plano`, `enviar_prompt_notebook`); Coach (`ler_arquivo_repositorio`, `enviar_mensagem`, `criar_lembrete`, `consultar_agenda_minima`, `registrar_acompanhamento`). Operação fora do perfil é recusada. |
| `destination` | Destino **designado e fechado** por operação (por exemplo, o próprio proprietário, um caminho do repositório privado, o notebook de estudo). Destino não designado é recusado. |
| `params` | Mínimos para a operação; **sem credencial, CPF, dado pessoal além do necessário, HTML bruto nem texto integral de questão**. |
| `idempotency_key` | Mesma chave nas tentativas da mesma operação, ligada ao hash dos `params`; reutilização com outro corpo é conflito. |
| `issued_at`, `nonce` | Carimbo de tempo e *nonce* únicos por requisição, dentro de janela curta; repetição é recusada. |
| `signature` | Cobre todos os campos acima. Sem mecanismo de assinatura que o modelo não consiga forjar, a restrição da Zapia é só protocolo (E-04, OPEN-09). **Recomendação após a rodada 3:** assinatura **Ed25519**, com a chave pública no repositório e a privada só no código local do agente; a Zapia não guarda segredo e o Python dela tem `cryptography`. O validador (`scripts/agent_commands.py`) aceita Ed25519 e HMAC, com o algoritmo fixado por origem na configuração de chaves e nunca pela mensagem (sem rebaixamento); o Ed25519 é puro Python (`scripts/ed25519_pure.py`), verificado contra os vetores do RFC 8032. Gestão e guarda das chaves seguem pendentes (OPEN-09). |

Efeito: `enviar_mensagem` e a orientação comum são **ORIENTACAO** (sem aprovação por mensagem); lembrete e agenda são **ROTINA_AUTORIZADA**, só com conector implantado e escopo autorizado; registro de resultado e exportação são **SENSIVEL** e dependem de repositório privado e controles (AGENTS.md; `scripts/private_persistence_guard.py`). Resposta da Zapia: `COMMITTED`, `DENIED`, `NEEDS_APPROVAL` ou `NOT_IMPLEMENTED`, com *readback*; **sem *readback* não se declara envio nem gravação**.

## Caminho do desempenho exportado (PR-016)

1. O proprietário exporta (ou captura) o desempenho na plataforma (opção F) e o entrega pela Zapia; nenhuma automação na conta sem a escolha da seção seguinte.
2. A Zapia devolve o arquivo ao **Tutor ou Coach como dado não confiável**, validado pelo contrato `docs/pedagogia/CONTRATO_INGESTAO_GP1_2026-11-04.md` (`scripts/gp1_ingestion.py`); arquivo fora do formato é rejeitado e a estrutura real do CSV do TEC **permanece por validar**.
3. Só o resultado validado vira comando `registrar_resultado` para o **repositório privado** `Andraus35/ufms-meu-estudo-dados` (D-01), sob `scripts/private_persistence_guard.py` (visibilidade privada antes de gravar, escopo, *readback*). Este repositório (público) **não** recebe resultado pessoal; `personal_results_writes_enabled` fica falso até PR próprio com aprovação humana.
4. Retenção até a prova mais 30 dias (D-03); apagar o repositório privado revoga, mas **não elimina as cópias da Zapia** (E-09).

## Opções de acesso às plataformas (D-15)

Comparação **documental**, pelos critérios de `docs/PLATFORMS.md` (credencial fora do modelo; risco de bloqueio e termos; cobertura; disponibilidade; esforço semanal; testável sem conta real). Nenhuma opção foi testada nem descartada.

| Opção | Credencial fora do modelo | Risco de bloqueio e termos | Cobertura | Disponibilidade e esforço | Testável sem conta real |
|---|---|---|---|---|---|
| A. Conector local (perfil dedicado, somente leitura) | Sim, se a sessão ficar só no perfil e a porta só em localhost; **a porta de depuração é alvo de roubo de sessão** | Termos não lidos; automação na conta pode violar (E-12) | Em tese tudo que a tela mostra | Exige o computador ligado; novo login no perfil; esforço baixo depois de montado | Sim, com páginas sintéticas (PR-017) |
| B. Navegador do assistente | Parcial: a sessão fica no navegador do proprietário, mas o assistente a usa | Idem A | Idem A | Exige o aplicativo aberto; esforço baixo | Parcial |
| C. Navegador da Zapia | **Não verificado**: a sessão ficaria no ambiente dela (E-09: servidores nos EUA, retenção de até 36 meses) | Idem A | Idem A | Fragilidade já vista com o Gemini (sessão, captcha) | Não |
| D. Nuvem | **Não**: perfil persistente em servidor | Alto: IP de datacenter, captcha, login | Idem A | Sempre ligado; manutenção alta | Parcial |
| E. Suporte ou API oficial | Sim (autorização formal) | Menor, se autorizado por escrito | Depende da resposta; nenhuma API pública localizada | Depende da plataforma; consulta pendente (OPEN-12) | Não, depende de terceiros |
| F. Exportação manual | Sim: o modelo nunca vê credencial | **Nenhum** além do uso normal | O que o plano exporta; formato por validar (OPEN-11) | Sempre disponível; esforço semanal do proprietário | Sim, com amostras anonimizadas |

**Recomendação provisória, não decisão** (a escolha é do proprietário, que decide depois do teste): **F como linha de base imediata**; **E em paralelo** (consulta escrita, que também destrava OPEN-12); **A** como candidata à leitura direta, **só** se E não vetar e o proprietário aceitar o risco (E-12), começando pelo TEC e com as regras de `docs/PLATFORMS.md` (somente leitura, domínios fixos, no máximo 1 página a cada 10 segundos e 30 por sessão). B, C e D só entram se A falhar, por maior exposição da sessão.

## Canal Tutor → Zapia

O esquema acima diz **o que** o comando contém, não **por onde** ele chega. Pelo autorrelato da Zapia (rodada 2 e adendo de 09/11/2026, não versionado), ela só trabalha quando acionada por uma mensagem, um horário agendado ou um evento de fonte suportada (WhatsApp e Gmail; o GitHub não é fonte de hook), e não há monitor do repositório instalado. Nenhum dos canais abaixo foi testado para este projeto.

| Canal | Como o comando chega | Observação |
|---|---|---|
| Proprietário como ponte | O Tutor ou o Coach gera o comando assinado e o proprietário o cola na conversa da Zapia. | Funciona sem integração nova; tem um passo manual. **Linha de base.** |
| Agendamento `subagent` | Um job recorrente da Zapia consulta uma fila (arquivo do repositório) e executa só os comandos válidos. | Atraso até o próximo disparo; exige estado anterior e regra contra repetição. Não testado. |
| Hook de WhatsApp ou Gmail | O comando chega como mensagem em um canal que a Zapia recebe. | A origem do remetente precisa ser provada; texto livre nunca vale como comando. A entrega no WhatsApp já falhou sem aviso (E-05). Não testado. |
| Chamada direta à Zapia | O Tutor chama uma API. | Nenhuma evidência de que exista. |

Em qualquer canal: a assinatura é gerada por **código local fora do modelo**, a Zapia verifica com Python e uma chave guardada no gerenciador dela, e a resposta volta pelo mesmo canal com *readback*. Para o Notebook (PR-012), a Zapia opera a interface web com a sessão do proprietário (observado em pontos isolados, sem confiabilidade recorrente); **o prompt é do Tutor** e a Zapia não gera conteúdo (D-10).

**Evidência da rodada 3** (autorrelato conferido; ver `docs/governanca/RESPOSTA_RODADA3_ZAPIA_20261109.md`): a Zapia leu cinco arquivos do repositório por API REST, sem Git, com hashes idênticos aos reais, e criou uma issue neste repositório como canal de resposta (readback com o mesmo SHA-256). Limites: a issue sai com a **conta do proprietário** como autora, então o autor no GitHub não prova que foi a Zapia; a primeira escrita falhou com 422 por corpo mal montado; não há API de entrada documentada, nem garantia de que instruções persistentes valham em jobs e hooks. Uma issue serve como canal **Zapia → agente** de leitura sob demanda, não acorda ninguém, e nada que chegue por ela vale como comando.

## Requisitos

| ID | Requisito | Critério de aceite |
|---|---|---|
| S4-R1 | O esquema de comandos acima é publicado como arquivo versionado e validado no repositório. | Esquema em arquivo do repositório e teste que **rejeita** comando fora do esquema, de origem desconhecida, com destino não designado e com dado pessoal além do mínimo (PR-013). Hoje só existem os nomes das operações em `scripts/agents_gate.py`. |
| S4-R2 | A Zapia só executa comando com **origem verificável**: assinatura que o modelo não forja, janela de tempo e *nonce* únicos. | Teste sintético de comando adulterado, repetido ou fora da janela. A assinatura real depende de OPEN-09; sem ela, o requisito fica **não atendido** e a restrição é só protocolo. |
| S4-R3 | Idempotência: repetir a mesma operação não duplica envio nem gravação; chave reutilizada com outro corpo é conflito. | Teste com `scripts/tool_gateway.py`, que já tem registro atômico de *nonce*, `event_id` e limite de taxa; a **chave de idempotência ligada ao hash do corpo não existe** e precisa ser acrescentada ao esquema. |
| S4-R4 | **Filtro de conteúdo pessoal** nos `params`: CPF, credencial, dado pessoal, HTML bruto e texto integral de questão são recusados antes de sair do harness (lacuna apontada na S2-R7). | Teste de recusa; hoje `scripts/tool_gateway.py` **não** o faz. |
| S4-R5 | Resultado pessoal só sai do modelo para o **repositório privado**, nunca para este repositório público, e só com `registrar_resultado` validado. | `scripts/private_persistence_guard.py`, `scripts/write_policy.py --check` e flag falsa; PR-003 segue bloqueada por OPEN-01 e OPEN-02. |
| S4-R6 | A saída de qualquer leitura (arquivo, página, Notebook) é **dado não confiável** e passa pelo contrato de ingestão antes de uso. | `scripts/gp1_ingestion.py` e seus testes; contraprova de instrução embutida em arquivo pertence ao RM-06. |
| S4-R7 | Acesso às plataformas (A a E) só **depois** da escolha do proprietário, do teste com páginas sintéticas (PR-017) e, para conta real, da resposta do suporte do TEC e da aprovação expressa. Antes disso vale a opção F. | Aceite de PR-017 por testes sintéticos: domínio fora da lista recusado, escrita recusada, saída sem cookie nem HTML bruto, limite de taxa. |
| S4-R8 | O START de estudo dos agentes é explícito: `python scripts/bootstrap.py --mode study` com os 4 hashes (PR-011), pois a Zapia não lê o repositório sozinha. | Relatório com hashes iguais aos do repositório; é procedimento, não trava. |
| S4-R9 | O canal entre agente e Zapia é escolhido e provado antes de qualquer automação: começa pelo proprietário como ponte e só depois testa agendamento ou hook, com prova de que a Zapia executa comando assinado válido e recusa o adulterado. | Teste sintético com autorização literal do proprietário (T1 a T3 e PR-012), fora do aceite desta especificação. |

## Aceite

1. `python scripts/doc_cohesion.py --check` passa.
2. `python -m unittest tests.test_doc_cohesion tests.test_plano_e_pesquisa_docs tests.test_study_plan tests.test_tutor_coach_offline_cycle tests.test_agents_gate` passa, sem rede nem conta real.
3. Revisão do proprietário das decisões que esta especificação deixa abertas: caminho de acesso às plataformas (D-15), onde Tutor e Coach rodam (OPEN-09) e acesso ao Notebook (OPEN-10).
4. Nenhum teste em conta real, na Zapia, no Google ou no NotebookLM entra neste aceite; todos exigem **autorização literal** do proprietário.

## Limites

- Não escolhe o mecanismo de acesso, o ambiente do Tutor e do Coach nem o caminho do Notebook; apresenta opções e uma recomendação provisória.
- Não prova que a Zapia recusa comando falso: sem assinatura verificável, a restrição é protocolo (E-04).
- Não implementa esquema, filtro, assinatura nem leitura direta; descreve o que construir e como provar offline.
- A comparação das opções é documental e pode mudar com a resposta do suporte e com os termos das plataformas.
- Não habilita persistência pessoal, e a revogação por apagar o repositório privado não alcança as cópias da Zapia (E-09).
