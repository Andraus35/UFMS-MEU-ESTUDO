"""S20-R6/R9, S15-R4: conferência OFFLINE do disparo único da rotina de teste da Zapia (sem rede, sem modelo, sem credencial).

A rotina de teste é de execução única: a Zapia acorda na hora agendada, entrega pela regra do F1 e grava o recibo de volta com `entregue_em`. Este módulo
confere, no checkout de `entrada`, que o recibo de volta (1) passa na conferência do F1 (mesmo hash, ENTREGUE, só campos fixos), (2) traz carimbo UTC
bem formado, (3) NÃO é anterior ao horário agendado (anterior = entrega manual, não disparo), (4) cai dentro da tolerância depois dele, (5) é a única
entrega daquele hash (sem reenvio em laço) e (6) não passa do teto diário da regra do F1. O carimbo é autorrelato da Zapia: o que se prova é a
consistência com o horário que o PROPRIETÁRIO anotou ao criar a rotina, não a pontualidade do gatilho em vários dias (S15-R4 pede três dias).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import zapia_entrega
except ModuleNotFoundError:  # uso como pacote
    from scripts import zapia_entrega

TOLERANCIA_PADRAO = timedelta(seconds=900)  # PROPOSTA a confirmar pelo proprietário (S15-R4)
_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _parse_utc(texto):
    if not isinstance(texto, str) or not _UTC.match(texto):
        return None
    try:
        return datetime.strptime(texto, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def conferir_disparo(entrega_bytes, recibos, nome, agendado, tolerancia=TOLERANCIA_PADRAO):
    """None se o recibo de volta é consistente com o disparo agendado; senão o código. `agendado` é datetime com fuso."""
    if not isinstance(agendado, datetime) or agendado.tzinfo is None or not isinstance(tolerancia, timedelta) or tolerancia <= timedelta(0):
        return "AGENDAMENTO_INVALIDO"
    codigo = zapia_entrega.conferir_entrega(entrega_bytes, recibos, nome)
    if codigo:
        return codigo
    entrega = json.loads(bytes(entrega_bytes).decode("utf-8"))
    quando = _parse_utc(entrega["entregue_em"])
    if quando is None:
        return "CARIMBO_INVALIDO"
    atraso = quando - agendado.astimezone(timezone.utc)
    if atraso < timedelta(0):
        return "ENTREGA_ANTES_DO_AGENDADO"
    if atraso > tolerancia:
        return "ENTREGA_FORA_DA_TOLERANCIA"
    return None


def conferir_pasta_unica(raiz, nome, agendado, tolerancia=TOLERANCIA_PADRAO) -> dict:
    """Confere um checkout de `entrada`: a entrega `nome` contra o disparo agendado e a ausência de reenvio em laço. Devolve {"ok", "codigo", ...}."""
    raiz = Path(raiz)
    recibos, entregas = {}, {}
    for caminho in sorted((raiz / "comandos" / "recibos").glob("*.json")):
        try:
            h = json.loads(caminho.read_text(encoding="utf-8")).get("hash_corpo")
        except (ValueError, OSError, AttributeError):
            continue
        if isinstance(h, str):
            recibos[caminho.name] = h
    for caminho in sorted((raiz / "comandos" / "entregas").glob("*.json")):
        entregas[caminho.name] = caminho.read_bytes()
    if nome not in entregas:
        return {"ok": False, "codigo": "SEM_ENTREGA", "entregas": len(entregas)}
    codigo = conferir_disparo(entregas[nome], recibos, nome, agendado, tolerancia)
    if codigo:
        return {"ok": False, "codigo": codigo, "entregas": len(entregas)}
    hash_alvo = recibos[nome]
    mesmos, por_dia = 0, 0
    dia = json.loads(entregas[nome].decode("utf-8"))["entregue_em"][:10]
    for outro, bruto in entregas.items():
        try:
            e = json.loads(bytes(bruto).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {"ok": False, "codigo": "ENTREGA_ILEGIVEL", "entregas": len(entregas)}
        if isinstance(e, dict) and e.get("hash_corpo") == hash_alvo:
            mesmos += 1
        if isinstance(e, dict) and str(e.get("entregue_em", ""))[:10] == dia:
            por_dia += 1
    if mesmos != 1:
        return {"ok": False, "codigo": "MAIS_DE_UMA_ENTREGA_DO_MESMO_HASH", "entregas": len(entregas)}
    if por_dia > zapia_entrega.TETO_POR_DIA:
        return {"ok": False, "codigo": "TETO_DIARIO_EXCEDIDO", "entregas": len(entregas)}
    return {"ok": True, "codigo": None, "entregas": len(entregas)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Confere o disparo único da rotina de teste da Zapia (S20-R6). Offline.")
    p.add_argument("--raiz", required=True, help="checkout do repositório `entrada`")
    p.add_argument("--nome", default="f1-rotina.json")
    p.add_argument("--agendado", required=True, help="horário agendado em UTC, AAAA-MM-DDTHH:MM:SSZ (o que você anotou ao criar a rotina)")
    p.add_argument("--tolerancia", type=int, default=int(TOLERANCIA_PADRAO.total_seconds()), help="segundos depois do agendado (proposta: 900)")
    a = p.parse_args(argv)
    agendado = _parse_utc(a.agendado)
    if agendado is None:
        print(json.dumps({"ok": False, "codigo": "AGENDAMENTO_INVALIDO"}))
        return 2
    r = conferir_pasta_unica(a.raiz, a.nome, agendado, timedelta(seconds=a.tolerancia))
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
