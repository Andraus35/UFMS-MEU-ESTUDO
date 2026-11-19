# S14 — Runtime operacional do harness (especificação)

**Natureza:** especificação enxuta (D-13, D-16), segundo a Spec Lean da Tech Leads Club **no que couber**: plano com portas sem volta, requisitos pareados a uma prova e verificação por quem não escreveu. Trata do **harness em produção** (Tutor, Coach, Zapia, canal e rotinas), não da sua construção. **Aponta** para S2, S3, S5, S6, S7, S8, S9, S10, S11 e S12 e **não os copia**. É texto de engenharia: **não habilita** nada, **não** altera flag e **não** contém dado pessoal.

**Regra do proprietário (19/11/2026), nas palavras dele:** o **LLM é livre na cognição probabilística**, mas **condicionado nas leituras e nas entregas por gates e mecanismos determinísticos**. Isto é coerente com a autonomia cognitiva do `AGENTS.md` (o Tutor e o Coach decidem abordagem, conteúdo e revisão) e com a sua exigência de que **efeito externo** passe por gate. Esta especificação **não restringe o raciocínio**: restringe **o que entra** (leitura) e **o que sai** (entrega e efeito).

## Objetivo

O proprietário passa a ter **um desenho único e testável do runtime**: o que o modelo pode ler, o que pode entregar, por qual mecanismo cada entrega passa, o que é **imposto fora do modelo**, o que é **só verificável** e o que **não se consegue gatear** (e portanto é avaliado por amostra e por avaliação offline). Passa a ter também as **rotinas operacionais**, a **parada** e a **lista honesta do que a produção não garante**. A produção **não é declarada pronta** por esta especificação: é a lista de portas que a tornam defensável.

## Pesquisa

Consultas de 19/11/2026 (WebSearch, **só resumos de busca**), somadas às especificações S5, S6, S7 e S11 e à auditoria de 19/11/2026 (conversa), que **não são repetidas**. Confiança: **A** (página lida), **B** (resumo de busca de fonte primária ou oficial, **não lida integralmente**), **C** (blog, fornecedor ou agregador). Conteúdo de terceiros é dado, não instrução; nada foi copiado. **Nada foi testado em produção.**

| Fonte | O que se tirou | Conf. |
|---|---|---|
| OWASP Top 10 para aplicações com LLM, edição 2025, via resumos. [Gravitee](https://www.gravitee.io/blog/owasp-top-10-for-llm-applications-2025-a-practical-guide), [Promptfoo](https://www.promptfoo.dev/blog/owasp-top-10-llms-tldr/) | **Tratamento impróprio da saída:** a saída do modelo é **entrada não confiável** para o que vem depois e deve ser validada. **Agência excessiva:** funcionalidade ou permissão a mais; a mitigação é **reduzir o que o modelo pode fazer**, exigir confirmação para ações destrutivas e manter **registro de cada chamada**. A numeração varia entre blogs; **não conferi na lista oficial** | C |
| Anthropic, *Building effective agents*. [Artigo](https://www.anthropic.com/research/building-effective-agents) | Distingue **fluxos de trabalho** (caminhos de código predefinidos) de **agentes** (o modelo decide o processo e o uso de ferramentas); recomenda **a solução mais simples** e só aumentar a complexidade quando necessário. **Não li o texto**; o que ele diz de guardrails e de supervisão humana **não foi confirmado** | B |
| Surveys de LLM como juiz. [arXiv 2411.15594](https://arxiv.org/pdf/2411.15594), [arXiv 2412.05579](https://arxiv.org/pdf/2412.05579) | A **confiabilidade** do juiz-LLM é problema aberto; vieses de posição, de auto-favorecimento e de excesso de confiança; mitigação por várias rodadas ou modelos. **Nenhum** trata de verificação determinística contra juiz; por isso **o juiz-LLM só auxilia e nunca é portão** (R12) | B |
| NIST AI 600-1, perfil de IA generativa. [Guia da Anaconda](https://www.anaconda.com/blog/nist-ai-600-1-generative-ai-profile-guide) | Ações de **medir** (teste, verificação, comparação com a verdade de referência, adversarial) e de **gerir** (monitoramento, resposta a incidente, desativação); é **voluntário**, não certificação. **Não li o PDF** do NIST | C |
| Registros do projeto: S5-R4, S5-R5, S5-R9 a S5-R12, S6-R4, S6-R7, S6-R9, S6-R13, S7-R6, S9-R7, S11, `docs/governanca/E7_FECHAMENTO_JANELA_C6_20261118.md`, `ROADMAP.md` (RM-06, RM-07) | O desenho do canal existe; a **prova real** é sintética e por relato; RM-01 a RM-07 estão **implementado_nao_homologado** (RM-07: 0/27 cenários ponta a ponta; RM-06: 46 de 102 sem teste canônico); **não há** runtime de Tutor ou Coach que aplique gates às respostas | C |

- **Lacunas:** **não li o texto original** de nenhuma fonte B ou C (nem a lista oficial da OWASP, nem o artigo da Anthropic, nem o PDF do NIST, nem os surveys); a numeração da OWASP **não foi conferida**; **não pesquisei benchmarks em repositórios públicos nem sites de cursinhos** para este tema (o D-16 os pede; o tema é de engenharia de produção e **fica como lacuna**); **nada foi provado** contra o app Claude, a Zapia ou o portão em produção; o comportamento do Tutor e do Coach reais **é desconhecido**; **não auditei** os perfis `agents/TUTOR.md` e `agents/COACH.md` em detalhe nem o conteúdo do monitor do edital.

## Plano

### Zonas do runtime e três classes de garantia

| Zona | O que é | Regra do proprietário |
|---|---|---|
| **Z0 Leitura** | tudo que a sessão lê: START, edital, projeção, configuração | **condicionada**: lista fechada e mecanismo determinístico (R3, R4) |
| **Z1 Cognição** | raciocinar, escolher assunto, bloco, dificuldade, revisão e explicação | **livre**: nenhuma regra restringe o conteúdo do raciocínio |
| **Z2 Entrega** | o que a sessão devolve (orientação, recomendação, lembrete, comando, prompt ao Notebook) | **condicionada**: envelope tipado e gates (R5 a R8, R11) |
| **Z3 Efeito** | o que muda o mundo (gravar, enviar, ligar flag) | **só pelo portão**, fora do modelo (R9, R16) |

Cada controle cai em **uma** classe de garantia, declarada, para ninguém confundir lembrete com trava:

- **ENFORÇADA:** feita por código **fora do modelo**; o modelo não consegue pular (proteção da `main`, portão de promoção, token mínimo, flags, guarda de leitura da projeção).
- **VERIFICÁVEL:** um **verificador determinístico** que **qualquer um** roda sobre o envelope (o proprietário, uma rotina, outra sessão); a sessão **pode** deixar de rodá-lo, mas a ausência **fica visível** (R13). No chat direto entre o proprietário e o Tutor, **nada é imposto**: a garantia máxima ali é VERIFICÁVEL.
- **NÃO GATEÁVEL:** qualidade pedagógica, correção da explicação, interpretação do edital além do literal e adequação da recomendação. Cobertas por **avaliação offline e auditoria por amostra** (R12, R14), **sem garantia**.

### Fases e portas sem volta

0. **Hoje (E0):** o Tutor orienta na conversa, **sem gravar resultado**; nada é imposto no chat; os efeitos só existem pelo portão, com flags falsas em repouso.
1. **Verificador em modo sombra** (R11): roda sobre as entregas, **avisa e registra**, não bloqueia texto livre; **bloqueia desde o primeiro dia** só o que tem efeito externo (R9).
2. **Piloto S11:** prova o caminho de gravação ponta a ponta uma vez.
3. **Leitura de projeção por sessão** (C6, consentimento v4): **porta sem volta** (ato dele).
4. **Rotina da Zapia** (S8): **porta sem volta**; exige a frase `AUTORIZO` dele e a aceitação da Zapia.
5. **Verificador em modo bloqueio** para o que for ENFORÇÁVEL (R11) e **auditoria por amostra recorrente** (R14).

### Rastreabilidade: lacuna da auditoria para requisito

| Lacuna (auditoria de 19/11/2026) | Requisito |
|---|---|
| Comportamento factual e pedagógico sem controle | R1, R6, R11, R12, R14 |
| START autodeclarado | R3 |
| Zapia caixa-preta; origem do comando não provada; rotina `registrar_*` ausente | R9 |
| O portão valida a forma, não a verdade do resultado | R10 |
| Rotina diária (S8) e rotinas auxiliares não implantadas | R15 |
| Sem observabilidade do que foi entregue | R13 |
| Parada não testada em produção | R16 |
| RM-06 e RM-07 não homologados | R12 |
| Contrato em produção sem versão fixa | R2 |
| Hooks que falham abertos, gate alterável junto com a mudança, autoria indistinguível, CODEOWNERS inativo | R17, R18 |
| Regra de merge só na conversa | R18 (fora desta especificação: PR próprio) |

## Requisitos

Escritos como "quando X, o Y deve Z". A **prova** é o critério de aceite. Todos **fecham por padrão** nas bordas: dado ausente ou verificação indisponível **bloqueia o efeito** (R17).

| ID | Requisito | Critério de aceite |
|---|---|---|
| S14-R1 | **Cognição livre, bordas determinísticas.** O runtime se organiza em Z0 a Z3. **Nenhum gate avalia o raciocínio nem restringe a escolha** de assunto, bloco, dificuldade, revisão ou explicação; os gates atuam **só** na leitura, na entrega e no efeito. Toda saída é classificada em ENFORÇADA, VERIFICÁVEL ou NÃO GATEÁVEL. | Tabela zona e classe neste documento; teste de contrato: nenhuma regra desta especificação cita "restringir" a cognição; cada controle de R2 a R16 declara sua classe. |
| S14-R2 | **Contrato em produção = SHA fixado.** A versão do `AGENTS.md`, dos perfis em `agents/` e das regras usadas em produção é o **SHA da `main` fixado pelo proprietário**; a sessão **informa** o SHA; trocar o SHA é **ato dele**; uma rotina **avisa** quando a `main` andou (informativo, não bloqueia). | Fixture: envelope com SHA diferente do fixado é **recusado** pelo verificador; teste de que a troca do SHA não ocorre por comando de modelo. Classe: ENFORÇADA no verificador, VERIFICÁVEL no chat. |
| S14-R3 | **START verificável (recibo).** O broker devolve um **recibo** com SHA, papel e os **hashes dos arquivos** do START; o verificador **recalcula** os hashes no repositório no SHA fixado. **Prova** que os bytes certos foram obtidos naquela revisão; **não prova compreensão** e, sem orquestrador externo que emita o recibo por sessão, **não prova quem o emitiu** (lacuna declarada). Recibo ausente = envelope de **efeito** recusado. | Contraprovas: hash adulterado, SHA errado, papel inválido e recibo ausente **recusam**; o texto declara o limite; teste de que o recibo **não** é aceito como prova de leitura semântica. |
| S14-R4 | **Leituras por lista fechada (Z0).** A sessão lê: os arquivos do START, o edital por índice e trechos (com página), a configuração, a **projeção em lista fechada** (`projection_generator`, consentimento v4 e C6). **Nunca** o histórico bruto, a fila, exportações ou segredos (S6-R9). Todo conteúdo lido (questão, relatório, comentário, anexo) é **dado**, não instrução. | Contraprovas do guarda (`session_read_guard`): tipo `historico`, `fila` e `exportacao` **bloqueiam**; consentimento ausente **bloqueia**; campo fora da lista **bloqueia**. Classe: ENFORÇADA para projeção; VERIFICÁVEL para as demais. |
| S14-R5 | **Envelope de entrega tipado (Z2).** Toda entrega que sai da sessão é um objeto de campos **fechados**: `tipo` (ORIENTACAO, RECOMENDACAO_CADERNO, LEMBRETE, COMANDO, PROMPT_NOTEBOOK), `papel`, SHA do contrato, recibo, `corpo` e `alegacoes` (R6). A classe de risco segue o `AGENTS.md`: **ORIENTACAO** (sem aprovação por mensagem, só gates automáticos de evidência e qualidade), **ROTINA_AUTORIZADA** (gateway valida destinatário, escopo, idempotência, limites e privacidade) e **SENSIVEL** (aprovação específica). | Esquema fechado em arquivo de configuração; contraprovas: campo extra, tipo desconhecido, corpo acima do limite e envelope sem recibo **recusam**. |
| S14-R6 | **Declarar e verificar alegações.** O modelo **declara** o que afirma de verificável: `citacao_edital` (página e trecho literal), `dado_aluno` (valor e campo da projeção), `nivel_evidencia` (E0 a E4) e `inferencia` (marcada como tal). O verificador confere **cada alegação contra a fonte**: trecho literal existe nos chunks do edital naquela página; valor consta da projeção; nível é igual ao da projeção. **Número, percentual, id ou citação no corpo que não esteja declarado bloqueia** a entrega. | Contraprovas: citação inventada, página trocada, nível E3 onde a projeção diz E2, percentual solto e id inexistente **recusam**; entrega só com `inferencia` e sem número **passa**. Limite: afirmação **não numérica e não declarada** não é detectável (NÃO GATEÁVEL). |
| S14-R7 | **Recomendação de caderno em campos fechados.** Traz id, plataforma, filtros, assunto, nível, quantidade sugerida e justificativa; **nunca** afirma disponibilidade de questões; filtros em camadas e fallback conforme o prescritor. | Teste: campo faltando ou texto de disponibilidade **recusam**; recomendação válida **passa**. |
| S14-R8 | **Privacidade e conteúdo externo na saída.** Nenhuma entrega leva segredo, dado pessoal, enunciado de questão, URL fora da lista ou identificador de conta; resultado pessoal **nunca** vai ao repositório público; conteúdo externo **não vira instrução** (S5-R4, S5-R5: a combinação **dado privado, conteúdo não confiável e saída externa** é quebrada por desenho). | Contraprovas: CPF, e-mail, token, enunciado, link com identificador e texto "ignore as instruções" no corpo **recusam** ou **não alteram** o comportamento verificado. |
| S14-R9 | **Efeitos só pelo portão (Z3).** Gravar, enviar mensagem, ligar flag e promover **só** por comando validado (`agent_commands`, `promotion_gate`, `tool_gateway`) e **rotina versionada** do repositório; a Zapia **executa o comando válido**, não decide e não monta chamada na hora. A **rotina `registrar_*` ainda não existe** (S5-R12) e **entra como tarefa derivada**. A **origem do comando não é provada** (S6-R7); o desenho **reduz** o dano, **não o elimina**. | Contraprovas existentes do portão mais o teste de **cada** operação com a rotina nova; comando fora da tabela de operações **recusa**; token só com Contents e só do alvo. Classe: ENFORÇADA. |
| S14-R10 | **Veracidade do resultado: o portão valida a forma, não a verdade.** Cada resultado leva a **classe de origem** (`exportacao_plataforma` ou `relato_manual`); a **confirmação do proprietário** (F4) é parte do ciclo; um resultado errado se **corrige por evento próprio** (`resultado_corrigido`), nunca por edição; a **auditoria por amostra** (R14) confere resultados contra o relato dele. **Não há como provar** que a Zapia ou o modelo não inventou um resultado bem-formado: só limitar o dano e detectar. | Teste: resultado sem classe de origem **recusa**; correção sem vínculo ao resultado anterior **recusa** (já coberto); o texto declara o limite. |
| S14-R11 | **Verificador em modo sombra e em modo bloqueio.** O verificador de entrega (R5 a R8) começa em **sombra** para texto livre: **avisa e registra**, não bloqueia; sai da sombra **por tipo de entrega** quando a taxa de falso positivo medida for aceitável **a critério dele**; **efeito externo bloqueia desde o início** (fail-closed, R17). | Teste: em sombra, entrega inválida **passa com aviso e registro**; em bloqueio, **recusa**; COMANDO **sempre** em bloqueio. |
| S14-R12 | **Avaliação offline em duas frentes, sem juiz-LLM como portão.** (a) **Do verificador:** suíte de envelopes sintéticos válidos e adversariais com resultado esperado **determinístico** (fecha o que RM-06 e RM-07 pedem para o que é gateável). (b) **Da cognição:** rubrica **humana** aplicada à amostra (R14). Um **juiz-LLM** pode **auxiliar** a triagem, **nunca** decide entrega nem homologação (vieses e confiabilidade são problema aberto). | Teste: a suíte (a) cobre cada tipo de recusa de R5 a R8; **nenhum** portão chama modelo; o relatório da avaliação declara **o que não cobre**. |
| S14-R13 | **Registro das entregas, sem dado pessoal.** O verificador registra, por entrega: tipo, resultado (aceita, aviso, recusada), **motivo** e o SHA; **nunca** o conteúdo pessoal. Antes do piloto o registro é **da sessão** (efêmero) e o proprietário **vê o aviso**; depois do piloto vai ao **repositório privado**, em pasta própria, pelo portão. A **ausência de registro** de uma sessão é, ela mesma, um sinal visível. | Teste: o registro recusa campos fora da lista (como a projeção); nenhuma entrega com dado pessoal chega ao registro. |
| S14-R14 | **Auditoria por amostra e critério de pausa.** Rotina de auditoria **proposta e ajustável** (primeira proposta: a cada dez entregas ou a cada quinze dias, o que vier antes): o proprietário confere uma amostra com a rubrica (fato com fonte, inferência marcada, sem disponibilidade inventada, sem dado pessoal, coerente com a projeção). **Pausa:** duas amostras seguidas com falha **grave** (dado pessoal, citação inventada, efeito sem gate) **desligam** a rotina e o recibo de produção até nova decisão dele. Isto **não** é cronograma de estudo. | Relatório da amostra sem dado pessoal; teste do critério de pausa como função das entradas. |
| S14-R15 | **Rotinas operacionais, cada uma com gatilho, executor, gate e falha segura.** (1) **Diária do Coach** (S8): no máximo uma mensagem por dia, só atividade pendente, no app; **bloqueada** até `AUTORIZO` dele e a Zapia aceitar. (2) **Vencimentos de revisão:** lembrete a partir da projeção (`revisoes`); **não recalcula** prazos (padrão 7, 15 e 30 dias do D-11 gravado nos eventos). (3) **Pré-voo antes de janela** (S11-R2). (4) **Renovação de tokens:** aviso ao proprietário **14 dias antes** do vencimento (hoje relato: 18/12/2026, aviso em 04/12/2026); a renovação é **ato dele**. (5) **Monitor do edital:** o fluxo existente do repositório (**não auditado aqui**). (6) **Auditoria por amostra** (R14). (7) **Deriva do contrato:** compara o SHA fixado com a `main` (R2). (8) **Parada** (R16). Falha de qualquer rotina **não envia nada** e **avisa**. | Tabela de rotinas testada: cada linha tem gatilho, executor, gate e falha segura; teste de que a rotina **diária** só existe com autorização registrada. |
| S14-R16 | **Parada e reversão testadas.** O proprietário pode **parar** o runtime em passos conhecidos: flags voltam a `false` por PR, token **revogado**, rotinas **desligadas**, SHA do contrato desfixado; o verificador **recusa** efeito sem recibo de produção. A parada é **exercida** na janela do piloto (S11-R12). | Procedimento escrito e verificado por teste de contrato; evidência na janela do piloto (relato com captura). |
| S14-R17 | **Fail-closed nas bordas; fail-open só em aviso.** Qualquer gate de **efeito** que não consiga decidir (leitura indisponível, resposta malformada, tempo esgotado) **recusa**. **Aviso** (lembrete de fim de rodada, sombra) pode falhar aberto. **A indisponibilidade de uma ferramenta impede o efeito externo, não a orientação pedagógica segura** (`AGENTS.md`). | Teste: cada gate de efeito, com leitura indisponível, **recusa**; orientação sem efeito **continua possível**. |
| S14-R18 | **Controle de mudança dos contratos em produção.** Pré-condição de produção real: o **agente tem identidade própria** no GitHub (usuário-máquina ou GitHub App) e o **`CODEOWNERS` fica ativo** (`require_code_owner_reviews` ligado) para `AGENTS.md`, `PRODUCT.md`, `agents/`, `.claude/`, `.github/` e o gateway; um **check de CI** reprova PR que altere esses caminhos sem a aprovação do dono. Hoje a **autoria é indistinguível** (o agente comita com o usuário do proprietário) e o **gate pode ser alterado junto com a mudança**; o **merge dele** é o único controle. Decisão e ato dele no GitHub; PR próprio. | Verificação por leitura autenticada da proteção da `main` (**relato dele até haver leitura**); teste do check de CI com fixtures; **sem isso o texto da S14 declara a produção "sem controle de mudança"**. |
| S14-R19 | **Honestidade sobre o que a produção não garante.** O runtime **não garante**: que o modelo leu e entendeu os contratos, que a explicação ou a recomendação é pedagogicamente boa, que a citação interpretada (além do literal) está certa, que a Zapia fez o que relatou, nem a veracidade de um resultado bem-formado. Garante, **quando os gates estiverem implantados e provados**: que **efeito externo** só ocorre pelo portão, que **leitura de projeção** exige consentimento v4 e lista fechada, que **entrega com alegação não verificável** é recusada ou avisada e que a **parada** funciona. A produção **não está homologada** (RM-01 a RM-07 em `implementado_nao_homologado`). | O texto termina com a linha **"Não garantido:"** e a lista; teste de presença. |

## Tarefas derivadas

Uma por vez, **fora deste PR**, cada uma um item de `work_queue` com testes e contraprovas:

1. **GE** — o script delivery_gate.py (a criar): envelope fechado, alegações verificadas, modo sombra e bloqueio (R5 a R8, R11, R13, R17).
2. **RS** — o script start_receipt.py (a criar): recibo de START e verificador (R2, R3).
3. **AE** — a suíte de avaliação do verificador (R12a), com envelopes sintéticos e adversariais; fecha parte de RM-06 e RM-07 **só para o que é gateável**.
4. **AM** — o gerador do relatório de amostra e do critério de pausa (R14).

**Não viram item de fila agora** (dependem de decisão ou ato dele): a rotina `registrar_*` (R9), a rotina diária da Zapia (R15, S8), o endurecimento de identidade e `CODEOWNERS` (R18) e o procedimento de parada em produção (R16, exercido na janela do piloto).

## Aceite

- Esta especificação passa em `doc_cohesion`, `product_gate`, `roadmap_gate`, `governance_sync_gate` e `single_flow_gate`, na suíte e na CI **no HEAD**.
- `tests/test_spec_s14.py` confere: R1 a R19 com critério; pesquisa com links, níveis B e C e linha de lacunas; a regra do proprietário; as três classes de garantia; a rastreabilidade; as rotinas; a ausência de portão por juiz-LLM; as tarefas derivadas na fila.
- **O aceite da produção não é este documento.** Depende do piloto (S11), das tarefas derivadas, da avaliação (R12), de **R18** e da decisão dele.

## Limites

- **Não implanta** gate, **não liga** flag, **não** altera `AGENTS.md`, `PRODUCT.md`, `agents/` nem `settings.json`, **não** grava resultado e **não** lê plataforma.
- **Não prova** nada contra o app Claude, a Zapia ou o portão reais; as afirmações do proprietário sobre o que fez continuam **relato**.
- **Nenhum gate avalia a qualidade da cognição**: ela é **livre por desenho** e controlada por avaliação offline e por amostra, **sem garantia**.
- **Não garantido:** que o modelo siga o contrato no chat direto; a veracidade de um resultado bem-formado; a conduta da Zapia; a utilidade pedagógica (RM-10); a produção como um todo.
