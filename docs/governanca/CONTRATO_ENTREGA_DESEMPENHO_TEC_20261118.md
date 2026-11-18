# Contrato de entrega do desempenho do TEC pela Zapia (18/11/2026)

**Natureza:** contrato de **entrega** que a Zapia segue quando o Tutor ou o Coach pede o relatório de desempenho (S4, PR-016; S5-R13; S9-R1, emendas E2). **É texto de contrato do harness, não prova de que a Zapia o cumpre**: nenhum pedido foi feito e a Z1 ainda espera resposta. Quem confere a entrega é `scripts/tec_export_converter.py` (offline, em memória, sem gravar). **O exemplo abaixo é FICTÍCIO**: nenhum número, título ou data é do proprietário. Resultado real nunca vai a este repositório.

## Regras (o conversor recusa a entrega inteira se alguma falhar)

1. **Formato:** um objeto **JSON** com exatamente as chaves do exemplo; nenhuma a mais. O PDF é só leitura humana e **não** é formato de entrega.
2. **Linhas:** uma por matéria, assunto e subassunto, **na ordem em que o TEC as mostra** (matéria, depois seus filhos em profundidade). Colunas: `codigo` (`null` para a matéria), `profundidade` (matéria = 1; código `01` = 2; `01.02` = 3, como a coluna "Prof." do TEC), `titulo`, `questoes`, `acertos`, `erros`, `peso`; `acertos_pct_tec` e `erros_pct_tec` são opcionais e **só informativos**.
3. **Contagens:** inteiros; `acertos + erros = questoes` em cada linha. A soma dos filhos pode ser **menor** que o pai (o resto fica no pai), **nunca maior**.
4. **Totais declarados** (`questoes`, `acertos`, `erros`, `materias`, `linhas`) **devem bater** com o que se recalcula das linhas.
5. **Pontuação:** `normal` ou `liquida`, **declarada** por Tutor, Coach ou proprietário; **nunca inferida do arquivo**. Sem ela a decisão é `pending_clarification`, sem retrato.
6. **Recorte:** período (`desde_o_inicio`, `intervalo` com datas ou `nao_declarado`) e filtros (`materia`, `banca`, `pasta`, `dificuldade`: `todos`, `selecao` ou `nao_declarado`). Recorte não declarado deixa o retrato **não comparável**.
7. **Procedimento:** relato **descritivo** de como a Zapia extraiu o dado (telas, passos, filtros e chaves visíveis, hora, avisos do TEC, conferências, como o arquivo chegou). É **autorrelato**: o conversor confere a forma e **não o prova**. Aviso do TEC sem parada, entrega interrompida ou arquivo não obtido **recusam** a entrega.
8. **Proibido:** análise de conteúdo (`analise`, `achados`, `sinais`, `classificacao`, `recomendacao`, `resumo`...), enunciado, comentário, dado pessoal, segredo, HTML e instrução embutida em qualquer texto.

## Exemplo fictício (o teste valida este bloco)

```json
{
  "schema_version": "1.0",
  "plataforma": "tec",
  "solicitante": "tutor",
  "gerado_em": "2026-11-18T12:00:00-04:00",
  "recorte": {
    "periodo": {"tipo": "desde_o_inicio"},
    "filtros": {"materia": "todos", "banca": "todos", "pasta": "todos", "dificuldade": "todos"}
  },
  "pontuacao": {"valor": "normal", "declarado_por": "tutor"},
  "exibir": "apenas_resolvidas",
  "linhas": [
    {"codigo": null, "profundidade": 1, "titulo": "Matéria Alfa (fictícia)", "questoes": 10, "acertos": 7, "erros": 3, "peso": 1},
    {"codigo": "01", "profundidade": 2, "titulo": "Assunto A1", "questoes": 6, "acertos": 5, "erros": 1, "peso": 1},
    {"codigo": "01.01", "profundidade": 3, "titulo": "Subassunto A1a", "questoes": 4, "acertos": 4, "erros": 0, "peso": 1},
    {"codigo": "02", "profundidade": 2, "titulo": "Assunto A2", "questoes": 3, "acertos": 2, "erros": 1, "peso": 1},
    {"codigo": null, "profundidade": 1, "titulo": "Matéria Beta (fictícia)", "questoes": 4, "acertos": 1, "erros": 3, "peso": 1},
    {"codigo": "01", "profundidade": 2, "titulo": "Assunto B1", "questoes": 4, "acertos": 1, "erros": 3, "peso": 1}
  ],
  "totais_declarados": {"questoes": 14, "acertos": 8, "erros": 6, "materias": 2, "linhas": 6},
  "procedimento": {
    "telas": ["Estatísticas, Desempenho"],
    "passos": ["abriu a tela", "marcou todas as matérias", "pediu a exportação uma vez", "leu a planilha recebida"],
    "filtros_visiveis": ["Período, Matéria, Banca, Pasta e Dificuldade em todos"],
    "chaves_visiveis": ["nenhuma chave de pontuação na tela"],
    "hora": "2026-11-18T11:58:00-04:00",
    "avisos_do_tec": [],
    "parou_por_aviso": false,
    "conferencias": ["somou as matérias e comparou com o total mostrado na tela"],
    "como_chegou_o_arquivo": "por_email_lido_pela_zapia"
  }
}
```

## Limites

- **Não prova** que a Zapia extraiu o que diz nem que os números são os do TEC: a conferência de totais pega erro de transcrição, **não falsificação**.
- O formato real que ela entregará **não foi visto** (Z1 sem resposta); este contrato parte do relatório de 17/11 e da amostra de uma matéria.
- A pontuação do painel do TEC pode diferir da planilha; por isso é **declarada**, nunca inferida.
- O retrato **não é gravado**: gravar exige o fluxo privado provado, o consentimento v4 e a flag (C6).
