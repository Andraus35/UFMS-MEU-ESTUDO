# E38: registro das aprovações do proprietário em 25/11/2026 (E3, frase de encerramento, gabarito) e dos atos dele no `entrada`

**Natureza:** **registro**, não contrato. Cada item abaixo é **resposta dele nesta sessão**, registrada como relato; a sessão não as verifica por outro meio. Nada foi aplicado em `agents/`, `AGENTS.md`, `PRODUCT.md`, `config/agent_command_schema.json`, `scripts/agents_gate.py` nem nos filtros.

## Aprovações

| Item | Resposta dele | Efeito |
|---|---|---|
| Texto da E3 (`docs/governanca/E3_OPERACAO_PEDIR_RELATORIO_20261118.md`, com a decisão C1) | **"Aprovo o texto da E3 como está"** | Primeira das duas aprovações expressas (texto). **Falta** a segunda (o merge que aplica, citando PR e head), **depois da janela do piloto** |
| Frase de encerramento do estudo | **"finalizar estudos"** confirmada (a de início segue "Iniciar estudos") | A frase antiga "Estudo de hoje finalizado." fica substituída |
| Gabarito oficial e resposta do aluno | **campos separados** (`gabarito`, `resposta_do_aluno`, `questao_id`) | Entra na especificação da aplicação (E37) |

## Atos dele no `entrada` (relato com captura, 25/11/2026)

- **Variável `FLUXO_SHA256`:** definida em `0b08e17b5bbe700a653fb9fed4b4fb3d6d0c93df77a6960f240ebeb1b465897d` (valia antes outro hash, o do fluxo sem a campainha). A captura mostra o hash do `promover.yml` instalado igual ao esperado e a leitura de volta igual. **Autorrelato com captura; a sessão não leu a variável.** A flag do fluxo segue falsa: nada é promovido.
- **Anexo do `entrada` à sessão:** **ainda não revogado** até este registro. A revogação é ato dele (encerrar a sessão ou remover o repositório do aplicativo do Claude nas instalações do GitHub). A sessão não grava mais nada no `entrada`.

## Limites

- Aprovação do texto **não** é aplicação; nenhum arquivo de contrato foi alterado.
- A pergunta do E3 sobre limites diários e a frase de início seguem como no texto aprovado.
