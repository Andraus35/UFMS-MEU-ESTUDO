# E41: hook de Gmail que executa o prompt do Tutor no Gemini Notebook (automação ponta a ponta, 25/11/2026)

**Natureza:** **proposta de modelo e roteiro**, não contrato nem prova. Decisão do proprietário: usar o mecanismo do E31 (issue no `entrada`, e-mail do GitHub, hook de Gmail da Zapia) para a cadeia Tutor, Zapia, Gemini Notebook, resposta, Tutor, Coach; **canal mantido: Gemini Notebook pela Zapia (D-26)**, sem Gemini API. Nada foi executado na Zapia nem no Notebook. Não altera `agents/`, `AGENTS.md`, `PRODUCT.md` nem o esquema de comandos.

## O que entrega este lote

- **Modelo `HOOK_NOTEBOOK`** em `config/rotina_instrucoes.json` (hash conferido por `agendar_rotina.py --check`): o hook acorda pelo **assunto** da issue (nunca o corpo), acha cada comando pelo `hash_corpo`, confere origem `tutor`, operação `enviar_prompt_notebook`, idade menor que 24 h, hash do comando e hash da **fonte** (`comandos/fontes/n1.txt`); cria **um** notebook descartável, cola a fonte e o campo `params.prompt` **sem editar**, copia a resposta e **uma** citação; grava `comandos/respostas/<nome>` nos campos fixos de `notebook_response_check` (ou `PARADO` com código); notifica uma vez; encerra o hook.
- `agendar_rotina.py --hook-notebook` (renderizador com falha fechada) e `zapia_n1_prep.py`, que passa a gerar `instrucao-hook-notebook.txt` com os três hashes e o SHA-256 da fonte; `prova_n1.sh colocar` grava também a fonte.
- **Tutor e Coach como subagents (offline, nesta sessão):** o Tutor propôs o prompt (art. 37, campos C1) e o Coach recebeu o resumo, sem dado do aluno (E0).

## Procedência dos prompts do N1 (a pedido dele: "precisa vir do Tutor")

Os **três** prompts do N1 vêm do **subagent Tutor** (somente leitura, offline, 25/11/2026), registrados em `config/propostas_tutor_n1.json` com autoria `subagent_tutor`, data e SHA-256 do texto canônico: `n1-fonte` (a fonte responde), `n1-contraprova` (o caput não traz prazo nem prorrogação do concurso) e `n1-questao` (campos C1). **O código do kit não contém texto de prompt**: `zapia_n1_prep.py` só lê esse arquivo e **recusa** gerar o N1 se faltar proposta, se a autoria não for `subagent_tutor`, se o validador recusar o prompt ou se o hash não bater (prompt alterado depois do Tutor). Testes: `ProcedenciaDoTutorTest` (5) e 5 mutações mortas. **Limite:** a autoria é **declarada, não provada** (S6-R7: a nuvem não tem assinatura que o modelo não possa forjar); o que o código garante é que nenhum prompt foi escrito no código do kit e que o texto não mudou desde a proposta. Mudar um prompt exige nova proposta do Tutor e novo hash.

## Cadeia e o que cada elo prova

| Elo | Estado |
|---|---|
| Tutor propõe prompt; validador e caixa aceitam | Offline, **provado por testes** |
| Comando e recibo no `entrada` | Colocados à mão (`SINTETICO_MANUAL`); promoção pelo fluxo **não provada** (flag, PJ) |
| Issue, e-mail, hook acorda, lê e confere hash | **Provado no E31** (B, duas execuções de uso único) |
| Hook executa no Notebook e grava a resposta | **Não provado**; é o que o run mede |
| `prova_n1.sh conferir` (forma, hash, citação aberta, contraprova) | Offline, testado com `gh` falso |
| Tutor verifica a afirmação contra a fonte e passa ao Coach | Subagents offline; **sem orquestrador** que feche o ciclo sozinho |

## Roteiro do run (atos dele)

1. Mesclar o PR do lote; atualizar o clone. 2. `bash scripts/termux/prova_n1.sh preparar` e `colocar` (ou a sessão grava, pela exceção de acesso ao `entrada`). 3. Na Zapia, criar **um** hook de Gmail com **só** `senders` = `notifications@github.com` e `subject_contains` = `[Andraus35/ufms-meu-estudo-entrada] SINAL`, com o texto de `~/n1/instrucao-hook-notebook.txt`; conferir conta, filtros e texto salvo lidos de volta. 4. Abrir **uma** issue `SINAL teste N1` e só fechá-la depois do relato. 5. `prova_n1.sh conferir`; trazer o texto literal da Zapia e as capturas. 6. Revogar o anexo do `entrada` e apagar o hook.

## Correção de tamanho (25/11/2026)

A ferramenta de hook da Zapia **recusou** o primeiro texto (4468 caracteres): `Invalid value: task: String should have at most 4000 characters`. O modelo `HOOK_NOTEBOOK` foi enxugado (nomes e hashes dos comandos no próprio texto, `name=hash_corpo`; sem listar os recibos) e o renderizador **recusa** texto acima de `LIMITE_TAREFA_HOOK` (4000); com os 3 comandos do N1 o texto tem 3375 caracteres. Por isso o texto do hook passou a ser regerado: o anterior **não deve ser usado**.

## Limites

- Autorrelato da Zapia (B); uma execução; o Notebook pode recusar, pedir login ou mudar de tela: nesse caso o resultado é `PARADO`, que é dado, não falha silenciosa.
- A conferência prova só que a citação existe na fonte; **não confere o gabarito** nem a fidelidade do Notebook (S10, limites).
- A Zapia pode divergir do texto (E31, 1ª execução): por isso o modelo manda relatar cada URL; a conferência de bytes do texto salvo continua sendo ato dele.
- Notebook e hook rodam na conta e na sessão do proprietário; a autoria dos commits não distingue a Zapia.
- Orquestrador Tutor, Coach de ponta a ponta **não existe**; o passo Tutor→Coach é manual por enquanto.
