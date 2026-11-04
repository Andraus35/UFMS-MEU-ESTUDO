# Referência isolada de GP-1 com testes verdes — ciclo 8

**Data:** 04/11/2026, fuso America/Campo_Grande.  
**Escopo:** demonstrar um desenho possível para IGP-12/13/14, **sem implementar a integração** no harness UFMS.  
**Repositório:** `Andraus35/UFMS-MEU-ESTUDO`, PR pedagógico #2.  
**HEAD técnico PR #1 inspecionado:** `1079d7aa2cadb97d099d1e478f9e83b36180a624` (draft, sem merge).  
**HEAD pedagógico anterior:** `66c218f91548ef4316b024930186036cece5fa49` (draft, sem merge).

## 1. Evidência executada

Criado um **módulo Python puro e não produtivo** `gp1_reference.py` e sua suíte `test_gp1_reference.py`, testados localmente com Python 3.13. O código foi mantido em artefato separado, **não foi gravado no PR #1 nem no PR #2**, para preservar a separação de frentes. Não há chamadas de rede, banco de dados, credenciais ou escrita de resultados. O módulo aceita apenas fixtures declaradas sintéticas, o que é um guard de demonstração, **não um mecanismo real de autorização**.

| Testes | Observação real | Escopo |
|---|---|---|
| Referência não produtiva | **15 executados / 15 PASS / 0 FAIL** | IGP-12 (5), IGP-13 (5), IGP-14 (5) |
| Regressões do `core.py` antigo | **11 PASS / 0 FAIL / 3 NOT_IMPLEMENTED** | IGP-01–14, mantendo três contratos antigos sem implantação |
| Testes do harness integrado no GitHub após mudança | **Não executados nesta entrega** | Não inferir da execução local |
| Dados de estudante utilizados | **0** | Todos os exemplos são fictícios |

## 2. Capacidades da referência — sem confusão com integração

**IGP-12 — normalização:** convenção desconhecida devolve `pending_clarification` sem evento canônico; convenção declarada e contagens coerentes permitem derivar `total=15`, `acertos=8`, `erros=4`, `nao_respondidas=3`. Percentuais arredondados não se transformam em contagens.

**IGP-13 — duas tentativas:** uma única identificação de caderno externo `EXT-FICT-44` admite `TRY-A` e `TRY-B`; a correção vinculada da segunda atualiza apenas `TRY-B`, deixando a primeira íntegra; duplicatas e correções órfãs são rejeitadas. A projeção matemática soma observações disponíveis, mas **não interpreta repetições das mesmas questões como evidência independente de domínio**.

**IGP-14 — tempo:** `recorded_at` é exigido com fuso; `attempt_at` é opcional, validado quando presente e nunca preenchido automaticamente pelo instante do registro. Timestamp sem fuso, malformado ou posterior ao registro é recusado no exemplo.

### Limitações importantes

- O módulo `gp1_reference.py` **não é um patch de produção**: usa tipos de evento `attempt_recorded` / `attempt_corrected` que o `core.py` original ainda não aceita.
- O módulo **não migra** eventos antigos, não implementa repositório de eventos, não conecta TEC/Qconcursos, não define controle real de permissões e não testa proteção contra concorrência em GitHub.
- A origem/semântica de relatórios do estudante exigirá confirmação efetiva da plataforma/usuário, e não um simples campo `source_confirmed` enviado por cliente não confiável.
- Embora os 15 testes sejam verdes, **GP-1 continua PENDENTE**, assim como GP-2 a GP-5. Esses testes **não** representam aprovação integral dos 102 critérios pedagógicos.

## 3. Integridade dos artefatos locais

| Artefato | Hash verificado |
|---|---|
| `gp1_reference.py`, Git blob | `224ed8e1c13299a3acf078e30e0877b48577ddfc` |
| `test_gp1_reference.py`, Git blob | `e16b95754f6b4c6d45756e92f797a70e2405e2d5` |
| `scripts/core.py`, blob fonte PR #1 (cópia local `core.py`) | `28649e5b649c239cb03d748ab5822c352ddfe1db` |
| `config/topics.csv`, blob fonte PR #1 | `d733ec5af292934fa4efa0e892470c27603065f6` |
| `FIXTURES_INGESTAO_GP1_2026-11-04.json`, blob fonte PR #2 (cópia local `fixtures.json`) | `bd060fd2263c686e7dc4f56bf0c97f5fc5112dfc` |
| Pacote local reproduzível `ufms_gp1_reference_ciclo8.zip`, SHA-256 | `dc3dc599a8aba4536de89311ffd4fb71725b6d745d92d98339a58aed3c201adb` |

O ZIP com código, testes, fixtures, readme, saídas e recibo está disponibilizado como artefato **desta conversa**; não foi enviado ao GitHub. A prova de integridade de cópias técnicas vale para os blobs enumerados. O relatório publicado neste PR preserva resultado e hashes para futura conferência independente, sem fingir que o código do protótipo está commitado.

### Reprodução

No diretório extraído do ZIP, com Python 3.10+:

```sh
python -m unittest -v test_gp1_reference.py
python run_fixtures.py
```

Os comandos atuam somente em dados sintéticos; o segundo cria `execution_report.json` local. A comparação de Git blobs está embutida na suíte antiga de fixtures. Para reproduzir, é preciso ter o pacote, pois **os novos dois arquivos Python não constam do PR pedagógico**.

## 4. Entrega à engenharia

Para ENG-01/02/06, a sequência recomendada é:
1. Reconsultar o HEAD técnico, regras e gates antes de editar; decidir esquema de eventos/migração, com provas de replay.
2. Traduzir o comportamento de referência em adaptador de plataforma e projeção de tentativas versionados, preservando o `core.py` legado.
3. Criar primeiro testes que falhem para as capacidades novas no harness real; executar regressões anteriores, sem duplicá-las.
4. Não habilitar `personal_results_writes_enabled` nem gravar resultados pessoais sem autorização e provas de privacidade.
5. Registrar SHA da candidata, testes e CI reais, readback e handoff técnico; **sem merge automático**.

**Próxima ação nesta sessão pedagógica:** revisar decisões de método somente diante de novos comportamentos implementados ou conflitos de requisitos. Não multiplicar documentos sem evidência ou copiar o protótipo para o PR #2.
