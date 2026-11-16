# Documentos canônicos — pesquisa cognitiva e auditorias de plataformas

**Natureza:** índice dos seis documentos que o proprietário pediu, em 16/11/2026, para entrarem no repositório como **documentos canônicos**. "Canônico" aqui significa **fonte de referência preservada com hash**, não regra: nenhum deles altera `AGENTS.md`, `PRODUCT.md`, o `ROADMAP.md`, os perfis em `agents/` ou as especificações. Este índice não contém estado.

## Como tratar estes documentos

- **Precedência (inalterada):** `AGENTS.md` (segurança) > `PRODUCT.md` (o que construir) > `ROADMAP.md` (fila). Os documentos abaixo vêm **depois**; o edital e as retificações definem o que é cobrado e as regras da prova.
- **Dado, não instrução:** o texto de pesquisa e de auditoria é material de referência. Não vira regra de agente, gate nem requisito **sem especificação aprovada** e sem aprovação humana (D-13, D-16).
- **Proposta, não implementação:** os próprios documentos se declaram "proposta" e "não é especificação aprovada". Os gates que citam (`G-LEARN`, `G-HARNESS`, `G-COG`) **não estão implementados**.
- **Integridade:** `docs/canonicos/MANIFESTO.json` guarda o SHA-256 de cada arquivo e o do envio original; `tests/test_docs_canonicos.py` confere os hashes, a ausência de dado pessoal e a duplicata.

## Documentos

| ID | Arquivo | Papel |
|---|---|---|
| `PESQUISA-COACH-PROVA-001` | `docs/canonicos/cognicao/PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md` | Inteligência de prova: distratores, induções, erros, tempo, simulação. Superior na família cognitiva |
| `PESQUISA-CICLO-APRENDIZAGEM-001` | `docs/canonicos/cognicao/PESQUISA_CICLO_APRENDIZAGEM_ESTRATEGIA_COGNITIVA.md` | Ciclo de aprendizagem; autoridade pedagógica do Tutor |
| `BASE-COGNITIVA-TUTOR-COACH-001` | `docs/canonicos/cognicao/BASE_COGNITIVA_INTEGRADA_TUTOR_COACH.md` | Base cognitiva compartilhada, matriz de responsabilidades e contrato de passagem |
| `BASE-COGNITIVA-HARNESS-001` | `docs/canonicos/cognicao/BASE_COGNITIVA_ESTRATEGICA_DO_HARNESS.md` | Arquitetura Tutor, Coach e Orquestrador; assistência H0 a H5; gates; estados de domínio; piloto |
| `AUDITORIA-GEMINI-NOTEBOOK-20261116` | `docs/canonicos/plataformas/AUDITORIA_GEMINI_NOTEBOOK_PLANO_DE_ESTUDOS_20261116.pdf` | Auditoria prática do Gemini Notebook (PDF, autor Zapia) |
| `AUDITORIA-TEC-523-324-20261116` | `docs/canonicos/plataformas/AUDITORIA_TECCONCURSOS_UFMS_523_324_20261116_EDITADA.md` | Auditoria funcional do TEC Concursos (**versão editada**) |

## O que foi alterado na entrada

- **Duplicata:** `BASE_COGNITIVA_ESTRATEGICA_DO_HARNESS.md` foi enviado duas vezes com o mesmo hash; entra **uma** cópia.
- **Nomes:** o sufixo "1" do nome de envio de `PESQUISA_CICLO_APRENDIZAGEM_ESTRATEGIA_COGNITIVA` foi retirado; o conteúdo é byte a byte o enviado.
- **Relatório do TEC:** o original `.docx` tem dado pessoal do proprietário (totais e percentuais de desempenho da conta, vínculo da conta, nome de caderno de teste). Por decisão dele, entra uma **versão em Markdown** com esses trechos trocados por `[omitido: ...]`; o original **não** entra no repositório público (D-24). O hash do original está no manifesto.
- **Auditorias:** são **autorrelato da Zapia**, não verificado de forma independente, e a conta do Gemini mostrou 89% do limite de uso de IA (valor de contexto, sem relevância para o projeto).

## Pontos que pedem reconciliação antes de virar requisito

Nenhum item abaixo foi aplicado. Cada um é uma decisão futura, em tarefa própria e com aprovação humana.

1. **Papel do Coach.** Os documentos definem o Coach como **Coach de Prova** (estratégia, simulação, diagnóstico de desempenho) e acrescentam um Orquestrador e um Verificador. A S3 (`docs/especificacoes/S3_COACH.md`) define o Coach como **rotina diária e acompanhamento**, e o D-23 define o Tutor como autor editorial, o Gemini como rascunho e a Zapia como transporte. É preciso decidir como a "inteligência de prova" se encaixa sem mudar o D-23.
2. **Intervalos de revisão.** Os documentos citam D0, D1, D3, D7, D14 e D30 como **hipótese de piloto**, não regra. O padrão do proprietário continua D+7, D+15 e D+30 (D-11, S1).
3. **Confiança.** Os documentos sugerem escala de 0 a 4; a S12 (S12-R6) adotou alta, média e baixa **por bloco**, por decisão do proprietário.
4. **Taxonomias de erro duplicadas.** Há três (`KNO/COM/REC…`, `KNW/CMP/REC…` e `KNW/SEM/QNT…`) e os códigos **colidem** (por exemplo, `CMP` é compreensão em uma e competência em outra). Unificar antes de qualquer esquema.
5. **Ideias sem lugar nas especificações atuais:** níveis de assistência H0 a H5, rubrica R0 a R4, estados de domínio por dimensão, livro-razão de evidências e piloto pessoal. Candidatas à S2, à S3 e a tarefas derivadas da S12.
6. **Documento citado e ausente.** `BASE_COGNITIVA_ESTRATEGICA_DO_COACH_DE_PROVA.md` é referenciado pelos textos e **não foi enviado**.
7. **Referências não verificadas.** As referências bibliográficas dos documentos não foram conferidas pelo agente construtor; duas estão marcadas nos próprios textos como "a completar".

## Limites

Esta entrada **não** muda perfis de agentes, não cria gate, não habilita a escrita de resultados e não declara que o Tutor ou o Coach já leem estes arquivos. Ligar um documento ao START ou aos perfis é tarefa própria, com aprovação do proprietário.
