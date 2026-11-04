# LLM-ALT-01 — GitHub Copilot SDK como opção de LLM (v0.1)

Data: 04/11/2026. Repositório: `Andraus35/UFMS-MEU-ESTUDO`.
Objeto: PR #3 (`feature/oracle-telegram-calendar-bridge`).
**Status: opção APENAS CATALOGADA / avaliação futura, não integrada nem habilitada.**

## Decisão mínima

- **Candidato principal:** Gemini Developer API Free Tier, sujeito a privacidade, cotas e comprovação humana de projeto sem faturamento.
- **Alternativa secundária:** GitHub Copilot SDK + franquia **Copilot Free** do usuário, condicionada a disponibilidade, autenticação autorizada, limites e viabilidade para uso conversacional pessoal.
- **Hospedagem:** Oracle Always Free permanece necessária para gateway Telegram, SQLite, lembretes e Agenda. GitHub Actions/Codespaces não substituem serviço disponível continuamente.
- **GitHub Pro != Copilot Pro:** a assinatura GitHub Pro não fornece Copilot Pro. Nenhuma assinatura nova, BYOK pago ou cobrança automática está autorizada.
- **Gemini Notebook gratuito** permanece ferramenta de estudo separada. Copilot SDK não substitui o Notebook nem concede acesso a ele.

## Evidências de documentação oficial do GitHub

1. O SDK é disponibilizado pelo GitHub para Python, TypeScript e outras linguagens; versão atual descrita como GA.
2. A autenticação aceita conta Copilot, OAuth GitHub ou tokens específicos, mas **Copilot Free tem franquia limitada**; a elegibilidade real deve ser verificada.
3. As interações do SDK consomem créditos de IA da franquia do Copilot. Atingido o limite, a opção **deve parar**, sem upgrade ou pagamento adicional.
4. BYOK significa uso de chave e custos do fornecedor externo; não é mecanismo de gratuidade. **Proibido BYOK com provedor pago** no escopo de custo zero.
5. O SDK pode expor ferramentas nativas, arquivos e execução; `tools=[]` para ferramentas personalizadas **não** é suficiente para bloquear ferramentas internas. Exigir lista vazia `availableTools: []` no nível da sessão, política que negue toda ação `onPreToolUse`, nenhum MCP/plugin ativo e isolamento de filesystem/rede verificável. A opção deve ser **somente texto**.
6. Não presumir que token de GitHub Actions ou GitHub Pro conceda acesso a modelos sem uma franquia válida; tokens com permissão a repositórios **não** devem ser entregues aos bots.

Fontes:
- https://github.com/github/copilot-sdk
- https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/authenticate
- https://docs.github.com/en/copilot/get-started/plans
- https://docs.github.com/en/copilot/concepts/billing-and-usage/individuals/billing
- https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/custom-agents
- https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/changing-tools
- https://github.com/github/copilot-sdk/blob/main/docs/features/hooks.md

## Restrições de segurança e governança

- Copilot SDK, se testado futuramente, será **motor de inferência sem permissões de escrita**, não um novo agente colaborador com acesso ao repositório.
- Nunca herdar configurações do CLI Copilot em diretórios de trabalho que contenham arquivos do GitHub, segredos da Oracle ou banco SQLite.
- Sem executar `bash`, `edit_file`, GitHub API, navegador, MCP ou funções; saída do modelo não executa ações. Tutor e Coach conservam prompts separados.
- Não expor `GITHUB_TOKEN`, `GH_TOKEN`, `COPILOT_GITHUB_TOKEN` nem qualquer token OAuth ao modelo ou ao código de teste.
- Controles de consentimento **específicos por provedor** antes de compartilhar dados pessoais, revogação, cotas globais e idempotência devem preceder qualquer teste real.
- Não adicionar o pacote SDK à imagem Docker, CI ou dependências de produção antes de teste isolado e auditoria de ferramentas.
- Modelo selecionado pelo runtime e forma de cobrança devem ser revalidados; não fixar nome de modelo ou prometer custos zero sem comprovação externa.

## Teste de viabilidade futuro — aceitação obrigatória

1. Confirmar se a conta efetivamente dispõe de **Copilot Free** e de franquia de créditos, sem plano pago e sem gasto adicional autorizado.
2. Estabelecer orçamento de uso adicional **US$ 0**, com bloqueio de uso quando a franquia terminar, e verificar os controles de faturamento na conta do usuário.
3. Num ambiente descartável (não na Oracle produtiva), usar somente pergunta **pública/sintética**, sem token real impresso, arquivo sensível, GitHub repo montado ou ferramenta de escrita.
4. Provar `availableTools: []` e bloqueio `onPreToolUse` com contraprovas adversariais (tentativa explícita de shell/editar arquivos/rede).
5. Confirmar consentimento separado, isolamento Tutor/Coach, limitação diária e erro de cota sem retentativa paga.
6. Avaliar simplicidade, latência e qualidade pedagógica versus Gemini Free. Só promover a alternativa mediante revisão independente, autorização humana, readback e CI no SHA exato.

## Estado de implementação

A configuração `configured_agent` em `bridge/agents.py` **continua aceitando exclusivamente `UFMS_LLM_PROVIDER=gemini`** com as declarações operacionais exigidas. Qualquer escolha `copilot`/`copilot_sdk` deve retornar `None`: não haverá autenticação nem chamada de rede Copilot nesta etapa. Testes offline impõem esse bloqueio.

**Gate LLM-ALT-01: REGISTRADO, NÃO EXECUTADO, NÃO HOMOLOGADO.**
