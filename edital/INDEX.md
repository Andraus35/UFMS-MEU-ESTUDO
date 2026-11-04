# Índice de recuperação — Edital UFMS 152/2026

**Fonte canônica:** [`EDITAL_UFMS_152_2026.md`](../EDITAL_UFMS_152_2026.md), com 47 páginas. Os chunks são cópias integrais e verificáveis, não resumos nem versões corrigidas do edital.

## Fluxo obrigatório de leitura econômica

1. Em cada sessão operacional, verificar a identidade do edital integral e **ler este índice**. Não carregar 47 páginas de uma vez.
2. Roteamento inicial por **página/cargo**, quando possível; caso contrário, buscar por palavras, expressões e números com `scripts/search_edital.py`.
3. Abrir somente os **3–5 chunks** mais relevantes. Conferir texto e página antes de afirmar fatos; se o enunciado ou uma tabela ultrapassar um corte, abrir o chunk adjacente.
4. Ampliar a busca se a evidência for insuficiente. Ausência de resultado lexical não significa que a regra não conste no edital.
5. Retificações oficiais **não estão incorporadas** automaticamente. Não tratar cadernos TEC/Qconcursos nem comentários como autoridades sobre o escopo.

## Roteamento rápido

| Pergunta | Páginas do edital |
|---|---|
| Regras, cronograma, cotas e demais procedimentos | 1–13 |
| Inscrição e pagamento | **2–3** |
| Prova objetiva e horários de ingresso | **8–9** |
| Eliminação e classificação | **9–10** |
| Recursos administrativos | **10–11** (e referências posteriores) |
| Remuneração inicial (Anexo I) | **12** |
| Vagas, formação e lotação | 14–18 |
| Cargo **523** — vaga e requisito | **15** |
| Cargo **324** — vaga e requisito | **18** |
| Atribuições de cargos | 20–28 |
| Atribuições do **523** (Anexo IV) | **23** |
| Atribuições do **324** (Anexo IV) | **28** |
| Conhecimentos gerais — 523 e 324 | **29** |
| Conteúdo específico **523** | **35–36** |
| Conteúdo específico **324** | **45** |
| Admissão e documentos | 46–47 |

## Índice temático derivado e recorte preciso

- `edital/topic_index.json` relaciona **23 tópicos** de `config/topics.csv` a **24 intervalos de texto** em chunks, com cargo, página e offsets no chunk e na página. Não é uma nova versão normativa.
- Conhecimentos gerais dos dois cargos: intervalos dentro de `p29-c01`; o restante da página 29 contém programas de outros cargos.
- Conteúdos específicos 523: `p35-c02` (início) e `p36-c01` (continuação), **recortados** para excluir os cargos 522 e 524–526.
- Conteúdos específicos 324: intervalo em `p45-c02`, excluindo o programa anterior na mesma página.
- Aliases para sinônimos são **metadados de busca derivados**: resultados exibem trecho literal e proveniência; o alias isolado não comprova um fato.
- O índice é regenerável com `python scripts/index_edital.py --write` e verificado com `--check`; o gate `scripts/validate.py` falha se o documento e o índice divergirem.

### Busca econômica em camadas

1. Conhecendo um **item numerado**: `python scripts/search_edital.py "3.6 inscrição" --full`. Localiza primeiro o marcador literal `3.6.` e fornece a origem da janela textual; use `--page` para expandir o contexto. O número não deve ser confundido com norma externa. 
2. Conhecendo o ID: `python scripts/search_edital.py --topic 523-06 --cargo 523 --area especificos --full`. Isso retorna somente o intervalo sobre orçamento, com página e offsets.
3. Por título ou sinônimo: `python scripts/search_edital.py "disciplina discente" --cargo 324 --area especificos`; `python scripts/search_edital.py "matemática" --area gerais`.
4. Sem rota exata: o BM25 busca lexicalmente. Com `--cargo`, limita os programas das páginas 29–45 ao cargo selecionado, mesmo sem `--area`; com `--area especificos`, restringe ainda mais aos seus tópicos específicos. Em consultas com 3+ termos úteis, exige pelo menos dois termos coincidentes para reduzir falsos positivos. O filtro não resolve automaticamente as tabelas de vagas das páginas 14–18.
5. Se o trecho estiver incompleto: `--neighbors` identifica os chunks adjacentes, a recuperar somente quando necessários; `--page 36` mostra a página completa para desambiguação.
6. Sem evidência suficiente: devolver resultado vazio/pendência. Não converter similaridade em afirmação normativa nem presumir retificações.

`python scripts/benchmark_edital.py` mede Hit@1, Hit@3, negativos e volume de caracteres recuperados em consultas diagnósticas versionadas em `tests/fixtures/retrieval_cases.json`. A métrica não representa recall universal nem comprova fidelidade do PDF original; tabelas devem ser cotejadas com o arquivo primário.

Registro de cotejo com o PDF original e anomalia do Anexo II: [`docs/AUDIT_RECUPERACAO_EDITAL_2026-11-04.md`](../docs/AUDIT_RECUPERACAO_EDITAL_2026-11-04.md). O conjunto adversarial adicional fica em `tests/fixtures/adversarial_cases.json` e é aferido na CI por `scripts/benchmark_adversarial.py`.

## Linhas do quadro de vagas — verificação por campo (Anexo III)

O arquivo `edital/vagas_index.json` é um **índice derivado não normativo**, ligado aos identificadores e SHA-256 do PDF original. Ele armazena os campos conferidos visualmente para o cargo 523 (página 15) e 324 (página 18), além das âncoras literais para localizar a linha certa na transcrição. Não substitui a tabela do PDF.

- `python scripts/search_edital.py --vagas-cargo 523 --full`: extrai apenas a linha do quadro associada ao código **523**, com código, 29 vagas, Campo Grande e ambas as alternativas de formação presentes no quadro.
- `python scripts/search_edital.py --vagas-cargo 324 --full`: extrai apenas a linha do **324**, com 18 vagas, Campo Grande e ensino médio completo.
- `python scripts/search_edital.py "requisitos do cargo 523" --full`: usa a rota estruturada, não a proximidade lexical entre linhas de outros cargos.
- `python scripts/index_vagas.py --check`: verifica a identidade da fonte, os códigos, os quantitativos, a lotação e as âncoras literais. Os offsets de campos são calculados sobre os chunks no momento da leitura.
- `python scripts/index_vagas.py --write`: regenera o índice a partir das âncoras declaradas, sem modificar o edital ou seus chunks.

**Regra de segurança:** não assumir que requisitos impressos nas linhas dos cargos 522, 524, 323 ou 325 se aplicam aos códigos 523 ou 324. A formatação vertical da tabela original deve ser verificada no PDF em casos de dúvida; os rótulos normalizados, coordenadas e classificações do índice são derivados, não normativos. Uma pergunta que identifique simultaneamente os dois cargos deve ser dividida em duas recuperações em vez de receber uma resposta parcial.

## Atribuições literais dos cargos (Anexo IV)

- `edital/atribuicoes_index.json` é um índice **derivado, não normativo**, com origem Git/PDF, página, chunk, offsets, caracteres e SHA-256 do recorte exato. Não altera o texto canônico.
- Cargo **523**, página **23**, chunk `p23-c01`: `python scripts/search_edital.py --atribuicoes-cargo 523 --full`. O recorte exclui a Produção Cultural anterior e a descrição do cargo Gestão Pública (Campus) que vem em seguida.
- Cargo **324**, página **28**, chunk `p28-c02`: `python scripts/search_edital.py --atribuicoes-cargo 324 --full`. O recorte exclui a descrição anterior de Veterinária e Zootecnia e o rodapé do documento.
- Consultas `"Quais as atribuições do cargo 523?"` ou `"Funções do cargo 324"` são encaminhadas diretamente aos respectivos trechos. Caso a mesma consulta misture **atribuições** e **requisitos**, o buscador exige separação para não apresentar uma resposta parcial.
- Mesmo na busca BM25 com `--cargo 523` ou `--cargo 324`, as páginas **20–28** são limitadas ao trecho de atribuições do cargo selecionado. O texto completo permanece acessível via `--page` quando for preciso revisar o PDF original.
- Reproduzir e verificar com `python scripts/index_atribuicoes.py --write` e `python scripts/index_atribuicoes.py --check`. A CI valida o manifesto, os recortes e testes adversariais; retificações continuam sendo fontes separadas.

## Separação determinística entre Anexos III, IV e V

O buscador distingue **requisitos de ingresso e vagas** (Anexo III), **atribuições funcionais** (Anexo IV) e **programa de conhecimentos cobrado** (Anexo V). Os três são fontes com funções diferentes; um tema presente nas atribuições **não é automaticamente** requisito de ingresso ou tópico da prova.

| Consulta | Comando | Resultado |
|---|---|---|
| Anexo III — requisito 523 | `python scripts/search_edital.py --anexo III --cargo 523 --full` | Linha literal da p. 15 |
| Anexo IV — atribuição 324 | `python scripts/search_edital.py --anexo IV --cargo 324 --full` | Recorte literal da p. 28 |
| Anexo V — programa completo 523 | `python scripts/search_edital.py --anexo V --cargo 523` | 14 tópicos: 4 gerais e 10 específicos |
| Anexo V — específicos 324 | `python scripts/search_edital.py --anexo V --cargo 324 --area especificos` | 9 tópicos, p. 45 |

Alternativamente, `--conteudo-cargo 523` ou `--conteudo-cargo 324` retorna o inventário completo do Anexo V, com áreas, páginas, chunks e offsets. Por padrão retorna **localizadores e pequenos excertos**, não os 47 páginas do documento; `--full` acrescenta cada trecho literal. O 523 tem 14 tópicos no total e o 324 tem 13 (quatro gerais e nove específicos). Em ambos os casos os conhecimentos gerais estão na p. 29.

Perguntas diretas como `"Anexo III do cargo 523"`, `"Quais as atribuições do cargo 324?"` e `"Conhecimentos específicos do cargo 523"` também podem ser roteadas. Consultas que misturam anexos ou pedem simultaneamente requisitos, atribuições e conteúdos são **rejeitadas para desambiguação**, em vez de retornar uma resposta parcial. O seletor `--anexo` exige `--cargo` e não aceita consulta textual na mesma chamada.

`tests/fixtures/annex_cases.json` mantém 23 contraprovas de roteamento e ambiguidade; `scripts/benchmark_anexos.py` mede seu resultado na CI. São consultas de diagnóstico versionadas pelo produtor, não evidência de acurácia universal ou homologação independente. Os índices continuam derivados e qualquer retificação exige fonte versionada independente.

## Proveniência, retificações e alerta do cronograma

- O registro não normativo `edital/fontes_oficiais.json` distingue fonte original comprovada, publicação FAPEC observada, **PDF institucional UFMS de 47 páginas, com título e p. 13 cotejados e hash remoto pendente**, e retificações verificadas. Ver `docs/RETIFICACOES_E_PROVENIENCIA.md` para o procedimento de cotejo dos bytes e atualização versionada.
- A inconsistência do **Anexo II, página 13** permanece aberta (`ALERTA-DOC-01`): resultado preliminar em `10/02/2027` e recurso impresso `11 e 12/01/2027`. Não inferir datas corretas.
- `python scripts/probe_pdf_ufms.py --live`: sonda apenas de leitura que compara SHA-256 **dos bytes recebidos** da URL institucional com o manifesto; não arquiva PDF, não muda o edital e não integra o gate online da CI.
- `python scripts/validate_fontes_oficiais.py --check`: gate offline obrigatório. `python scripts/monitor_fapec.py --live`: busca **somente leitura** em uma página oficial; saída inconclusiva não comprova inexistência de retificação.

## Localização e comandos

- `edital/manifest.json`: índice máquina-legível com IDs, páginas, offsets e categorias; **81 chunks**.
- `edital/chunks/pNN-cMM.md`: trecho literal com metadados. O `char_start/char_end` permite remontar a página sem perda.
- `python scripts/chunk_edital.py --check`: confere integralidade contra o Markdown canônico.
- `python scripts/search_edital.py "consulta" --cargo 523 --limit 4`: resultados classificados, sem rede ou dependência de vetores.
- `python scripts/search_edital.py --page 45`: leitura completa da página, incluindo todos os chunks.

**Política:** priorizar rota exata por seção; caso necessário, BM25 lexical; ampliar contexto só depois. Não confundir relevância do resultado com verdade jurídica ou ausência de atualização.
