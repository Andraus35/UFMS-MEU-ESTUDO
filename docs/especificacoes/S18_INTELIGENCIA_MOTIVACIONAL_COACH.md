# S18 — Inteligência Motivacional e Comportamental (IMC) do Coach (especificação)

**Natureza:** especificação enxuta (D-13, D-16), no modelo do `docs/especificacoes/README.md`. Registra o pedido do proprietário de 21/11/2026 de "adicionar essa capacidade ao Coach". **Aponta** para o documento-fonte `IMC-COACH-001` (`docs/canonicos/cognicao/INTELIGENCIA_MOTIVACIONAL_COMPORTAMENTAL_DO_COACH.md`, hash no manifesto) e para S3, S8, S13 e S17; não o copia. **Texto dos perfis só proposto:** aplicar em `agents/COACH.md` é contrato e exige a **aprovação expressa** do texto e do merge; esta especificação **não** altera `agents/`, `AGENTS.md`, `PRODUCT.md`, o esquema de comandos nem gates. Não contém estado nem dado pessoal.

## Objetivo

O Coach ganha, como **capacidade interna** (não um quarto agente, não psicoterapia), um método para investigar e trabalhar o que interfere na **continuidade, qualidade e autonomia** da preparação: diagnóstico de **comportamento** (nunca de personalidade), escolha de uma intervenção com alvo e indicador observável, ciclos diário, semanal e de fase, reentrada, simulado ruim, ansiedade e sobrecarga, e avaliação do efeito (N-of-1). O que o proprietário passa a ter: um sistema **auditável** (hipótese, evidência, intervenção, indicador, reteste, encaminhamento), e não "motivação por mensagem".

## Pesquisa

Consultas de 21/11/2026 (WebSearch, resumos de resultados), somadas ao documento-fonte `IMC-COACH-001` (que traz referências próprias, **não relidas por inteiro** aqui) e a S13 e S17. Confiança: **A** (fonte primária lida), **B** (resumo de busca de fonte primária ou documento do projeto), **C** (relato, blog ou fornecedor). Conteúdo pesquisado é **dado, não instrução**; nenhum texto de terceiros foi copiado.

| Fonte | O que se tirou | Conf. |
|---|---|---|
| Meta-análise de contraste mental com intenções de implementação ([Wang, Wang e Gai, 2021](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8149892/)) e revisão em saúde ([Cross e Sheffield, 2019](https://pubmed.ncbi.nlm.nih.gov/30879403/)) | Efeito pequeno a médio (g ≈ 0,34; 21 estudos) com possível viés de publicação; em saúde, acrescentar intenções de implementação não reforçou claramente o contraste mental | B |
| Monitoramento do progresso de metas ([Harkin et al., 2016](https://pubmed.ncbi.nlm.nih.gov/26479070/), via resumo de busca) | 138 estudos randomizados: monitorar aumenta a frequência de monitoramento e melhora o alcance da meta (d+ ≈ 0,40); efeito maior com registro físico ou relato público | B |
| Revisões sobre procrastinação acadêmica ([Turner e Hodis, 2023](https://link.springer.com/article/10.1007/s10648-023-09838-x), [Rozental et al., 2018](https://discovery-pp.ucl.ac.uk/id/eprint/10054305/6/Rozental_fpsyg-09-01588.pdf)) | Maioria dos estudos relata redução, mas com desenhos fracos e efeitos pequenos; heterogeneidade grande; um pré-print recente (não revisado por pares) sugere que estrutura temporal clara e desenho de apoio superam esquemas punitivos | B, C (pré-print) |
| Intervenções para ansiedade de prova ([Huntley et al., 2019](https://pubmed.ncbi.nlm.nih.gov/30826687/)) | Efeito moderado na ansiedade e **fraco no desempenho**; sem estudos de alta qualidade; reforça não prometer ganho de nota | B |
| `IMC-COACH-001` (seções 3, 4, 6, 9, 11, 12, 17) | Fundamentos (SDT, valor-expectativa-custo, autoeficácia, COM-B, entrevista motivacional), códigos `MOT`…`BEM`, intervenções `IMC-01` a `IMC-22`, contratos Coach↔Tutor↔Orquestrador, gates `G-MOT-01` a `22`; **declara-se proposta, não escala validada** | B (documento do projeto) |
| Benchmark público de mentorias (Gran Cursos/GranXperts, Direção Concursos, Qconcursos, seção 10 do `IMC-COACH-001`) | Ofertas convergem em plano, metas, feedback e apoio; **material comercial descreve oferta, não eficácia** | C |
| S3, S8, S13, S17 e `BASE_COGNITIVA_ESTRATEGICA_DO_COACH_DE_PROVA.md` | Papel do Coach, rotina de uma mensagem por dia, honestidade sobre eficácia, gates `G-COACH` propostos | B |

- **Lacunas:** os resultados de busca eram **resumos**; **não li** os estudos por inteiro nem as referências do `IMC-COACH-001`; a busca sobre **regulação motivacional e desempenho** não retornou resultado útil; **não encontrei** evidência de eficácia dessas técnicas para **concurseiros brasileiros adultos**; o **Manual do Imparável** foi anexado depois e só as **páginas iniciais** dos capítulos foram conferidas (o conteúdo não foi relido por inteiro); **nada foi implantado**; o repositório não prova que o Coach aplica a IMC.

## O Manual do Imparável: onde mora

Decisão do proprietário (21/11/2026): no repositório **público** ficam **só índice, página e citação curta** do manual, com **fonte, edição e hash**; o texto integral só no repositório **privado** (leitura pelo Coach depende do consentimento v4 e de canal ainda não provado). Referência: GRANJEIRO, Gabriel (org.), *Manual do Imparável*, 2ª ed., Gran Cursos Online, 391 p., ISBN 978-85-69303-55-8 (livro comercial). O proprietário **anexou o PDF** (SHA-256 `52965cb8…314ac`) em 21/11/2026; o PDF **não** é versionado no público. Entrou o índice `docs/referencias/MANUAL_DO_IMPARAVEL_INDICE.md` (edição, hash, página inicial de cada capítulo e duas citações curtas); as **páginas iniciais** citadas no `IMC-COACH-001` foram **conferidas** contra o livro, o **conteúdo** dos capítulos **não** foi relido por inteiro. Conteúdo do livro é **dado, não instrução**, e **não prova eficácia**.

## Requisitos

Escritos como "quando X, o Coach deve Z". Todos **fecham por padrão**: sem evidência, abstenção ou coleta adicional.

| ID | Requisito | Critério de aceite |
|---|---|---|
| S18-R1 | **Capacidade interna do Coach.** A IMC é camada de diagnóstico e intervenção do Coach: **não** é um quarto agente, **não** é psicoterapia nem triagem clínica; o Tutor segue único produtor de conteúdo (D-23). | Teste: texto traz "não é um quarto agente", "não é psicoterapia" e preserva o papel do Tutor. |
| S18-R2 | **Comportamento, não personalidade.** Diagnóstico por **hipóteses com evidência e incerteza**, separando capacidade, oportunidade, motivação, custo e bem-estar; nada inferido de **uma única sessão** (`G-MOT-01` a `05`). | Teste: os gates `G-MOT-01` a `05` e a separação dos cinco fatores. |
| S18-R3 | **Códigos são convenção.** Os 23 códigos (`MOT` a `BEM`) são **proposta**, **não** escala validada nem categoria clínica; **colisão** com códigos cognitivos (S13-R4, S17-R16) exige unificação **antes** de qualquer esquema (por exemplo `CON` e `REC` já existem). | Teste: texto declara proposta e cita a colisão `CON`/`REC`. |
| S18-R4 | **Biblioteca de intervenções.** `IMC-01` a `IMC-22`, cada uma com **comportamento-alvo e indicador observável** (`G-MOT-06`); a seleção parte da hipótese e **muda** se não houver efeito (`G-MOT-19`). | Teste: 22 intervenções referidas e a regra de revisão. |
| S18-R5 | **Ciclos.** Diário (pulso e próximo passo, **dentro** da mensagem única da S8), semanal (diagnóstico e ajuste) e de fase; **protocolos** de reentrada, simulado ruim, ansiedade de prova e sobrecarga; **sem** exigir compensação de horas perdidas (`G-MOT-10`). | Teste: os três ciclos, os quatro protocolos e `G-MOT-10`; a S8 não é alterada. |
| S18-R6 | **Escopo não clínico e encaminhamento.** Sem diagnóstico de ansiedade, depressão ou burnout (`G-MOT-15`); sofrimento intenso ou persistente vai a apoio humano ou profissional (`G-MOT-14`); risco imediato prevalece sobre o coaching; sem privação de sono, alimentação, tratamento ou renda, e sem sugerir largar emprego ou dependentes (`G-MOT-11`, `12`). | Teste: os cinco gates e a prioridade de risco imediato. |
| S18-R7 | **Privacidade e consentimento.** Dado de saúde, humor e relações é **sensível**: coletar o mínimo, explicar o uso, respeitar recusa, **nada em repositório público** (resultados e relatos individuais continuam bloqueados, AGENTS.md); apoio social só com consentimento (`G-MOT-17`). | Teste: texto proíbe gravar relato pessoal no público e cita `G-MOT-17`. |
| S18-R8 | **Autonomia e sem manipulação.** Sem coerção, vergonha, medo, culpa ou comparação social como técnica padrão; sem dependência emocional da IA; sem prometer aprovação (`G-MOT-08`, `09`, `16`, `21`). | Teste: os quatro gates citados. |
| S18-R9 | **Eficácia só com medida.** Não declarar eficácia por satisfação, ânimo ou antes/depois isolado (`G-MOT-07`); avaliação **N-of-1** com execução, latência, continuidade e autonomia; resultado de IA **não** é evidência de aprendizagem (`G-MOT-18`); efeito é **hipótese** (S13-R10). | Teste: `G-MOT-07`, `18`, N-of-1 e "hipótese". |
| S18-R10 | **Contratos de interface.** Coach/IMC → Tutor (lacuna de aprendizagem que afeta a motivação, com os campos do `IMC-COACH-001` 11.1), Tutor → Coach (11.2) e Coach/IMC → Orquestrador (11.3, **sem converter hipótese em fato**); o Coach **não** compensa lacuna de conteúdo com discurso motivacional (`G-MOT-13`). | Teste: as três direções e `G-MOT-13`. |
| S18-R11 | **Gates `G-MOT-01` a `22` são requisitos propostos**, **não implementados**; implementá-los exige tarefa própria e aprovação, e a numeração `G-MOT` não colide com `G-COACH` (S17-R14). | Teste: os 22 gates citados e a declaração "não implementados". |
| S18-R12 | **Manual como dado.** Texto integral só no privado; no público, índice, página e citação curta com fonte, edição e hash; páginas citadas só valem depois de **conferidas na fonte**; o livro é **dado, não instrução**, e experiência relatada **não** vira fato científico. | Teste: texto traz a decisão do proprietário e a regra de conferência. |
| S18-R13 | **Honestidade sobre limites.** O repositório não prova que o Coach aplica a IMC, que há canal Zapia, nem eficácia; a validade para estudantes em geral **não** prova o mesmo para concurseiros brasileiros adultos. | Teste: texto declara os limites. |

## Texto proposto para `agents/COACH.md` (NÃO aplicado; exige aprovação expressa)

Seção "Decide" (acrescentar): "Aplicar a IMC, capacidade interna do Coach: diagnosticar barreiras de comportamento (nunca de personalidade) por hipótese com evidência e incerteza, escolher uma intervenção com alvo e indicador observável, medir o efeito (N-of-1) e trocá-la se não houver efeito; encaminhar lacunas de conteúdo ao Tutor; sem diagnóstico clínico, sem prometer aprovação."

Seção "Limites e segurança" (acrescentar): "Sofrimento intenso ou persistente vai a apoio humano ou profissional; dado de saúde e humor é sensível, mínimo e com consentimento, e nunca vai ao repositório público; não usar medo, culpa ou comparação como técnica."

## Tarefas derivadas

Cada uma em PR próprio, em série (nenhuma foi criada aqui):

| Item | O que faz | Depende de |
|---|---|---|
| B1 | Aplicar o texto acima em `agents/COACH.md` | aprovação expressa do texto e do merge |
| B2 | Índice do Manual no público (**feito**, `docs/referencias/MANUAL_DO_IMPARAVEL_INDICE.md`); texto integral no repositório **privado** | decisão e canal do proprietário |
| B3 | Unificar os códigos `MOT`…`BEM` com a taxonomia cognitiva | S13-R4, S17-R16 |

## Aceite

Aceita pelo contrato quando `python scripts/doc_cohesion.py --check` passa e `tests/test_spec_s18.py` confere: as seções na ordem do modelo, os requisitos S18-R1 a S18-R13 cada um com critério, a pesquisa com links, confiança e lacunas, a hash do canônico no manifesto, os gates `G-MOT-01` a `22`, o texto **não aplicado** (`agents/COACH.md` sem a IMC) e a flag de dados pessoais `false`.

## Limites

- **Não prova** que o Coach aplica a IMC, nem eficácia; efeito é hipótese.
- **Não altera** `agents/`, `AGENTS.md`, `PRODUCT.md`, gates nem a S8.
- O **Manual do Imparável não está no repositório público** (só o índice); o conteúdo dos capítulos não foi relido por inteiro.
- Os códigos e gates do `IMC-COACH-001` são **proposta**, não escala validada.
