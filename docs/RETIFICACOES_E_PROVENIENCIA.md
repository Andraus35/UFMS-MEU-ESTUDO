# Monitoramento documental e retificações — Edital UFMS 152/2026

**Escopo:** recuperação e proveniência documental dos cargos 523 e 324. O conteúdo deste documento e os registros JSON são **derivados e não normativos**. Uma publicação observada não altera automaticamente o texto do edital.

**Política confirmada pelo responsável pelo projeto em 04/11/2026:** o PDF local do projeto ESTUDO UFMS, Edital PROGEP/UFMS nº 152/2026, é a **fonte oficial primária** para consultas e estudo. Não há pendência de autenticação remota que impeça seu uso. Monitorar somente a possibilidade de **retificações posteriores**, a serem comprovadas, preservadas e aplicadas separadamente. O cotejo de hash de outra cópia da edição inicial é um controle auxiliar opcional, não requisito de início dos estudos.

## Fontes e graus de verificação

| Camada | Documento / endereço | Grau de verificação |
|---|---|---|
| PDF oficial local do projeto (fornecido pelo responsável) | `e5f1c2b364f19beadf2685d8fb836065.pdf`, 47 páginas | **Bytes verificados**: SHA-256 `c758bb421ad848bf76757f6ece7a7b786e80e45123b80c3e01a13d0985f09675` |
| Transcrição canônica | `EDITAL_UFMS_152_2026.md` | Git blob `a4129cceabd20fc119625d71b1c1599b3ce644e1`; 81 chunks reversíveis |
| Página do concurso | <https://portal.concurso.fundacaofapec.org.br/edital/ver/22> | **Listagem observada** em 04/11/2026; não verificada a integridade do PDF remoto |
| PDF institucional UFMS | <https://www.ufms.br/wp-content/uploads/2026/10/SEI_6775306_Edital.pdf> | **47 páginas e título conferidos via publicação institucional**; Anexo II p. 13 preserva a mesma inconsistência; **SHA dos bytes oficiais não calculado** |
| Publicações da UFMS | <https://boletimoficial.ufms.br/> | Fonte institucional para pesquisa, **não auditada exaustivamente** nesta entrega |
| Retificações oficiais | `edital/fontes_oficiais.json.verified_amendments` | **Zero documentos comprovados/importados** até o checkpoint; isso não afirma inexistência |

No portal da FAPEC, a publicação de 30/10/2026 aparece como `EDITAL PROGEP/UFMS N. º 001/2026 - Edital de Abertura`. O documento original fornecido pelo estudante ostenta `EDITAL PROGEP/UFMS nº 152, de 29/10/2026`. **A relação entre as numerações não foi comprovada por ato específico**. O link DOWNLOAD do portal redireciona para arquivo com mesmo nome, mas a comparação do hash da cópia hospedada ainda não foi possível. Não considerar nomes de arquivos prova de igualdade de bytes.

**Gate de evidência (04/11/2026):** o validador offline bloqueia agora qualquer promoção da observação FAPEC para `remote_pdf_equivalence=verified` por simples edição do JSON, mesmo que o hash declarado coincida com o SHA-256 do PDF enviado pelo estudante. O mesmo vale para o status `observed_listing_remote_pdf_hash_verified` isolado. Até que exista arquivo remoto da FAPEC preservado, origem verificável e recomputação de seus bytes, **somente a equivalência dessa cópia remota** deve permanecer `unverified`, hash remoto nulo e `observed_listing_not_remote_pdf_hash_verified`. Esta checagem evita falso positivo, mas **não calcula nem valida os bytes de uma URL externa**. Duas contraprovas específicas testam os casos de falsificação declarativa.

**Hierarquia temporal:** texto do edital oficial local como base; retificações oficiais futuras comprovadas prevalecem apenas nos dispositivos expressamente afetados. Divulgação ou link sem documento íntegro verificado é observação, não retificação. **Nenhum dos mecanismos de sonda/arquivamento remoto bloqueia o estudo do edital local**, nem atesta sozinho a vigência de uma retificação.

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

## Sonda de hash do PDF institucional — comparação reproduzível

A primeira tentativa de obter o arquivo institucional diretamente neste ambiente em 04/11/2026 não chegou aos bytes: o download falhou e o acesso HTTP por linha de comando apresentou erro de resolução DNS. Isso **não significa que o PDF seja inexistente ou diferente**. A página oficial segue acessível para leitura textual e visual por outro mecanismo, mas esse acesso não fornece o arquivo bruto para hash.

Foi criado `scripts/probe_pdf_ufms.py`, um comparador **somente leitura**, estritamente fixado à URL institucional `https://www.ufms.br/wp-content/uploads/2026/10/SEI_6775306_Edital.pdf`. Em ambiente que permita rede, executar:

```bash
python scripts/probe_pdf_ufms.py --live
```

O programa obtém o SHA-256 esperado de `edital/manifest.json`, recusa redirecionamentos, limita o download a 12 MiB, exige HTTP 200, tipo PDF e marcadores `%PDF-` e `%%EOF`, e calcula o SHA-256 **dos bytes recebidos em streaming**. O resultado é JSON, sem alterações no repositório:

- `digest_match_unarchived` — códigos de saída **0**: SHA-256 remoto recebido coincide com o original **naquela consulta**, mas **os bytes não foram arquivados** e não há aprovação de retificação.
- `digest_mismatch` — código **2**: houve bytes com aparência de PDF e SHA-256 diferente; **não** reescrever automaticamente a fonte, investigar versão e proveniência.
- `unverifiable` — código **3**: rede, redirecionamento, HTML, arquivo inválido ou erro de leitura; **não** inferir equivalência ou diferença.

A sonda não é um gate online da CI: testes determinísticos offline exercitam 12 cenários sem dependência de serviços externos. A CI não deve tornar-se frágil por indisponibilidade de rede; a execução real exige ambiente com acesso externo e registro de evidência. Mesmo um digest remoto igual registrado em logs não preenche automaticamente os campos `verified` do JSON: o gate atual requer a preservação dos bytes oficiais e auditoria separada antes de liberar equivalência normativa.

## Arquivamento externo de bytes oficiais — evidência recuperável

`scripts/archive_pdf_ufms.py` amplia a sonda anterior para guardar **bytes efetivamente recebidos** da URL fixa da UFMS e um recibo JSON lado a lado. Exige Python 3.11, HTTPS, resposta não redirecionada, HTTP 200, tipo PDF, limites de tamanho e assinatura/EOF de PDF; não modifica `edital/fontes_oficiais.json`, nem a fonte canônica, nem habilita retificações automaticamente.

Em um ambiente com acesso à URL institucional, crie previamente uma pasta **fora do checkout Git** e execute:

```bash
mkdir -p /tmp/ufms-evidencias
python scripts/archive_pdf_ufms.py --live --out-dir /tmp/ufms-evidencias
```

Se os bytes forem recebidos e validados, serão salvos com nome derivado do SHA-256 (`ufms152-2026-<SHA>.pdf`), juntamente com `ufms152-2026-<SHA>.json`. A escrita usa criação exclusiva, sem sobrescrever evidência existente; o arquivo é relido e rehashed após a gravação. Para reconferir o pacote:

```bash
python scripts/archive_pdf_ufms.py --verify /tmp/ufms-evidencias/ufms152-2026-<SHA>.json
```

Estados de `--live`: **0** = `archived_digest_match` (hash igual à cópia original do estudante, arquivo e recibo guardados), **2** = `archived_digest_mismatch` (hash diferente, preservar evidência e investigar), **3** = `unverifiable` (consulta, escrita ou readback inconclusivo). Não interpretar 3 como inexistência nem 0 como homologação jurídica ou incorporação de retificação. Não publicar o recibo `offline_fixture` dos testes como prova de aquisição HTTPS oficial. O JSON identifica o método da aquisição, mas não é assinado por autoridade externa, portanto não constitui atestação independente da origem.

Há **17 contraprovas offline** em `tests/test_archive_pdf_ufms.py`, incluindo duplicação, adulteração de PDF e recibo, URL redirecionada, diretório inseguro, rollback após falha no readback, hash esperado forjado e diferença entre teste offline e coleta direta. O validador compara o hash esperado também com o manifesto canônico, não apenas com um valor declarado no recibo. A CI executa os testes, mas **não** o download remoto; a comparação real continua pendente até execução em ambiente com conectividade e revisão da evidência.

## Ferramentas e estados de saída

- `python scripts/validate_fontes_oficiais.py --check` é **offline**: verifica identidade original, hashes, datas literais do alerta e consistência do registro; participa do gate de CI.
- `python scripts/monitor_fapec.py --live` é **somente leitura**: consulta a página do concurso e imprime JSON; não modifica registro nem documentos.
- `python scripts/monitor_fapec.py --fixture caminho.html` permite testes offline em HTML conhecido. Os casos simulados estão em `tests/test_monitor_fapec.py`.
- Código de saída **0**: nenhuma mudança detectável na **única página monitorada** (não comprova ausência de retificações fora dela); **2**: possível mudança exige análise; **3**: consulta inconclusiva ou fonte não validada. Qualquer erro de rede deve falhar de modo inconclusivo, nunca ser transformado em conclusão de inexistência.
- As 9 contraprovas de `tests/test_fontes_oficiais.py` e as 9 de `tests/test_monitor_fapec.py` são testes locais da engenharia do registro e monitor, não auditoria oficial do concurso.

## Limites do loop autônomo

A execução de um agente pode usar o registro e o monitor para localizar **candidatas** a novas publicações, mas **não** tem autorização para fazer merge no PR, reescrever a fonte normativa ou presumir retificação. Uma rotina de GitHub Actions `schedule` que exista apenas nesta branch draft **não seria executada automaticamente**: cron do GitHub Actions usa a branch padrão. Qualquer monitorização recorrente anterior a um merge deverá usar uma automação externa efetivamente criada e confirmada, não uma promessa baseada neste documento.
