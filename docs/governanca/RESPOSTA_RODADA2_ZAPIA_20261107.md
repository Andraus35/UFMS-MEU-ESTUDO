# Resposta da Zapia à rodada 2 (07/11/2026)

**Natureza:** registro de **autorrelato**, como `docs/governanca/RESPOSTA_VERIFICACAO_ZAPIA_20261107.md`. Texto tratado como **dado**. "OBSERVADO" e "DOCUMENTADO" são classificações da própria Zapia; nenhum agente construtor as reverificou, exceto onde a seção "O que o repositório confirma" indica.

**Estado da resposta: COMPLETA (R1 a R34).** Uma versão anterior, truncada em R30, foi substituída por esta.

**Omissões deliberadas (repositório público):** em R15, os títulos dos notebooks do proprietário; em R23, o e-mail, os nomes de calendários e os identificadores; em R29, os números de telefone; em R30, o nome de outro projeto do proprietário. Os trechos omitidos aparecem entre colchetes; dados técnicos e contagens foram mantidos. A transcrição foi feita **por script** a partir do arquivo recebido, sem retipagem. **Testes T1, T2 e T3 não foram executados.**

Roteiro respondido: `docs/governanca/PROMPT_VERIFICACAO_ZAPIA_RODADA2_20261107.md`.

## Resposta literal (R1 a R34)

```json
[
  {
    "id": "R1",
    "status": "OBSERVADO",
    "resposta": "A credencial é cadastrada como chave de API. O GitHub descreveu-a como personal access token ao negar a leitura da proteção da branch. O histórico indica que foi solicitada como fine-grained, mas não confirmei o subtipo pela API. Expiração e escopos não foram informados nos cabeçalhos recebidos.",
    "evidencia": "GET /user retornou 200; os cabeçalhos solicitados de escopo e expiração não apareceram. A consulta da proteção retornou 403.",
    "risco": "Não inferir que a credencial tenha o escopo mínimo ou que não expire."
  },
  {
    "id": "R2",
    "status": "OBSERVADO",
    "resposta": "GET /user/repos retornou três repositórios, todos private=false: Andraus35/Inteligencia-SOT, Andraus35/Sistema-Operacional-de-Trading--SOT e Andraus35/UFMS-MEU-ESTUDO. Para cada um, o campo permissions retornou admin=true, push=true e pull=true. A segunda página veio vazia; nenhum privado foi listado.",
    "evidencia": "GET autenticado /user/repos?per_page=100, páginas 1 e 2.",
    "risco": "Os campos permissions não comprovam, isoladamente, as permissões efetivas específicas da credencial em cada endpoint."
  },
  {
    "id": "R3",
    "status": "OBSERVADO",
    "resposta": "UFMS-MEU-ESTUDO: private=false, visibility=public, default_branch=main; permissions admin=true, push=true, pull=true. A proteção de main não é legível com esta credencial: sem permissão.",
    "evidencia": "GET dos metadados do repositório; GET de branch protection retornou HTTP 403, recurso inacessível pelo token.",
    "risco": "O campo admin=true no repositório não demonstrou acesso administrativo efetivo à proteção."
  },
  {
    "id": "R4",
    "status": "DOCUMENTADO",
    "resposta": "É possível guardar credenciais separadas, com nomes distintos, e escolher uma referência nominal na chamada ao GitHub. O proprietário pode criar outra credencial com escopo para um repositório específico e fornecê-la pelo formulário seguro, sem colocar o valor no texto da conversa.",
    "evidencia": "Gerenciador de credenciais da Zapia; documentação do GitHub sobre tokens fine-grained por repositório.",
    "risco": "A separação depende de o proprietário configurar corretamente os repositórios e permissões no GitHub."
  },
  {
    "id": "R5",
    "status": "OBSERVADO",
    "resposta": "Gravar conteúdo: sim, foi executado nas POCs anteriores. Abrir PR: desconhecido, não testado e a permissão específica não foi obtida. Alterar workflows: desconhecido; exige permissão apropriada, não confirmada. Administrar repositório: não comprovado; leitura da proteção foi negada com 403 apesar de permissions.admin=true. Apagar branch: desconhecido, não testado.",
    "evidencia": "Commits anteriores; metadados atuais do repositório e resposta 403 da proteção de main.",
    "risco": "Não tratar o objeto permissions como autorização efetiva para todas as operações."
  },
  {
    "id": "R6",
    "status": "DOCUMENTADO",
    "resposta": "A API de conteúdo aceita mensagem de commit e objetos opcionais author e committer; a mensagem pode conter um trailer de identificação. Isso não foi testado nesta conversa. Nos commits da POC, a autoria e o committer apareceram como Andraus35, sem trailer de operação.",
    "evidencia": "Documentação GitHub REST de conteúdo: https://docs.github.com/en/rest/repos/contents ; leitura do commit 220ef558db9571265ce25a3194dd938666ce675f.",
    "risco": "Nome de autor em commit é metadado configurável e não constitui, sozinho, prova de identidade ou assinatura."
  },
  {
    "id": "R7",
    "status": "OBSERVADO",
    "resposta": "Na POC-007, li o arquivo e verifiquei um operation_id estável; ao repetir a mesma resposta, não fiz nova escrita e comparei o SHA do blob e o HEAD antes e depois. Para atualizar arquivos pela API de conteúdo, usei o SHA do blob existente. Consultei HEADs antes e depois, mas não demonstrei um bloqueio atômico por HEAD esperado.",
    "evidencia": "Teste sequencial da POC-007: blob e HEAD iguais antes e depois do no-op; atualização posterior documentada em commit.",
    "risco": "Esse procedimento não garante idempotência automática, exclusão mútua ou segurança contra escritas concorrentes."
  },
  {
    "id": "R8",
    "status": "DESCONHECIDO",
    "resposta": "Não há uma política única de novas tentativas comprovada para GitHub. 403 pode indicar falta de permissão ou limite; 404 pode indicar ausência ou acesso oculto; 409 e 422 exigem inspecionar conflito ou validação; rate limit exige respeitar o prazo informado pelo GitHub. Não executei testes controlados de cada código.",
    "evidencia": "Nesta rodada observei um 403 ao ler proteção; os demais comportamentos não foram testados.",
    "risco": "Não repetir cegamente escritas nem interpretar automaticamente um 404 como prova de inexistência."
  },
  {
    "id": "R9",
    "status": "DESCONHECIDO",
    "resposta": "Não forneço um mapeamento detalhado do ambiente interno. Posso executar Python e fazer chamadas HTTP permitidas; não estabeleci uma garantia geral de conectividade, memória ou duração para execuções futuras.",
    "evidencia": "As POCs anteriores executaram Python e acessaram GitHub e Google.",
    "risco": "Não assumir que ferramentas instaladas ou recursos de uma execução permanecerão disponíveis em outra."
  },
  {
    "id": "R10",
    "status": "DOCUMENTADO",
    "resposta": "Arquivos próprios podem persistir entre conversas, inclusive um script de verificação. Posso seguir a regra de usá-lo antes de gravar, mas não demonstrei uma trava técnica que impeça toda escrita por outro caminho. Dependências e artefatos de instalação podem precisar ser reinstalados.",
    "evidencia": "Comportamento documentado do espaço de arquivos da Zapia e testes anteriores de execução de Python.",
    "risco": "Um protocolo ou script isolado não equivale a um controle obrigatório tecnicamente imposto."
  },
  {
    "id": "R11",
    "status": "OBSERVADO",
    "resposta": "O arquivo scripts/bootstrap.py existe na branch feat/product-md-20261107 e Python pode ser executado. O executável Git não estava disponível na verificação desta sessão. Obter uma cópia por arquivo compactado e executar o bootstrap é uma alternativa possível, mas não foi testada; não sei estimar o tempo nem garantir que todas as dependências estarão disponíveis.",
    "evidencia": "GET do arquivo na branch solicitada; teste local de disponibilidade do executável Git. O bootstrap não foi executado.",
    "risco": "Executar código obtido de repositório exige revisar origem, versão e efeitos antes da execução."
  },
  {
    "id": "R12",
    "status": "OBSERVADO",
    "resposta": "Memórias do projeto atualmente visíveis para mim: 1) No projeto de estudos UFMS do André, o Gemini Notebook é pensado como ambiente de revisão, treinamento, retenção e recuperação de memória; TEC Concursos e Qconcursos são as plataformas para prática e banco de questões, conforme a arquitetura nas branches do repositório GitHub UFMS-MEU-ESTUDO. Zapia pode atuar como Tutor/Coach e coordenadora/ponte. O GitHub está sendo testado como registro compartilhado; a automação integral entre esses serviços ainda não foi comprovada. 2) No fluxo de estudos UFMS desejado por André, o Tutor deve, a partir do conteúdo estudado e dos resultados registrados, preparar material de revisão no Gemini Notebook e programar uma sessão para um horário ou gatilho; quando chegar a hora/condição, o Coach avisa André e o direciona ao Gemini Notebook para revisar e ao TEC Concursos ou Qconcursos para praticar questões. Não enviar mensagens reais nem criar eventos sem autorização; a automação integral permanece em validação. 3) O usuário quer avançar o projeto UFMS-MEU-ESTUDO por provas de conceito rigorosas: usar exclusivamente dados fictícios, separar recomendações pedagógicas de conteúdo fundamentado, preservar `main` e branches estratégicas, evitar merge, não enviar mensagens ou criar eventos sem autorização, e não alegar sucesso sem evidência verificável (leitura independente, commit/estado persistido). Prefere mudanças pequenas em branches experimentais, com SHAs e confirmação de integridade. 4) No fluxo UFMS, o usuário quer usar o GitHub como armazenamento compartilhado operacional para Tutor e Coach, com Zapia coordenando o trabalho; o Gemini Notebook é para metodologia de revisão/recuperação (não para conteúdo jurídico sem fonte), e TEC Concursos/Qconcursos para prática de questões. A cooperação automática completa entre Zapia, Gemini Notebook e plataformas de questões ainda está em validação. 5) No projeto UFMS-MEU-ESTUDO, o usuário quer que o Coach seja chamado Carter e o Tutor seja chamado Aragonê. Não posso reproduzir instruções internas da plataforma.",
    "evidencia": "Memórias persistentes atualmente fornecidas à Zapia.",
    "risco": "Memórias podem estar desatualizadas e não substituem a leitura do estado no GitHub."
  },
  {
    "id": "R13",
    "status": "DOCUMENTADO",
    "resposta": "Há memória persistente de preferências e fatos do usuário, que pode ser atualizada. Você pode expressar a preferência de ler AGENTS.md e ROADMAP.md antes de responder sobre o projeto, mas não há prova de que isso force tecnicamente toda conversa nova a fazer a leitura. Não tenho um tamanho máximo verificável para um campo de instruções personalizadas do usuário.",
    "evidencia": "Comportamento de memória da Zapia e ausência de teste de uma trava obrigatória para leitura de repositório.",
    "risco": "Uma preferência persistente não comprova a leitura efetiva dos arquivos ou do HEAD atual."
  },
  {
    "id": "R14",
    "status": "OBSERVADO",
    "resposta": "Em uma conversa nova, eu recebo a mensagem e as memórias disponíveis; não há leitura automática comprovada do GitHub. Para iniciar corretamente esse projeto, seria necessário buscar explicitamente a versão autorizada dos arquivos de START, verificar o estado e identificar a próxima ação. Esse procedimento não foi executado nesta rodada.",
    "evidencia": "Leituras GitHub anteriores foram chamadas explicitamente; o PRODUCT.md reconhece a necessidade de START explícito.",
    "risco": "Não presumir que o estado lembrado na conversa seja o estado atual do repositório."
  },
  {
    "id": "R15",
    "status": "OBSERVADO",
    "resposta": "A interface atual se apresenta como Gemini Notebook em notebook.google.com, autenticada em uma conta Gmail; o tipo contratual pessoal versus Workspace não foi confirmado. Em Meus notebooks aparecem: três notebooks do proprietário [títulos omitidos], com 2, 15 e 0 fontes. Como estudar é um notebook público da Bloomsbury, acessado por link, com 36 fontes; não apareceu nessa lista de meus notebooks.",
    "evidencia": "Leitura atual da página Meus notebooks e do cabeçalho do notebook Como estudar.",
    "risco": "Não presumir propriedade, plano ou acesso de edição ao notebook público."
  },
  {
    "id": "R16",
    "status": "OBSERVADO",
    "resposta": "O acesso foi realizado por navegador controlado pela Zapia. A sessão apareceu autenticada nesta visita e também nos testes anteriores; isso não garante autenticação permanente. Se expirar, for exigida verificação em duas etapas ou surgir captcha, o acesso pode precisar de intervenção ou nova autenticação.",
    "evidencia": "Interface atual mostrou a conta conectada; histórico de testes anteriores.",
    "risco": "A interface e a sessão podem mudar ou expirar."
  },
  {
    "id": "R17",
    "status": "OBSERVADO",
    "resposta": "Em 04/11 houve um teste agendado único que reportou consulta concluída ao Notebook sem nova solicitação no momento do disparo. Isso não prova confiabilidade recorrente. Não medi tempo típico de consulta.",
    "evidencia": "Histórico da POC com tarefa única agendada às 10h32 e resultado reportado posteriormente.",
    "risco": "Sessão, captcha, termos do Google ou alterações da interface podem impedir execuções futuras."
  },
  {
    "id": "R18",
    "status": "DOCUMENTADO",
    "resposta": "A documentação do Google descreve criação de notebooks e adição de fontes; essas operações não foram testadas agora. O plano Standard documentado tem 100 notebooks por usuário e 50 fontes por notebook; a FAQ cita até 500.000 palavras por fonte ou 200 MB por upload local. A quota diária de consultas aplicável à sua conta não foi confirmada.",
    "evidencia": "https://support.google.com/gemininotebook/answer/16206563 ; https://support.google.com/gemininotebook/answer/16213268 ; https://support.google.com/gemininotebook/answer/16269187",
    "risco": "Limites podem mudar e variam conforme plano; não confirmei o plano efetivo da conta."
  },
  {
    "id": "R19",
    "status": "DESCONHECIDO",
    "resposta": "Não foi observado um teste do formato exato com assunto, lacuna, fonte e trecho. Nas POCs, o Notebook produziu listas estruturadas em resposta a pedidos, mas isso não garante obediência a um esquema específico.",
    "evidencia": "Respostas anteriores com etapas e citações; nenhum teste do formato pedido nesta pergunta.",
    "risco": "Uma saída estruturada precisa ser validada antes de processamento automático."
  },
  {
    "id": "R20",
    "status": "OBSERVADO",
    "resposta": "As respostas exibem marcadores numerados ligados a títulos de fontes. Ao abrir um marcador, a interface mostrou um trecho da fonte; não observei uma página específica para essa citação. Um título citado apenas no corpo da resposta não é fonte efetivamente inspecionada.",
    "evidencia": "Na POC-005, abri o marcador de Ace Your Exam e conferi o trecho; outras fontes citadas não foram todas abertas.",
    "risco": "Não atribuir confirmação de fonte ou número de página sem leitura correspondente."
  },
  {
    "id": "R21",
    "status": "DOCUMENTADO",
    "resposta": "Não consultei as configurações de atividade dessa conta. Para verificar, o proprietário pode abrir Conta Google > Dados e privacidade > Configurações do histórico, e consultar a atividade dos Apps Gemini quando disponível. A política específica do Notebook deve ser conferida no aviso do Google.",
    "evidencia": "Aviso do Google: https://support.google.com/gemininotebook/answer/17004255",
    "risco": "Não presumir que desativar uma configuração do Gemini controle toda retenção do Notebook. O Google informa tratamento adicional quando o usuário envia feedback."
  },
  {
    "id": "R22",
    "status": "OBSERVADO",
    "resposta": "As integrações são Google Calendar e Google Tasks. O retorno de autenticação informou Calendar com escopos calendar e calendar.readonly e Tasks com tasks; eles contemplam leitura e escrita, conforme a autorização recebida. A leitura atual de calendários e listas funcionou. A permissão em cada calendário depende do papel retornado; a lista de Tasks não retornou papel de acesso.",
    "evidencia": "Eventos de autorização Google de 04/11 e consultas atuais de metadados de calendários e listas.",
    "risco": "Escopo concedido não substitui a verificação de permissão efetiva em cada recurso."
  },
  {
    "id": "R23",
    "status": "OBSERVADO",
    "resposta": "Calendários: o calendário principal do proprietário, papel owner; um calendário \"Família\", papel owner; dois calendários de feriados do Brasil, papel reader [e-mail, nomes e identificadores omitidos]. Lista de tarefas: uma lista padrão, papel não retornado pela API.",
    "evidencia": "Consultas atuais somente dos metadados de calendários e listas.",
    "risco": "O calendário Família é compartilhado/agrupado; o papel exibido não identifica sozinho a titularidade pessoal de cada participante."
  },
  {
    "id": "R24",
    "status": "DOCUMENTADO",
    "resposta": "O Calendar suporta extendedProperties.private em eventos; a ferramenta de criação também apresenta um campo para propriedade privada. Não testei gravar esse campo. A definição de ID próprio estável pelo caminho de criação disponível não foi demonstrada nesta conversa.",
    "evidencia": "Metadados de capacidade da integração Calendar; nenhuma criação com ID próprio ou propriedade privada foi executada.",
    "risco": "Não assumir que um ID arbitrário será aceito: o Google impõe regras para IDs de eventos."
  },
  {
    "id": "R25",
    "status": "OBSERVADO",
    "resposta": "Em 04/11, as exclusões retornaram deleted=true; uma segunda tentativa de exclusão do evento retornou HTTP 410 deleted. As leituras textuais seguintes mostraram os objetos, mas não exibiram os campos técnicos de exclusão. Nesta rodada, uma consulta apenas desses campos retornou Calendar status=cancelled e Tasks deleted=true, status=needsAction; hidden não foi retornado. Isso corrige minha conclusão anterior: há agora evidência de que o evento está cancelado e a tarefa marcada como excluída, embora seus registros ainda sejam recuperáveis por ID. Não tenho os códigos HTTP exatos das primeiras exclusões nem leituras.",
    "evidencia": "Histórico das chamadas de exclusão e consultas atuais por ID selecionando exclusivamente status, deleted e hidden.",
    "risco": "Cancelamento ou marcação deleted não comprovam eliminação física irreversível dos dados."
  },
  {
    "id": "R26",
    "status": "OBSERVADO",
    "resposta": "Calendar principal: America/Campo_Grande, lembrete padrão popup 30 minutos antes; há configurações de e-mail para alterações de eventos. Calendário Família: UTC e popup padrão de 30 minutos. Para Tasks, os metadados consultados não informaram preferência de lembrete ou canal. Não verifiquei configurações Android nem se alertas chegam ao celular.",
    "evidencia": "Leitura atual dos metadados de calendários; nenhuma leitura de conteúdo de evento ou tarefa nesta rodada.",
    "risco": "Um popup configurado não comprova sua entrega no dispositivo."
  },
  {
    "id": "R27",
    "status": "OBSERVADO",
    "resposta": "No teste da POC-008, consultei a agenda e a lista antes de criar um evento e uma tarefa; havia uma associação lógica por identificador da atividade. Não foi demonstrado um mecanismo automático de deduplicação dos lembretes. A POC-007 testou um no-op sequencial por operation_id no GitHub, não no Calendar ou Tasks.",
    "evidencia": "Leituras e criação da POC-008; teste sequencial da POC-007.",
    "risco": "Consultas prévias não eliminam duplicações causadas por concorrência ou repetição após falha."
  },
  {
    "id": "R28",
    "status": "OBSERVADO",
    "resposta": "O agendador aceita tarefas únicas e recorrentes. Uma tarefa estática mostra texto fixo no app; uma tarefa com execução de agente pode usar ferramentas e gerar conteúdo. Foram observados um lembrete estático entregue no app e um teste pontual agendado de consulta ao Notebook. Execução agendada de Python ou de escrita no GitHub não foi comprovada nesta conversa.",
    "evidencia": "Agendamentos e resultados observados em 04/11; configuração do agendador da Zapia.",
    "risco": "Uma execução pontual não prova confiabilidade de uma rotina recorrente nem elimina limites de plano."
  },
  {
    "id": "R29",
    "status": "OBSERVADO",
    "resposta": "Na POC-006, o comando de identidade retornou o chat [identificador de 12 dígitos, omitido], enquanto o estado da conexão e o contexto da conta indicavam [número de 13 dígitos, omitido]. Envios direcionados ao segundo foram registrados pelo conector no primeiro; você informou que não recebeu as mensagens. Não identifiquei a causa nem uma correção comprovada. No Telegram, a documentação da integração diz que operações de envio e abertura de conversa exigem aprovação; não verifiquei a duração ou reutilização específica dessa aprovação para cada caso.",
    "evidencia": "Resultados dos comandos de identidade, conexão e histórico de 04/11; seu relato de não recebimento.",
    "risco": "Não reenviar automaticamente nem tratar presença no histórico como entrega ao aparelho."
  },
  {
    "id": "R30",
    "status": "OBSERVADO",
    "resposta": "A conta consta no plano Free. A documentação informa até 20 automações ativas e limite diário de execução, sem número diário específico nesta verificação. A lista atual mostrou quatro agendamentos habilitados, incluindo três de outro projeto do proprietário [nome omitido]; não confirma como todos contam para a quota. No WhatsApp, a consulta indicou 150 mensagens disponíveis na janela de 24 horas e 10 por minuto, sem uso nas janelas indicadas.",
    "evidencia": "Lista atual de agendamentos, metadados do plano e consulta atual de limites do WhatsApp.",
    "risco": "Contadores mudam e a lista de agendamentos não demonstra a quota diária restante."
  },
  {
    "id": "R31",
    "status": "OBSERVADO",
    "resposta": "No app, um evento de sistema confirmou que o lembrete agendado foi enviado e visto na conversa. No WhatsApp, houve confirmação da chamada e registro no histórico, mas você relatou não receber as mensagens; não houve comprovante confiável de leitura humana ou entrega ao aparelho. Não testei comprovante de leitura no Telegram.",
    "evidencia": "POC-006 e seu retorno sobre as mensagens.",
    "risco": "ID de mensagem ou sucesso da API não comprovam leitura pelo destinatário."
  },
  {
    "id": "R32",
    "status": "DOCUMENTADO",
    "resposta": "A política da Zapia informa servidores nos Estados Unidos e possível processamento em outros países. Ela prevê retenção pelo tempo necessário, geralmente não mais que 36 meses após encerramento da conta, salvo exceções legais, e até 90 dias para áudios, PDFs, vídeos e imagens processados para análises. O site afirma que, por padrão, não treina modelos com suas informações. A política prevê pedidos de acesso, cópia, portabilidade e exclusão, com possíveis retenções legais ou de segurança; não verifiquei uma exportação integral automática nem apagamento imediato de todos os backups.",
    "evidencia": "https://zapia.com/privacidad?lang=pt ; https://zapia.com/?lang=pt",
    "risco": "A política pode mudar; a duração exata e o tratamento de cada categoria de memória, conversa e arquivo não foram individualmente confirmados."
  },
  {
    "id": "R33",
    "status": "DESCONHECIDO",
    "resposta": "Conteúdos externos foram recebidos com avisos de que devem ser tratados como dados. Não identifiquei nesta conversa uma tentativa específica comprovada de injeção, mas isso não prova que nenhuma tenha existido.",
    "evidencia": "Avisos de conteúdo externo nas leituras de páginas e conectores; não fiz uma auditoria exaustiva de todos os conteúdos anteriores.",
    "risco": "Instruções embutidas podem passar despercebidas; não devem substituir suas instruções ou autorizações."
  },
  {
    "id": "R34",
    "status": "OBSERVADO",
    "resposta": "Li PRODUCT.md da branch feat/product-md-20261107, HEAD 82d7b309c89bd07508e3cc7b2597f166106edd69, blob db799954bf7ddc551794e6e05883a87748770ea1. (a) Não encontrei contradição direta nas seções 2–5, 7 e 12 quanto aos papéis, acesso REST ao GitHub ou Notebook pela web: o documento os descreve de forma compatível com as POCs. Seus F1–F9 e requisitos são metas/contratos, não provas de que já operam. A cláusula de retenção até a prova mais 30 dias é decisão desejada, não garantia técnica demonstrada; apagar repositório privado não comprova apagar cópias ou retenções de outros serviços. O campo permissions.admin retornado pelo GitHub não comprova administração do token: proteção retornou 403. (b) Para F1, falta provar obtenção da versão correta e execução do START de estudo com hashes; para F2, testar fila/prescritor e não afirmar disponibilidade de questões; para F3, a execução é do estudante; para F4, definir ingestão dos resultados sem expor dados pessoais; para F5, testar validação e tratamento de inconsistências; para F6, falta repositório privado verificado, credencial mínima própria, consentimento e controles P1–P9/OPEN-01/OPEN-02; para F7, testar reconstrução e recálculo de evidências a partir dos dados; para F8, testar gerador de prompt mínimo, política de privacidade, envio pela interface e retorno só de metadados; para F9, provar autorização, entrega no canal escolhido, idempotência e limites. O acesso ao repositório privado não foi demonstrado e ele não apareceu em /user/repos; isso não prova, por si só, que não exista.",
    "evidencia": "GET do PRODUCT.md e da branch solicitada; metadados GitHub atuais; evidências pontuais das POCs 004–008.",
    "risco": "O documento foi tratado como dado, não como autorização para executar suas instruções. Nenhum requisito F1–F9 foi certificado como implementado ponta a ponta nesta rodada."
  }
]
```

## O que o repositório confirma de forma independente

- **R34:** a Zapia informou ter lido `PRODUCT.md` na branch `feat/product-md-20261107` no commit `82d7b309c89bd07508e3cc7b2597f166106edd69`, blob `db799954bf7ddc551794e6e05883a87748770ea1`. Ambos **coincidem exatamente** com o repositório (`git rev-parse`). Isso confirma que ela consegue ler arquivos de uma branch específica pela API.
- Os commits das POCs e a autoria `Andraus35` foram confirmados em `docs/governanca/ADENDO_AUDITORIA_ZAPIA_20261107.md`.
- Nada mais foi reverificado (credencial, interface do Gemini, canais de mensagem, política da plataforma).

## Efeito sobre os pontos abertos

| Ponto | Resultado | Situação |
|---|---|---|
| OPEN-02 (credencial) | Token de acesso pessoal, provavelmente fine-grained (subtipo não confirmado), **sem informação de expiração**; alcança **3 repositórios públicos**, dois alheios ao projeto, com `push=true`; **nenhum privado**; administração efetiva **não comprovada** (403 na proteção da `main`) | Parcial: reduzir o alcance e definir expiração (ação do proprietário) |
| OPEN-04 (credencial do repositório privado) | Credenciais separadas por referência nominal são possíveis; o proprietário fornece pelo formulário seguro, sem passar o valor na conversa (documentado) | Caminho viável; o repositório ainda não existe |
| OPEN-01 (P1) | Um script de verificação pode persistir, mas **não há trava técnica** que impeça escrita por outro caminho (R7, R10, R13) | Continua bloqueando o PR-003 |
| OPEN-03 (mecanismo do Gemini) | Interface web controlada por navegador; sessão pode expirar, exigir verificação em duas etapas ou captcha; 1 teste agendado único em 04/11 | Mecanismo resolvido; estabilidade não comprovada |
| OPEN-05 (privacidade do Gemini) | Não verificada; caminho para o proprietário conferir informado (R21) | Aberto; ação do proprietário |
| OPEN-06 (exclusão no Google) | Exclusão **lógica** comprovada (`status=cancelled`, `deleted=true`, HTTP 410); eliminação física não | Praticamente resolvido |
| OPEN-07 (notebook de revisão) | "Como estudar" é público, de terceiros, fora dos notebooks do proprietário | Aberto; decisão do proprietário |
| **OPEN-08 (novo): consentimento e ciclo de vida dos dados** | A plataforma da Zapia armazena conversas, memórias e arquivos em **servidores nos Estados Unidos**, com retenção geral de **até 36 meses após o encerramento da conta** e até 90 dias para áudios, PDFs, vídeos e imagens; por padrão não treina modelos; exclusão e portabilidade por pedido, sem backup apagado comprovado (R32, documentado) | **O consentimento v1 e a decisão D-03 não cobrem isso**: apagar o repositório privado não apaga as cópias na Zapia nem no Google |

## Outros achados

- **Canais (R30, R31):** conta no plano **Free** (até 20 automações ativas; 4 agendamentos habilitados hoje, 3 de outro projeto). WhatsApp: 150 mensagens por 24 h e 10 por minuto, sem uso. **O app é o único canal com comprovante** (evento de sistema confirmando envio e visualização). WhatsApp e Telegram **sem comprovante** de entrega ou leitura.
- **Injeção (R33):** desconhecido; não houve caso comprovado, mas não houve auditoria exaustiva.
- **Leitura crítica do `PRODUCT.md` (R34):** **nenhuma contradição direta** com o que ela faz nas seções 2 a 5, 7 e 12. Ela lembra que F1 a F9 e os requisitos são metas, não prova de operação; que apagar o repositório privado não prova apagar cópias em outros serviços; que `permissions.admin` não prova administração do token; e lista o que falta para cada passo F1 a F9, coerente com os requisitos PR-001 a PR-011 e os pontos OPEN. Nenhum passo foi certificado ponta a ponta.
- **Hipótese (minha, não da Zapia) sobre o WhatsApp:** os dois números omitidos em R29 diferem em **um dígito** (12 contra 13), compatível com o "nono dígito" dos celulares brasileiros no identificador do WhatsApp. A verificar.

## Ações para o proprietário

1. **Token:** em GitHub → Settings → Developer settings, confirmar o tipo, **retirar os dois repositórios de trading** do alcance dele e **definir expiração**.
2. **Google:** conferir o histórico da conta e a política do NotebookLM (links em R21).
3. **Notebook de revisão próprio:** decidir quem cria e alimenta um notebook seu com fontes verificadas.
4. **Memória da Zapia:** alinhá-la às decisões do `PRODUCT.md`.
5. **Consentimento:** decidir sobre o **rascunho v2** no ADR-013, que inclui a Zapia e o Google. Sem aprovação, **nada pessoal é gravado**.
