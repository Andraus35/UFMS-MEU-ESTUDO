# E47: diagnóstico do passo "adicionar fonte" no Notebook (27/11/2026)

**Natureza:** registro de **evidência**, não contrato. **Confiança B:** é autorrelato da Zapia (conta nova, Notebook integrado ao Gemini, conta `andraus.dev@gmail.com`), colado pelo proprietário. Nenhuma captura de tela foi vista nesta sessão. O que o relato **não** prova está na seção "Não provado".

## O que a Zapia relatou ter visto (teste manual do apêndice A do E46, uma execução)
1. **Conta:** ao abrir o Notebook a sessão mostrava **outra conta**; ela selecionou `andraus.dev@gmail.com` antes de criar o caderno (endereço com `authuser=1`).
2. **Caderno:** criou "diagnostico-n1-descartavel"; apareceu na lista com **"0 fonte"**. **Já havia outro caderno com o mesmo título** (origem desconhecida; não foi alterado).
3. **Opções de adicionar fonte (literais):** "Enviar arquivos", "Sites", "Play Livros", "Drive", "Livros didáticos" e **"Texto copiado"**; mais a pesquisa na "Web" e "Pesquisa rápida". **Existe opção de texto colado.**
4. **Colar e salvar:** colou o trecho do caput do art. 37 em "Texto copiado" e clicou em "Inserir". O trecho apareceu **selecionado na lista "Fontes"**, mas a visualização abriu em **"Estúdio > Observação"**, identificada como **nota**. O cabeçalho do caderno mostrava **"0 fonte"** e o chat mostrava **"1 fonte"**. Avisos literais: "Conheça as novas anotações! Agora as anotações ficam junto às suas fontes. Você pode conversar, citar e gerar conteúdo com elas." e "O texto colado é apenas para acesso de visualização".
5. **Pergunta:** enviou "Quais entes o trecho cita?"; **houve resposta** citando União, Estados, Distrito Federal e Municípios, com referências ao trecho.
6. Não parou em nenhum passo e não viu mensagem de erro. Hipótese dela (marcada como hipótese): a diferença entre o contador "0 fonte" e a presença do texto como anotação na lista de fontes pode ter levado à interpretação de que a inclusão falhou; ela mesma diz que o teste **não comprova** a causa das falhas anteriores.

## Leitura do registro (nossa; indício, não conclusão)
- O texto colado **existe e é usável** pelo chat do caderno, mas aparece como **anotação** e **não** incrementa o contador do cabeçalho. Um critério de sucesso baseado em "N fontes" do cabeçalho daria **falso negativo**: é uma explicação **compatível** com o `FONTE_NAO_ADICIONADA` das rodadas 2 e 3 (`n1b`, `n1c`), **não provada**.
- A **conta errada** na abertura é uma segunda causa possível, **não provada**: nas rodadas anteriores a Zapia não relatou qual conta estava selecionada.
- Combinam com o que já se sabia: a Zapia **não vê** a execução do hook; só o estado. Por isso o diagnóstico foi pedido como teste manual, na conversa.

## Consequências para a rodada 4 (a testar, não a afirmar)
1. Critério de sucesso do passo "adicionar fonte": **não usar o contador do cabeçalho**; usar a presença do texto na lista de fontes **e** a resposta do chat que cita o trecho, e relatar o contador do chat e o do cabeçalho separadamente.
2. **Confirmar e relatar a conta** (e-mail) antes de criar o caderno; parar com `LOGIN` se não for `andraus.dev@gmail.com`.
3. Códigos de parada por etapa (E46 §7): `SEM_CADERNO`, `MENU_SEM_TEXTO_COLADO`, `COLAR_FALHOU`, `SALVAR_FALHOU`, `LOGIN`, `LIMITE`; acrescentar `CONTA_ERRADA`. Resultado: **só a rodada `n1d`, conferida por código, decide** se funcionou.
4. O mnemônico e conteúdo "de fora" da contraprova (rodada 1) é problema **separado** (fidelidade), não coberto aqui.

## Não provado
- A causa do `FONTE_NAO_ADICIONADA`; que o hook (e não só a conversa) consiga colar o texto; que o comportamento se repita; a conta que estava ativa nas rodadas 2 e 3; a origem do caderno duplicado; o efeito de "O texto colado é apenas para acesso de visualização" sobre o uso em comandos. **Uma execução, um relato, sem captura.**

## Atos do proprietário relacionados
Renomear o caderno duplicado "diagnostico-n1-descartavel" (prompt entregue no chat; a Zapia **renomeia, não apaga**) e manter "REVISAO UFMS DIREITO ADM" e "AUDITORIA..." intocados.
