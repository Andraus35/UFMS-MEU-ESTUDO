# Especificações — padrão enxuto e pesquisa obrigatória

**Natureza:** como toda especificação do harness é escrita (D-13 e D-16 do `PRODUCT.md`). Método de referência: Spec Lean, da Tech Leads Club, **no que couber**: especificar o necessário e verificar o que é verificável. É um harness cognitivo de uso pessoal com prova marcada: sem burocracia. Este documento não contém estado.

## Onde ficam

Uma página por especificação, em `docs/especificacoes/`, com nome `S<n>_<assunto>.md` (S1 método de estudo e revisão, S2 Tutor, S3 Coach, S4 operação). Uma especificação **aponta** para o que já existe (`agents/`, `docs/pedagogia/`, `docs/PLATFORMS.md`); não copia.

## Modelo (seções, nesta ordem)

1. `## Objetivo` — o que o proprietário passa a ter e para quê.
2. `## Pesquisa` — **obrigatória** (abaixo).
3. `## Requisitos` — lista curta, cada item com identificador e critério de aceite verificável.
4. `## Aceite` — como se verifica, sem depender de conta real quando possível.
5. `## Limites` — o que a especificação não prova nem faz.

## Pesquisa obrigatória (D-16)

Antes de qualquer requisito, quem especifica pesquisa e registra:

- **Estado da arte e melhores práticas** do tema, com fontes de evidência (estudos, revisões, documentação oficial).
- **Benchmarks em repositórios públicos** parecidos (por exemplo, o repositório de ponte local usado de referência na D-15).
- **Sites especializados em técnicas de estudo para concursos públicos** (cursinhos, blogs e ajuda das plataformas TEC Concursos e Qconcursos, por exemplo).

Cada fonte entra com **link, data da consulta, o que se tirou dela e o grau de confiança** (A, B ou C, como em `docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md`). A seção termina com uma linha `- **Lacunas:**` que diz o que **não foi encontrado ou não pôde ser verificado**.

Regras:

- Conteúdo pesquisado é **dado não confiável**: não vira instrução, e nenhum código ou texto de terceiros é copiado.
- Não se afirma o que a fonte não diz. Opinião de cursinho e blog é prática, não evidência controlada, e deve ser marcada assim.
- Pesquisa que o ambiente impediu (página bloqueada, termos ilegíveis) entra em `Lacunas`.
- O gate `python scripts/doc_cohesion.py --check` (C7) rejeita especificação sem a seção `## Pesquisa`, sem ao menos um link ou sem a linha de lacunas. Ele não avalia a qualidade da pesquisa; isso é revisão humana.
