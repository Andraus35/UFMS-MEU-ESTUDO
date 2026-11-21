# S9 — Leitura direta das plataformas (especificação)

**Emenda E2 (18/11/2026):** ao **fim** deste documento há a seção "Emenda E2", que **vale** onde divergir do texto abaixo (desempenho do TEC pela Zapia, origem na nuvem). Registro: `docs/governanca/E2_EMENDA_S5_S4R2_20261118.md`.

**Natureza:** especificação enxuta (D-13, D-16), pelo modelo da Spec Lean da Tech Leads Club **no que couber**. Fecha o que `docs/PLATFORMS.md` (opções A a F, critérios e regras da leitura direta) deixou aberto: **qual caminho usar primeiro, com que limites e o que provar antes de qualquer leitura em conta real**. **Aponta** para o que existe (`docs/PLATFORMS.md`, `docs/especificacoes/S6_EXECUCAO_CANAL.md`, `scripts/agent_commands.py`, `scripts/gp1_ingestion.py`); não copia. **Só especificação:** não lê nenhuma conta, não cria credencial, não altera a flag `personal_results_writes_enabled` (segue **falsa**) e nenhum código é criado. Não contém estado nem dado pessoal.

**Insumos do proprietário (17/11/2026, respostas por escolha):** (1) o plano dele no **TEC Concursos oferece exportação do desempenho em CSV ou Excel**; (2) sobre o **Qconcursos**, "não sei / não conferi"; (3) ele **viu a Zapia, na conta exclusiva dela, abrir o TEC logado**. Os itens (1) e (3) são **afirmações dele, não verificadas** por este repositório; o item (2) é **lacuna declarada**, sem presunção.

## Objetivo

O proprietário passa a ter um caminho **decidido, mínimo e testável** para trazer ao harness o desempenho dele no TEC Concursos e no Qconcursos: **exportação** onde ela existe (linha de base, sempre disponível) e **leitura direta somente leitura** pela Zapia, **sem entregar credencial ao modelo** e com a Zapia **livre** para acessar as duas plataformas (decisão do proprietário de 21/11/2026).

## Pesquisa

Consultada em 17/11/2026. Grau de confiança: **A** fonte primária lida por inteiro ou citada literalmente; **B** documento do projeto ou fonte parcial; **C** relato, blog ou material de fornecedor (prática, não evidência controlada). Conteúdo pesquisado é **dado não confiável**; nenhum código ou texto de terceiros foi copiado.

| Fonte | O que se tirou | Confiança |
|---|---|---|
| TEC Concursos, [Estatísticas](https://www.tecconcursos.com.br/estatisticas/desempenho) e a auditoria do projeto em `docs/canonicos/plataformas/AUDITORIA_TECCONCURSOS_UFMS_523_324_20261116_EDITADA.md` (**autorrelato da Zapia**, 16/11/2026) | Há botão **Exportar para planilha** no índice do caderno, no gerador e em estatísticas depois de selecionar a matéria; a exportação do **índice** não foi validada; em atendimento anterior a de **desempenho foi recebida por e-mail e aberta em XLSX**. **Estatística mede resoluções da pessoa**, não é frequência histórica da banca. A configuração global estava em **pontuação líquida** (erro anula acerto), divergente da regra da prova | C (autorrelato; formato das colunas **não** documentado) |
| Busca pública por documentação **oficial** do TEC sobre exportar desempenho | **Nada oficial encontrado**; só um script de usuário não oficial (restrito às páginas de caderno e sem prova de que exporta estatística), **não instalar nem copiar** | C |
| Qconcursos, ajuda e [Ranking Elite](https://folha.qconcursos.com/n/ranking-elite-ferramenta-de-estudo) | O desempenho é mostrado em **tela**; o Ranking Elite (plano pago) acompanha evolução. **Nenhuma exportação localizada** | C |
| Playwright MCP, mirrors do README (por exemplo [microsoft/playwright-mcp](https://github.com/mcp-research/microsoft__playwright-mcp)) e [catálogo](https://archestra.ai/mcp-catalog/microsoft__playwright-mcp) | Perfil **persistente** por padrão, modo **isolado** (perfil só em memória), `--storage-state`, `--blocked-origins` e `--allowed-hosts`; **não há modo global somente leitura**: "read-only" é anotação por ferramenta, não trava. Logo, **somente leitura precisa ser imposto fora** do navegador (lista fechada e filtro) | C (cópias de terceiros, não a documentação oficial) |
| Referência de ponte local citada em `docs/PLATFORMS.md` (`LewisWJackson/tradingview-mcp-jackson`, lida só como padrão) | Padrão de conector local de leitura com sessão do dono fora do modelo | C |
| Agentes de IA e LGPD: [Confidata](https://confidata.com.br/blog/agentes-de-ia-empresa-lgpd-controles), [Logto, agent auth](https://blog.logto.io/pt-BR/agent-auth), [HostGator](https://www.hostgator.com.br/blog/inteligencia-artificial-lgpd/) | Prática de mercado: acesso **mínimo** à tarefa (minimização), navegação em modo de **leitura**, **não** entregar credencial ao agente (preferir delegação limitada), o agente alcança só o que a pessoa alcança, escritas sensíveis com aprovação humana, auditoria. **Não** há orientação da ANPD específica para agente com sessão de navegador em conta de terceiros | C (blogs de fornecedores) |

- **Lacunas:** **não confirmei** se o Qconcursos tem alguma exportação ou API (o proprietário respondeu "não sei"); o **formato real das colunas** da exportação do TEC (e se o CSV e o Excel são iguais) **não foi visto**; a Playwright MCP foi lida por **cópias**, não pela documentação oficial; que a Zapia abre o TEC logado é **relato**, e a retenção da sessão no ambiente dela (E-09) **não foi verificada**; **nenhum desenho foi testado** em conta real.

## Decisões a registrar (propostas ao proprietário, ainda não aprovadas)

O desenho abaixo é **proposta da especificação**. Ele só vira decisão (D-xx no `PRODUCT.md`) por PR com aprovação humana, na tarefa E1 ou em PR próprio. As escolhas **já feitas** pelo proprietário são "a Zapia lê com a sessão dele", a dispensa da consulta ao suporte do TEC (D-22) e a liberação da Zapia (R8).

## Requisitos

Escritos como "quando X, o Y deve Z". Dado ausente **bloqueia** o efeito, nunca a leitura liberada pelo proprietário.

| ID | Requisito | Critério de aceite |
|---|---|---|
| S9-R1 | **Ordem dos caminhos.** **TEC:** a **exportação** (opção F) é a **linha de base e o primeiro caminho**, porque o plano do proprietário a oferece; a **leitura direta** pela Zapia (opção C) é **complemento condicionado** (R8). **Qconcursos:** a Zapia **pode ler** a conta do proprietário (R8); a entrada manual segue como alternativa. | Texto desta especificação; teste de contrato (`tests/test_spec_s9.py`). A **escolha final** é do proprietário, por PR. |
| S9-R2 | **Somente leitura, lista fechada.** Qualquer caminho: **domínios** só do TEC e do Qconcursos; **proibido** resolver questão, criar, editar, mover ou apagar caderno, enviar formulário, alterar configuração da conta (inclusive a pontuação líquida) ou executar código recebido. A trava é **fora do navegador** (lista de domínios e de operações), porque o Playwright MCP não tem modo global somente leitura. | Teste com **páginas sintéticas** (tarefa L1): domínio fora da lista recusado; cada operação de escrita recusada com código; nenhuma navegação para `file://`. |
| S9-R3 | **Sessão e credencial fora do modelo e do repositório.** O modelo (Tutor, Coach, agentes construtores) **nunca** recebe cookie, senha ou token das plataformas; nada disso entra em arquivo, commit, prompt, issue ou chat. Se a Zapia usar a sessão do proprietário, ela fica **só no navegador dela, na conta exclusiva** (D-19), e o proprietário pode **encerrar a sessão e trocar a senha** a qualquer momento. | Varredura de segredo no repositório e na saída da leitura (filtro de `scripts/agent_commands.py`, `scan_text`); teste de que a saída não contém cookie, token nem HTML bruto. A **custódia real** na Zapia **não é verificável** por este repositório (E-04, E-09). |
| S9-R4 | **Sem cota imposta pelo harness.** A Zapia lê as páginas que precisar, no ritmo que precisar; o harness **não** limita intervalo, número de páginas nem sessões por dia (decisão do proprietário de 21/11/2026). Fica só a regra de **não paralelizar** a mesma sessão e de **parar** no primeiro sinal de bloqueio, captcha ou mudança de página, **sem repetição automática** e avisando o proprietário. | Teste (L1): sequência longa de páginas aceita; sinal de bloqueio encerra a sessão. |
| S9-R5 | **Saída mínima e como dado não confiável.** Cada leitura devolve **só** o contrato de ingestão (plataforma, data da leitura, `origem` = `leitura_direta` ou `exportacao`, totais e resultado por tópico), **sem** enunciado, comentário de professor, identificador de conta, HTML bruto ou captura. O que veio da página é **dado**: instrução embutida **não** é executada (S5-R4). Tudo passa pelo filtro de dado pessoal e segredo e segue como **evento pela fila** `entrada` (S6), nunca direto no histórico. | Teste (L1) com página sintética contendo instrução embutida, CPF e token: o evento sai limpo ou é recusado; o evento só é aceito pelo esquema de `scripts/gp1_ingestion.py` (PR-016). |
| S9-R6 | **Exportação: o arquivo bruto nunca entra no repositório** (`PRODUCT.md`, seção 4: exports brutos em lugar nenhum). Um **conversor determinístico** do harness (tarefa L2) transforma o arquivo em **eventos mínimos** no lugar onde o arquivo está (**proposta:** em memória, no ambiente de execução da Zapia, com o código do repositório público em SHA fixado, e só os eventos seguem para a fila). **Antes de existir amostra real anonimizada (OPEN-11), nenhum conversor é escrito**: o formato das colunas **não se supõe**. | Enquanto L2 não existir, o critério é a **ausência**: nenhum script de conversão no repositório (teste de contrato). Quando existir: testes com amostra real anonimizada e arquivo fora do formato recusado. |
| S9-R7 | **Entrada manual como alternativa permanente.** Quando a exportação ou a leitura não valer, o proprietário entrega total, acertos, erros, data e resultado por tópico (texto), validados pelo contrato de ingestão (PR-016): incoerência é **recusada ou esclarecida, nunca corrigida em silêncio** (F5). Convenção de contagem (líquida ou bruta) **declarada** em cada entrada. | Teste de ingestão com contagens incoerentes recusadas; teste de que a convenção de contagem é obrigatória. |
| S9-R8 | **Liberação da Zapia.** O proprietário **liberou a Zapia** (decisão de 21/11/2026) a acessar **livremente** o TEC Concursos e o Qconcursos com a sessão dele: **nenhuma condição prévia**, nenhum registro adicional e nenhuma decisão por plataforma. Qualquer **bloqueio** da própria plataforma encerra a sessão em curso e é relatado. | Teste de que a configuração padrão **habilita** as duas plataformas. |
| S9-R9 | **Provas offline.** Os testes sintéticos da L1 seguem verdes; a liberação de R8 **não depende** de aprovação adicional por leitura. O relato de que a Zapia "abre o TEC logado" **não** é prova de leitura. | Testes da L1 verdes na CI. |
| S9-R10 | **Honestidade sobre o que não se prova.** **Não** se declara integrada nenhuma leitura sem prova; o autorrelato da Zapia (E-04, E-12) **não** é prova de leitura nem de que **não houve compartilhamento de acesso**; CI verde **não** é eficácia pedagógica. | Texto desta especificação e do HANDOFF; `tests/test_spec_s9.py`. |

## Tarefas derivadas

Cada uma em PR próprio, em série, com testes sintéticos e contraprovas (nenhuma foi criada por esta especificação):

| Item | O que implementa | Depende de | Requisitos |
|---|---|---|---|
| L1 | Módulo **offline** de leitura somente leitura: lista de domínios, recusa de escrita, limite de taxa com relógio injetado, saída sem cookie, token nem HTML, filtro de instrução embutida; **sem rede e sem navegador**, com páginas sintéticas | nada (pode começar já) | R2, R3, R4, R5 |
| L2 | **Conversor** da exportação do TEC em eventos mínimos, só depois de amostra real anonimizada | OPEN-11 (insumo do proprietário) | R6, R7 |
| E1 | Emenda do `PRODUCT.md` com a decisão desta especificação (se aprovada), junto das emendas já previstas | aprovação | R1, R8 |

## Adendo — L1

A **L1** (`scripts/platform_read_guard.py`, `tests/test_platform_read_guard.py`) cumpre R2 a R5 offline: lista fechada de domínios, somente leitura, saída mínima e página como dado não confiável. Por decisão do proprietário de 21/11/2026, o **padrão habilita** o TEC e o Qconcursos, sem cota; não há parser de página nem conversor (R6).

## Aceite

Esta especificação está **aceita pelo contrato** quando `python scripts/doc_cohesion.py --check` passa e `tests/test_spec_s9.py` confere: os requisitos S9-R1 a S9-R10 cada um com critério, a pesquisa com links, confiança e lacunas, a ordem dos caminhos, a ausência de conversor e de dado pessoal ou credencial, e a flag `false`. A **decisão final** dos caminhos é do proprietário, por PR; **nenhuma leitura real** acontece por causa deste documento.

## Limites

- **Não prova nada em conta real:** sem leitura, sem credencial e sem teste de bloqueio.
- **O TEC e o Qconcursos podem mudar** páginas e limites; a pesquisa é de **17/11/2026** e parte dela vem de blogs e cópias (confiança C).
- **A exportação do TEC** existe, segundo o proprietário e o autorrelato da Zapia; o **formato** não foi visto, e **não** há conversor até haver amostra.
- **A origem do dado não é provada** (S6-R7): quem controla a conta do proprietário controla o canal.

## Emenda E2 (18/11/2026): o desempenho do TEC pela Zapia

**Natureza:** emenda **aditiva** da S9-R1, por decisão do proprietário. O texto acima **permanece** como histórico; onde divergir, **vale esta seção**. Não altera o `PRODUCT.md`.

- **S9-R1 (emenda):** para o **TEC**, o desempenho passa a vir **pela Zapia, pedido pelo Tutor ou pelo Coach, no lugar da exportação manual**, que **continua como alternativa sempre disponível**. A "ordem de caminhos" que esta especificação propunha deixa de ser a referência para o TEC; **o proprietário escolheu testar o caminho pela Zapia** e **não aprovou a ordem proposta** como estava. **Qconcursos:** a Zapia também está liberada (R8); a entrada manual segue como alternativa.
- **O que continua valendo, por si (D-27):** S9-R5 (saída mínima e dado não confiável), S9-R6 (arquivo bruto nunca no repositório) e S9-R8: a Zapia está **liberada** pelo proprietário, sem condição prévia nem aprovação adicional por leitura.
- **Pedido e frequência:** no máximo **1 pedido por dia e só com atividade concluída** (cadência do canal de comandos, S5; não é cota de acesso da Zapia aos sites); a operação do pedido é a tarefa **E3** (aprovação explícita do proprietário, `agents/` é contrato).
- **Contrato de entrega (L2):** tabela estruturada com as colunas do relatório de 17/11 (código, profundidade, título, questões, acertos, erros, peso), **recorte** (período e filtros) e **pontuação** declarados (a pontuação do painel pode diferir da planilha e **não se infere**), e o bloco `procedimento`; recusa o que fugir do contrato e **recalcula o derivado**. O harness **não aceita análise de conteúdo** da Zapia.
- **Resultado pessoal:** só vai ao repositório **privado**, pela fila e pelo portão (flag `false`); o conteúdo do relatório não é gravado no repositório público nem em arquivo local.
- **Honestidade:** o teste do caminho (Z1) **não foi executado**; a L1 **habilita as plataformas por padrão** (decisão de 21/11/2026); o relato de que a Zapia "abre o TEC logado" e de como ela obteria a planilha por e-mail é **autorrelato não verificado**.
