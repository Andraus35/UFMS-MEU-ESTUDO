# E27: aplicação da operação `agendar_rotina` ao contrato (lote ZAPIA-APL, 23/11/2026)

**Natureza:** registro do lote `ZAPIA-APL` (RM-09, S20). Aplica a proposta da **E24** depois da decisão do proprietário de excluir o `AUTORIZO` por mensagem (**E26**, D-31, em vigor desde o merge do #185). **Altera arquivos de contrato** (`agents/`, `config/agent_command_schema.json`, `scripts/agents_gate.py`, `settings.json`): o merge exige o pedido expresso dele, citando PR e head. Escolhas dele nesta rodada: abrir já; chave de parada em `settings.json`; os quatro modelos.

## O que foi aplicado

- **Operação `agendar_rotina`**, compartilhada por Tutor e Coach (`SHARED` em `agents_gate.py`), destino `zapia_rotina` (`config/agent_command_schema.json`), listada em `agents/TUTOR.md`, `COACH.md` e `ZAPIA.md`.
- **Params fechados, sem texto livre** (`command_params_schema.py`): `modelo`, `agendado_utc`, `comandos_sha256`.
- **Modelos presos à origem** (`scripts/agendar_rotina.py`): `F1_ENTREGA_UNICA` (Tutor ou Coach, 1 dia, 1 hash), `ROTINA_ESTUDO_DIARIA` (Tutor, 2 dias), `ROTINA_ESTUDO_SEMANAL` (Tutor, 7 dias) e `BRIEFING_DIARIO` (Coach, 7 dias, **proposta de 7 dias**). Os três últimos são modelos de **escuta**: a rotina entrega, a cada disparo, os comandos validados da origem emitidos há menos de 24 h; **sem hash antecipado**, porque o comando de cada dia só existe no dia (validade de 24 h).
- **Limites determinísticos na caixa** (`command_box.py`, depois da forma): primeiro disparo entre **90 min e 24 h** depois do `issued_at`; **1 pedido por dia por origem**; cada hash tem de ser de **comando já promovido**; recusas com código (`ORIGEM_FORA_DO_MODELO`, `AGENDAMENTO_FORA_DA_JANELA`, `ALVO_NAO_PROMOVIDO`, `TETO_DIARIO_AGENDAMENTO`, `ROTINA_PARADA`...). Tudo o que o contexto não informa **recusa**.
- **Chave de parada versionada:** `settings.json` > `automation.agendar_rotina_enabled` (entregue **ligada**, porque o proprietário quer a automação sem interferência). Falsa, ausente, repetida ou ilegível desliga a emissão (`ROTINA_PARADA`). O runner lê a chave do SHA fixado do validador. O proprietário também pausa ou apaga a rotina no app a qualquer momento.
- **Modelos de instrução versionados** (`config/rotina_instrucoes.json`, com hash conferido por `python scripts/agendar_rotina.py --check`): **URLs completos e literais** (`comandos`, nunca `commands`), ordem de **não traduzir**, **relato de cada chamada** (URL e resultado), credencial só por nome, `rotina_id_relatado` no recibo. `python scripts/agendar_rotina.py --instrucao <MODELO> --agendado <UTC> [--hash <h>] --origem <tutor|coach>` imprime o texto exato para o pedido à Zapia.
- **Runner** (`command_box_runner.py`): repassa o contexto, conta o pedido promovido no teto da origem e o comando promovido como alvo válido para o pedido seguinte (execução em série).
- **Testes:** `tests/test_agendar_rotina.py` (40 casos: forma, modelo-origem, janela nos limites, alvo, teto por origem, parada, caixa, runner em série, instruções com mutação de hash, de URL traduzida e de segredo) e ajuste dos testes que enumeravam as operações; mutações do módulo, da caixa e do runner mortas.

## O que NÃO está feito (declarado)

- **O runner real ainda não alimenta o contexto do pedido:** `main` do `command_box_runner.py` fornece a chave de parada, mas **não** `hashes_promovidos` nem `agendamentos_do_dia` (leitura dos recibos e dos comandos do dia no `entrada`). Como a caixa **recusa o que o contexto não informa**, no fluxo real todo `agendar_rotina` é recusado (`ALVOS_DESCONHECIDOS` ou `TETO_DESCONHECIDO`) até esse item. É o próximo item da fila (`ZAPIA-CTX`); a mesma lacuna já existia para `dia_de_descanso`, `atividades_pendentes` e `chaves_do_dia` do lembrete.
- **A Zapia não executa este Python:** o pedido é dado; a rotina continua sendo criada por prompt (o texto vem do modelo versionado) e a prova é o **recibo de volta** e o verificador (`zapia_disparo.py`). Não está provado que ela crie a rotina **a partir de um comando do repositório** sem o prompt; no E23 ela a criou por prompt.
- **Origem não provada na nuvem** (S4-R2): a defesa é o escopo fechado, os tetos, o recibo e a parada.
- Modelos `ROTINA_ESTUDO_*` e `BRIEFING_DIARIO` **não** foram provados com a Zapia real; só `F1_ENTREGA_UNICA` tem prova (E23). A S21 (revisões por escopo) segue sendo outra frente.

## Para o proprietário

Aprovar o merge, citando PR e head. Esse merge aplica, no contrato, o que a E24 propunha e a E26 autorizou.
