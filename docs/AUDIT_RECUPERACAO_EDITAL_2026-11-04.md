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
- **Limitação residual conhecida:** quadro de vagas (p. 14–18) e atribuições (p. 20–28) ainda não têm intervalos específicos por linha de cargo. Um resultado lexical nessas páginas não deve ser interpretado como requisito do cargo sem conferência visual da linha da tabela.

## 5. Consulta a fontes externas

- Portal da banca FAPEC para o concurso UFMS: `https://portal.concurso.fundacaofapec.org.br/edital/ver/22`, consultado em 04/11/2026. A página mostra a publicação de abertura com etiqueta `001/2026`; **não presumir** que a numeração seja idêntica ao Edital PROGEP/UFMS nº 152/2026.
- Boletim oficial UFMS: `https://boletimoficial.ufms.br/`.
- Nenhuma retificação específica foi **comprovada** nesta inspeção pontual; isso **não comprova inexistência**. A fonte canônica não foi atualizada com atos externos.
- Evitar confusão com outros órgãos da UFMS: há um Edital **152/2026-PROPP** (iniciação científica) que é **outro certame**, não retificação do Edital 152/2026-PROGEP.

### Evidência adicional de robustez (CI)

- [Execução 41789110667](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41789110667), commit `e6d35913d1485200285ba129e03bb0ebb0b05ef2`: **34 testes aprovados**, 47 páginas e 81 chunks fiéis; benchmark curado Hit@1 **27/27**; conjunto adversarial **9/9** no Top 1 com **rota BM25 e frase literal ancorada**, 3/3 isolamentos, 2/2 negativos, 1/1 conflito, 2/2 códigos de leis não confundidos com itens.
- A [execução 41789035123](https://github.com/Andraus35/UFMS-MEU-ESTUDO/actions/runs/41789035123) registrou falha legítima no *fixture*: a expressão esperada `não discriminação` não estava literal na transcrição; a consulta adversarial foi preservada, e a âncora de prova foi corrigida para `administração de conflitos`. Revalidação posterior aprovada. **Não apagar a falha histórica.**
- A validação adversarial foi criada e refinada pela mesma frente produtora; é evidência de testes separados, **não** homologação independente.

## 6. Próxima retomada técnica

1. Reconfirmar HEAD exato e CI do PR #1, sem merge.
2. Conferir novamente fonte oficial FAPEC/Boletim quanto à anomalia do Anexo II, registrando eventual ato separado.
3. Avaliar se é necessário indexar linha/célula de vagas e requisitos dos cargos 523 e 324 para impedir contaminação em p. 14–18, com contraprovas e evidências.
4. Ampliar holdout com perguntas não usadas na construção dos aliases; manter testes adversariais e documento canônico intacto.
