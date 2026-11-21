"""Chave de idempotência única da rotina e vínculo LEMBRETE↔COMANDO (GAP-A2, GA-4 e GA-5).

GA-5 (divergência de 21/11/2026): a S8-R1 usava `rotina-AAAA-MM-DD-briefing` e `rotina-AAAA-MM-DD-lembrete2`; a S8-R4 e a S15-R6 usam
`rotina-AAAA-MM-DD-<tipo>-<id>`. **Formato único (proposta, a confirmar pelo proprietário):** o da S15-R6, com `tipo` em
`TIPOS` e `id` obrigatório (`briefing` usa `dia`; `lembrete2` usa o `atividade_id`). O formato antigo (sem id) é recusado com código próprio.
A data da chave é a **data local** de `America/Campo_Grande` (UTC−4, sem horário de verão desde 2019, S15-R2, proposta) do relógio injetado.
Duas janelas distintas: a de **assinatura** (120 s, `config/agent_command_schema.json`, vale para todo comando) e a de **dia** (a chave de
rotina só vale no dia local do relógio injetado; chave de outro dia é recusada).

GA-4: o LEMBRETE passa a levar uma **lista** de atividades pendentes; `hash_lembrete` liga o texto e a lista ao COMANDO `criar_lembrete`,
que carrega o hash em `params.lembrete_sha256`.

Função pura: sem rede, arquivo, relógio próprio nem modelo. Não prova que a Zapia use o validador.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone

PREFIXO = "rotina-"
TIPOS = ("briefing", "lembrete2")
FUSO = "America/Campo_Grande"
FUSO_FIXO = timezone(timedelta(hours=-4), "America/Campo_Grande")  # sem horário de verão desde 2019; evita depender do tzdata
JANELA_ASSINATURA_SEGUNDOS = 120
MAX_ATIVIDADES = 5
_ID = r"[A-Za-z0-9._-]{1,40}"
ID_ATIVIDADE = re.compile(_ID)
_CHAVE = re.compile(r"^rotina-(\d{4}-\d{2}-\d{2})-(" + "|".join(TIPOS) + r")-(" + _ID + r")$")
_ANTIGA = re.compile(r"^rotina-\d{4}-\d{2}-\d{2}-(" + "|".join(TIPOS) + r")$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def montar_chave(data_local, tipo: str, ident: str) -> str:
    """Monta a chave no formato único. Levanta ValueError se algum campo não couber."""
    chave = f"{PREFIXO}{data_local if isinstance(data_local, str) else data_local.isoformat()}-{tipo}-{ident}"
    if analisar_chave(chave) is None:
        raise ValueError("chave fora do formato único")
    return chave


def analisar_chave(chave) -> dict | None:
    """Campos da chave no formato único, ou None (data impossível, tipo desconhecido, id vazio ou fora do conjunto)."""
    if not isinstance(chave, str):
        return None
    m = _CHAVE.fullmatch(chave)
    if not m:
        return None
    try:
        date.fromisoformat(m.group(1))
    except ValueError:
        return None
    return {"data": m.group(1), "tipo": m.group(2), "id": m.group(3)}


def data_local(agora_utc) -> str | None:
    """Data de calendário em Campo Grande do instante UTC injetado; None se o relógio não tiver fuso."""
    if not isinstance(agora_utc, datetime) or agora_utc.tzinfo is None:
        return None
    return agora_utc.astimezone(FUSO_FIXO).date().isoformat()


def eh_chave_de_rotina(chave) -> bool:
    return isinstance(chave, str) and chave.startswith(PREFIXO)


def conferir_chave(chave, agora_utc) -> str | None:
    """None se a chave de rotina está no formato único e é do dia local do relógio; senão o código da recusa."""
    hoje = data_local(agora_utc)
    if hoje is None:
        return "RELOGIO_AUSENTE"
    if isinstance(chave, str) and _ANTIGA.fullmatch(chave):
        return "CHAVE_ROTINA_FORMATO_ANTIGO"
    campos = analisar_chave(chave)
    if campos is None:
        return "CHAVE_ROTINA_INVALIDA"
    if campos["data"] != hoje:
        return "CHAVE_ROTINA_DE_OUTRO_DIA"
    return None


def conferir_chave_do_comando(operation, chave, agora_utc) -> str | None:
    """Regra única do validador e da caixa: `criar_lembrete` exige chave de rotina; toda chave `rotina-` segue o formato único e é do dia."""
    if operation == "criar_lembrete" and not eh_chave_de_rotina(chave):
        return "CHAVE_ROTINA_OBRIGATORIA"
    if eh_chave_de_rotina(chave):
        return conferir_chave(chave, agora_utc)
    return None


def lista_de_atividades_valida(ids) -> bool:
    """Lista de 1 a MAX_ATIVIDADES identificadores textuais, sem repetição."""
    return (isinstance(ids, list) and 1 <= len(ids) <= MAX_ATIVIDADES and all(isinstance(i, str) and ID_ATIVIDADE.fullmatch(i) for i in ids)
            and len(set(ids)) == len(ids))


def hash_lembrete(corpo: str, atividade_ids) -> str:
    """SHA-256 do texto do LEMBRETE e do conjunto de atividades (ordem irrelevante); liga o envelope ao COMANDO `criar_lembrete`."""
    bruto = json.dumps({"corpo": corpo, "atividade_ids": sorted(atividade_ids)}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(bruto.encode("utf-8")).hexdigest()
