# Auditoria adversarial pré-aprovação — Spec Lean UFMS (ciclo de revisão v0.2)

**Data:** 04/11/2026. **Parecer:** **PLAN REVISADO, AINDA NÃO APROVÁVEL AUTOMATICAMENTE**. Não autoriza CHECKS oficial, BUILD, push, merge ou persistência pessoal.

## Objeto e método

- Fonte examinada: `plan.md` v0.1 (21 EARS), `checks-preview.md` (21 linhas) e `benchmark.md` local, além das regras atuais do repositório UFMS.
- Norma de procedimento: Tech Leads Club **Spec Lean v2.2.0**, especialmente obrigação de um critério observável por check, exemplos adversariais, aprovação humana do PLAN e verificador diferente do autor.
- Natureza: **auditoria estática de especificação**, não teste de segurança do LLM nem validação oficial da skill. A tentativa do `npx` falhou por DNS `EAI_AGAIN` no npm.
- Resultado desta revisão: 6 critérios adicionais AC22–AC27, atualização de interfaces, quatro propostas de one-way doors e prévia de checks expandida para 27. Nenhuma obrigação está congelada.

## Findings priorizados e tratamento

| ID | Severidade | Falha na v0.1 | Correção no draft v0.2 | Evidência de aceitação futura |
|---|---|---|---|---|
| AU-01 | P0 | Gate existia no desenho, mas não era o único caminho técnico das ferramentas | Gateway isolado de credenciais, C22, D2; proibição de rota direta | Zero chamadas externas quando LLM tentar bypass + verificação de configuração real |
| AU-02 | P0 | Autorização vinculada sem prova de uso único/replay | Nonce/expiração/consumo atômico, C23 e D2 | Repetição e corrida com mesmo token não geram segundo efeito |
| AU-03 | P0 | Citação `page+span` poderia ser válida com afirmação normativa falsa | AC3 somente localidade; AC25 verifica valor do fato crítico já conferido | Falsa data de prova citando a página certa continua bloqueada |
| AU-04 | P0 | Saída do modelo poderia contornar verificação de conteúdo e aparecer diretamente | `safe_renderer` como único publicador, C26, D4 | Resposta sem aprovação vinculada não aparece no canal de saída |
| AU-05 | P1 | Estado `STALE` vs `STALE_STATE`, ausência de `UNCONFIRMED` na interface | Superfície/diagrama/status coerentes | Testes de falha parcial e estado defasado, mesmas strings |
| AU-06 | P1 | Entrada sem tamanho máximo, risco de overload e custos não delimitados | Limites provisórios 65.536/262.144 bytes (AC24) | Testes UTF-8 no limiar e um byte acima; nenhum acesso ao modelo |
| AU-07 | P1 | Avaliação 40 × 5 podia virar selo de qualidade sem manifesto reproduzível | Metadados de modelo/dataset/grader/trials exigidos, AC27 | Release bloqueado na ausência de qualquer campo, holdout separado |
| AU-08 | P1 | Defesa contra prompt injection dependia de reconhecer qualquer instrução maliciosa | AC11 restringe fonte da política e ações a versões confiáveis | PDF/CSV/tool/Telegram não alteram política mesmo quando texto parece autorizado |
| AU-09 | P1 | Aprovação humana, modelo executor, retenção e segregação de segredos não decididos | Mantidos como `blocks`/`blocks go-live` explícitos | Decisão humana documentada antes de aprovar portas semânticas |
| AU-10 | P2 | Preview com 21 checks ficaria desatualizado após novas obrigações | Prévia atualizada para 27 mapeamentos, sem criar `checks.md` | Cobertura `AC1–27` bijetiva e 9 dimensões revisadas |

**Validação estrutural auxiliar executada:** 27/27 critérios e mapeamentos; nove seções detectadas; **6/6 mutantes estruturais rejeitados** (exclusão de critério, troca de mapeamento, falsa aprovação, porta D4 ausente, seção Sources ausente e estado inconsistente). Isso verifica a sanidade documental, **não** os controles de segurança do futuro harness nem os validadores oficiais da Spec Lean. Veja `validacao-mutantes.txt` e `validar_rascunho.py`.

## Controle adversarial de qualidade da própria prova

- Um teste que afirma “PDF foi citado” **não prova** que o valor do edital foi reproduzido corretamente. C25 exige caso de falsa conclusão com referência verdadeira.
- Um teste que chama apenas `tool_gateway` **não prova** exclusividade de credenciais. C22 requer tentativa direta deliberada e auditoria real dos segredos no go-live.
- Um teste verde com `nonce` repetido na mesma sessão **não prova** corrida entre processos. C23 exige disputa concorrente por uso único.
- Um `allow_private=True` para fixtures na memória **não libera escrita real**; o bloqueio administrativo segue obrigatório.
- Zero falhas em 200 trials não significa segurança absoluta. Mesmo sob simplificação iid, o limite superior unilateral de 95% é ~1,49% para uma taxa comum desconhecida; repetições correlacionadas reduzem a força dessa aproximação.

## Decisões que pertencem ao usuário

1. **D2/D4:** aprovar fronteira de gateway e renderer como obrigações do produto, inclusive a exigência de não expor credenciais ao LLM; alternativa: operar apenas com aconselhamento sem ferramentas externas.
2. **Fatos críticos:** aprovar a obrigação de verificar datas, requisitos, notas e eliminações por registros estruturados conferidos e **abster-se** quando houver lacuna; não substituir por julgamento livre do LLM.
3. **Go-live (depois):** definir provedor, autorização de segredos, TTL/nonce, armazenamento de recibo e retenção/privacidade. A execução com fixtures pode ser elaborada antes desse go-live, mas não comprova a segregação operacional.

## Veredito e próxima tarefa

O `plan.md` v0.2 é **rascunho adequado para revisão humana**, condicionado às decisões acima e à validação oficial da skill quando disponível. O `checks-preview.md` é só mapa, não `checks.md`. **Próximo passo após aceite explícito do PLAN**: registrar a aprovação com as palavras do usuário, executar `validate_plan.py`, gerar `checks.md`, executar `validate_checks.py --execute`, congelar obrigações e iniciar BUILD isolado; somente então auditor independente de provas.
