# RM-05 — prescritor de cadernos

**Data:** 05/11/2026  
**Base:** `main@3cbe6ffe74babf9f778216c52596994830e64143`  
**Tarefa:** ENG-05 / GP-2  
**Escopo:** gerar instruções para o estudante, sem operar plataformas.

## Contrato de saída

`prescribe_notebook` recebe candidato de um snapshot RM-04, objetivo, modalidade, plataforma preferida, capacidades/estoque confirmados e meta opcional de questões. Gera:
- `recommendation_id` interno determinístico;
- referência ao snapshot, edital, commit e política;
- cargos/tópicos e filtros em camadas;
- quantidade sugerida somente quando estoque e meta estão confirmados;
- fallback em cinco passos;
- retorno mínimo esperado;
- justificativa, alternativa adiada e estado honesto.

## Camadas e fallback

- Camada 0: cargo/tópico são escopo obrigatório. Se filtros não estiverem confirmados, ficam `pending_confirmation`; o fallback não pode removê-los.
- Camada 1: novidade e diversidade, como preferências pedagógicas.
- Camada 2: FAPEC apenas se houver filtro/amostra confirmado.
- Camada 3: ano, dificuldade, novidade e comentários somente se a plataforma oferecer tais filtros.
- Fallback: remover refinamentos opcionais; ampliar período; considerar banca comparável com ressalva; ampliar nível/tipo sem rotular como oficial-equivalente; combinar tópicos somente com justificativa e dentro do escopo.

## Estados e limites

- `status=recommended` não significa caderno criado.
- `creation_status=not_created`, `platform_notebook_id=null`, `platform_notebook_id_status=unknown`.
- Disponibilidade desconhecida/zero resulta em `unavailable_or_unverified`; não inventar estoque.
- `questions_suggested` permanece null sem quantidade-alvo e estoque confirmado.
- Capacidade de filtro marcada `confirmed` exige `evidence_ref`.
- Nenhuma rede, login, scraping, API privada, escrita ou efeito externo ocorre.

## Testes

`tests/test_notebook_prescriber.py` cobre ausência de disponibilidade, confirmação com evidência, limite de estoque, filtros pendentes, fallback, override, IDs determinísticos e ausência de efeitos externos. Dados e IDs são fictícios.
