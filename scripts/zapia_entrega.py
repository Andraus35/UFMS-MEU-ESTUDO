"""Entrega do comando validado à Zapia e recibo de volta (S20 F0/F1; decisões do proprietário de 22/11/2026: D1 = a Zapia lê a fila por um
conector de GitHub a pedir, D2 = a rotina da Zapia acorda, D3 = o fluxo do repositório privado valida e promove). OFFLINE, função pura.

O que este módulo é: a regra do lado da Zapia, escrita como código testável. A rotina da Zapia lê `comandos/validados/` e `comandos/recibos/`
(por conector de GitHub, SIMULADO nos testes), escolhe só o que tem recibo de MESMO hash (`command_box.selecionar_executaveis`), monta uma
notificação "em nome" do Tutor ou do Coach e a envia por um `enviar` injetado. Para cada envio devolve um recibo de volta (`comandos/entregas/`),
com hash e sem o texto, que `conferir_entrega` confere contra o recibo da promoção. NADA aqui fala com a Zapia, a rede ou o GitHub.

Regras (S20-R3, R4, R6, R8, R9): só `enviar_mensagem` do Tutor ou do Coach (a origem é DECLARADA, não provada, e a notificação diz isso); texto
conferido de novo no lado da Zapia (defesa em profundidade); comando velho (mais de 24 h) não vira notificação; teto de 2 por dia; sem reenvio
em laço nem envio substituto: falha no envio não gera recibo e a próxima rodada o vê de novo só até expirar; o mesmo hash nunca é entregue duas vezes.

Limites: NÃO prova que a Zapia tenha conector de GitHub, que a rotina dispare, que o `enviar` notifique o celular nem que ela rode este código
(autorrelato, confiança C); a prova real é o roteiro do proprietário (`docs/governanca/ROTEIRO_ZAPIA_IDA_F1_20261122.md`).
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

try:
    import agent_commands
    import command_box
    import content_filters
    import gates_mot
except ModuleNotFoundError:  # uso como pacote
    from scripts import agent_commands, command_box, content_filters, gates_mot

ENTREGAS = "comandos/entregas/"
OPERACAO = "enviar_mensagem"
ORIGENS = {"tutor": "Tutor", "coach": "Coach"}
IDADE_MAXIMA = timedelta(hours=24)
TETO_POR_DIA = 2
MAX_NOTIFICACAO = 600
CAMPOS_ENTREGA = {"entrada_id", "hash_corpo", "status", "entregue_em", "origem_declarada"}
CAMPO_ROTINA = "rotina_id_relatado"  # opcional: id da rotina como a Zapia o relata (autorrelato); o F1 sem ele continua valendo
_ID_ROTINA = __import__("re").compile(r"^[A-Za-z0-9._:-]{1,64}$")
ENTREGUE = "ENTREGUE"


def _canonico(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def montar_notificacao(comando):
    """Texto da notificação em nome do agente, ou None. Só `enviar_mensagem` de Tutor ou Coach; reconfere o texto (defesa em profundidade)."""
    if not (isinstance(comando, dict) and comando.get("operation") == OPERACAO and comando.get("origin") in ORIGENS):
        return None
    params = comando.get("params")
    texto = params.get("texto") if isinstance(params, dict) and set(params) == {"texto"} else None
    if not (isinstance(texto, str) and texto.strip()) or agent_commands.scan_text(texto, html=True) or agent_commands.texto_de_questao(texto):
        return None
    if content_filters.tem_url(texto) or content_filters.instrucao_embutida(texto) or content_filters.mistura_de_scripts(texto):
        return None
    if any(f["gate"] != "FORMA" for f in gates_mot.verificar_mensagem(texto)["falhas"]):
        return None
    saida = f"{ORIGENS[comando['origin']]} (origem declarada): {texto.strip()}"
    return saida if len(saida) <= MAX_NOTIFICACAO else None


def _expirado(comando, agora) -> bool:
    try:
        emitido = agent_commands._parse_time(comando["issued_at"])
    except (KeyError, ValueError, TypeError):
        return True
    return not (timedelta(seconds=-120) <= agora - emitido <= IDADE_MAXIMA)  # velho demais ou emitido no futuro (relógio fora)


def _recibo_de_entrega(nome, comando, hash_corpo, agora) -> dict:
    return {"entrada_id": nome, "hash_corpo": hash_corpo, "status": ENTREGUE, "origem_declarada": comando["origin"],
            "entregue_em": agora.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


def executar_rotina(listagem, recibos, entregues, enviar, agora, entregues_hoje=0) -> dict:
    """Uma rodada da rotina da Zapia. Nunca levanta. Devolve {estado, itens, entregas}.

    `listagem` {caminho: bytes} de `comandos/validados/`; `recibos` {nome: hash}; `entregues` conjunto de hashes já entregues (recibos de volta já
    gravados); `enviar` callable(texto) que notifica (levanta ou devolve não-True se falhar); `agora` datetime UTC com fuso;
    `entregues_hoje` quantas notificações já saíram no dia local. `entregas` = {nome: bytes do recibo de volta}, a gravar em `ENTREGAS`."""
    resumo = {"estado": "PROCESSADO", "itens": [], "entregas": {}}
    if not (isinstance(agora, datetime) and agora.tzinfo is not None) or not callable(enviar):
        return {**resumo, "estado": "CONTEXTO_INVALIDO"}
    entregues = set(entregues or ())
    executaveis = command_box.selecionar_executaveis(listagem, recibos)  # só validado COM recibo de mesmo hash
    hoje = entregues_hoje if type(entregues_hoje) is int and entregues_hoje >= 0 else TETO_POR_DIA
    for caminho in sorted(executaveis):
        comando, nome = executaveis[caminho], caminho.rsplit("/", 1)[-1]
        item = {"entrada_id": nome}
        resumo["itens"].append(item)
        h = command_box.command_hash(comando)
        if h in entregues:
            item["status"] = "JA_ENTREGUE"
        elif comando.get("operation") != OPERACAO:
            item["status"] = "IGNORADO"
            item["codigo"] = "OPERACAO_NAO_SUPORTADA"  # criar_lembrete e demais ficam para outra fase (S20-R10)
        elif _expirado(comando, agora):
            item["status"], item["codigo"] = "RECUSADA", "COMANDO_EXPIRADO"
        elif (texto := montar_notificacao(comando)) is None:
            item["status"], item["codigo"] = "RECUSADA", "TEXTO_OU_ORIGEM_RECUSADOS"
        elif hoje >= TETO_POR_DIA:
            item["status"], item["codigo"] = "RECUSADA", "TETO_DIARIO"
        else:
            try:
                ok = enviar(texto) is True
            except Exception:  # falha no envio: sem recibo, sem nova tentativa nesta rodada, sem envio substituto
                ok = False
            if not ok:
                item["status"], item["codigo"] = "FALHA", "FALHA_NO_ENVIO"
                continue
            hoje += 1
            entregues.add(h)
            item["status"] = ENTREGUE
            resumo["entregas"][nome] = _canonico(_recibo_de_entrega(nome, comando, h, agora))
    return resumo


def conferir_entrega(entrega_bytes, recibos, nome) -> str | None:
    """Confere o recibo de volta contra o recibo da promoção: None se confere, senão o código. Volta fiel: mesmo hash, status ENTREGUE, só campos fixos."""
    try:
        e = json.loads(bytes(entrega_bytes).decode("utf-8"))
    except (UnicodeDecodeError, ValueError, TypeError):
        return "ENTREGA_ILEGIVEL"
    if not isinstance(e, dict) or set(e) not in (CAMPOS_ENTREGA, CAMPOS_ENTREGA | {CAMPO_ROTINA}):
        return "ENTREGA_FORA_DO_FORMATO"
    if CAMPO_ROTINA in e and not (isinstance(e[CAMPO_ROTINA], str) and _ID_ROTINA.match(e[CAMPO_ROTINA])):
        return "ROTINA_ID_INVALIDO"
    if e["entrada_id"] != nome or e["status"] != ENTREGUE or e["origem_declarada"] not in ORIGENS:
        return "ENTREGA_INCONSISTENTE"
    esperado = (recibos or {}).get(nome)
    if not isinstance(esperado, str) or e["hash_corpo"] != esperado:
        return "ENTREGA_COM_HASH_DIFERENTE_DO_RECIBO"
    return None


def conferir_pasta(raiz) -> dict:
    """Confere TODOS os recibos de volta de um checkout de `entrada` (`comandos/entregas/*.json`) contra `comandos/recibos/*.json`. Offline.
    Devolve {"conferidas": n, "falhas": {nome: codigo}}. É a prova de que a notificação saiu para o hash que o fluxo promoveu."""
    from pathlib import Path
    raiz = Path(raiz)
    recibos = {}
    for caminho in sorted((raiz / "comandos" / "recibos").glob("*.json")):
        try:
            h = json.loads(caminho.read_text(encoding="utf-8")).get("hash_corpo")
        except (ValueError, OSError):
            continue
        if isinstance(h, str):
            recibos[caminho.name] = h
    falhas, n = {}, 0
    for caminho in sorted((raiz / "comandos" / "entregas").glob("*.json")):
        n += 1
        codigo = conferir_entrega(caminho.read_bytes(), recibos, caminho.name)
        if codigo:
            falhas[caminho.name] = codigo
    return {"conferidas": n, "falhas": falhas}


def main(argv=None) -> int:
    import argparse
    import sys
    p = argparse.ArgumentParser(description="Confere os recibos de volta da Zapia contra os recibos da promoção (S20 F1). Offline.")
    p.add_argument("--raiz", required=True, help="checkout do repositório `entrada`")
    p.add_argument("--exigir-ao-menos", type=int, default=1, help="falha se houver menos recibos de volta que isto")
    a = p.parse_args(argv)
    r = conferir_pasta(a.raiz)
    print(json.dumps(r, ensure_ascii=False))
    return 0 if not r["falhas"] and r["conferidas"] >= a.exigir_ao_menos else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
