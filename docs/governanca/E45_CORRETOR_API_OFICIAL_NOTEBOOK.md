# E45: proposta do corretor fora do modelo com a API oficial do NotebookLM Enterprise (27/11/2026)

**Natureza:** **proposta**, não contrato e não aplicada. Sem credencial, sem rede, sem tocar o `entrada`. A emenda da D-26 **não** é proposta aqui como texto de `PRODUCT.md`: só ficam as condições para o proprietário decidir. Código: `scripts/corretor_notebook.py` (corretor **simulado**); testes: `tests/test_corretor_notebook.py`.

## Resultado em uma frase
A API oficial lida em 27/11/2026 **gerencia cadernos e fontes, mas nenhuma das duas páginas descreve método para fazer pergunta ao caderno e receber resposta com citação**; portanto ela **não substitui sozinha** a etapa que a Zapia faz no Notebook (colar fonte **e** perguntar). Só a metade "criar caderno e adicionar fonte" tem caminho oficial documentado, e essa é exatamente a metade que falhou nas rodadas 2 e 3 do N1.

## Pesquisa (consulta de 27/11/2026; confiança A = documentação oficial, B = relato de terceiros)
- **A:** [Criar e gerenciar cadernos (API)](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks): `notebooks.create`, `get`, `listRecentlyViewed`, `batchDelete`, `share`; versão `v1alpha`; aviso de **Preview** (Pre-GA, "as is"); exige "an authenticated user account with an active Gemini Notebook for business license" e o papel `roles/discoveryengine.notebookLmUser`; autenticação por `gcloud auth print-access-token` (token de **usuário**, não de conta de serviço, segundo a página).
- **A:** [Adicionar e gerenciar fontes (API)](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks-sources): `sources.batchCreate` aceita **uma** entre `textContent` (`sourceName`, `content`), `webContent`, `videoContent` e `googleDriveContent` (só Docs e Slides); `sources.uploadFile` aceita PDF, TXT, MD, DOCX e outros; também `get` e `batchDelete`.
- **B:** [nblm-core (cliente Rust não oficial)](https://docs.rs/crate/nblm-core/0.2.0/source/src/client/api/mod.rs) e [nblm-cli](https://docs.rs/nblm-cli/0.1.0/nblm): afirmam suporte a conta de serviço (com papel amplo) e relatam a API como alpha e erro HTTP 500 em fonte do Drive em 19/10/2025. **Não verificado por mim.**
- **A:** [O que é o NotebookLM Enterprise](https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/overview) e [Usar o NotebookLM com conta de trabalho ou escola](https://support.google.com/notebooklm/answer/16337734): a oferta enterprise usa identidade do Cloud Identity ou de provedor externo e licença atribuída; a leitura das tabelas comparativas indica conta pessoal só no NotebookLM de consumo (**trecho de busca, tabela truncada**).
- **Lacunas:** (1) **método de pergunta/chat com citações**: não encontrado nas duas páginas lidas (não li a referência completa de métodos nem a página de áudio); (2) **conta pessoal `@gmail.com`**: as páginas não dizem se é aceita; a evidência indireta aponta que **não**; (3) projeto com faturamento, ativação da API, escopos OAuth, cotas, limites de fonte e preço: **não informados**; (4) se uma conta de serviço pode ser usada: a página diz "user account", terceiros dizem que sim; **não testado**; (5) a relação entre o "Notebook integrado ao Gemini" que a Zapia usa na conta do proprietário e este produto enterprise: **desconhecida**.

## Desenho proposto do corretor (futuro, fora deste repositório)
1. **Um processo pequeno, fora do modelo**, guarda a credencial e a execução. O modelo (Tutor, Coach, Zapia) nunca vê token, cookie nem sessão (D-26, D-27).
2. **Entrada única:** o comando JÁ promovido (`comandos/validados`), o recibo e a fonte de `comandos/fontes`. O corretor **revalida em código** a caixa de comandos, o hash do recibo, a operação (`enviar_prompt_notebook`) e a origem (`tutor`), e não confia em nada que a Zapia tenha conferido.
3. **Saída única:** um objeto de campos fixos (`entrada_id`, `hash_corpo`, `estado`, `resposta`, `fonte_sha256`, `respondido_em`, `nao_confiavel: true`) ou `PARADO` com **código fechado**; a resposta do Notebook é **dado não confiável**, nunca instrução, e é conferida depois por `scripts/volta_n1.py`.
4. **Backend trocável:** `BackendSimulado` (testes) e `BackendOficialV1Alpha`, que só **monta** as requisições (`textContent`, sem URL, vídeo nem Drive) e levanta `CapacidadeNaoDocumentada` para a pergunta e `SemCredencial` para qualquer envio. Quando existir método de pergunta documentado, só esse backend muda.
5. **Idempotência** por hash do comando: reexecução devolve `JA_RESPONDIDO` sem chamar o backend; falha não marca como respondido.

## Modelo de ameaça (o que o código trava, com teste)
| Ameaça | Controle | Teste |
|---|---|---|
| Comando adulterado, vencido ou ilegível | caixa de comandos reaplicada no corretor | `test_comando_adulterado_ou_ilegivel...`, `test_comando_vencido...` |
| Recibo falso ou hash trocado | `RECIBO_INVALIDO`, `HASH_NAO_CONFERE` antes de qualquer chamada | `test_recibo_sem_promover...`, `test_hash_do_recibo...` |
| Outra operação ou origem aprovada por engano | `OPERACAO_NAO_PERMITIDA` (defesa em profundidade) | `test_outra_operacao_ou_origem...` |
| Repetição do mesmo comando | idempotência por hash | `test_reexecucao_do_mesmo_hash...` |
| Fonte ausente, enorme ou binária | `FONTE_AUSENTE` (teto do corretor, **não** da API) | `test_fonte_ausente...` |
| Token ou chave na fonte, no prompt ou na resposta do Notebook | `SEGREDO_NA_SAIDA`; a resposta é descartada | `test_segredo_na_resposta...`, `test_segredo_na_fonte...` |
| Injeção na resposta virar ação | saída só em campos fixos e `nao_confiavel` | `test_caminho_feliz...` |
| Corretor usado para algo fora do N1 | só `textContent`; sem URL, vídeo, Drive | `test_requisicoes_oficiais_so_texto...` |
| Credencial no repositório | `BackendOficialV1Alpha` nunca envia nem guarda token | `test_backend_oficial_nao_tem...` |
Mutações verificadas à mão (removendo cada controle, a suíte falha): hash, idempotência, filtro de segredo na resposta e na fonte, marca de respondido, operação/origem, status do recibo.

## O que decidir e fazer (atos do proprietário; nada é feito pela sessão)
1. **Decidir se vale seguir:** a API é Preview, exige conta com licença de trabalho/escola e **não documenta a pergunta**. Sem método de pergunta, o corretor só ajudaria no passo de adicionar fonte; o resto continuaria com a Zapia. Recomendação: **não** emendar a D-26 agora; reavaliar quando existir método de pergunta documentado ou se o N1-DIAG-FONTE mostrar que o texto colado não vira fonte.
2. **Verificar a elegibilidade da conta** (licença Gemini Notebook for business, projeto no Google Cloud): só ele consegue; nenhuma credencial vai ao chat.
3. Se um dia o corretor for ligado, ele precisa de aprovação expressa do texto de `PRODUCT.md` (D-26) e de PR próprio.

## Limites
Não prova nada sobre o Notebook real nem sobre a conta dele. O corretor simulado prova o contrato e as recusas, não a segurança de uma implantação. Pesquisa em páginas de Preview que podem mudar; trechos B não verificados.
