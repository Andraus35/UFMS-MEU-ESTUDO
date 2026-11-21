"""Entrega diária e recorte do plano ao top 10 (S16 T3; S16-R7, R8, R9, R14; decisões C1 e C2). Offline, função pura, falha fechada.

Recebe um item já selecionado pela T2 (`top10_materia`) e as decisões do TUTOR (material, atividade, quantidade de questões,
filtros, objetivo) e devolve a entrega do dia EM MEMÓRIA. Não decide pedagogia, não lê plataforma, não grava, não envia, não usa rede
e não impõe cronograma: indica UM assunto do dia dentre os selecionados (C1); o plano determinístico do Método 4.2 segue como insumo.

R8: a entrega tem cargo, matéria, caminho inteiro, posição e percentual QUANDO VERIFICADOS (senão "não verificado"), material,
atividade, quantidade (definida pelo Tutor), filtros e objetivo. R7: sem filtros registrados a entrega é recusada e o texto não
afirma disponibilidade de questões. R9: só cita como recurso o que está marcado como verificado para aquele nó (pdf, videoaula,
mapa mental, questões), sem presumir. R3/P2: o percentual é composição da amostra; a palavra "probabilidade" é recusada.

Recorte (C2, R4, R14): o plano fica só com os nós do top 10; o restante vira LACUNA registrada (com cargo e fonte), nunca entra no plano
em silêncio; item fora do top 10 só entra com decisão registrada do proprietário; matéria sem lista definitiva (PENDENCIA_ABERTA etc.)
vai a `pendentes`, sem decidir. O casamento é pelo caminho EXATO, nunca por nome parecido.

Limites: heurístico no filtro de texto (reaproveita o da L1); não prova que o recurso nem a quantidade de questões existam na plataforma.
"""
from __future__ import annotations

import re
from datetime import date

try:
    import platform_read_guard
    import tec_no
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import platform_read_guard, tec_no

VERSAO = "1.0"
RECURSOS = ("pdf", "videoaula", "mapa_mental", "questoes")
NAO_VERIFICADO = "não verificado"
MAX_QUESTOES = 500
MAX_TEXTO = 400
CAMPOS_ITEM = ("cargo_pedido", "materia", "caminho", "posicao", "modalidade", "percentual_materia", "estado_amostra")
_CONTROLE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f<>]")
# afirmação que a entrega não pode fazer (R3, R7): chance de cobrança e disponibilidade de questões
_PROIBIDO = re.compile(r"probabilidad|chance de cair|garant\w+|disponibilidade confirmada|\bdispon[ií]ve(?:l|is)\b", re.I)
AVISO = ("Percentual é composição da amostra, não incidência histórica da FAPEC nem chance de cair na prova; "
         "a disponibilidade de questões e de recursos não foi presumida.")


class Recusa(Exception):
    def __init__(self, codigo):
        super().__init__(codigo)
        self.codigo = codigo


def _nao(codigo):
    raise Recusa(codigo)


def _texto(v, codigo):
    if not isinstance(v, str):
        _nao(codigo)
    t = v.strip()
    if not t or len(t) > MAX_TEXTO or _CONTROLE.search(t):
        _nao(codigo)
    if _PROIBIDO.search(t):
        _nao("AFIRMACAO_PROIBIDA")
    if platform_read_guard.classificar_texto(t) is not None:
        _nao("TEXTO_SUSPEITO")
    return t


def _dia(v):
    if not isinstance(v, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        _nao("DIA_INVALIDO")
    try:
        date.fromisoformat(v)
    except ValueError:
        _nao("DIA_INVALIDO")
    return v


def _item(item):
    if not isinstance(item, dict) or not all(c in item for c in CAMPOS_ITEM):
        _nao("ITEM_INCOMPLETO")
    if item["modalidade"] != 1 or item["estado_amostra"] != "definitiva":
        _nao("ITEM_SEM_LISTA_DEFINITIVA")  # só a modalidade 1 e amostra definitiva geram entrega
    if item["cargo_pedido"] not in tec_no.CARGOS:
        _nao("CARGO_INVALIDO")
    pos = item["posicao"]
    if isinstance(pos, bool) or not isinstance(pos, int) or pos < 1:
        _nao("POSICAO_INVALIDA")
    cam = item["caminho"]
    if not isinstance(cam, (tuple, list)) or not cam or not all(isinstance(c, str) and c.strip() for c in cam):
        _nao("CAMINHO_INVALIDO")
    return item


def montar_entrega(item, *, dia, material, atividade, quantidade_questoes, filtros, objetivo, verificado=False, recursos_verificados=()):
    """Devolve {"estado": "ENTREGA", ...} ou {"estado": "RECUSADA", "codigo": ...}. Nunca levanta por dado ruim."""
    try:
        return _montar(item, dia, material, atividade, quantidade_questoes, filtros, objetivo, verificado, recursos_verificados)
    except Recusa as e:
        return {"estado": "RECUSADA", "codigo": e.codigo}
    except tec_no.Recusa as e:  # pragma: no cover - defesa
        return {"estado": "RECUSADA", "codigo": e.codigo}


def _montar(item, dia, material, atividade, quantidade, filtros, objetivo, verificado, recursos):
    item = _item(item)
    if not isinstance(verificado, bool):
        _nao("VERIFICADO_INVALIDO")
    if isinstance(quantidade, bool) or not isinstance(quantidade, int) or not 1 <= quantidade <= MAX_QUESTOES:
        _nao("QUANTIDADE_INVALIDA")  # a quantidade é decisão do Tutor; o módulo só recusa o absurdo
    if not isinstance(recursos, (list, tuple, set, frozenset)) or not set(recursos) <= set(RECURSOS):
        _nao("RECURSO_INVALIDO")
    valor = item["percentual_materia"].get("valor") if isinstance(item["percentual_materia"], dict) else None
    ok = verificado and valor is not None
    return {
        "estado": "ENTREGA",
        "dia": _dia(dia),
        "cargo": item["cargo_pedido"],
        "materia": _texto(item["materia"], "MATERIA_INVALIDA"),
        "caminho": " > ".join(_texto(c, "CAMINHO_INVALIDO") for c in item["caminho"]),
        "posicao": item["posicao"] if ok else NAO_VERIFICADO,
        "percentual": f"{valor:g}% da matéria na amostra" if ok else NAO_VERIFICADO,
        "material_teorico": _texto(material, "MATERIAL_INVALIDO"),
        "atividade": _texto(atividade, "ATIVIDADE_INVALIDA"),
        "quantidade_questoes": quantidade,
        "filtros": _texto(filtros, "FILTROS_AUSENTES"),  # R7: sem filtros registrados, sem entrega
        "objetivo": _texto(objetivo, "OBJETIVO_INVALIDO"),
        "recursos_verificados": [r for r in RECURSOS if r in set(recursos)],
        "aviso": AVISO,
    }


def texto_da_entrega(e):
    """Texto simples para o Tutor entregar. Só cita recurso marcado como verificado (R9); não afirma disponibilidade (R7)."""
    if not isinstance(e, dict) or e.get("estado") != "ENTREGA":
        return None
    nomes = {"pdf": "PDF do assunto", "videoaula": "videoaula", "mapa_mental": "mapa mental", "questoes": "caderno de questões"}
    recursos = ", ".join(nomes[r] for r in e["recursos_verificados"]) or "nenhum recurso verificado para este nó"
    return "\n".join([
        f"Estudo de {e['dia']} (cargo {e['cargo']})",
        f"Matéria: {e['materia']}",
        f"Caminho: {e['caminho']}",
        f"Posição: {e['posicao']} · Percentual: {e['percentual']}",
        f"Material: {e['material_teorico']}",
        f"Atividade: {e['atividade']} · {e['quantidade_questoes']} questões (definidas pelo Tutor; a existência no acervo não foi verificada)",
        f"Filtros: {e['filtros']}",
        f"Objetivo: {e['objetivo']}",
        f"Recursos verificados: {recursos}",
        e["aviso"],
    ])


def _cand(c):
    if (not isinstance(c, dict) or c.get("cargo") not in tec_no.CARGOS or not isinstance(c.get("materia"), str) or not c["materia"].strip()
            or not isinstance(c.get("caminho"), (tuple, list)) or not c["caminho"]
            or not all(isinstance(x, str) and x.strip() for x in c["caminho"])
            or not isinstance(c.get("fonte"), str) or not c["fonte"].strip()):
        _nao("CANDIDATO_INVALIDO")  # sem cargo, matéria, caminho ou fonte não há como registrar nem lacuna (R14)
    return {"cargo": c["cargo"], "materia": c["materia"].strip(), "caminho": tuple(c["caminho"]), "fonte": c["fonte"].strip()}


def _excecao(x):
    if (not isinstance(x, dict) or x.get("autor") != "proprietario" or not isinstance(x.get("registrado_em"), str)
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", x["registrado_em"])):
        _nao("EXCECAO_INVALIDA")
    c = _cand({**x, "fonte": "decisao do proprietario"})
    try:
        date.fromisoformat(x["registrado_em"])
    except ValueError:
        _nao("EXCECAO_INVALIDA")
    return {"cargo": c["cargo"], "materia": c["materia"], "caminho": c["caminho"], "registrado_em": x["registrado_em"]}


def recortar_plano(candidatos, resultados, *, excecoes=()):
    """Restringe os candidatos do plano ao top 10 (C2). `resultados` são as saídas da T2; `excecoes` são decisões registradas."""
    try:
        if not isinstance(candidatos, (list, tuple)) or not isinstance(resultados, (list, tuple)) or not isinstance(excecoes, (list, tuple)):
            _nao("ENTRADA_INVALIDA")
        cands = [_cand(c) for c in candidatos]
        excs = {(e["cargo"], e["materia"], e["caminho"]): e for e in (_excecao(x) for x in excecoes)}
        listas, pend = {}, {}
        for r in resultados:
            if not isinstance(r, dict) or "status" not in r or "cargo" not in r or "materia" not in r:
                _nao("RESULTADO_INVALIDO")
            chave = (r["cargo"], r["materia"])
            if r["status"] == "LISTA":
                listas[chave] = {tuple(i["caminho"]): i["posicao"] for i in r["itens"]}
            else:
                pend[chave] = r.get("codigo", "DESCONHECIDO")
    except Recusa as e:
        return {"estado": "RECUSADA", "codigo": e.codigo}
    no_plano, lacunas, pendentes = [], [], []
    for c in cands:
        chave = (c["cargo"], c["materia"])
        if chave in listas and c["caminho"] in listas[chave]:
            no_plano.append({**c, "posicao": listas[chave][c["caminho"]], "motivo": "top_10"})
        elif (c["cargo"], c["materia"], c["caminho"]) in excs:
            no_plano.append({**c, "posicao": None, "motivo": "decisao_do_proprietario"})
        elif chave in listas:
            lacunas.append(c)  # fora do top 10: lacuna registrada, não entra no plano (R14)
        else:
            pendentes.append({"cargo": c["cargo"], "materia": c["materia"], "caminho": c["caminho"],
                              "codigo": pend.get(chave, "SEM_RESULTADO")})  # sem lista definitiva não se decide
    return {"estado": "RECORTE", "no_plano": no_plano, "lacunas": lacunas, "pendentes": pendentes, "aviso": AVISO}
