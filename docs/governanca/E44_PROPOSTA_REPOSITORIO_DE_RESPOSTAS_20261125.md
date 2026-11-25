# E44: proposta de repositório separado só para as respostas da Zapia (25/11/2026)

**Natureza:** **proposta**, não contrato e não aplicada. Escolha do proprietário de 25/11/2026 ("repositório separado só para respostas"), vinda da pesquisa: o token da Zapia hoje grava em **todo** o `entrada`, e um token fine-grained **não limita por pasta**. A Zapia junta escrita no repositório, leitura de conteúdo não confiável (o Notebook) e comunicação externa; reduzir o que ela pode sobrescrever reduz o dano de uma injeção.

## Desenho proposto

- Novo repositório **privado** `ufms-meu-estudo-respostas` (nome a decidir): só `respostas/<nome>.json`. A Zapia ganha um token **só dele** (escrita) e **leitura** do `entrada` (comandos, recibos, fontes). O token de escrita do `entrada` sai da Zapia para os hooks do N1.
- O fluxo e a sessão do construtor leem as respostas de lá; a promoção a `dados` continua só pelo fluxo.
- **Efeitos:** o hook v2 troca a URL do PUT; `volta_n1.py` lê de outro checkout; S6 (dois privados) passa a três privados.

## O que isto NÃO resolve

- Não impede a Zapia de gravar **lixo** no repositório de respostas (a conferência por código continua obrigatória); não prova o que ela executou no Notebook; **não foi testado** que o token fine-grained de leitura de um repositório e escrita de outro funciona no formulário da Zapia.

## Atos do proprietário (nada é feito pela sessão)

1. Decidir o nome e criar o repositório privado. 2. Criar o token fine-grained novo (escrita só nele; leitura do `entrada`). 3. Guardá-lo no formulário seguro da Zapia. 4. Revogar a escrita da Zapia no `entrada` depois da prova. A aplicação em `PRODUCT.md` (S6, D-18) exige aprovação expressa do texto e do merge, em PR próprio.

**Alternativa não verificada:** regras de proteção de caminho do GitHub no próprio `entrada`; **não** confirmei na documentação se existem nem se valem para esse tipo de token.
