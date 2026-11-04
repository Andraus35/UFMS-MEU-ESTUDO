# Auditoria de recuperação e proveniência — 04/11/2026

**Objeto:** Edital PROGEP/UFMS nº 152/2026, repositório `Andraus35/UFMS-MEU-ESTUDO`, PR #1 (draft).

## 1. Identidade documental verificada

- PDF original disponibilizado pelo estudante: **47 páginas**, SHA-256 recalculado `c758bb421ad848bf76757f6ece7a7b786e80e45123b80c3e01a13d0985f09675`; coincide com `edital/manifest.json.source_pdf_sha256`.
- Markdown canônico: `EDITAL_UFMS_152_2026.md`, SHA de blob Git `a4129cceabd20fc119625d71b1c1599b3ce644e1`. A CI verifica a reversibilidade dos **81 chunks** para esse Markdown, não a identidade visual automática com o PDF.
- **Proveniência distinta:** PDF original (primário), Markdown e chunks (extração derivada), índices e aliases (classificação derivada), resultados da busca (localizadores), eventual retificação oficial (nova fonte versionada). Jamais converter uma camada em outra silenciosamente.

## 2. Cotejo visual amostral contra PDF original

Páginas críticas **renderizadas** para inspeção de estrutura, limites de programas e quadros (amostra, não auditoria exaustiva de 47 páginas):

| Página PDF | Verificação pontual contra transcrição | Situação |
|---|---|---|
| **12** | Anexo I, remuneração: R$ 5.215,39 (superior), R$ 3.181,39 (médio); auxílio-alimentação R$ 596,00 (20h) e R$ 1.192,00 (40h) | Valores conferidos na extração |
| **15** | Quadro de vagas: cargo **523**, **29** vagas, **Campo Grande** | Valores conferidos; requisitos extensos exigem cautela na leitura de colunas |
| **18** | Quadro de vagas: cargo **324**, **18** vagas, **Campo Grande**, **Ensino Médio completo** | Valores conferidos |
| **29** | Anexo V: conhecimentos gerais e começo de conteúdos específicos de outros cargos na mesma página | Separação imposta por índices derivados |
| **35–36** | Programa **523** começa no fim da p. 35 e prossegue no início da p. 36, seguido de programas de outros cargos | Limites de programa conferidos visualmente |
| **45** | Programa **324 a 330** fica abaixo de programas de outras especialidades na mesma página | Limites de programa conferidos visualmente |

**Limites do cotejo:** não houve comparação visual linha a linha do texto inteiro, nem validação de todas as células de todos os quadros.

## 3. Anomalia encontrada no PDF original — não corrigir silenciosamente

**ALERTA-DOC-01 — cronograma do Anexo II, p. 13.** O resultado preliminar de heteroidentificação/análise consta em **10/02/2027**, mas o período de recurso logo abaixo aparece como **11 e 12/01/2027**. A sequência é cronologicamente inconsistente. A mesma redação está no PDF original e na extração, portanto **não é erro causado pelo chunking**. Não substituir `01` por `02` sem ato oficial; buscar esclarecimento/retificação no canal competente e registrar como fonte separada.

## 4. Busca adversarial e regressões

- Conjunto inicial versionado: `tests/fixtures/retrieval_cases.json`, 29 consultas curadas, métricas Hit@k. Não é avaliação de generalização.
- Conjunto adicional **fora das frases de treino dos aliases**, mas preparado na mesma frente de engenharia (não equivale a auditoria externa independente): `tests/fixtures/adversarial_cases.json` com 17 contraprovas: recuperações lexicais, contaminação entre cargos, citações de leis que parecem números de item e conflitos explícitos.
- `tests/test_adversarial.py` verifica isolamento e falha segura; `scripts/benchmark_adversarial.py` mede o conjunto adicional na CI.
- Busca por `--cargo` agora impede leitura lexical dos programas de outros cargos **nas páginas 29–45**, mesmo sem `--area`. Para consultas com várias palavras, um único termo coincidente não basta no BM25. Se consulta e filtro identificam cargos distintos, ocorre erro explícito.
- **Limitação residual:** o quadro de vagas (p. 14–18) passou a ter recortes auditáveis para **523 e 324**, usando `edital/vagas_index.json`, `scripts/index_vagas.py` e a opção `--vagas-cargo`. As linhas dos **demais** cargos e as atribuições (p. 20–28) não foram indexadas campo a campo. Para os dois cargos-alvo, a qualificação integral deve continuar sendo cotejada com o PDF quando houver dúvida.

## 5. Consulta a fontes externas

- Portal da banca FAPEC para o concurso UFMS: `https://portal.concurso.fundacaofapec.org.br/edital/ver/22`, consultado em 04/11/2026. A página mostra etiqueta `001/2026`, embora o PDF disponibilizado ao estudante traga `152/2026`. O link **DOWNLOAD** do portal redireciona a um arquivo com o mesmo nome (`e5f1c2b364f19beadf2685d8fb836065.pdf`) do PDF original inspecionado, mas os bytes da cópia remota não foram obtidos para recalcular o hash. **Não equiparar a etiqueta ao número do ato nem afirmar equivalência criptográfica do download remoto sem verificá-lo.**
- Boletim oficial UFMS: `https://boletimoficial.ufms.br/`.
- Nenhuma retificação específica foi **comprovada** nesta inspeção pontual; isso **não comprova inexistência**. A fonte canônica não foi atualizada com atos externos.
- Evitar confusão com outros órgãos da UFMS: há um Edital **152/2026-PROPP** (iniciação científica) que é **outro certame**, não retificação do Edital 152/2026-PROGEP.

### Evidência adicional de robustez (CI)

- [Execução 41789110667](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41789110667), commit `e6d35913d1485200285ba129e03bb0ebb0b05ef2`: **34 testes aprovados**, 47 páginas e 81 chunks fiéis; benchmark curado Hit@1 **27/27**; conjunto adversarial **9/9** no Top 1 com **rota BM25 e frase literal ancorada**, 3/3 isolamentos, 2/2 negativos, 1/1 conflito, 2/2 códigos de leis não confundidos com itens.
- A [execução 41789035123](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41789035123) registrou falha legítima no *fixture*: a expressão esperada `não discriminação` não estava literal na transcrição; a consulta adversarial foi preservada, e a âncora de prova foi corrigida para `administração de conflitos`. Revalidação posterior aprovada. **Não apagar a falha histórica.**
- A validação adversarial foi criada e refinada pela mesma frente produtora; é evidência de testes separados, **não** homologação independente.

### 6. Recorte adicional de atribuições (Anexo IV)

- Em 04/11/2026 foram conferidas visualmente as páginas **23** e **28** do PDF original de SHA-256 `c758bb421ad848bf76757f6ece7a7b786e80e45123b80c3e01a13d0985f09675`.
- A descrição do **523** ocupa `p23-c01`, sem invadir a atribuição da Produção Cultural anterior nem a de Gestão Pública (Campus) na sequência. O texto literal tem **2.349 caracteres**, com SHA-256 do recorte `965513446559f2f54bdc23b971b3057303af4d6506b7c9b6419c79aeb31ca933`.
- A descrição do **324** ocupa `p28-c02`, sem incluir a atribuição anterior de Veterinária e Zootecnia ou o rodapé. Tem **2.370 caracteres**, SHA-256 do recorte `52b8ef5302b52bc247037591623eafbabc66b0c29caa2df660f560bef36c4cbe`.
- `edital/atribuicoes_index.json` é derivado e não normativo; `scripts/index_atribuicoes.py` verifica limites literais, fonte e hashes. `scripts/search_edital.py` fornece roteamento por cargo e restringe BM25 do Anexo IV, quando há filtro de cargo, aos trechos verificados.
- `tests/test_atribuicoes.py` adiciona **8 testes** de integridade, contaminação, busca, mutação e custo de contexto; a CI integra `scripts/index_atribuicoes.py --check`. Testes são evidência técnica, **não** parecer de auditoria independente.

## 7. Contraprovas cruzadas entre anexos — 04/11/2026

**Objetivo:** impedir falsa equivalência entre requisito de ingresso (Anexo III), descrição de atribuições (Anexo IV) e conteúdo da prova (Anexo V) para os cargos 523 e 324.

- A busca admite `--anexo III|IV|V --cargo 523|324`, com `--area` apenas para o Anexo V; `--anexo` não deve ser combinado com consulta textual, `--topic` ou seletores concorrentes.
- A rota `search_programa` lista **todos os tópicos aplicáveis**: 523 — 14 (4 gerais + 10 específicos), 324 — 13 (4 gerais + 9 específicos). Ela retorna página, ID, chunk, offsets e pequeno excerto; `--full` recupera os trechos literais. Esse inventário **não** cria conteúdo curricular nem plano de estudos.
- Perguntas que misturam duas ou três naturezas documentais são rejeitadas, não respondidas parcialmente. A `tests/fixtures/annex_cases.json` contém agora **23 contraprovas**: 15 rotas positivas e 8 conflitos, incluindo pedidos com dois ou três numerais romanos de anexos.
- `tests/test_anexos.py` acrescenta **7 testes** de rotas explícitas, recuperação integral, offsets, isolamento e falha segura; a CI executa `scripts/benchmark_anexos.py`.
- **Defeito encontrado na primeira execução de CI:** a consulta `responsabilidades e procedimentos Resolução 497-Coun` estava explicitamente sob `--area especificos`, mas foi inicialmente confundida com Anexo IV. A CI [41793492274](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41793492274) **falhou**, motivando a correção para respeitar o escopo programático. A falha histórica permanece documentada.
- **Evidência confirmada após correção:** GitHub Actions [41793859691](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41793859691), SHA `3db50c23b058b0219f27362e7a0b65dd974b3837`: **56/56 testes**, benchmark cruzado **21/21** (15/15 positivos, 6/6 conflitos), benchmark inicial Hit@1 27/27 e adversarial 9/9. Auditoria e testes foram preparados pela mesma frente; não equivalem a avaliação externa cega.

### Verificação pontual de publicação oficial — 04/11/2026

O portal de editais da [FAPEC](https://portal.concurso.fundacaofapec.org.br/edital/ver/22) mostra a publicação de abertura sob etiqueta **001/2026**, datada de 30/10/2026; o PDF do estudante traz Edital PROGEP/UFMS **152/2026**, de 29/10/2026. Não se deve presumir correspondência de numeração nem equivalência de bytes sem baixar e conferir o arquivo remoto. **Na página oficial consultada, não foi identificada retificação que esclareça o ALERTA-DOC-01** sobre o recurso de heteroidentificação do Anexo II, p. 13. Essa inspeção pontual não comprova inexistência de ato em outros locais ou após a consulta. A anomalia permanece pendente, sem modificação normativa.

### Revalidação ampliada (23/23)

- Detectada a ambiguidade de perguntas como `"Anexos III e IV do cargo 523"`, anteriormente roteáveis só pelo primeiro numeral romano. A extração de numerais foi modificada para verificar **todos** os anexos citados quando houver referência a anexos. O conjunto ganhou dois conflitos adicionais.
- **Execução comprovada:** [run 41794387965](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41794387965), SHA `a595cfa4b41aad0c6b949870439e270e6c0f9855`, `success`: **62 testes**, diagnóstico dos Anexos III/IV/V **23/23** (15 roteamentos, 8 ambiguidades rejeitadas), benchmark original 27/27 Hit@1, adversarial 9/9 Hit@1, 81 chunks íntegros e índices de 23 tópicos, 2 linhas de vagas e 2 descrições de atribuições.
- Na consulta ao portal da FAPEC, o botão de download redirecionou para armazenamento externo com endereço temporário, mas não foi possível obter e comparar os bytes oficiais. **O hash da cópia hospedada pela FAPEC não foi verificado**, embora o hash do PDF originalmente fornecido pelo estudante esteja comprovado. Manter o documento primário e suas futuras retificações versionados separadamente.

## 8. Próxima retomada técnica

1. Reconfirmar HEAD exato e CI do PR #1, sem merge.
2. Conferir novamente fonte oficial FAPEC/Boletim quanto à anomalia do Anexo II, registrando eventual ato separado.
3. **Concluído:** indexação das linhas III, atribuições IV e dos tópicos V, com 21 contraprovas de não equivalência. Próximo passo: verificar fontes primárias da FAPEC/UFMS para eventual esclarecimento ou retificação do ALERTA-DOC-01 e conferir a identidade dos bytes oficiais, sem aplicar alterações automáticas.
4. Ampliar holdout com perguntas não usadas na construção dos aliases; manter testes adversariais e documento canônico intacto.
