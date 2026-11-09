# Agentes: Tutor (Aragonê), Coach (Carter) e perfil da Zapia

Este diretório define o **perfil** dos dois agentes que decidem no produto (`PRODUCT.md`, D-10 e D-12). A Zapia é só a interface com o humano e a executora das ferramentas; ela cumpre os comandos dos agentes dentro das diretrizes do harness.

## Como funciona

- `agents/TUTOR.md` e `agents/COACH.md` são o **texto de instrução** de cada agente, usado pelo orquestrador como instrução inicial. Contêm regras, não estado.
- O estado vem do START de estudo (4 arquivos do `AGENTS.md`), pelo ponto de entrada controlado. O edital integral está na raiz (`EDITAL_UFMS_152_2026.md`), com índice em `edital/INDEX.md`.
- **Divisão de trabalho:** o Tutor cuida do conteúdo (ensino, revisão, fixação, técnicas, plano e material para o NotebookLM) e é o único produtor de conteúdo; o Coach cuida do acompanhamento (motivação, organização, estatísticas, recomendações).
- **Separação verificável:** `python scripts/agents_gate.py --check` confere a estrutura de cada perfil e que cada operação exclusiva pertence a um só agente. O bootstrap de engenharia o executa.

## Fluxo com o humano

1. O Tutor entrega o plano de estudos (Método 4.2 e revisão em 7, 15 e 30 dias, D-11) à disposição do Coach.
2. O Coach acompanha o humano no dia a dia.
3. O humano estuda no TEC Concursos e no Qconcursos e entrega a exportação de desempenho pela Zapia, que grava no repositório.
4. Os agentes avaliam; o Tutor propõe revisões e fixação (material no NotebookLM); o Coach ajusta a rotina.
5. O ciclo repete até fechar o edital ou o conteúdo priorizado.

## Pontos em aberto

- **Onde rodam** os agentes e como emitem comandos à Zapia: `PRODUCT.md`, OPEN-09. Os perfis não dependem de um modelo específico.
- **Perfil da Zapia:** `agents/ZAPIA.md` é o texto de instrução da interface e executora; contrato e justificativas em `docs/especificacoes/S5_ZAPIA.md`; formato dos comandos: `config/agent_command_schema.json` e `scripts/agent_commands.py`.
- **Acesso ao NotebookLM:** o caminho direto do Tutor tem prioridade; a Zapia é a alternativa (D-12, PR-012).

## Alteração

Qualquer mudança nestes perfis é por PR com aprovação humana. Precedência em conflito: `AGENTS.md` > `PRODUCT.md` > perfis.
