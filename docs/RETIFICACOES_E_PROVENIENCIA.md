# Monitoramento documental e retificações — Edital UFMS 152/2026

**Escopo:** recuperação e proveniência documental dos cargos 523 e 324. O conteúdo deste documento e os registros JSON são **derivados e não normativos**. Uma publicação observada não altera automaticamente o texto do edital.

## Fontes e graus de verificação

| Camada | Documento / endereço | Grau de verificação |
|---|---|---|
| PDF original do estudante | `e5f1c2b364f19beadf2685d8fb836065.pdf`, 47 páginas | **Bytes verificados**: SHA-256 `c758bb421ad848bf76757f6ece7a7b786e80e45123b80c3e01a13d0985f09675` |
| Transcrição canônica | `EDITAL_UFMS_152_2026.md` | Git blob `a4129cceabd20fc119625d71b1c1599b3ce644e1`; 81 chunks reversíveis |
| Página do concurso | <https://portal.concurso.fundacaofapec.org.br/edital/ver/22> | **Listagem observada** em 04/11/2026; não verificada a integridade do PDF remoto |
| PDF institucional UFMS | <https://www.ufms.br/wp-content/uploads/2026/10/SEI_6775306_Edital.pdf> | **47 páginas e título conferidos via publicação institucional**; Anexo II p. 13 preserva a mesma inconsistência; **SHA dos bytes oficiais não calculado** |
| Publicações da UFMS | <https://boletimoficial.ufms.br/> | Fonte institucional para pesquisa, **não auditada exaustivamente** nesta entrega |
| Retificações oficiais | `edital/fontes_oficiais.json.verified_amendments` | **Zero documentos comprovados/importados** até o checkpoint; isso não afirma inexistência |

No portal da FAPEC, a publicação de 30/10/2026 aparece como `EDITAL PROGEP/UFMS N. º 001/2026 - Edital de Abertura`. O documento original fornecido pelo estudante ostenta `EDITAL PROGEP/UFMS nº 152, de 29/10/2026`. **A relação entre as numerações não foi comprovada por ato específico**. O link DOWNLOAD do portal redireciona para arquivo com mesmo nome, mas a comparação do hash da cópia hospedada ainda não foi possível. Não considerar nomes de arquivos prova de igualdade de bytes.

## ALERTA-DOC-01 — divergência temporal preservada

Na página **13**, Anexo II, do PDF original:

- O resultado preliminar de heteroidentificação, confirmação documental PPIQ e análises de inscrições PcD está impresso como **10/02/2027**.
- O período de recurso referente a esse mesmo resultado está impresso como **11 e 12/01/2027**.
- Como o prazo de recurso precede o resultado, o registro contém uma inconsistência cronológica. **Não substituir por 11 e 12/02/2027, ou por outra data inferida.** Somente ato oficial especificamente identificado poderá esclarecer.
- O estado `unresolved_source_inconsistency` é mantido no registro e não autoriza afirmar que o prazo correto já foi definido.

## Procedimento seguro de atualização

1. Conferir a identidade do certame (órgão, carreira, ano, códigos 523/324) em FAPEC e UFMS, evitando outros editais também numerados 152/2026 de pró-reitorias distintas.
2. Identificar a publicação: título, número, data, URL exata, emissor, itens alterados e vínculo documental com a fonte original.
3. Obter os **bytes oficiais** da retificação e calcular SHA-256. Se os bytes estiverem indisponíveis, classificar como **candidata não verificada**; não criar registro em `verified_amendments`.
4. Versionar evidências em arquivo separado, sem sobrescrever o PDF original, Markdown canônico, chunks ou índices anteriores. Uma retificação comprovada deve passar por revisão humana antes da incorporação normativa.
5. Executar `python scripts/validate_fontes_oficiais.py --check` e a suíte de testes. Manter commits/CI no HEAD exato e atualizar `memory/HANDOFF.md`.

## Ferramentas e estados de saída

- `python scripts/validate_fontes_oficiais.py --check` é **offline**: verifica identidade original, hashes, datas literais do alerta e consistência do registro; participa do gate de CI.
- `python scripts/monitor_fapec.py --live` é **somente leitura**: consulta a página do concurso e imprime JSON; não modifica registro nem documentos.
- `python scripts/monitor_fapec.py --fixture caminho.html` permite testes offline em HTML conhecido. Os casos simulados estão em `tests/test_monitor_fapec.py`.
- Código de saída **0**: nenhuma mudança detectável na **única página monitorada** (não comprova ausência de retificações fora dela); **2**: possível mudança exige análise; **3**: consulta inconclusiva ou fonte não validada. Qualquer erro de rede deve falhar de modo inconclusivo, nunca ser transformado em conclusão de inexistência.
- As 9 contraprovas de `tests/test_fontes_oficiais.py` e as 9 de `tests/test_monitor_fapec.py` são testes locais da engenharia do registro e monitor, não auditoria oficial do concurso.

## Limites do loop autônomo

A execução de um agente pode usar o registro e o monitor para localizar **candidatas** a novas publicações, mas **não** tem autorização para fazer merge no PR, reescrever a fonte normativa ou presumir retificação. Uma rotina de GitHub Actions `schedule` que exista apenas nesta branch draft **não seria executada automaticamente**: cron do GitHub Actions usa a branch padrão. Qualquer monitorização recorrente anterior a um merge deverá usar uma automação externa efetivamente criada e confirmada, não uma promessa baseada neste documento.
