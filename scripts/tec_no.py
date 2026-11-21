"""Nó da hierarquia do TEC (S16 T1; S16-R1, R2, R3, R5). Offline, função pura, falha fechada.

Recebe objetos Python já lidos (a Zapia traz a amostra a cada plano; ela NÃO é versionada, S16 P6) e devolve nós normalizados EM
MEMÓRIA. Nada é lido de arquivo, gravado, enviado ou consultado na rede. Não escolhe top 10 (isso é a T2) e não monta entrega (T3).

O que cada nó carrega (R1, R2, R5): cargos (324, 523 ou ambos), guia, bloco do edital (a matéria do TEC NÃO é o bloco de pontuação),
caderno de origem, matéria, **caminho inteiro** do nó (o título isolado não identifica), modalidade (1 = amostra exclusiva FAPEC;
2 = guias do TEC), origem (fonte, data, filtros), estado da amostra e os dois percentuais (da matéria e do caderno), cada um com
seu denominador. Percentual ou denominador que a fonte não trouxe fica **desconhecido** (None / "desconhecido"), nunca preenchido.

Regras de árvore (P1, R3): só nós terminais (folhas) entram em contagem; pai marcado como folha com filho presente, identidade
repetida e soma de folhas acima de 100% da matéria são recusados (indício de contagem dupla de pai e filho). O percentual é a
COMPOSIÇÃO DA AMOSTRA, nunca probabilidade de cobrança (P2).

Limites: heurístico no filtro de texto (reaproveita o da L1); não prova que a amostra veio do TEC nem que os números são os do guia.
"""
from __future__ import annotations

import re
from datetime import date

try:
    import platform_read_guard
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import platform_read_guard

VERSAO = "1.0"
CARGOS = frozenset({"324", "523"})
MODALIDADES = frozenset({1, 2})
ESTADOS = frozenset({"definitiva", "nao_definitiva", "instavel"})
MAX_NOS = 5000
MAX_NIVEIS = 8
MAX_TEXTO = 200
TOLERANCIA_SOMA = 1.0  # pontos percentuais: arredondamento do guia; acima disso há contagem dupla
CHAVES = frozenset({"cargos", "guia", "bloco", "caderno", "materia", "caminho", "modalidade", "origem", "estado_amostra", "folha",
                    "percentual_materia", "percentual_caderno"})
CHAVES_ORIGEM = frozenset({"fonte", "data", "filtros"})
CHAVES_PCT = frozenset({"valor", "denominador"})
_CONTROLE = re.compile(r"[\x00-\x1f\x7f<>]")
_DATA = re.compile(r"\d{4}-\d{2}-\d{2}")
DESCONHECIDO = "desconhecido"


class Recusa(Exception):
    """Recusa do conjunto inteiro: só código e, quando há, o índice do nó (nunca o texto)."""

    def __init__(self, codigo, indice=None):
        super().__init__(codigo)
        self.codigo, self.indice = codigo, indice


def _nao(codigo, indice=None):
    raise Recusa(codigo, indice)


def _texto(v, codigo, indice):
    if not isinstance(v, str):
        _nao(codigo, indice)
    t = v.strip()
    if not t or len(t) > MAX_TEXTO or _CONTROLE.search(t):
        _nao(codigo, indice)
    if platform_read_guard.classificar_texto(t) is not None:
        _nao("TEXTO_SUSPEITO", indice)
    return t


def _chaves(obj, permitidas, codigo, indice):
    if not isinstance(obj, dict) or not set(obj) <= permitidas or not all(isinstance(k, str) for k in obj):
        _nao(codigo, indice)


def _inteiro(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _pct(raw, rotulo, indice):
    """{valor, denominador} → valor float em [0, 100] ou None; denominador inteiro > 0 ou 'desconhecido'."""
    if raw is None:
        return {"valor": None, "denominador": DESCONHECIDO}
    _chaves(raw, CHAVES_PCT, f"{rotulo}_INVALIDO", indice)
    valor, den = raw.get("valor"), raw.get("denominador")
    if valor is not None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor != valor or not 0 <= valor <= 100:
            _nao(f"{rotulo}_FORA_DA_FAIXA", indice)
        valor = float(valor)
    if den is None:
        den = DESCONHECIDO
    elif not _inteiro(den) or den <= 0:
        _nao(f"{rotulo}_DENOMINADOR_INVALIDO", indice)
    return {"valor": valor, "denominador": den}


def _data(v, indice):
    if not isinstance(v, str) or not _DATA.fullmatch(v):
        _nao("DATA_INVALIDA", indice)
    try:
        date.fromisoformat(v)
    except ValueError:
        _nao("DATA_INVALIDA", indice)
    return v


def normalizar_no(raw, indice=None):
    """Valida UM nó e devolve a cópia normalizada. Recusa campo faltando ou sobrando, tipo errado e texto suspeito."""
    _chaves(raw, CHAVES, "CHAVE_FORA_DO_CONTRATO", indice)
    if not CHAVES - {"percentual_materia", "percentual_caderno"} <= set(raw):
        _nao("CAMPO_OBRIGATORIO_AUSENTE", indice)  # origem preservada (R1): sem cargo, guia, bloco, caderno ou caminho não entra
    cargos = raw["cargos"]
    if not isinstance(cargos, (list, tuple)) or not cargos or not set(cargos) <= CARGOS or len(set(cargos)) != len(cargos):
        _nao("CARGO_INVALIDO", indice)
    caminho = raw["caminho"]
    if not isinstance(caminho, (list, tuple)) or not 1 <= len(caminho) <= MAX_NIVEIS:
        _nao("CAMINHO_INVALIDO", indice)
    caminho = tuple(_texto(c, "CAMINHO_INVALIDO", indice) for c in caminho)
    materia = _texto(raw["materia"], "MATERIA_INVALIDA", indice)
    if caminho[0] != materia:
        _nao("CAMINHO_FORA_DA_MATERIA", indice)  # o caminho começa pela matéria do TEC
    if not _inteiro(raw["modalidade"]) or raw["modalidade"] not in MODALIDADES:
        _nao("MODALIDADE_INVALIDA", indice)
    if raw["estado_amostra"] not in ESTADOS:
        _nao("ESTADO_AMOSTRA_INVALIDO", indice)
    if not isinstance(raw["folha"], bool):
        _nao("FOLHA_INVALIDA", indice)
    origem = raw["origem"]
    _chaves(origem, CHAVES_ORIGEM, "ORIGEM_INVALIDA", indice)
    if set(origem) != CHAVES_ORIGEM:
        _nao("ORIGEM_INVALIDA", indice)
    return {
        "cargos": tuple(sorted(cargos)),
        "guia": _texto(raw["guia"], "GUIA_INVALIDO", indice),
        "bloco": _texto(raw["bloco"], "BLOCO_INVALIDO", indice),  # use "desconhecido": a matéria do TEC não é o bloco do edital
        "caderno": _texto(raw["caderno"], "CADERNO_INVALIDO", indice),
        "materia": materia,
        "caminho": caminho,
        "modalidade": raw["modalidade"],
        "origem": {"fonte": _texto(origem["fonte"], "ORIGEM_INVALIDA", indice), "data": _data(origem["data"], indice),
                   "filtros": _texto(origem["filtros"], "ORIGEM_INVALIDA", indice)},
        "estado_amostra": raw["estado_amostra"],
        "folha": raw["folha"],
        "percentual_materia": _pct(raw.get("percentual_materia"), "PERCENTUAL_MATERIA", indice),
        "percentual_caderno": _pct(raw.get("percentual_caderno"), "PERCENTUAL_CADERNO", indice),
    }


def chave(no):
    """Identidade do nó: o caminho INTEIRO dentro do caderno e da modalidade (R2). O título isolado não identifica."""
    return (no["cargos"], no["caderno"], no["modalidade"], no["caminho"])


def validar_conjunto(brutos):
    """Valida a lista inteira e devolve os nós normalizados. Recusa o conjunto todo ao primeiro problema (fecha por padrão)."""
    if not isinstance(brutos, (list, tuple)) or not brutos or len(brutos) > MAX_NOS:
        _nao("CONJUNTO_INVALIDO")
    nos = [normalizar_no(b, i) for i, b in enumerate(brutos)]
    vistos = {}
    for i, no in enumerate(nos):
        if chave(no) in vistos:
            _nao("NO_DUPLICADO", i)
        vistos[chave(no)] = i
    # pai e filho (P1, R3): um nó marcado folha não pode ter descendente no mesmo caderno e modalidade
    for i, no in enumerate(nos):
        if no["folha"]:
            for outro in nos:
                if (outro is not no and outro["caderno"] == no["caderno"] and outro["modalidade"] == no["modalidade"]
                        and len(outro["caminho"]) > len(no["caminho"]) and outro["caminho"][:len(no["caminho"])] == no["caminho"]
                        and set(outro["cargos"]) & set(no["cargos"])):
                    _nao("PAI_MARCADO_FOLHA", i)
    # contagem dupla: a soma das folhas de uma matéria não passa de 100% (composição da amostra)
    somas = {}
    for no in nos:
        v = no["percentual_materia"]["valor"]
        if no["folha"] and v is not None:
            k = (no["cargos"], no["caderno"], no["modalidade"], no["materia"])
            somas[k] = somas.get(k, 0.0) + v
    if any(s > 100 + TOLERANCIA_SOMA for s in somas.values()):
        _nao("SOMA_DE_FOLHAS_EXCEDE_100")
    return nos


def folhas(nos):
    """Só os nós terminais: pai e descendentes nunca se somam nem competem entre si (P1)."""
    return [n for n in nos if n["folha"]]


def caminho_texto(no):
    """Caminho inteiro legível (R2): níveis separados por ' > '."""
    return " > ".join(no["caminho"])
