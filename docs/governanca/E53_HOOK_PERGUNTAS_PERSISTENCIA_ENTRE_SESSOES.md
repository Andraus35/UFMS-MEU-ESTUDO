# E53 — Hook de perguntas: persistência entre sessões (opção B)

**Natureza:** registro da decisão do proprietário de 28/11/2026 ("Opção B"). Altera `.claude/hooks/perguntas_boas_praticas.py` (**arquivo de contrato**): **o merge exige aprovação expressa do texto, citando PR e head.**

**Problema:** o hook só lia o transcript da própria sessão; sessão nova repetia as perguntas de um estado já respondido, e as respostas só sobreviviam se o modelo as copiasse ao HANDOFF.

**Mudança:** (1) `scripts/registrar_perguntas.py` grava `memory/PERGUNTAS.json` (estado lido de `next_task.py` + respostas; últimas 10 entradas; recusa e-mail, 9+ dígitos e prefixos de token, pois o repositório é público); (2) o hook **continua só lendo** e usa o último estado registrado: igual ao atual, não bloqueia; diferente, mostra o que mudou; arquivo ausente, ilegível ou sem prefixo: cai no transcript (E13) e, na dúvida, pergunta; (3) o motivo do bloqueio manda rodar o registrador e comitar o arquivo.

**Limites:** o registro depende de o modelo rodá-lo e comitá-lo (instrução, não imposição); não foi observado em Claude Code real; resposta registrada com estado que depois mudou apenas gera a pergunta do que mudou. Testes: `tests/test_hook_perguntas.py` (9 novos; mutação que ignora o arquivo é morta).
