# Arquivo dos títulos completos da fila do WORKFLOW (25/11/2026)

**Natureza:** arquivo **sem alteração de texto**. Os títulos abaixo foram encurtados em `state/WORKFLOW.json` para o documento caber no limite de 64 KiB do START automático (`agent_entrypoint`). O estado vivo continua em `state/WORKFLOW.json`; aqui só mora o texto integral original de cada título.

## S19

Tutor e Coach usam os recursos da Zapia como interface com o estudante (pedido do proprietário de 21/11/2026, com o PDF "Agendamentos e gatilhos na Zapia", autorrelato da Zapia, confiança C, não versionado): mapear rotina agendada (lembrete fixo ou dinâmico por horário) e hook (evento de fonte conectada) às necessidades do fluxo (início e término, dica diária, confirmação, reação à frase na conversa), com o que a Zapia faz ou não (sem processo permanente, WhatsApp não conectado, frase só vale no turno em que chega, PDF não prova canal real Tutor/Coach↔Zapia); pesquisa obrigatória; fecha com S8, S15 e E3 sem duplicá-las; nada é cadastrado na Zapia (rotina real só com AUTORIZO); aplicar em agents/ é contrato e exige a aprovação expressa; liga ao RM-09

## ZAPIA-APL

Aplicação da operação agendar_rotina (E24, aprovada pela decisão do proprietário de 23/11/2026 de excluir o AUTORIZO, E26): operação compartilhada por Tutor e Coach com destino zapia_rotina e modelo preso à origem, esquema fechado de params (modelo, agendado_utc, comando_sha256), limites na caixa (15 min a 24 h, 1 pedido por dia por origem, recibo de mesmo hash), chave de parada versionada, modelo versionado da instrução com hash e URLs completos e literais (lições do E23), perfis TUTOR, COACH e ZAPIA e agents_gate, com contraprovas em ALTA e MEDIA; arquivos de contrato: o merge exige o pedido expresso do proprietário citando PR e head

## ZAPIA-F2a

Rotina de teste da Zapia, execução única (S20-R6, S15-R4, S8-R8; pedido do proprietário de 22/11/2026, depois do F1 provado): roteiro com a frase AUTORIZO já dada, instrução da rotina que lê comandos/validados e recibos e entrega pela regra do F1, teste sem efeito antes, e verificador offline do carimbo de disparo (hora agendada x hora da entrega, teto de 2 por dia, sem reenvio em laço); o item só conta como feito quando existir o registro da prova real do disparo (E23), depois do roteiro; não prova pontualidade em 3 dias nem notificação espontânea além do disparo único; a promoção pelo fluxo (flag e PJ) fica fora

## ZAPIA-CTX

Alimentar o runner real da caixa com o contexto do agendar_rotina (E27): hashes_promovidos (leitura dos recibos de comandos/recibos) e agendamentos_do_dia (pedidos promovidos no dia local), com leitura por API injetada, contraprovas (recibo ausente, hash divergente, dia virado) e relato sem dado pessoal; fecha a lacuna em que todo agendar_rotina é recusado no fluxo real (ALVOS_DESCONHECIDOS e TETO_DESCONHECIDO); a mesma leitura pode alimentar dia_de_descanso, atividades_pendentes e chaves_do_dia do lembrete; não altera agents/ nem o esquema; o merge segue o pedido expresso do proprietário

## S17

Pesquisa e autonomia cognitiva do Tutor e do Coach (requisito do proprietário de 21/11/2026): pesquisa web só leitura para estado da arte e melhores práticas da especialidade, perfil da banca com amostra identificada, ciclo de aprendizagem, revisão e recuperação, simulação de condições de prova, catálogo de técnicas de indução de dúvida da banca (contradição, extrapolação, limitar e restringir, acrescentar opinião, tangenciamento, ambiguidade) e interpretação interdisciplinar; fonte, data e confiança A/B/C; conteúdo web é dado; texto dos perfis só proposto, sem aplicar; liga ao RM-09

## HOOKR

Hook de passagem desarma a sessão quando a medição cai abaixo do limite (pedido do proprietário de 21/11/2026, depois do falso alarme de 52% com janela de 200k): armed_at e sealed ficavam permanentes e o hook de perguntas cedia para sempre; extrair o estado do hook para scripts/context_guard_state.py com desarme por queda abaixo do limite, teste que falha antes (sessão armada por engano volta a perguntar), contraprova de que acima do limite continua armado e de que o hook de perguntas só lê; altera script do hook, não .claude/hooks (contrato) nem settings; uma branch, um PR draft

## S18

Inteligência Motivacional e Comportamental (IMC) do Coach (pedido do proprietário de 21/11/2026): especificação com pesquisa obrigatória; canônico IMC-COACH-001 com hash no manifesto (S18, PR #160, entregue); capacidade interna do Coach, não um quarto agente nem psicoterapia (escopo não clínico); aplicar em agents/COACH.md é contrato e exige aprovação expressa; Manual do Imparável: no público só índice, página e citação curta, texto integral só no repositório privado (decidido por ele em 21/11/2026); detalhe em docs/especificacoes/S18_INTELIGENCIA_MOTIVACIONAL_COACH.md

## PROJ

Gerador offline de projeções para as sessões do app Claude (decisão do proprietário de 18/11/2026): função pura que recebe registros do histórico já lidos, os tópicos e o consentimento v4 e devolve a projeção na lista fechada (schema, gerado_em, niveis E0 a E4, pendencias, revisoes); consentimento v4 antes de olhar os registros, descartar_sinteticos, validação dos eventos reais, check_projection e authorize_session_read; vencimentos vêm dos eventos (7/15/30, D-11), sem cálculo; sem rede, credencial, arquivo ou flag; não liga a leitura por sessão (isso é a C6)

## GAP-A2

Lote da fila de gaps de 21/11/2026 (docs/governanca/FILA_GAPS_E_DIVERGENCIAS_20261121.md), continuação do GAP-A: GA-3 a GA-5 (hash do prompt obrigatório no validador, LEMBRETE com várias atividades e vínculo com o COMANDO, formato único da chave de idempotência S8-R1 x S15-R6 e janelas) e o fechamento do esquema de params das operações que ficaram sem esquema (ler_arquivo_repositorio, criar_lembrete, consultar_agenda_minima, registrar_plano); reproduzir o achado com teste que falha antes de corrigir; uma branch, um PR draft, contraprovas em ALTA e MEDIA

## S14

Especificação do runtime operacional do harness (regra do proprietário de 19/11/2026: LLM livre na cognição, condicionado nas leituras e entregas por gates e mecanismos determinísticos): zonas Z0 a Z3, três classes de garantia (enforçada, verificável, não gateável), contrato fixado por SHA, recibo de START, envelope de entrega com alegações verificadas, modo sombra e bloqueio, avaliação offline sem juiz-LLM como portão, registro, auditoria por amostra, rotinas, parada e controle de mudança; rastreia cada lacuna da auditoria de 19/11/2026

## RS

Recibo de START verificável (S14-R2, R3): o broker emite o recibo (SHA, papel, hashes) e o verificador recalcula no repositório no SHA fixado; recusa recibo ausente, SHA errado e hash adulterado; declara que não prova compreensão. Decisão do proprietário de 20/11/2026: os hashes do recibo cobrem os arquivos do START do papel (quatro de estudo, seis de engenharia, como o broker usa) mais o SHA; o verificador recalcula no repositório no SHA fixado, sem rede; o mesmo módulo roda local (Termux) e no CI, sem rede

## TOP3

S16 T3: entrega diária (S16-R7, R8, R9) e recorte do plano ao top 10 (C2, R4, R14): cargo, matéria, caminho, posição e percentual só quando verificados, material, atividade, quantidade definida pelo Tutor, filtros obrigatórios e objetivo; só cita recurso verificado, não afirma disponibilidade nem probabilidade; fora do top 10 vira lacuna com cargo e fonte e só entra com decisão registrada do proprietário; matéria sem lista definitiva vai a pendentes; sem cronograma imposto; função pura offline

## HOOK2

Hook Stop de entrega final versionado em .claude/hooks/entrega_final.py e registrado em .claude/settings.json, ativo até 20/11/2026: ao fim de rodada com entrega confere git limpo e enviado, gates e suíte de testes, bloqueia o fim da rodada se algo estiver vermelho, mostra a contagem regressiva e os desbloqueios pendentes do proprietário; só lê e avisa, falha aberta; código e testes já preparados (22 de 22 mutações mortas, execução real de 66 s), a entrar em PR próprio

## HOOKG

Hook geral claude-context-guard (pedido do proprietário de 21/11/2026): mede a janela de contexto e, aos 50%, injeta a ordem de preparar memória e o prompt de start da próxima sessão; hook de USUÁRIO (~/.claude) instalado por ele; pacote versionado fora de áreas de contrato; ativar no projeto (.claude/settings.json) é contrato; limites: percentual estimado, conteúdo do prompt é do modelo; detalhe em docs/governanca/E12_HOOK_GERAL_PASSAGEM_ENTRE_SESSOES.md
