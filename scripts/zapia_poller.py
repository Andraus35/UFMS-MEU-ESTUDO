"""ZAPIA-F3 (E29): preparo e conferência OFFLINE do teste "rotina cria rotina" com a Zapia real (sem rede, sem modelo, sem credencial).

Desenho do teste: (1) um ALVO sintético (`enviar_mensagem` do Coach, como no F1) e um PEDIDO sintético (`agendar_rotina`, `F1_ENTREGA_UNICA`, apontando
para o alvo) entram à mão em `comandos/validados/` e `comandos/recibos/` do `entrada`, com recibo `SINTETICO_MANUAL` (a promoção pelo fluxo é outro teste);
(2) a Zapia cria um POLLER de execução única (instrução `POLLER`, com o commit público e o hash do modelo filho fixados); (3) no horário do poller ele lê o
pedido, cria por conta própria a rotina FILHA no horário do pedido e grava `comandos/criadas/<pedido>` (status CRIADA); (4) a filha dispara e entrega o alvo
como no F1/E23. Este módulo prepara o par e confere (a) o recibo CRIADA e (b) a entrega da filha. O carimbo e o id da rotina são AUTORRELATO da Zapia:
o que se prova é a consistência com o pedido e com o texto versionado (o hash da instrução da filha é recalculado aqui); NÃO se prova que a rotina foi
criada pelo app (só a captura da lista de rotinas do app, ato do proprietário), nem a promoção pelo fluxo, nem vários dias.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import agendar_rotina
    import agent_commands
    import command_box
    import command_idempotency
    import zapia_disparo
    import zapia_entrega
    import zapia_f1_prep
except ModuleNotFoundError:  # uso como pacote
    from scripts import agendar_rotina, agent_commands, command_box, command_idempotency, zapia_disparo, zapia_entrega, zapia_f1_prep

CRIADAS = "comandos/criadas/"
CRIADA = "CRIADA"
CAMPOS_CRIADA = {"entrada_id", "hash_corpo", "status", "criada_em", "agendado_utc", "rotina_id_relatado", "instrucao_sha256"}
NOME_ALVO, NOME_PEDIDO = "f3-alvo.json", "f3-pedido.json"
TOLERANCIA_PADRAO = timedelta(seconds=900)  # PROPOSTA (como no F2a), ajustável
_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_ID = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _utc(texto):
    return zapia_disparo._parse_utc(texto)


def montar_pedido(agora_utc, agendado_filha_utc, alvo_hash, nome=NOME_PEDIDO, origem="coach"):
    """Pedido sintético `agendar_rotina` (passa pela MESMA caixa) e recibo manual. Levanta ValueError se a caixa o recusar."""
    hoje = command_idempotency.data_local(agora_utc)
    if hoje is None:
        raise ValueError("relógio sem fuso")
    schema = agent_commands.load_schema()
    comando = {"schema_version": schema["schema_version"], "origin": origem, "operation": agendar_rotina.OPERACAO, "destination": agendar_rotina.DESTINO,
              "params": {"modelo": "F1_ENTREGA_UNICA", "agendado_utc": agendado_filha_utc, "comandos_sha256": [alvo_hash]},
              "idempotency_key": f"agenda-{origem}-{agora_utc.astimezone(timezone.utc).strftime('%H%M%S')}", "nonce": "f3-" + hashlib.sha256(agendado_filha_utc.encode()).hexdigest()[:16],
              "issued_at": agora_utc.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    bruto = json.dumps(comando, ensure_ascii=False).encode("utf-8")
    veredito = command_box.validar(nome, bruto, {"agora": agora_utc, "ledger": agent_commands.CommandLedger(), "dia_de_descanso": False, "atividades_pendentes": [],
                                                 "chaves_do_dia": [], "agendar_rotina_habilitada": True, "hashes_promovidos": [alvo_hash], "agendamentos_do_dia": []})
    if veredito["status"] != command_box.PROMOVER:
        raise ValueError("a caixa recusaria o pedido de teste: " + str(veredito.get("codigo")))
    h = command_box.command_hash(comando)
    recibo = {"entrada_id": nome, "status": "PROMOVER", "codigo": "SINTETICO_MANUAL", "hash_corpo": h, "execucao": "manual-f3", "validador_sha": "0" * 40}
    return {"nome": nome, "hash_corpo": h, "comando_bytes": bruto, "recibo_bytes": zapia_entrega._canonico(recibo)}


def instrucao_esperada(pedido, repo, credencial="github_ufms_repo_token", root=None):
    """Texto que a rotina FILHA deve ter (modelo `UNICA` versionado, preenchido com o pedido); base do `instrucao_sha256`."""
    p = pedido["params"]
    kw = {"root": root} if root else {}
    return agendar_rotina.renderizar("F1_ENTREGA_UNICA", repo=repo, credencial=credencial, agendado_utc=p["agendado_utc"], hashes=p["comandos_sha256"],
                                     origem=pedido["origin"], **kw)


def conferir_criada(criada_bytes, pedido_bytes, recibos, nome, poller_agendado, repo, credencial="github_ufms_repo_token", tolerancia=TOLERANCIA_PADRAO, root=None):
    """None se o recibo CRIADA é consistente com o pedido e com o horário do poller; senão o código. `poller_agendado`: datetime com fuso."""
    if not isinstance(poller_agendado, datetime) or poller_agendado.tzinfo is None or not isinstance(tolerancia, timedelta) or tolerancia <= timedelta(0):
        return "AGENDAMENTO_INVALIDO"
    try:
        pedido = json.loads(bytes(pedido_bytes).decode("utf-8"))
        c = json.loads(bytes(criada_bytes).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return "ARQUIVO_ILEGIVEL"
    if not (isinstance(pedido, dict) and isinstance(c, dict)) or pedido.get("operation") != agendar_rotina.OPERACAO:
        return "PEDIDO_INVALIDO"
    if set(c) != CAMPOS_CRIADA:
        return "CAMPOS_FORA_DO_CONTRATO"
    if c["entrada_id"] != nome or c["status"] != CRIADA:
        return "STATUS_OU_NOME_INVALIDO"
    esperado = recibos.get(nome)
    if not (isinstance(esperado, str) and esperado == c["hash_corpo"] == command_box.command_hash(pedido)):
        return "HASH_DIVERGE"
    params = pedido.get("params") or {}
    if c["agendado_utc"] != params.get("agendado_utc"):
        return "AGENDADO_DIVERGE_DO_PEDIDO"
    criada, agendado_filha = _utc(c["criada_em"]), _utc(c["agendado_utc"])
    if criada is None or agendado_filha is None:
        return "CARIMBO_INVALIDO"
    atraso = criada - poller_agendado.astimezone(timezone.utc)
    if atraso < timedelta(0):
        return "CRIADA_ANTES_DO_POLLER"
    if atraso > tolerancia:
        return "CRIADA_FORA_DA_TOLERANCIA"
    if criada >= agendado_filha:
        return "CRIADA_DEPOIS_DO_DISPARO_DA_FILHA"
    if not (isinstance(c["rotina_id_relatado"], str) and _ID.fullmatch(c["rotina_id_relatado"])):
        return "ROTINA_ID_INVALIDO"
    try:
        texto = instrucao_esperada(pedido, repo, credencial, root)
    except ValueError:
        return "MODELO_INCONSISTENTE"
    if c["instrucao_sha256"] != hashlib.sha256(texto.encode("utf-8")).hexdigest():
        return "INSTRUCAO_DA_FILHA_DIVERGE_DO_MODELO"
    return None


def _recibos(raiz):
    out = {}
    for caminho in sorted((Path(raiz) / "comandos" / "recibos").glob("*.json")):
        try:
            h = json.loads(caminho.read_text(encoding="utf-8")).get("hash_corpo")
        except (ValueError, OSError, AttributeError):
            continue
        if isinstance(h, str):
            out[caminho.name] = h
    return out


def conferir_pasta(raiz, nome_pedido, nome_alvo, poller_agendado, repo, credencial="github_ufms_repo_token", tolerancia=TOLERANCIA_PADRAO):
    """Confere um checkout de `entrada`: (a) o recibo CRIADA do poller e (b) a entrega da filha (reaproveita o verificador do disparo único)."""
    raiz = Path(raiz)
    criada, pedido = raiz / "comandos" / "criadas" / nome_pedido, raiz / "comandos" / "validados" / nome_pedido
    if not criada.is_file():
        return {"ok": False, "fase": "poller", "codigo": "SEM_RECIBO_CRIADA"}
    if not pedido.is_file():
        return {"ok": False, "fase": "poller", "codigo": "SEM_PEDIDO"}
    codigo = conferir_criada(criada.read_bytes(), pedido.read_bytes(), _recibos(raiz), nome_pedido, poller_agendado, repo, credencial, tolerancia)
    if codigo:
        return {"ok": False, "fase": "poller", "codigo": codigo}
    agendado_filha = _utc(json.loads(criada.read_text(encoding="utf-8"))["agendado_utc"])
    filha = zapia_disparo.conferir_pasta_unica(raiz, nome_alvo, agendado_filha)
    if not filha["ok"]:
        return {"ok": False, "fase": "filha", "codigo": filha["codigo"], "poller": "CRIADA conferido"}
    return {"ok": True, "fase": "completo", "codigo": None,
            "limite": "autorrelato da Zapia; nao prova que a rotina foi criada pelo app (so a captura da lista de rotinas) nem a promocao pelo fluxo; um dia, uma vez"}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="ZAPIA-F3: preparar o par sintético (alvo e pedido) ou conferir o resultado (offline).")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("preparar")
    a.add_argument("--saida", required=True)
    a.add_argument("--agendado-filha", required=True, help="horário UTC da rotina FILHA (pelo menos 90 min depois de agora)")
    c = sub.add_parser("conferir")
    c.add_argument("--raiz", required=True, help="checkout do repositório `entrada`")
    c.add_argument("--poller-agendado", required=True, help="horário UTC que você anotou para o poller")
    c.add_argument("--repo", default="Andraus35/ufms-meu-estudo-entrada")
    c.add_argument("--nome-pedido", default=NOME_PEDIDO)
    c.add_argument("--nome-alvo", default=NOME_ALVO)
    c.add_argument("--tolerancia", type=int, default=int(TOLERANCIA_PADRAO.total_seconds()))
    args = p.parse_args(argv)
    if args.cmd == "preparar":
        agora = datetime.now(timezone.utc)
        if _utc(args.agendado_filha) is None:
            print(json.dumps({"ok": False, "codigo": "AGENDADO_INVALIDO"}))
            return 2
        try:
            alvo = zapia_f1_prep.montar(agora, nome=NOME_ALVO)
            ped = montar_pedido(agora, args.agendado_filha, alvo["hash_corpo"])
        except ValueError as erro:
            print(json.dumps({"ok": False, "codigo": str(erro)[:120]}))
            return 1
        d = Path(args.saida)
        (d / "validados").mkdir(parents=True, exist_ok=True)
        (d / "recibos").mkdir(parents=True, exist_ok=True)
        for m in (alvo, ped):
            (d / "validados" / m["nome"]).write_bytes(m["comando_bytes"])
            (d / "recibos" / m["nome"]).write_bytes(m["recibo_bytes"])
        print(json.dumps({"ok": True, "alvo": alvo["nome"], "alvo_hash": alvo["hash_corpo"], "pedido": ped["nome"], "pedido_hash": ped["hash_corpo"]}))
        return 0
    pol = _utc(args.poller_agendado)
    if pol is None:
        print(json.dumps({"ok": False, "codigo": "AGENDAMENTO_INVALIDO"}))
        return 2
    r = conferir_pasta(args.raiz, args.nome_pedido, args.nome_alvo, pol, args.repo, tolerancia=timedelta(seconds=args.tolerancia))
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
