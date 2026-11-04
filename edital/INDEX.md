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

## Localização e comandos

- `edital/manifest.json`: índice máquina-legível com IDs, páginas, offsets e categorias; **81 chunks**.
- `edital/chunks/pNN-cMM.md`: trecho literal com metadados. O `char_start/char_end` permite remontar a página sem perda.
- `python scripts/chunk_edital.py --check`: confere integralidade contra o Markdown canônico.
- `python scripts/search_edital.py "consulta" --cargo 523 --limit 4`: resultados classificados, sem rede ou dependência de vetores.
- `python scripts/search_edital.py --page 45`: leitura completa da página, incluindo todos os chunks.

**Política:** priorizar rota exata por seção; caso necessário, BM25 lexical; ampliar contexto só depois. Não confundir relevância do resultado com verdade jurídica ou ausência de atualização.
