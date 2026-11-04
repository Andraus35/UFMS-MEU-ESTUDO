# Verificação de prontidão GP-0 / GP-1 — 04/11/2026

**Classificação:** relatório de verificação independente e limitada, READ ONLY sobre a branch técnica.  
**Escopo:** confirmação parcial do edital original e dos contratos do harness atual. Não é implementação nem homologação dos gates.  
**Repositório:** `Andraus35/UFMS-MEU-ESTUDO`  
**PR pedagógico:** #2, branch `docs/especificacao-pedagogica-v1-2`, HEAD **anterior**: `db2a7fba1c86bc8e988854a0cde759d4036624ee`.  
**PR técnico:** #1, branch `setup/harness-memory-v0-2`, HEAD efetivamente lido: `ab5394acf4343ecb7848d16b64876f493cb530b3`.  
**main:** `c020f78ba07ebb4e2949021b45a7f9b8f2c26d42`. Nenhum merge realizado.

## 1. GP-0 — Verificação externa do edital original

**Fonte primária UFMS encontrada e consultada:**  
- Página oficial: https://www.ufms.br/ufms-lanca-154-vagas-em-concurso-de-tecnicos-em-educacao-para-fortalecer-a-educacao-superior-em-ms/ (texto atualizado em 30/10/2026).  
- PDF oficial: https://www.ufms.br/wp-content/uploads/2026/10/SEI_6775306_Edital.pdf  
- Documento exibido: **Edital PROGEP/UFMS nº 152, de 29/10/2026**; 47 páginas no PDF consultado. A primeira e a décima páginas foram visualmente inspecionadas; a seção da pontuação foi consultada na extração textual. **Não se afirma revisão visual integral das 47 páginas nem hash do PDF.**

### Evidências verificadas no texto original da UFMS

| Elemento | Referência | Verificação |
|---|---|---|
| Identidade do edital | PDF, pág. 1, cabeçalho | Nº 152, de 29/10/2026 |
| Períodos por nível | Item 1.4; item 9.3, págs. 1/8 | Superior pela manhã; médio à tarde |
| Composição e duração | Itens 9.1–9.2, pág. 8 | 60 itens, 100 pontos, 4 horas por prova |
| Português | Item 9.1, quadro da pág. 8 | 15 questões / 15 pontos |
| Inglês | Item 9.1 | 5 questões / 5 pontos |
| Legislação | Item 9.1 | 10 questões / 20 pontos |
| Raciocínio Lógico | Item 9.1 | 10 questões / 20 pontos |
| Específicos | Item 9.1 | 20 questões / 40 pontos |
| Corte global | Item 10.1, pág. 10 | Mínimo de 50% da pontuação máxima |
| Nota zero | Item 10.2, pág. 10 | Eliminação se zerar qualquer das cinco áreas |
| Duas inscrições | Itens 3.6.1 e 3.6.1.1 | Até duas inscrições, observando grupos/turnos |
| Data de prova | Anexo II, conforme PDF e notícia oficial | 17/01/2027 |
| Inscrições | Anexo II e notícia da UFMS | 04/11 a 04/12/2026 |
| Isenção de taxa | Anexo II do edital consultado | 04 a 11/11/2026 |

**Verificação parcial concluída:** identidade e estrutura-base do edital original conferidas. Os valores do `config/concursos.json` técnico relativos a questões, pontuação, duração e corte **coincidem com o texto original consultado**, mas isso não confirma atualidade após retificações.

### Pendências normativas que impedem GP-0 aprovado

1. **Retificações:** buscas públicas em UFMS/FAPEC em 04/11/2026 não localizaram retificação inequivocamente vinculada ao objeto; isso **não comprova inexistência ou completude de buscas**. `config/concursos.json` mantém `retificacoes_verificadas = false`, corretamente conservador.
2. **Página da FAPEC:** https://portal.concurso.fundacaofapec.org.br/edital/ver/22 exibe o mesmo concurso, mas rotula o documento listado como `EDITAL PROGEP/UFMS N.º 001/2026` (30/10/2026), diferente do **nº 152** no PDF primário da UFMS. A descarga do arquivo da FAPEC não foi acessível nesta consulta. **Não concluir que é retificação, erro definitivo ou documento idêntico**; solicitar confronto de bytes/versões à sessão técnica.
3. **Subtópicos e sobreposição 523/324:** a verificação acima não revalidou integralmente anexos e equivalências por item. Os aliases de `config/topics.csv` não constituem prova de identidade conceitual.
4. **Fonte imutável:** a URL consultada não fornece, por si só, um SHA-256 local verificável do PDF; a engenharia deve calcular hash de bytes efetivamente baixados, com proveniência, e comparar com o manifesto, sem substituir fonte canônica silenciosamente.

**Veredito GP-0:** `PARCIALMENTE_VERIFICADO` para o edital original, `PENDENTE` para atualidade normativa, retificações, equivalência dos programas e reconciliação FAPEC. **Não homologado.**

## 2. GP-1 — Contratos e estado efetivamente observados no PR #1

**HEAD consultado:** `ab5394acf4343ecb7848d16b64876f493cb530b3`. Os pontos abaixo decorrem da leitura direta de arquivos desse commit, não da fotografia histórica da matriz v1.7.

| ID | Arquivo e evidência no HEAD | Avaliação |
|---|---|---|
| VGP1-01 | `settings.json.bootstrap.mandatory` enumera **9 arquivos**; `AGENTS.md` enumera os mesmos 9 | Lista principal documental coerente |
| VGP1-02 | `rules/CORE.md` item 2 e `docs/OPERACAO.md` item 1 ainda citam **7 arquivos** | Divergência confirmada; sincronização técnica pendente |
| VGP1-03 | `scripts/bootstrap.py` confere presença e produz resumo; não prova leitura semântica por agente ou registro nativo de hooks | Automação de bootstrap completo não demonstrada |
| VGP1-04 | `settings.json.storage.personal_results_writes_enabled = false` | Bloqueio ativo; não habilitar sem autorização |
| VGP1-05 | `scripts/core.py` aceita tipos de eventos específicos, exige `event_id`, timestamp ISO com fuso e `caderno_id` para certos eventos | Contrato técnico de evento existente; separar do esquema pedagógico de recomendação/attempt |
| VGP1-06 | `validate_events` exige `acertos + erros + nao_respondidas = total` com números inteiros não negativos | Normalização de convenção de plataforma ainda necessária para relatórios diferentes |
| VGP1-07 | `rebuild` mantém resultado corrigido como versão corrente e só agrega subtópicos em `topic_results` | Proteção parcial existente; não atribui resultado global a tópicos inventados |
| VGP1-08 | `scripts/core.py` não contém implementação declarada de projeção E0–E4 nem fila/adaptação multicritério | Especificações v1.2 e v1.5 ainda não integradas nessa rotina |
| VGP1-09 | `state/CURRENT.json` possui 0 eventos, 0 resultados, lista de cadernos pendentes vazia | **Nenhum histórico de desempenho pessoal disponível nesse estado**; ausência ≠ nota zero |
| VGP1-10 | `templates/RESULTADO.md` permite origem manual/CSV/imagem e discriminação opcional; não fornece adaptadores reais das plataformas | Contrato humano de devolução presente; importação robusta não demonstrada |

**Não foi demonstrado neste relatório:** execução local de testes, resistência de hooks, autorização de gravação, conclusão de integração nativa, execução do motor ou ciclo com dados reais.

**Veredito GP-1:** `PENDENTE`. Invariantes de validação e projeção parcial estão presentes, mas divergências e contratos de integração ainda precisam de correções/testes em frente técnica própria.

## 3. Encaminhamentos delimitados (sem duplicar o backlog)

| Ordem | ID já existente | Próxima evidência exigida | Responsável pela futura execução |
|---|---|---|---|
| 1 | ENG-00 / REC-10 | Verificar retificações em canais oficiais, identidade FAPEC e hashes, cotejar anexos 523/324 | Sessão técnica |
| 2 | ENG-01 / REC-01/02 | Reconciliar nove arquivos obrigatórios e provar START sem alegar leitura indevida | Sessão técnica |
| 3 | ENG-01/02 / REC-03/04/05/08 | Desenhar IDs, tempo do evento vs. tentativa, normalização e estados de caderno com fixtures | Sessão técnica |
| 4 | ENG-02 / REC-09 | Manter bloqueio de escrita pessoal até gates/consentimento específicos | Sessão técnica, com aceite humano |
| 5 | ENG-03/04 / REC-06/07/14/16 | Implementar evidência E0–E4 e fila adaptativa de forma reproduzível | Sessão técnica após contratos |
| 6 | ENG-06 / REC-13 | Converter os 102 critérios já catalogados em testes executáveis, sem duplicá-los | Sessão técnica |

Este documento **não acrescenta** novos cenários aos 102 existentes; acrescenta **constatações** sobre o código e fontes. Os IDs VGP1-xx são referências de observação, não novos testes.

## 4. Limitações e próximo checkpoint

- A página FAPEC não disponibilizou o arquivo para confronto nesta sessão; não declarar hash ou equivalência.
- Nenhuma retificação foi positivamente identificada nas páginas consultadas; impossível demonstrar completude da busca como fato universal.
- A leitura dos arquivos foi **remota por SHA**, sem executar scripts do PR #1.
- A confirmação do commit que publicar este relatório deverá ser feita separadamente por **readback remoto**; o SHA atual deste documento não é sua identidade futura.
- Não editar PR #1, `main`, arquivo canônico do edital, `settings.json`, `rules/` ou dados de estudante nesta sessão.

**Próxima ação pedagógica concreta:** usar um diagnóstico inicial por questões **sem armazenar resultado pessoal no GitHub enquanto a escrita estiver bloqueada**, se o estudante desejar iniciar; ou aguardar da engenharia uma verificação reproduzível de ENG-00/ENG-01 para fechar o parecer.

## 5. Complemento de conferência das fontes oficiais — 04/11/2026

**Objetivo:** verificar especificamente a discrepância de identificação entre UFMS/FAPEC e os prazos operacionais do edital, sem sugerir que foi concluída a revisão de retificações. Este complemento atualiza evidências, **não** revisa os vereditos GP-0/GP-1.

### Identidade do documento

1. **UFMS, fonte primária e PDF inspecionado:** https://www.ufms.br/wp-content/uploads/2026/10/SEI_6775306_Edital.pdf — página 1 traz `EDITAL PROGEP/UFMS Nº 152, DE 29 DE OUTUBRO DE 2026`. Arquivo exibido com 47 páginas no visualizador utilizado.
2. **FAPEC, página específica do concurso:** https://portal.concurso.fundacaofapec.org.br/edital/ver/22 — continua exibindo `EDITAL PROGEP/UFMS N.º 001/2026 - Edital de Abertura`, com data 30/10/2026.
3. **FAPEC, link DOWNLOAD fornecido pela própria página:** `https://concurso.fundacaofapec.org.br/arquivo.php?file=edital%2F1%2F22%2Fe5f1c2b364f19beadf2685d8fb836065.pdf`. A consulta retornou redirecionamento a objeto S3 com URL temporária que **não foi acessível** pelo mecanismo de consulta. Não houve leitura do PDF da FAPEC, hash ou cotejo byte a byte.
4. **Busca sobre retificações no escopo do concurso:** não surgiu documento positivo e inequívoco nas buscas realizadas. Isso **não significa** confirmação de inexistência de retificações nem conferência exaustiva de boletins/portal.

**Resultado da verificação:** discrepância de rótulo **confirmada**, equivalência de documentos **NÃO VERIFICÁVEL NESTA CONSULTA**, efeito normativo **DESCONHECIDO**. Manter o PDF original da UFMS como fonte de referência já verificada e não renomear/fundir documentos; a outra sessão deverá baixar oficialmente o arquivo FAPEC com acesso legítimo, conferir página inicial, escopo, assinatura e hash.

### Anexo II — cronograma original verificado visualmente

**Fonte:** PDF da UFMS acima, página 13 do documento (página 12 em índice iniciado em zero), Anexo II, inspecionada em captura visual.

| Etapa original | Período/data constante do PDF |
|---|---|
| Inscrições | 04/11 a 04/12/2026 |
| Solicitação de isenção | 04 a 11/11/2026 |
| Resultado preliminar de isenção | 18/11/2026 |
| Pagamento da inscrição | Até 07/12/2026 |
| Divulgação do ensalamento e convocação | 11/01/2027 |
| Provas objetivas | 17/01/2027 |

As datas acima pertencem à **redação original**, sujeita a eventuais atos posteriores. O fato de ser 04/11/2026 torna especialmente relevante não esperar implementação do tutor para tomar providências de inscrição; este documento não realiza inscrição nem presume que o estudante já esteja inscrito.

**Anomalia adicional identificada no texto original:** o mesmo Anexo II apresenta um período de recurso indicado como `11 e 12/01/2027` para resultado preliminar de procedimento divulgado em `10/02/2027`, uma ordem cronológica incompatível na leitura literal. Tratar como **possível erro de data a esclarecer** por fonte oficial; **não corrigir automaticamente para fevereiro**, nem alterar calendário/regras por suposição. Essa anomalia afeta etapas posteriores à prova, não altera o intervalo de inscrições confirmado no próprio texto.

### Encaminhamento e estado

- **GP-0 permanece PENDENTE** para retificações, equivalência do arquivo FAPEC e reconciliação cronológica. O edital original foi confirmado quanto aos pontos aqui listados.
- **GP-1 permanece PENDENTE**, sem nova inspeção técnica nesta atualização; ver a seção 2 e os SHAs do último readback de código.
- **Sem alteração de fonte canônica, configuração, scripts, histórico, PR técnico ou permissões de escrita.**
- Não acrescentar novos casos ao catálogo de 102 critérios: são **evidências de verificação**, a serem vinculadas aos pacotes ENG-00/GP-0 já cadastrados.

**Próxima evidência necessária:** obter o arquivo oficial FAPEC e seu SHA-256, identificar o conteúdo de abertura e quaisquer retificações aplicáveis, depois verificar cronograma e anexos dos cargos 523/324 no objeto normativo atualizado.
