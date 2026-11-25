# E43: primeira execução do N1 e melhorias vindas da pesquisa (25/11/2026)

**Natureza:** registro de evidência (confiança B, autorrelato da Zapia, uma execução de uso único) e de mudanças offline. Não altera `agents/`, `AGENTS.md`, `PRODUCT.md`, o esquema nem a caixa.

## O que aconteceu (issues #8 e #9 no `entrada`, hook `2bef6d04`)

1. **1ª tentativa de criar o hook:** recusada por tamanho (4468 > 4000 caracteres); 2ª: recusada por inscrição idêntica; resolvida **atualizando** o hook existente (ver `CAPACIDADES_ZAPIA_VERIFICADAS.md`).
2. **1º disparo (issue #8):** o hook leu recibo, comando e fonte pelos URLs certos e **parou** na conferência do SHA-256 pelo LLM; o arquivo estava íntegro (conferido por código). Disparo consumido, nada executado no Notebook.
3. **2º disparo (issue #9), com o texto corrigido:** a Zapia respondeu os **3** comandos no Gemini Notebook e gravou `comandos/respostas/*` (commits `88675aa`, `55e97bd`, `f952d52`); ela **não conseguiu desativar o hook**.
4. **Conferência por código (`volta_n1.py`):** `n1-fonte` e `n1-questao` conferidos; **`n1-contraprova` recusada**. **Verificação do Tutor (subagent, S10-R7b):** fonte = aceitar com ressalva (mnemônico L.I.M.P.E. de fora da fonte); questão = aceitar; contraprova = **recusar** (disse "não consta nas fontes", mas completou com conteúdo de fora, fez três perguntas e trouxe citação sem relação). **Coach (subagent):** proposta de mensagem ao proprietário **aprovada pela caixa** (`PROMOVER`) e **recusada** a versão com eco do Notebook; **nada foi enviado**.

**Veredito: `N1_NAO_PROVADO` (B).** Provou o trajeto Tutor, caixa, `entrada`, campainha, hook, Notebook, resposta; **não** provou fidelidade (a contraprova falhou), promoção pelo fluxo nem a autoria do Tutor por prova.

## Melhorias implementadas (pesquisa de 25/11/2026; fontes: blogs e preprints, não padrões consolidados)

| Pesquisa | Mudança |
|---|---|
| Decisão de segurança fora do LLM (Dual LLM, CaMeL) | `HOOK_NOTEBOOK` v2: a Zapia **não calcula hash**; só compara o texto do `hash_corpo` do recibo. A integridade do comando é conferida **offline** (`volta_n1.processar(comandos=)`: `command_hash` do arquivo em `validados/` contra o esperado; comando trocado ou ausente derruba o veredito) |
| Entrega pelo menos uma vez, consumidor idempotente | Passo 0 do hook: se `comandos/respostas/<nome>` já existe, **pula** (retomável: um novo `SINAL` refaz só o que faltou) |
| Medir a abstenção separada da sustentação (canaries, penalidade assimétrica) | `notebook_response_check.avaliar` e `codigos_da_avaliacao`: três partes (disse "não consta"? completou com conteúdo de fora? citação solta?), só booleanos e contagem, nunca o texto do Notebook; `tests/fixtures/canaries_notebook_n1.json` (10 casos: 3 respostas **reais** do N1 com o veredito do Tutor e 7 sintéticos) e `tests/test_notebook_canaries.py`; as 10 mutações do código novo foram mortas |

**Limites:** a triagem é por lista fixa de marcadores (números, "inciso", "parágrafo", "lei n", anos, meses, dias, mnemônico com pontos); **não acha** conteúdo externo escrito com palavras comuns. O hook v2 **confia na comparação de texto** do recibo; um comando trocado só é detectado **depois** (offline), não impede a execução. n=3, uma fonte de uma frase.

## Fica para depois (decidido pelo proprietário)

Aprovação assinada com pacote de evidência **não** foi pedida (mantém só o hash do comando). **Isolar onde a Zapia escreve:** ver `E44_PROPOSTA_REPOSITORIO_DE_RESPOSTAS_20261125.md` (proposta, não aplicada). Prompts do Tutor a revisar para um 2º N1: sem acrônimos, contraprova só "não consta nas fontes", exatamente uma pergunta, sem oferta de pesquisa na web.

## 2ª rodada do N1 (PR #207, 25/11/2026)

Depois da falha da contraprova, o **Tutor (subagent)** revisou os três prompts: sem acrônimos nem mnemônicos, **exatamente uma pergunta**, sem oferta de pesquisa na web nem conhecimento externo, dica só apoiada em palavra citada do trecho e, na contraprova, a resposta inteira é **exatamente** `não consta nas fontes`. A questão passou a perguntar qual ente **não** é citado no caput (gabarito `E`, Territórios; âncora: "de qualquer dos Poderes da União, dos Estados, do Distrito Federal e dos Municípios"). Os prompts novos estão em `config/propostas_tutor_n1.json` (`rodada: 2`, autoria e hash conferidos pelo kit); os da rodada 1 ficam no histórico do Git e nos canaries. O kit ganhou `--prefixo n1b`, para os comandos novos (`n1b-*.json`) **não** sobrescreverem os da 1ª rodada no `entrada`. **Mesmos limites:** autoria declarada, autorrelato da Zapia, n=3, uma fonte de uma frase.
