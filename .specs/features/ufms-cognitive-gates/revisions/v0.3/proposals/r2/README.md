# PLAN v0.3-r2 — proposta para corrigir o gate oficial TLC

**Não aprovada.** Esta revisão NÃO modifica o PLAN v0.3-r1 aprovado nem os CHECKS congelados: é uma candidata documental separada. Nenhuma obrigação EARS foi alterada.

## Motivação independente

O GitHub Actions executou de fato `validate_plan.py` e `validate_checks.py` oficiais, fixados ao commit `1da2195067c14ae5d44dc615b31cb26f50ebeb91` do repositório Tech Leads Club. As duas execuções do HEAD `677d91e7c06f50ca9f3a96f0348454ad8de00896` falharam (push `41867793245`; pull_request `41867808884`).

Falhas reproduzidas: `validate_plan.py` encontra 2 erros (um nome de módulo lido incorretamente por adjacência de backticks no hop 2 e ausência de status 3xx/403 na interface CLI restrita). `validate_checks.py` detecta 2 erros no original (marcador de aprovação no arquivo original e Coverage de 16 estados sem Cn) e 1 erro na view temporária com aprovação (Coverage). Há warnings não bloqueadores de diagramas e provas sem seletores reconhecíveis, não declarados sanados nesta revisão.

## Alterações estritamente delimitadas

1. PLAN Shape: remover backticks ambíguos em `(exists)` sem mudar o bootstrap.
2. PLAN Surface: declarar o runner CLI de fixtures acessível somente dentro do ambiente local/CI, sem endpoint externo, e documentar que qualquer processo local com acesso ao runner pode invocá-lo. Isso não amplia permissões de ferramentas reais.
3. CHECKS Coverage: enumerar os 16 estados do Surface e associar cada um a um Cn, sem inferir execução dos testes.

## Gates

- 27/27 critérios EARS originais idênticos; CHECKS C1–C27 continuam testes futuros, **0/27 PASS funcional**.
- Novo PLAN é PROPOSTA: requer aprovação humana própria. Não reutilizar o `APROVO` anterior.
- Executar `validate_plan.py` oficial na proposta. `validate_checks.py` sem marcador de aprovação deve reprovar, corretamente, até o novo aceite.
- GQ-D segue REPROVADA até reauditoria independente; GQ-C NOT_RUN; GQ-O BLOCKED.

Nenhum merge/deploy/credencial/resultado pessoal; PR #1, #2 e #4 intocados.
