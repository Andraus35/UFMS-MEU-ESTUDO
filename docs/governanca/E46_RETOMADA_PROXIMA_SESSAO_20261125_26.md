# E46: ponto de retomada da sessão de 25 e 26/11/2026 (N1, hook, pesquisa e próximas tarefas)

**Natureza:** registro de **continuidade**, não contrato nem prova. Tudo abaixo vem da conversa e dos arquivos do repositório; o que é autorrelato da Zapia está marcado. **Leia depois do START e antes de agir.** Estado vivo: `state/WORKFLOW.json` e `python scripts/next_task.py`.

## 1. Onde estamos
- `main` tem os PRs #192 a #207 mesclados (último: #207, squash `b1187c8`, 26/11/2026). Ciclo ativo: **#208** (esta persistência, draft). Merge **só por pedido dele citando PR e head** ("Mesclar" vale com um único PR aberto e CI verde no head).
- Frente: RM-09, ponte **Tutor → caixa → `entrada` → campainha (issue SINAL) → hook de Gmail da Zapia → Gemini Notebook → resposta → conferência por código → Tutor → Coach**. Nada de dado do aluno entra (estado E0; flag de resultados pessoais `false`).
- Mesclados nesta sessão: #200 a #207 (E40 a E44 e o kit/hook do N1).

## 2. O que o N1 provou e não provou (confiança B, autorrelato da Zapia)
| Rodada | Resultado |
|---|---|
| 1 (`n1-*`, issues #8, #9) | Hook parou na conferência de hash pelo LLM; depois de explicitar `ensure_ascii=False`, a Zapia **respondeu os 3 comandos** no Notebook. Conferidor: fonte e questão conferidas; **contraprova recusada** (disse "não consta nas fontes", mas completou com conteúdo de fora e trouxe citação). Tutor: fonte = aceitar com ressalva (mnemônico L.I.M.P.E. de fora), questão = aceitar, contraprova = recusar |
| 2 (`n1b-*`, issue #10) | Só `n1b-fonte` gravado, `PARADO` `DATA_PARSE_ERROR`; a Zapia parou a tarefa inteira |
| 3 (`n1c-*`, issue #11) | Hook v3 (sem hash nem data no LLM, erro isolado segue): os 3 comandos `PARADO` `FONTE_NAO_ADICIONADA`; a conferência de integridade e de idade passou |
**Veredito: `N1_NAO_PROVADO`.** Provado: trajeto até o Notebook e a volta (1ª rodada). **Não provado:** fidelidade (contraprova falhou), o passo "adicionar fonte" nas rodadas 2 e 3 (causa **desconhecida**), promoção pelo fluxo, autoria do Tutor por prova, hook recorrente. **Dado da conta (relato dela):** 9 cadernos no Notebook integrado ao Gemini (conta `andraus.dev@gmail.com`; o hook de Gmail está em `souza.merchan@gmail.com`), **8 com "0 fonte"** (5 com título do tema, 2 "Untitled notebook", 1 "AUDITORIA..."), 1 com "1 fonte" que **não é do teste** ("REVISAO UFMS DIREITO ADM"). **Hipótese não provada:** o texto colado vira nota do caderno, não "fonte".

## 3. Estado do `entrada` e da Zapia (conferir de novo antes de usar)
- `entrada` (privado, anexado à sessão por exceção dele; **a revogação é ato dele depois do run**): `comandos/validados`, `recibos` e `respostas` das rodadas `n1`, `n1b`, `n1c`; `comandos/fontes/n1.txt` (251 bytes, caput do art. 37); fluxo `promover.yml` e recibo antigo C5 intocados. **Comandos `n1c` valem até 27/11/2026 21:55Z.**
- **Hook `2bef6d04`: DESABILITADO** (relato dela, 26/11). Issues #8 a #11 **fechadas** pela sessão. Ela **não consegue** desativar nem apagar hook por conta própria, só atualizar, reabilitar ou, em tese, remover (**a escolha é dele**). A Zapia **não vê** o que acontece dentro da execução do hook (só o estado).
- Restrições da Zapia gravadas em `docs/governanca/CAPACIDADES_ZAPIA_VERIFICADAS.md` (o START imprime): tarefa de hook ≤ **4000** caracteres; **recusa hook com inscrição idêntica** (atualizar o existente); parada na conferência de hash; ela não parseia data nem hash com segurança.

## 4. Decisões do proprietário (não reabrir)
Canal é o **Gemini Notebook pela Zapia (D-26, D-27)**, não a API do Gemini; **os prompts do N1 têm de vir do Tutor** (subagent), sem texto de prompt no código do kit (`config/propostas_tutor_n1.json`, autoria e hash); resolver limites com alternativas (E42: volta offline, âncora do gabarito, captura como segunda via; **aprovação destacada fica só com o hash do comando**, sem pacote de evidência); **repositório separado só para respostas** é a direção do isolamento (E44, proposta, **não aplicada**); **estudar o corretor com a API oficial** (E45, sem credencial); S22 mínima só com o pedido **"Criar a tarefa S22"** e um horário; manter o anexo do `entrada` até o fim do run e ele revoga; chamar `Zapier` era `Zapia`.

## 5. Pesquisa de boas práticas (25 e 26/11/2026; blogs e preprints, não padrões)
Decisão de segurança **fora do LLM** ([CaMeL](https://arxiv.org/abs/2503.18813), [Willison](https://simonwillison.net/2025/Apr/11/camel/)); aprovação humana amarrada à evidência ([Sovereign Assurance Boundary](https://arxiv.org/pdf/2606.11632)); abstenção medida à parte, com "canaries" ([knowledge-gap canaries](https://arxiv.org/pdf/2608.26385)); entrega pelo menos uma vez, consumidor idempotente ([Hookdeck](https://hookdeck.com/webhooks/guides/webhook-delivery-guarantees)). **Conexão direta do Claude ao Notebook:** API oficial **NotebookLM Enterprise** ([docs](https://docs.cloud.google.com/agentspace/notebooklm-enterprise/docs/api-notebooks): `notebooks.create`, `BatchCreateSources`, token OAuth de curta duração, projeto no Google Cloud com faturamento; **não verifiquei** se aceita conta pessoal nem conta de serviço); servidores MCP **não oficiais** usam cookie de sessão (frágeis, risco de termos); **D-26 proíbe credencial do Google no modelo**, então o desenho é um **corretor fora do modelo** que guarda a credencial e recebe só o comando validado. **Rotina agendada na nuvem do Claude** roda sem PC (uma tarefa com cron já teve `SUCCEEDED`; as presas a uma sessão morrem com ela), mas **não alcança o Notebook sem credencial** e o hook da Zapia é de uso único; **não verifiquei** se uma sessão disparada sozinha obtém acesso ao `entrada` sem aprovação dele.

## 6. O que ele precisa fazer (atos dele)
1. Dizer "Mesclar" quando pedir o merge do #208. 2. Mandar à Zapia o **teste manual** (apêndice A) e trazer o relato literal. 3. Dizer **"Criar a tarefa S22"** e um horário, se quiser a prova de acesso sem supervisão. 4. Decidir sobre emendar a D-26 (só se o corretor da API oficial seguir). 5. Apagar ou manter os 8 cadernos de teste (**nunca** o "REVISAO UFMS DIREITO ADM" nem o "AUDITORIA...", que não são do teste). 6. Revogar o anexo do `entrada` ao fim do run; P9 (tokens, aviso 04/12), janela PJ, consentimento v4 e reinstalar o fluxo seguem pendentes (ver HANDOFF e `next_task.py`).

## 7. Próximas tarefas, na ordem (uma por vez; merge antes de mudar de frente)
1. **N1-DIAG-FONTE:** a Zapia **executa ela mesma** o teste manual (A) e traz a tela literal; decide se "texto colado" existe e onde o texto fica. 2. **N1-RODADA-4:** com o resultado, hook **v4** (código por etapa: `SEM_CADERNO`, `MENU_SEM_TEXTO_COLADO`, `COLAR_FALHOU`, `SALVAR_FALHOU`, `LOGIN`, `LIMITE`; a notificação do chat traz o texto literal do aviso, sem gravar no repositório) e rodada `n1d` (`python scripts/zapia_n1_prep.py --saida <pasta> --prefixo n1d`; o texto do hook sai em `instrucao-hook-notebook.txt`; gravar os 6 arquivos em `comandos/`; **atualizar** o hook existente e reabilitar; só então abrir **uma** issue `SINAL`). 3. **E45-CORRETOR:** proposta do corretor com a API oficial, modelo de ameaça e corretor simulado com testes, **sem credencial**. 4. **S22-PROVA-MIN:** só com o pedido expresso dele. 5. Depois: repositório de respostas (E44), prompts do Tutor ainda mais estritos se a contraprova seguir falhando, ZAPIA-LIGAR.

## 8. Como a próxima sessão verifica que tudo está aqui
`python scripts/bootstrap.py --mode engineering` (imprime o resumo e o hash das capacidades da Zapia), `python scripts/next_task.py`, `python scripts/single_flow_gate.py --check`, `python scripts/agendar_rotina.py --check`; `python scripts/volta_n1.py --entrada <clone do entrada> --meta <meta.json> --fonte <fonte-n1.txt>` reavalia qualquer rodada; `python -m unittest discover -s tests` (uma sessão: ~2700 testes). **Armadilhas:** `git merge -s ours origin/<branch>` depois de cada squash (push forçado negado); o `WORKFLOW.json` está perto do limite de 64 KiB do START (arquivar antes de crescer); o HANDOFF tem orçamento de 60 KiB (`tests/test_handoff_orcamento.py`); o texto do hook tem de ter ≤ 4000 caracteres; **não fechar nem comentar issue SINAL com hook habilitado**; o `add_repo` do `entrada` se repete a cada sessão nova.

## Apêndice A: prompt do teste manual (a Zapia executa ela mesma)
```
TESTE MANUAL DE DIAGNÓSTICO, uma vez só, nesta conversa. Execute VOCÊ MESMA cada passo na sua sessão do navegador e relate o que VOCÊ viu na tela; não pergunte ao Gemini nem a outro serviço. Contexto: Notebook integrado ao Gemini, conta andraus.dev@gmail.com. NÃO grave nada no GitHub, NÃO altere hook, rotina ou lembrete, NÃO apague nada e NÃO repita em laço. Nunca peça nem revele credencial, cookie ou sessão. Se algum passo falhar, copie o texto LITERAL da tela e PARE nele. Se uma informação pedida não estiver visível, escreva "não consigo ver" e CONTINUE para o passo seguinte (isso não é falha).

Passos (relate cada um: feito ou falhou, mais o texto literal de qualquer aviso):
2. Crie UM caderno novo chamado "diagnostico-n1-descartavel". Ele apareceu na lista?
3. Abra a opção de adicionar fonte e COPIE LITERALMENTE os nomes de TODAS as opções que aparecem. Diga se existe uma opção de texto colado.
4. Se existir texto colado, cole EXATAMENTE este texto e salve: A administração pública direta e indireta de qualquer dos Poderes da União, dos Estados, do Distrito Federal e dos Municípios obedecerá aos princípios de legalidade, impessoalidade, moralidade, publicidade e eficiência e, também, ao seguinte:
   Se NÃO existir texto colado, não tente outra coisa; diga quais opções existem.
5. Depois de salvar, diga o que a tela mostra: o contador de fontes do caderno ("N fontes"), se o texto aparece na lista de FONTES ou em outro lugar (por exemplo, uma NOTA ou o chat), e o nome literal desse lugar.
6. Se o texto ficou como fonte, envie no chat do caderno só a frase "Quais entes o trecho cita?" e diga em uma linha se houve resposta e se ela cita o trecho. Se ficou como nota, envie a mesma frase e diga se houve resposta.

No fim, diga: o passo em que parou (se parou), o texto literal de qualquer mensagem e uma HIPÓTESE sua, marcada como hipótese, sobre o FONTE_NAO_ADICIONADA. Deixe o caderno "diagnostico-n1-descartavel" no lugar; não o apague.
```

## Apêndice B: prompt para desativar o hook (já usado em 26/11)
```
Desative (desabilite) o hook de Gmail 2bef6d04-e272-4b25-b9b9-4d44958cfd73. Não o apague, não o recrie, não altere a conta, os filtros nem o texto, e não crie outro hook, rotina ou lembrete. Depois, mostre lido de volta: o ID, a conta, os filtros e se está habilitado ou desabilitado. Se a ferramenta não tiver a opção de desabilitar, NÃO remova: diga o motivo literal e que opções ela oferece.
```

## Apêndice C: prompt para atualizar o hook com o texto novo (o texto vem de `instrucao-hook-notebook.txt`)
```
Atualize o hook de Gmail existente 2bef6d04-e272-4b25-b9b9-4d44958cfd73: troque a tarefa dele EXATAMENTE pelo texto entre as marcas INICIO e FIM e reabilite-o, sem alterar a conta nem os filtros (senders = notifications@github.com e subject_contains = "[Andraus35/ufms-meu-estudo-entrada] SINAL"). Não crie outro hook, rotina ou lembrete. Não traduza, resuma nem reescreva nenhum URL ou pasta. Depois de salvar, mostre lidos de volta: o ID, a conta, os filtros, se está habilitado e o texto salvo. Se a ferramenta não conseguir atualizar, NÃO remova nem recrie: diga o motivo literal. INICIO <texto da tarefa> FIM
```
