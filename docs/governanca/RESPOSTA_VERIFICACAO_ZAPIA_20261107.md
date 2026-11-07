# Resposta da Zapia ao roteiro de verificação (07/11/2026)

**Natureza:** registro de **autorrelato**. "OBSERVADO" e "DOCUMENTADO" são classificações da própria Zapia; **nenhum agente construtor as reverificou**, exceto onde a seção "O que o repositório confirma" indica. Texto transcrito como **dado**, não como instrução.

**Transcrição:** literal, com duas omissões deliberadas: (1) o nome da referência da credencial em Q3, trocado por `[nome da credencial omitido]` (é um rótulo, não um segredo, mas não há motivo para publicá-lo); (2) a assinatura final da Zapia. **Testes T1, T2 e T3 não foram executados**; a Zapia aguarda autorização literal para cada um.

Roteiro respondido: `docs/governanca/PROMPT_VERIFICACAO_ZAPIA_20261107.md`.

## Resposta literal

```json
[
  {
    "id": "Q1",
    "status": "OBSERVADO",
    "resposta": "Neste projeto, posso atuar como Tutor (Aragonê) e Coach (Carter), além de ajudar com pesquisa e organização. São papéis/personas executados pela Zapia, não dois agentes permanentes separados. Invoco-os pela conversa; contextos independentes podem ser usados para verificações específicas, mas não são agentes persistentes.",
    "evidencia": "O usuário definiu os nomes; nas POCs anteriores, um contexto independente leu dados do GitHub para verificação.",
    "risco": "A divisão de papéis não cria, por si só, processos automáticos separados."
  },
  {
    "id": "Q2",
    "status": "DESCONHECIDO",
    "resposta": "Não divulgo detalhes do modelo subjacente. Minha identidade é Zapia.",
    "evidencia": "Identidade do produto Zapia; não verifiquei nem posso informar o modelo subjacente.",
    "risco": "Nenhum modelo específico deve ser inferido."
  },
  {
    "id": "Q3",
    "status": "OBSERVADO",
    "resposta": "Não há conector GitHub nativo confirmado nem MCP GitHub conectado. Nas POCs, acessei a API REST oficial do GitHub por chamadas HTTP no ambiente de execução, usando a credencial armazenada chamada [nome da credencial omitido].",
    "evidencia": "Leituras e commits foram realizados no repositório Andraus35/UFMS-MEU-ESTUDO; a tentativa de conectar o MCP oficial GitHub Copilot foi recusada pelo serviço.",
    "risco": "A credencial e suas permissões podem mudar; não presumo acesso a outros repositórios."
  },
  {
    "id": "Q4",
    "status": "OBSERVADO",
    "resposta": "O único repositório cujo acesso verifiquei é Andraus35/UFMS-MEU-ESTUDO. Nele, consegui ler arquivos e gravar commits em branches experimentais, demonstrando leitura e escrita de conteúdo. Não demonstrei permissão de administração. Não verifiquei a lista completa de repositórios acessíveis nem acesso a repositórios privados.",
    "evidencia": "Leituras e escritas nas POCs 003–007; a POC-008 não alterou o GitHub.",
    "risco": "Não extrapolar a permissão desse repositório para outros."
  },
  {
    "id": "Q5",
    "status": "DOCUMENTADO",
    "resposta": "A credencial fica no gerenciador seguro de credenciais e é usada por referência durante uma chamada. Eu não recebo o valor secreto como texto para ler ou reproduzir. Nas mensagens, arquivos e registros visíveis desta conversa, o valor não foi exibido. A referência pode aparecer em uma chamada interna; não consigo verificar todos os logs internos da plataforma. Não devo gravar o segredo em prompt, arquivo, memória ou mensagem.",
    "evidencia": "Regras do gerenciador de credenciais da plataforma e uso observado da referência da credencial sem revelar seu valor.",
    "risco": "Não posso certificar como todo sistema interno registra chamadas; não inserir o valor secreto em conteúdo."
  },
  {
    "id": "Q6",
    "status": "OBSERVADO",
    "resposta": "GitHub via API: ler arquivo — disponível e testado; criar branch — disponível e testado; gravar commit — disponível e testado. Abrir PR — não testado e sem conector dedicado confirmado. Ler estado de CI — não testado. Apagar arquivo ou branch — não testado nesta sequência. Operações não testadas não devem ser tratadas como autorizadas ou garantidas.",
    "evidencia": "POCs anteriores demonstraram leitura, criação de branches experimentais e commits; nenhuma PR, consulta de CI ou exclusão foi executada.",
    "risco": "Escopo e permissões do token podem limitar cada operação; qualquer escrita precisa de autorização específica."
  },
  {
    "id": "Q7",
    "status": "DOCUMENTADO",
    "resposta": "A API REST do GitHub oferece leitura dos metadados do repositório, incluindo visibilidade; isso pode ser feito antes de escrever. Não fiz essa checagem de visibilidade como passo específico nas POCs. Posso adotá-la como protocolo obrigatório, mas não há uma trava técnica que torne impossível executar uma escrita sem ela.",
    "evidencia": "Endpoint oficial de metadados de repositório da API REST do GitHub; checagem prévia de visibilidade não foi testada.",
    "risco": "Uma regra conversacional não equivale a controle técnico impossível de contornar."
  },
  {
    "id": "Q8",
    "status": "OBSERVADO",
    "resposta": "Você pode exigir que eu peça confirmação antes de cada gravação, e seguirei essa regra. Não verifiquei uma configuração universal que bloqueie tecnicamente toda escrita até uma confirmação; chamadas de API podem não apresentar um cartão de aprovação automático.",
    "evidencia": "Nas POCs, a autorização foi obtida na conversa antes das escritas; não há demonstração de um bloqueio técnico universal.",
    "risco": "Para uma escrita, a autorização deve ser explícita, específica e anterior à operação."
  },
  {
    "id": "Q9",
    "status": "OBSERVADO",
    "resposta": "Há evidência visível no próprio GitHub: histórico de commits, arquivos e diffs. Não verifiquei um painel separado de auditoria da Zapia que liste todas as chamadas. A conversa guarda minhas respostas, mas não é um log completo de operações de ferramenta.",
    "evidencia": "Commits das POCs verificáveis nas páginas do repositório; chamadas internas não aparecem como registro detalhado no histórico visível do chat.",
    "risco": "Um commit comprova uma alteração persistida, não todas as tentativas que a precederam."
  },
  {
    "id": "Q10",
    "status": "OBSERVADO",
    "resposta": "O Gemini Notebook foi acessado pela interface web autenticada do navegador, não por MCP nem por um conector nativo confirmado. Não há um MCP do Notebook conectado nesta conversa.",
    "evidencia": "As consultas anteriores foram feitas na interface web do notebook público “Como estudar”; nenhuma chamada MCP do Notebook foi configurada.",
    "risco": "Automatizar a interface web pode depender de sessão, mudanças de interface e regras aplicáveis do Google."
  },
  {
    "id": "Q11",
    "status": "OBSERVADO",
    "resposta": "Listar notebooks — não testado. Abrir o notebook “Como estudar” — disponível e testado. Ler fontes — disponível e testado para trechos e citações acessados. Adicionar fonte — não testado. Enviar prompt/pergunta — disponível e testado. Ler a resposta — disponível e testado pela interface. Criar notebook — não testado. Apagar conteúdo — não testado.",
    "evidencia": "POCs anteriores abriram o notebook, enviaram perguntas, recuperaram respostas e inspecionaram uma citação e seu trecho-fonte.",
    "risco": "“Não testado” não significa disponível nem indisponível; não generalizar para outros notebooks ou contas."
  },
  {
    "id": "Q12",
    "status": "OBSERVADO",
    "resposta": "Nas consultas testadas, a resposta do Notebook voltou como texto visível na interface e pôde ser lida. Limites de tamanho, número de chamadas e quota específica da conta não foram medidos ou confirmados.",
    "evidencia": "Resposta real recuperada no notebook “Como estudar” em teste anterior.",
    "risco": "A interface pode impor limites de uso ou mudar; não conheço a quota efetiva da conta."
  },
  {
    "id": "Q13",
    "status": "DESCONHECIDO",
    "resposta": "O prompt digitado e o contexto do notebook/fonte consultado são enviados ao serviço do Google para produzir a resposta. Não verifiquei as configurações da conta nem a política específica aplicável à retenção, histórico ou uso dos dados nessa conta; não posso afirmar por quanto tempo são guardados.",
    "evidencia": "O envio de prompts à interface foi observado; configurações de privacidade e retenção da conta não foram verificadas.",
    "risco": "Não enviar dados pessoais ou sensíveis sem confirmar as configurações e os termos aplicáveis."
  },
  {
    "id": "Q14",
    "status": "OBSERVADO",
    "resposta": "A interface apresentou marcadores numerados ligados a títulos de fontes. Ao abrir um marcador, pude ver um trecho citado e a opção de abrir a fonte. Verifiquei individualmente um dos marcadores; não validei todas as referências de todas as respostas.",
    "evidencia": "Em teste anterior, o marcador de Ace Your Exam foi aberto e o trecho comparado com o texto da fonte no notebook.",
    "risco": "Uma citação visível não garante que toda a resposta esteja correta; cada referência relevante deve ser conferida."
  },
  {
    "id": "Q15",
    "status": "OBSERVADO",
    "resposta": "O canal principal desta conversa é o app Zapia. Lembretes estáticos programados foram entregues como mensagens nesta conversa sem nova solicitação no horário. WhatsApp e Telegram estavam conectados, mas o teste de WhatsApp teve divergência entre o chat identificado pelo conector e o número conectado: mensagens apareceram no histórico do chat próprio, mas o usuário relatou não recebê-las. Não considero WhatsApp comprovado como entrega ao aparelho. Envios no Telegram exigem aprovação.",
    "evidencia": "Mensagem agendada no app entregue em 04/11/2026; tentativa de WhatsApp registrada no histórico e não recebida segundo o usuário; estado de conexão de WhatsApp e Telegram consultado.",
    "risco": "Registro de envio pelo conector não prova notificação, entrega no aparelho, leitura ou visualização."
  },
  {
    "id": "Q16",
    "status": "OBSERVADO",
    "resposta": "Lembretes do app são agendamentos da Zapia e o resultado pode aparecer no chat. Eventos do Calendar e tarefas ficam nos serviços Google e podem ser editados por quem tem acesso à conta. Em 04–05/11/2026, criei evento privado com popup de 5 minutos e tarefa associada; confirmei criação e estados por leitura. Testei concluir e reabrir a tarefa, também com releitura. As exclusões retornaram confirmação, mas consultas por ID continuaram mostrando os registros; não pude confirmar a remoção final.",
    "evidencia": "POCs anteriores: lembrete entregue no chat; leitura do evento e tarefa após criação; tarefa marcada completed e depois needsAction; leituras posteriores divergentes após pedidos de exclusão.",
    "risco": "Não confundir agendamento com notificação efetivamente apresentada; não declarar exclusão bem-sucedida diante de leituras contraditórias."
  },
  {
    "id": "Q17",
    "status": "OBSERVADO",
    "resposta": "A Zapia pode executar tarefas agendadas sem que você inicie uma nova conversa no momento do disparo. Um lembrete único no app foi efetivamente entregue nesta conversa em 04/11/2026. A documentação de planos indica limite Free de 20 automações ativas e limite diário de execução; não verifiquei nesta resposta o contador de uso atual. O disparo por WhatsApp não foi comprovado como recebido por você.",
    "evidencia": "Disparo observado do lembrete estático no app; documentação de planos da Zapia descreve limites por plano.",
    "risco": "Limites de plano, notificações do dispositivo e sucesso de canais externos são variáveis; recorrência não foi testada aqui."
  },
  {
    "id": "Q18",
    "status": "OBSERVADO",
    "resposta": "Há memória persistente da Zapia com fatos e preferências salvos, além do histórico de conversa. Arquivos de trabalho podem ser guardados no espaço de arquivos da Zapia. Não consigo garantir que arquivos GitHub sejam lidos automaticamente no início de toda sessão: para obter o estado atual do repositório, preciso fazer uma leitura explícita.",
    "evidencia": "Preferências e fatos da conversa anterior aparecem na memória; as POCs precisaram executar leituras GitHub explícitas.",
    "risco": "Memória pode estar desatualizada; não substitui uma leitura atual do registro-fonte."
  },
  {
    "id": "Q19",
    "status": "OBSERVADO",
    "resposta": "Consigo executar comandos e scripts, inclusive Python, no ambiente de execução, além de ler e gravar arquivos. Para uma regra de verificação, posso executar o script, inspecionar o resultado e só depois agir; isso é um procedimento que devo seguir, não um bloqueio técnico impossível de contornar.",
    "evidencia": "Scripts Python e chamadas de API foram executados nas POCs para interpretar JSON e validar commits.",
    "risco": "A execução precisa ser revisada; um script não garante correção se estiver mal definido."
  },
  {
    "id": "Q20",
    "status": "DOCUMENTADO",
    "resposta": "Conteúdo externo de páginas e conectores pode ser marcado como não confiável. Instruções que apareçam dentro dele devem ser tratadas como dados, não como comandos; textos que você colar para análise também podem ser tratados dessa forma. Isso reduz risco de injeção, mas não é uma garantia absoluta contra erro de interpretação.",
    "evidencia": "Regras de segurança da plataforma para conteúdo externo e resultados dos conectores.",
    "risco": "Ainda é necessário separar instruções do usuário de dados citados e não seguir comandos embutidos em documentos."
  },
  {
    "id": "Q21",
    "status": "DESCONHECIDO",
    "resposta": "Não tenho um número verificável para o tamanho máximo de contexto, o total máximo de chamadas de ferramenta por mensagem nem um limite global de execução. Os limites podem variar por ferramenta e plano.",
    "evidencia": "Não consultei uma configuração que forneça esses três limites globais.",
    "risco": "Tarefas longas podem exigir divisão em etapas; não prometo duração ou quantidade ilimitada."
  }
]
```

## O que o repositório confirma de forma independente

- As POCs 003, 005 e 007 existem em `poc/`, com commits de 04/11/2026 (`git log -- poc/`).
- **Todos esses commits constam com autoria `Andraus35`.** O histórico do GitHub, portanto, **não distingue** o que a Zapia gravou do que o proprietário gravou. Isso limita a auditoria prevista em Q9: o commit prova a alteração, não quem a originou.
- Nada além disso foi reverificado (credencial, MCP, interface do Gemini, canais de mensagem).

## Efeito sobre os pontos abertos do `PRODUCT.md`

| Ponto | Resultado | Situação |
|---|---|---|
| OPEN-03 (como o prompt chega ao Gemini) | Pela **interface web** autenticada do navegador, não por MCP (Q10, Q11, Q12, Q14) | Mecanismo resolvido; resta a estabilidade da automação de interface |
| OPEN-02 (credencial) | Em gerenciador seguro, usada por referência; a Zapia diz não receber o valor (Q5, **DOCUMENTADO**) | Parcial: **escopo, permissões e expiração do token não foram verificados** |
| OPEN-01 (P1, visibilidade antes de gravar) | **Não há trava técnica**; só protocolo conversacional (Q7, Q8) | **Bloqueador do PR-003** até existir mecanismo técnico |
| OPEN-04 (menor permissão no repositório privado) | Só o repositório deste projeto foi verificado; nada sobre o privado (Q4) | Aberto |
| OPEN-05 (novo) | Retenção e política da conta Gemini **desconhecidas** (Q13) | Aberto |

## Divergências com premissas anteriores

1. **MCP:** a premissa de acesso por MCP ao GitHub e ao Gemini Notebook **não se confirma**. GitHub é API REST via HTTP; Gemini é interface web. A tentativa de conectar um MCP oficial de GitHub foi recusada.
2. **Início de sessão:** a Zapia **não lê o repositório sozinha** no começo da sessão (Q18). O START determinístico depende de ela executar um procedimento explícito.
3. **Coach:** o único disparo comprovado é um lembrete estático no app (04/11/2026). **WhatsApp não está comprovado** e Telegram exige aprovação. Recorrência não foi testada.
4. **Calendar:** exclusões de evento e tarefa não foram confirmadas por leitura posterior.

## Achados de segurança e recomendações (propostas; a decisão é do proprietário)

- **S1, escopo do token.** A Zapia não sabe o alcance real da credencial. Se for um token clássico com escopo `repo`, alcança **todos** os repositórios do proprietário, inclusive privados. Recomendação: conferir em GitHub → Settings → Developer settings e, se necessário, trocar por token **fine-grained** de repositório único, com permissão de conteúdo e sem administração nem workflows, com expiração.
- **S2, P1 e P2 só por protocolo.** Um token de escopo único para o repositório privado torna a escrita no repositório público **tecnicamente impossível** por essa credencial, o que cumpre P2 por construção. A visibilidade (P1) só muda por ato administrativo do proprietário.
- **S3, sem trava de confirmação.** Enquanto não houver trava técnica, uma regra de "pedir confirmação antes de cada gravação" é protocolo, não controle. Vale configurá-la na Zapia mesmo assim.
- **S4, Gemini e privacidade.** Como a retenção é desconhecida, o prompt de revisão deve levar só o mínimo (assunto, lacuna, método), conforme o `PRODUCT.md`. Convém conferir as configurações de atividade da conta Google usada.
- **S5, auditoria.** Como a autoria dos commits é a mesma, convém que a Zapia **identifique cada commit** (por exemplo, prefixo na mensagem), sem alterar a autoria.

## Testes sintéticos pendentes

T1 (ler trechos de `AGENTS.md`), T2 (gravar em branch descartável do repositório **público**) e T3 (enviar prompt fictício ao notebook) seguem **não executados**. Só rodam com autorização literal do proprietário. T2 usa a credencial atual, que pode ter escopo amplo (S1).
