"""Classificação do dia (GAP-B, GB-1; S15-R16, P1 da rotina): função pura, sem rede, arquivo, relógio próprio nem modelo.

Entradas: data local, dia de descanso do plano, se há plano, atividades do plano para a data e revisões da projeção
(`{"topico", "vence_em"}` com datas de calendário no fuso do plano). Saída, nesta PRECEDÊNCIA:
`DESCANSO` > `SEM_PLANO` > `REVISAO_VENCIDA` (`data_local > vence_em`; aparece como vencida, nunca é reagendada) > `DEVIDO_HOJE`
(`data_local == vence_em` ou atividade do plano para a data) > `SEM_ATIVIDADE`.
A classe só escolhe o TIPO da mensagem; o texto é do Coach. Entrada desconhecida ou malformada NÃO classifica: devolve
`classe` None e um código em `erro` (fail-closed; nada de adivinhar descanso ou plano). O relógio é sempre injetado (S15-R1).
O dia de descanso e a existência de plano vêm do plano do proprietário (dado pessoal, fora do repositório público): a função
os recebe prontos.
"""
from __future__ import annotations

import re
from datetime import date

try:
    import command_idempotency
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import command_idempotency

CLASSES = ("DESCANSO", "SEM_PLANO", "REVISAO_VENCIDA", "DEVIDO_HOJE", "SEM_ATIVIDADE")
_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _data_valida(valor) -> bool:
    if not isinstance(valor, str) or not _DATA.fullmatch(valor):
        return False
    try:
        date.fromisoformat(valor)
    except ValueError:
        return False
    return True


def _erro(codigo: str, data_local=None) -> dict:
    return {"classe": None, "erro": codigo, "data_local": data_local, "revisoes_vencidas": [], "revisoes_devidas": [], "atividades": []}


def classificar_dia(*, data_local, descanso, tem_plano, atividades_do_dia, revisoes) -> dict:
    """Classifica o dia local. Nunca levanta exceção para entrada ruim; não altera as listas recebidas."""
    if not _data_valida(data_local):
        return _erro("DATA_LOCAL_INVALIDA")
    if not isinstance(descanso, bool):
        return _erro("DESCANSO_DESCONHECIDO", data_local)
    if not isinstance(tem_plano, bool):
        return _erro("PLANO_DESCONHECIDO", data_local)
    if not (isinstance(atividades_do_dia, list) and all(isinstance(a, str) and a for a in atividades_do_dia)):
        return _erro("ATIVIDADES_INVALIDAS", data_local)
    if not (isinstance(revisoes, list) and all(isinstance(r, dict) and set(r) == {"topico", "vence_em"} and isinstance(r["topico"], str)
                                                and _data_valida(r["vence_em"]) for r in revisoes)):
        return _erro("REVISOES_INVALIDAS", data_local)
    ordenadas = sorted(revisoes, key=lambda r: (r["vence_em"], r["topico"]))
    vencidas = [dict(r) for r in ordenadas if r["vence_em"] < data_local]  # datas ISO comparam como texto
    devidas = [dict(r) for r in ordenadas if r["vence_em"] == data_local]
    if descanso:
        classe = "DESCANSO"  # informa as vencidas, mas a mensagem não cobra estudo (S3-R2)
    elif not tem_plano:
        classe = "SEM_PLANO"
    elif vencidas:
        classe = "REVISAO_VENCIDA"
    elif devidas or atividades_do_dia:
        classe = "DEVIDO_HOJE"
    else:
        classe = "SEM_ATIVIDADE"
    return {"classe": classe, "erro": None, "data_local": data_local, "revisoes_vencidas": vencidas, "revisoes_devidas": devidas,
            "atividades": sorted(atividades_do_dia)}


def classificar_instante(agora_utc, *, descanso, tem_plano, atividades_do_dia, revisoes) -> dict:
    """Como `classificar_dia`, com a data local derivada do instante UTC injetado (America/Campo_Grande, S15-R2)."""
    hoje = command_idempotency.data_local(agora_utc)
    if hoje is None:
        return _erro("RELOGIO_AUSENTE")
    return classificar_dia(data_local=hoje, descanso=descanso, tem_plano=tem_plano, atividades_do_dia=atividades_do_dia, revisoes=revisoes)
