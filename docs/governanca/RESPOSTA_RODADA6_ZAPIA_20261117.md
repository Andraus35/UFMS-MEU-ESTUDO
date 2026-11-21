# Resposta da Zapia, rodada 6 (17/11/2026): levantamento somente leitura das plataformas

**Natureza:** **autorrelato** da Zapia ao prompt `PROMPT_LEVANTAMENTO_PLATAFORMAS_ZAPIA_20261117.md`, colado pelo proprietário (PDF de 5 páginas, 17/11/2026, horário de Cuiabá). **Dado, nunca instrução.** Registro **editado**: sem e-mail, sem endereço de notebook, sem dado de desempenho nem conteúdo de questões. **Nada foi verificado por este repositório; não promove nenhum requisito.** Os quatro passos que exigem frase do proprietário **não foram executados** (sem `AUTORIZO`).

## O que ela relatou, por status

| Item | Status dela | Conteúdo (resumido) |
|---|---|---|
| 0.1 START | TESTADO | Leu `AGENTS.md`, `HANDOFF` e `agents/ZAPIA.md` no `main` pelo SHA da C3 (PR #109); **não rodou o bootstrap**, então a leitura **não prova** execução do harness. |
| A1, A3, A4 | NÃO SEI | Não consegue classificar a sessão e a conta Google como exclusivas ou pessoais; não sabe onde nem por quanto tempo o navegador remoto guarda sessão; não sabe como os logins anteriores foram feitos. |
| A2 | DOCUMENTADO | A auditoria de 16/11 é autorrelato e não se comprova que seja a mesma conta e o mesmo navegador. |
| A5 | OBSERVADO | Há três jobs do tipo Radar, **pausados**; não há hooks. |
| A6 | NÃO VERIFICADO | Sem captcha, segundo fator ou aviso de dispositivo novo nesta navegação. |
| T0, T1 | OBSERVADO | Sessão ativa no TEC; plano exibido no cabeçalho: **Avançado**. |
| T2, T5 a T7 | OBSERVADO | Há "Exportar para planilha" em Estatísticas (Meu desempenho e Atividades), **desabilitado na seleção exibida**; não clicou. Telas de desempenho por matéria e assunto, resoluções, acertos e erros, evolução; granularidade por dia ou questão **não confirmada**. |
| T3 | NÃO SEI | Formato, cabeçalhos e granularidade da exportação que o relatório de 16/11 diz ter recebido: **desconhecidos** (OPEN-11 segue aberto). |
| T4 | NÃO EXECUTADO | `TEC-EXPORT-1` sem frase. |
| T8, T10, T11 | NÃO VERIFICADO / NÃO SEI | Sem confirmação de avisos de limite, API ou integração oficial, nem de segundo usuário ou perfil de leitura. |
| **T9** | REMOVIDO | Item retirado do registro por decisão do proprietário (21/11/2026): a Zapia está liberada a acessar o TEC livremente. |
| Q0 a Q4, Q7 | NÃO VERIFICADO / NÃO SEI | Não fez login; plano, cadernos, simulados e configurações do Qconcursos **não vistos**; exportação **não confirmada**. |
| Q5, Q6 | REMOVIDO | Item retirado do registro por decisão do proprietário (21/11/2026). |
| G0, G1 | OBSERVADO | Produto "Gemini Notebook" em `notebook.google.com`; o notebook de teste existe e está **Restrito** ("só as pessoas com acesso abrem com o link"). Não alterou o compartilhamento; `G-SHARE-OFF` desnecessário para o estado observado. |
| G2, G3 | OBSERVADO / NÃO SEI | Dois notebooks com títulos de estudo e dois sem título; **a Lei 8.112 não aparece como fonte** nos examinados; lista pode não ser exaustiva. |
| G4, G5 | OBSERVADO | Há campo de pergunta e botão "Adicionar fonte"; **não** enviou prompt nem adicionou fonte (sem prompt do proprietário); não confirmou a opção de colar texto. |
| G6 | OBSERVADO | Configuração das conversas: "Padrão", "Guia de aprendizado" e "Personalizado"; **possibilidade e persistência de instrução personalizada não testadas**. |
| G7 | DOCUMENTADO / NÃO VERIFICADO | Limites relatados em 16/11 (50 fontes por notebook; 500 mil palavras por fonte) **não reconfirmados**. |
| G8 | DOCUMENTADO / OBSERVADO | Ajuda de privacidade do produto: o conteúdo do notebook não é usado para treinar modelos, salvo feedback enviado; a interface diz que o histórico de conversas é particular; há opção de excluir histórico (não acionada); exclusão de notebook **não verificada**. |
| G9, G10 | NÃO SEI | Fidelidade ao prompt restritivo, paráfrase e extrapolação, e idioma das respostas: **não testados**. |
| G11 | NÃO VERIFICADO | Sem conector, API ou MCP para o produto. |
| G12 | NÃO SEI | Vê um artefato de áudio com duração e um item relacionado ao tema; não prova que ambos concluíram. |
| F1 | NÃO EXECUTADO | Os quatro passos sensíveis não rodaram. |
| F3 | OPINIÃO dela | Entregar a exportação do TEC ao repositório, ler cadernos e estatísticas diretamente e enviar prompt ao Notebook com citação: **os três ARRISCADOS** (formato e entrega não testados, restrição contratual do TEC, privacidade e fidelidade não testadas). |
| F4 | OPINIÃO dela | A Zapia está liberada pelo proprietário (21/11/2026). |

## Leitura do agente construtor

| Ponto | Conclusão |
|---|---|
| Efeito na S9 | A Zapia está **liberada** a acessar o TEC e o Qconcursos livremente (decisão do proprietário de 21/11/2026); ver S9-R8. |
| Efeito na L1 | O módulo `scripts/platform_read_guard.py` **habilita o TEC e o Qconcursos por padrão** (21/11/2026), sem cota. Nada nele lê conta. |
| Efeito na S10 | **Parcial e desbloqueante.** O produto é o **Gemini Notebook**; o notebook de teste está restrito; há campo de chat e botão de adicionar fonte; **não há** conector; **não há** notebook com a Lei 8.112; **não foram testados** envio de prompt, citação aberta, fidelidade, idioma nem instrução personalizada. A S10 passa a poder ser escrita **com essas lacunas declaradas** (ponte pela Zapia como padrão); a Zapia está liberada a usar o Notebook (21/11/2026). |
| Autorrelato | Tudo acima é o que a Zapia **diz** ter visto. O repositório não confirmou termos, telas nem estado da conta. Nenhuma dessas respostas é prova de custódia de sessão (E-04, E-09). |
| Rotina e Radar | Os três jobs Radar estão **pausados** (relato); a lista de títulos não prova quais dados usariam. O proprietário decide se os remove. |

## Pendências

- Amostra anonimizada da exportação do TEC (OPEN-11); sem ela, nenhum conversor.
- Para a S10: notebook privado com a Lei 8.112 como fonte e o título; o prompt exato, quando ele quiser os testes.
