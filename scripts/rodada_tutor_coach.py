"""E51: rodada Tutor–Coach, OFFLINE e SINTÉTICA. Sem rede, sem credencial, sem dado real do estudante.

Modelo aprovado (28/11/2026): um ORQUESTRADOR único (única escrita) chama Tutor e Coach como subagentes em FASES FIXAS (Tutor, depois Coach), com pacote de
entrada fechado e saída de esquema fechado, validadas aqui em código. Nenhuma conversa livre entre os papéis: o que o Coach "diz" ao Tutor é um pedido de
ajuste estruturado (S3-R6); o que qualquer papel quer da Zapia (TEC, Notebook) é um pedido do canal de engenharia (E49), validado por `canal_engenharia`.
Regras de papel: o Coach NÃO pede operação do Notebook (não redige prompts, COACH.md); o Tutor decide conteúdo e plano. Texto livre é curto e passa pelos
mesmos filtros do registro de passagem (segredo, dado pessoal, texto de questão, URL, instrução embutida, resultado pessoal).
Este módulo é função pura: a gravação da rodada em `entrada` é do orquestrador.
"""
from __future__ import annotations

import hashlib
import json
import re

try:
    import canal_engenharia as ce
    import tutor_coach_handoff as th
except ModuleNotFoundError:  # uso como pacote
    from scripts import canal_engenharia as ce
    from scripts import tutor_coach_handoff as th

PAPEIS = ("tutor", "coach")
FASES = ("tutor", "coach")  # ordem fixa: o Coach só roda depois do Tutor e recebe o hash da saída dele
TIPOS = {
    "tutor": ("plano", "pedido_api", "sem_acao"),
    "coach": ("organizacao", "pedido_ajuste", "pedido_api", "sem_acao"),
}
OPERACOES_DO_PAPEL = {
    "tutor": tuple(ce.OPERACOES),  # o Tutor acessa o Notebook e a estrutura do TEC
    "coach": tuple(o for o in ce.OPERACOES if o.startswith("tec_")),  # o Coach não redige nem pede Notebook
}
ID = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")
ID_RODADA = re.compile(r"^rodada-[0-9]{4}$")
MAX_REFS = 20
CAMPOS_PACOTE = {"papel", "objetivo", "referencias", "saida_esperada", "tutor_sha256"}


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _refs_ok(refs) -> bool:
    return isinstance(refs, list) and len(refs) <= MAX_REFS and all(isinstance(r, str) and ID.fullmatch(r) and not th.agent_commands.texto_de_questao(r) for r in refs)


def montar_pacote(papel, objetivo, referencias, saida_esperada, tutor_sha256=None) -> dict:
    """Pacote de entrada FECHADO de um subagente. Levanta ValueError em qualquer desvio. O Coach exige o hash da saída do Tutor (ordem de fases)."""
    if papel not in PAPEIS:
        raise ValueError("papel fora da lista")
    if saida_esperada not in TIPOS[papel]:
        raise ValueError("tipo de saída não permitido para o papel")
    if not _refs_ok(referencias):
        raise ValueError("referências inválidas (só identificadores, até 20)")
    motivo = th._texto_livre_ok(objetivo, sem_resultado_pessoal=True)
    if motivo:
        raise ValueError("objetivo recusado: " + motivo)
    if papel == "coach" and not (isinstance(tutor_sha256, str) and re.fullmatch(r"[0-9a-f]{64}", tutor_sha256)):
        raise ValueError("o Coach só roda depois do Tutor: falta o hash da saída dele")
    if papel == "tutor" and tutor_sha256 is not None:
        raise ValueError("o Tutor é a primeira fase e não recebe hash")
    p = {"papel": papel, "objetivo": objetivo, "referencias": list(referencias), "saida_esperada": saida_esperada, "tutor_sha256": tutor_sha256}
    return {**p, "pacote_sha256": _sha(p)}


def validar_saida(papel, saida, tipo_esperado=None) -> tuple:
    """(True, None) ou (False, codigo). A saída é DADO do subagente: formato fechado, texto curto e limpo, pedido de API só de operação do canal permitida ao papel."""
    if papel not in PAPEIS:
        return False, "PAPEL"
    if not isinstance(saida, dict) or saida.get("tipo") not in TIPOS[papel]:
        return False, "TIPO"
    if tipo_esperado and saida["tipo"] != tipo_esperado:
        return False, "TIPO_DIFERENTE_DO_PEDIDO"
    tipo = saida["tipo"]
    campos = {"tipo", "resumo"} | ({"refs"} if tipo in ("plano", "organizacao") else set()) | ({"pedido"} if tipo == "pedido_api" else set()) | ({"topico"} if tipo == "pedido_ajuste" else set())
    if set(saida) != campos:
        return False, "CAMPOS"
    if th._texto_livre_ok(saida["resumo"]):
        return False, "RESUMO"
    if "refs" in saida and not _refs_ok(saida["refs"]):
        return False, "REFS"
    if tipo == "pedido_ajuste" and saida["topico"] not in th._topicos():
        return False, "TOPICO"
    if tipo == "pedido_api":
        ped = saida["pedido"]
        if not isinstance(ped, dict) or set(ped) != {"operacao", "params"} or ped["operacao"] not in OPERACOES_DO_PAPEL[papel]:
            return False, "OPERACAO_NAO_PERMITIDA_AO_PAPEL"
        try:
            ce.montar_pedido("eng-0000", ped["operacao"], ped["params"], "")
        except ValueError:
            return False, "PEDIDO_API_INVALIDO"
    return True, None


def rodada(id_rodada, saida_tutor, saida_coach, ids_pedidos=(), usados=()) -> dict:
    """Monta o registro da rodada a partir das duas saídas JÁ produzidas pelos subagentes. Levanta ValueError se algo violar o contrato.
    `ids_pedidos`: ids `eng-NNNN` novos, um por `pedido_api` (do Tutor primeiro, depois do Coach); `usados`: ids que já existem no canal."""
    if not isinstance(id_rodada, str) or not ID_RODADA.fullmatch(id_rodada):
        raise ValueError("id de rodada inválido")
    for papel, s in (("tutor", saida_tutor), ("coach", saida_coach)):
        ok, cod = validar_saida(papel, s)
        if not ok:
            raise ValueError(f"saída do {papel} recusada: {cod}")
    pedidos_api = [(p, s["pedido"]) for p, s in (("tutor", saida_tutor), ("coach", saida_coach)) if s["tipo"] == "pedido_api"]
    ids = list(ids_pedidos)
    if len(ids) != len(pedidos_api) or len(set(ids)) != len(ids) or set(ids) & set(usados):
        raise ValueError("ids de pedidos ausentes, repetidos ou já usados")
    emitidos = []
    for i, (papel, ped) in zip(ids, pedidos_api):
        emitidos.append({"de": papel, "pedido": ce.montar_pedido(i, ped["operacao"], ped["params"], f"Pedido do {papel} na {id_rodada}.")})
    tutor_sha = _sha(saida_tutor)
    reg = {"id": id_rodada, "tutor": {"saida": saida_tutor, "saida_sha256": tutor_sha}, "coach": {"saida": saida_coach, "saida_sha256": _sha(saida_coach), "viu_tutor_sha256": tutor_sha},
           "pedidos": emitidos, "sintetica": True}
    return {**reg, "rodada_sha256": _sha(reg)}
