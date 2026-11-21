"""Seleção do top 10 por matéria do TEC (S16 T2; S16-R4, R5, R6; regras P1 a P5, P7, P8). Função pura, offline, falha fechada.

Recebe nós brutos (a amostra que a Zapia traz a cada plano, NÃO versionada, P6), valida-os com `tec_no` e devolve um dicionário EM
MEMÓRIA. Não lê arquivo, não grava, não consulta rede e NÃO traz lista alguma embutida: o top 10 vem só dos percentuais fornecidos.

Regras aplicadas:
- só a modalidade 1 (amostra exclusiva FAPEC) decide a seleção; a modalidade 2 (guias do TEC) nunca entra no ranking (R4, P5);
- só nós terminais (folhas), sem somar pai e filho (P1); ranking pelo percentual da MATÉRIA, do maior para o menor;
- empate no 10º lugar: entram TODOS os empatados até o teto de 15 (P3); acima do teto devolve `DECISAO_DO_PROPRIETARIO` com os
  empatados e SEM lista, sem desempate inventado; a ordem de apresentação entre empatados (caminho, alfabética) não é desempate:
  eles têm a MESMA posição;
- matéria com menos de 10 folhas com percentual: lista as encontradas e marca `parcial` (P4); item sem percentual fica de fora e é
  declarado em `sem_percentual`, sem estimativa (P4); se NENHUM nó tem percentual, a geração é recusada (R4);
- amostra ausente, não definitiva (hoje os específicos do 523) ou instável (324 pequeno) → `PENDENCIA_ABERTA`, sem lista (R6, P7);
- correspondência com o guia do TEC só pelo mapa explícito `correspondencias` (caminho da modalidade 1 → caminho da modalidade 2);
  nunca por nome (P8): sem mapa o item sai "nao_avaliada"; com mapa e sem entrada, "sem correspondência".

O percentual é a composição da amostra, não incidência histórica da FAPEC nem chance de cair na prova (P2).
Limites: não prova que a amostra veio do TEC nem que os números são os do guia.
"""
from __future__ import annotations

try:
    import tec_no
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import tec_no

VERSAO = "1.0"
TOP = 10
TETO = 15
AVISO = ("Percentual é composição da amostra (questões do nó sobre o total da matéria no caderno amostral); "
         "não é incidência histórica da FAPEC nem chance de cair na prova. O top 10 não exclui conteúdo do edital.")
SEM_CORRESPONDENCIA = "sem correspondência"
NAO_AVALIADA = "nao_avaliada"


def _saida(status, codigo, materia, cargo, **extra):
    out = {"status": status, "codigo": codigo, "materia": materia, "cargo": cargo, "itens": [], "parcial": False,
           "sem_percentual": [], "aviso": AVISO}
    out.update(extra)
    return out


def _item(no, posicao, guia_tec):
    return {"cargo_pedido": None, "cargos": no["cargos"], "guia": no["guia"], "bloco": no["bloco"], "caderno": no["caderno"],
            "materia": no["materia"], "caminho": no["caminho"], "posicao": posicao, "modalidade": no["modalidade"],
            "percentual_materia": dict(no["percentual_materia"]), "percentual_caderno": dict(no["percentual_caderno"]),
            "fonte": no["origem"]["fonte"], "data": no["origem"]["data"], "filtros": no["origem"]["filtros"],
            "estado_amostra": no["estado_amostra"], "guia_tec": guia_tec}


def _mapa(correspondencias):
    if correspondencias is None:
        return None
    if not isinstance(correspondencias, dict):
        raise tec_no.Recusa("CORRESPONDENCIAS_INVALIDAS")
    mapa = {}
    for k, v in correspondencias.items():
        if not (isinstance(k, (tuple, list)) and isinstance(v, (tuple, list)) and k and v
                and all(isinstance(x, str) for x in list(k) + list(v))):
            raise tec_no.Recusa("CORRESPONDENCIAS_INVALIDAS")
        mapa[tuple(k)] = tuple(v)
    return mapa


def selecionar_top10(brutos, *, materia, cargo, correspondencias=None):
    """Devolve {status: LISTA | PENDENCIA_ABERTA | DECISAO_DO_PROPRIETARIO | RECUSADA, codigo, itens, ...}. Nunca levanta por dado ruim."""
    if cargo not in tec_no.CARGOS:
        return _saida("RECUSADA", "CARGO_INVALIDO", materia, cargo)
    if not isinstance(materia, str) or not materia.strip():
        return _saida("RECUSADA", "MATERIA_INVALIDA", materia, cargo)
    try:
        nos = tec_no.validar_conjunto(brutos)
        mapa = _mapa(correspondencias)
    except tec_no.Recusa as e:
        return _saida("RECUSADA", e.codigo, materia, cargo)
    materia = materia.strip()

    do_cargo = [n for n in nos if cargo in n["cargos"] and n["materia"] == materia]
    m1 = [n for n in tec_no.folhas(do_cargo) if n["modalidade"] == 1]  # a modalidade 2 só aprofunda, nunca ranqueia (R4)
    if not m1:
        return _saida("PENDENCIA_ABERTA", "AMOSTRA_AUSENTE", materia, cargo)
    if any(n["estado_amostra"] != "definitiva" for n in m1):
        return _saida("PENDENCIA_ABERTA", "AMOSTRA_NAO_DEFINITIVA", materia, cargo)  # P7: sem lista final

    com = [n for n in m1 if n["percentual_materia"]["valor"] is not None]
    sem = [tec_no.caminho_texto(n) for n in m1 if n["percentual_materia"]["valor"] is None]  # P4: fora, sem estimativa
    if not com:
        return _saida("RECUSADA", "PERCENTUAL_AUSENTE", materia, cargo, sem_percentual=sem)

    com.sort(key=lambda n: (-n["percentual_materia"]["valor"], n["caminho"]))
    if len(com) > TOP:
        corte = com[TOP - 1]["percentual_materia"]["valor"]
        escolhidos = [n for n in com if n["percentual_materia"]["valor"] >= corte]
        if len(escolhidos) > TETO:
            empatados = [n for n in escolhidos if n["percentual_materia"]["valor"] == corte]
            return _saida("DECISAO_DO_PROPRIETARIO", "EMPATE_ACIMA_DO_TETO", materia, cargo, sem_percentual=sem,
                          empatados=[tec_no.caminho_texto(n) for n in empatados], valor_do_empate=corte)
    else:
        escolhidos = com

    # posição de competição: empatados repartem a MESMA posição (1, 2, 2, 4), sem desempate inventado
    valores = [n["percentual_materia"]["valor"] for n in escolhidos]
    itens = []
    for n, v in zip(escolhidos, valores):
        posicao = 1 + sum(1 for x in valores if x > v)
        if mapa is None:
            guia_tec = NAO_AVALIADA
        else:
            alvo = mapa.get(n["caminho"])
            existe = alvo is not None and any(o["modalidade"] == 2 and o["caminho"] == alvo and cargo in o["cargos"] for o in nos)
            guia_tec = " > ".join(alvo) if existe else SEM_CORRESPONDENCIA
        it = _item(n, posicao, guia_tec)
        it["cargo_pedido"] = cargo
        itens.append(it)
    return _saida("LISTA", "OK", materia, cargo, itens=itens, parcial=len(com) < TOP or bool(sem), sem_percentual=sem)
