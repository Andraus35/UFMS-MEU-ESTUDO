# Cognitive Gates v0.3-r2 — estado da especificação

**Escopo desta recuperação SIM-06:** preservar no repositório atual o PLAN v0.3-r2 e seus 27 CHECKS, o aceite humano literal registrado no recibo, os bytes de origem, e o verificador de proveniência. Esta integração é **documental**; não instala nem ativa o motor cognitivo.

## Proveniência e escopo do aceite

- Aceite registrado: **“APROVO”**, em 04/11/2026, restrito ao PLAN v0.3-r2 e à derivação dos CHECKS sem alteração dos requisitos normativos.
- Commit de origem congelado: `426286a913ea17adddb2cdb951120b45282ad938`; blob Git do PLAN de origem `a1482c25e064a1ccc06c4a649a704fbd5bf97cf5`; SHA-256 de origem `e528bd36ff4e106622e04b009a8cce381ea5fa079558cc14adc3f5227f90362c`.
- O `approval-receipt.json` mantém `no_merge=true`, `no_deploy=true`, `no_personal_results_writes=true` no contexto do aceite original. Este PR incorpora somente artefatos de especificação e sua proveniência; não promove o motor a operação nem revoga esses limites.
- O plano r1 anterior permanece preservado e é verificado pelo validador de snapshot.

## Situação das provas

| Camada | Estado registrado | Interpretação |
|---|---|---|
| Requisitos EARS | 27/27 | Conteúdo documental identificado |
| CHECKS | 27/27 | Oráculos especificados; não significa execução |
| Provas funcionais ponta a ponta | **0 PASS / 27 NOT_RUN** | Nenhum dos 27 comportamentos foi homologado em Tutor/Coach |
| Testes isolados de subconjuntos | 43/43 para C2/C3/C25/C26, conforme snapshot | Não equivalem a E2E, nem cobrem C1–C27 |
| GQ-D | **REPROVADA** | Requer reauditoria independente |
| GQ-C | **NOT_RUN** | Não executada |
| GQ-O | **BLOCKED** | Não há enforcement/implantação demonstrados |

## Limites de integração

1. A aprovação do PLAN é aprovação para especificação, não homologação funcional nem aprovação de produção.
2. A versão r3 e seus CHECKS preview permanecem **não aprovados** e não são importados.
3. Nenhum gate cognitivo é adicionado ao caminho de orientação cotidiana nesta integração; não introduzir aprovação humana por mensagem.
4. Nenhuma credencial, integração Telegram/Calendar, escrita pessoal ou publicação externa é habilitada.
5. Os arquivos históricos e o recibo devem permanecer imutáveis; alterações futuras exigem nova revisão e nova proveniência.

## Validação

Executar a partir da raiz:

```sh
python -m unittest discover -s .specs/features/ufms-cognitive-gates/revisions/v0.3/approved-r2/tests -v
python .specs/features/ufms-cognitive-gates/revisions/v0.3/approved-r2/verify_approval_snapshot.py --root .specs/features/ufms-cognitive-gates/revisions/v0.3/approved-r2
```

O resultado PASS do verificador prova somente identidade, cadeia de bytes e limites do recibo. Não altera GQ-D/GQ-C/GQ-O.
