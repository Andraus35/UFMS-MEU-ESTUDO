"""Preparo e conferência do teste F1 de entrega à Zapia (S20 F1): um comando SINTÉTICO validado e o recibo, e a conferência do recibo de volta.

Offline e puro nas funções; a CLI só lê e escreve arquivos locais. O fluxo real só promove comando com a flag do fluxo ligada (janela PJ); para provar o
CAMINHO DE ENTREGA sem ligar a flag, o proprietário coloca à mão este par sintético em `comandos/validados/` e `comandos/recibos/` de `entrada`. O recibo
é marcado `SINTETICO_MANUAL`: NÃO prova a promoção pelo fluxo. O comando passa pelo MESMO validador da caixa antes de ser gerado (se a caixa o recusasse,
nada é gerado). Sem dado pessoal. NÃO prova rotina agendada nem notificação espontânea (a Zapia só responde dentro da conversa).
"""
from __future__ import annotations

import argparse
import json
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import agent_commands
    import command_box
    import command_idempotency
    import zapia_entrega
except ModuleNotFoundError:  # uso como pacote
    from scripts import agent_commands, command_box, command_idempotency, zapia_entrega

NOME = "f1-teste.json"
TEXTO = "Teste F1 do Coach: notificação sintética, sem dado pessoal."


def montar(agora_utc, nome: str = NOME, texto: str = TEXTO) -> dict:
    """Comando sintético (Coach, `enviar_mensagem`, chave de rotina do dia) e recibo manual. Levanta ValueError se a caixa o recusar."""
    hoje = command_idempotency.data_local(agora_utc)
    if hoje is None:
        raise ValueError("relógio sem fuso")
    schema = agent_commands.load_schema()
    comando = {"schema_version": schema["schema_version"], "origin": "coach", "operation": "enviar_mensagem", "destination": "proprietario",
              "params": {"texto": texto}, "idempotency_key": command_idempotency.montar_chave(hoje, "briefing", "dia"),
              "nonce": "f1-" + secrets.token_hex(8), "issued_at": agora_utc.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    bruto = json.dumps(comando, ensure_ascii=False).encode("utf-8")
    veredito = command_box.validar(nome, bruto, {"agora": agora_utc, "ledger": agent_commands.CommandLedger(), "dia_de_descanso": False,
                                                 "atividades_pendentes": [], "chaves_do_dia": []})
    if veredito["status"] != command_box.PROMOVER:
        raise ValueError("a caixa recusaria o comando de teste: " + str(veredito.get("codigo")))
    h = command_box.command_hash(comando)
    recibo = {"entrada_id": nome, "status": "PROMOVER", "codigo": "SINTETICO_MANUAL", "hash_corpo": h, "execucao": "manual-f1", "validador_sha": "0" * 40}
    return {"nome": nome, "hash_corpo": h, "comando_bytes": bruto, "recibo_bytes": zapia_entrega._canonico(recibo)}


def conferir(entrega_bytes, meta: dict):
    """None se o recibo de volta confere com o hash do comando sintético; senão o código."""
    return zapia_entrega.conferir_entrega(entrega_bytes, {meta["nome"]: meta["hash_corpo"]}, meta["nome"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Teste F1: preparar o par sintético ou conferir o recibo de volta (offline).")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("preparar")
    a.add_argument("--saida", required=True)
    c = sub.add_parser("conferir")
    c.add_argument("--entrega", required=True)
    c.add_argument("--meta", required=True)
    args = p.parse_args(argv)
    if args.cmd == "preparar":
        m = montar(datetime.now(timezone.utc))
        d = Path(args.saida)
        (d / "validados").mkdir(parents=True, exist_ok=True)
        (d / "recibos").mkdir(parents=True, exist_ok=True)
        (d / "validados" / m["nome"]).write_bytes(m["comando_bytes"])
        (d / "recibos" / m["nome"]).write_bytes(m["recibo_bytes"])
        (d / "meta.json").write_text(json.dumps({"nome": m["nome"], "hash_corpo": m["hash_corpo"]}))
        print(json.dumps({"nome": m["nome"], "hash_corpo": m["hash_corpo"]}))
        return 0
    meta = json.loads(Path(args.meta).read_text())
    codigo = conferir(Path(args.entrega).read_bytes(), meta)
    print(json.dumps({"confere": codigo is None, "codigo": codigo}))
    return 0 if codigo is None else 1


if __name__ == "__main__":
    sys.exit(main())
