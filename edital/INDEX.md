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
| Inscrição, taxas, prova, regras, recursos, datas, cotas | 1–13 |
| Vagas, formação e lotação | 14–18 |
| Cargo **523** — vaga e requisito | **15** |
| Cargo **324** — vaga e requisito | **18** |
| Atribuições de cargos | 20–28 |
| Conhecimentos gerais — 523 e 324 | **29** |
| Conteúdo específico **523** | **35–36** |
| Conteúdo específico **324** | **45** |
| Admissão e documentos | 46–47 |

## Localização e comandos

- `edital/manifest.json`: índice máquina-legível com IDs, páginas, offsets e categorias; **81 chunks**.
- `edital/chunks/pNN-cMM.md`: trecho literal com metadados. O `char_start/char_end` permite remontar a página sem perda.
- `python scripts/chunk_edital.py --check`: confere integralidade contra o Markdown canônico.
- `python scripts/search_edital.py "consulta" --cargo 523 --limit 4`: resultados classificados, sem rede ou dependência de vetores.
- `python scripts/search_edital.py --page 45`: leitura completa da página, incluindo todos os chunks.

**Política:** priorizar rota exata por seção; caso necessário, BM25 lexical; ampliar contexto só depois. Não confundir relevância do resultado com verdade jurídica ou ausência de atualização.
