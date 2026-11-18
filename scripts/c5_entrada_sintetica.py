#!/usr/bin/env python3
"""Monta a ENTRADA SINTÉTICA da segunda metade da C5 (S6, prova real da promoção até `dados`).

Offline e puro: não faz rede, não lê credencial e não grava nada além do arquivo pedido em `--saida`. A entrada é um evento
`caderno_recomendado` (não traz resultado pessoal, só um tópico do edital) com a marca `sintetico: true`, que o portão guarda no
envelope e as projeções descartam (`session_read_guard.descartar_sinteticos`). Antes de devolver, a entrada passa pelas mesmas
etapas de forma e de esquema do portão (`promotion_gate.parse_entry` e `check_schema`), para que um defeito apareça aqui e não
no fluxo real.

Uso: python scripts/c5_entrada_sintetica.py --saida CAMINHO.json     (imprime NOME=... e EVENTO=... para o roteiro do Termux)
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promotion_gate as pg  # noqa: E402
from core import topic_rows  # noqa: E402

FUSO = timezone(timedelta(hours=-4))  # horário de Mato Grosso do Sul, como nas fixtures do portão
TOPICO = "GER-LEG"  # existe em config/topics.csv; a conferência de esquema falha se sumir


def montar(agora=None):
    """Devolve (nome_do_arquivo, bytes_da_entrada, caminho_do_evento_no_historico)."""
    agora = (agora or datetime.now(FUSO)).astimezone(FUSO).replace(microsecond=0)
    carimbo = agora.strftime("%Y%m%dT%H%M%S")
    evento = {"type": "caderno_recomendado", "timestamp": agora.isoformat(), "caderno_id": "c5-sintetico-" + carimbo,
              "recommendation_id": "C5-SINT-" + carimbo, "topic_ids": [TOPICO]}
    evento["event_id"] = pg.derive_event_id(evento)
    entrada = {"entrada_versao": pg.ENTRY_VERSION, "evento": evento, pg.SYNTHETIC_KEY: True,
               "origem": {"agente": "tutor", "escritor": pg.DELIVERER,
                          "comando_hash": hashlib.sha256(("c5-sintetico:" + carimbo).encode("utf-8")).hexdigest()}}
    bruto = json.dumps(entrada, ensure_ascii=False, sort_keys=True).encode("utf-8")
    verificada = pg.parse_entry(bruto)  # forma (inclui a marca booleana)
    caminho = pg.check_schema(verificada["evento"], [], topic_rows(ROOT))  # esquema e id derivado
    return f"c5-sintetica-{carimbo}.json", bruto, caminho


def main(argv=None):
    p = argparse.ArgumentParser(description="Monta a entrada sintética da C5 (segunda metade).")
    p.add_argument("--saida", required=True)
    a = p.parse_args(argv)
    nome, bruto, caminho = montar()
    Path(a.saida).write_bytes(bruto)
    print("NOME=" + nome)
    print("EVENTO=" + caminho)
    return 0


if __name__ == "__main__":
    sys.exit(main())
