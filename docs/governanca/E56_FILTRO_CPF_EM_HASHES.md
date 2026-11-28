# E56 — Filtro de CPF e hashes (`FILTRO-HASH-CPF`) e correção do perfil `privado_issues` (28/11/2026)

**Natureza:** entrega do item `FILTRO-HASH-CPF` da fila (decisão do proprietário de 28/11/2026: "isentar campos de hash") e correção do perfil da sonda de token achada no uso real. **Muda código de segurança** (`scripts/agent_commands.py`, `scripts/termux/verifica_token.sh`); o merge continua só por pedido dele, citando PR e head. Não altera `agents/`, `AGENTS.md`, `PRODUCT.md`, `.claude/` nem o esquema de comandos. (Não confundir com `E56_RETOMADA_PROXIMA_SESSAO_20261128_B.md`.)

## 1. Filtro de CPF em hashes
- **Problema:** `agent_commands.scan_text` recusava, em cerca de 0,7% dos casos, um texto legítimo cujo hash hexadecimal trouxesse 11 dígitos seguidos com dígitos verificadores de CPF (`PARAMS_DADO_PESSOAL`); o #210 só estabilizou um teste.
- **Correção:** antes da busca de 11 dígitos, o texto passa por `_HASH_HEX`: um token **hexadecimal inteiro** de comprimento de hash (32, 40, 56, 64, 96 ou 128 caracteres, com pelo menos uma letra, delimitado por não alfanumérico) é ignorado. Todo o resto do filtro fica igual (e-mail, CPF formatado, segredo, HTML).
- **Contraprovas (`tests/test_agent_commands.py`, `FiltroCpfEmHashTests`):** hash de 32, 40, 64 e 128 caracteres com um CPF válido dentro passa; **CPF de verdade segue recusado** (sozinho, formatado, no meio de texto, colado a letras, ao lado de um hash, dentro de um blob de comprimento errado ou não hexadecimal); 5000 hashes SHA-256 reais não geram recusa. Duas mutações (sem a isenção; com a isenção sem delimitar) são mortas.
- **Limite declarado:** quem embrulhar um CPF dentro de um token hexadecimal de **exatamente** um desses comprimentos escapa do filtro. O filtro continua **heurístico**; reduz, não prova ausência de dado pessoal.

## 2. Perfil `privado_issues` da sonda de token
- **Problema (achado na sonda real de 28/11/2026):** a sonda de comentário usava a issue **#75**, que existe no repositório público e **não** no `entrada`; o 404 saiu como "sem permissão" e deu `DIVERGE` falso.
- **Correção:** no perfil `privado_issues` a issue padrão é a **#12** (existe no `entrada`); `ISSUE=<n>` continua valendo; um 404 na sonda de comentário agora imprime a dica de que a issue pode não existir. 2 testes novos; a mutação que volta o padrão a 75 é morta.
- **Limite:** a sonda só vale com a issue indicada existindo; o token real só é conferido no Termux dele, sem mostrar o valor.
