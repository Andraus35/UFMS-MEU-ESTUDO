"""Derivado PAGINADO de um livro e prova de leitura por página (GAP-E, GE-1; S18-R14). Função pura: sem rede, arquivo, relógio nem escrita.

Problema (21/11/2026): o Coach não leu as p. 148 a 153 do Manual do Imparável (o conector do Drive truncou a leitura) e não havia como PROVAR
o que foi aberto nem validar uma citação por página. Aqui o PÚBLICO guarda só o que não é texto do livro: um MANIFESTO por página
(número, SHA-256 do texto normalizado, contagem de palavras). O texto integral e o derivado paginado ficam no ambiente PRIVADO do proprietário
(direito autoral, decisão de 21/11/2026); `montar_manifesto` roda onde o texto está, e só o manifesto sai de lá.
- `prova_de_leitura`: uma página só conta como lida se o texto aberto bate com o hash do manifesto (página truncada ou alterada não conta).
- `conferir_citacao`: citação de até 25 palavras, literal na página aberta e conferida pelo hash; devolve a página.
- `afirmar_leitura`: só se afirma ter lido o que foi aberto.
- `suspeitas_de_truncamento`: sequência de páginas quase vazias (o sintoma do conector).
Limites: não lê o Manual, não prova que a página seja fiel ao livro impresso (o derivado é feito pelo proprietário) nem que o Coach compreendeu.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata

MAX_PALAVRAS_CITACAO = 25
MIN_PALAVRAS_CITACAO = 2
MIN_PALAVRAS_PAGINA = 20  # abaixo disso a página é "quase vazia" para a suspeita de truncamento
MIN_SEQUENCIA_TRUNCADA = 2
MAX_PALAVRAS_PAGINA = 3000
TOPO = frozenset({"fonte", "edicao", "total_paginas", "paginas"})
PAGINA = frozenset({"pagina", "sha256", "palavras"})
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def normalizar_pagina(texto: str) -> str:
    """Espaços e quebras de linha repetidos viram um espaço; as pontas saem. NFC, para o acento não mudar o hash."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", texto)).strip()


def hash_pagina(texto: str) -> str:
    return hashlib.sha256(normalizar_pagina(texto).encode("utf-8")).hexdigest()


def _inteiro(v) -> bool:
    return type(v) is int


def montar_manifesto(textos: dict, fonte: str, edicao: str) -> dict:
    """Roda no ambiente PRIVADO, onde está o texto. `textos`: {página: texto}, páginas de 1 a N sem lacuna. O manifesto NÃO leva texto."""
    if not isinstance(textos, dict) or not textos or not all(_inteiro(p) and isinstance(t, str) for p, t in textos.items()):
        raise ValueError("textos deve ser {pagina:int, texto:str} não vazio")
    paginas = [{"pagina": p, "sha256": hash_pagina(textos[p]), "palavras": len(normalizar_pagina(textos[p]).split())} for p in sorted(textos)]
    return {"fonte": fonte, "edicao": edicao, "total_paginas": len(paginas), "paginas": paginas}


def validar_manifesto(m) -> list[str]:
    """Lista de problemas (vazia se íntegro)."""
    if not isinstance(m, dict):
        return ["manifesto_nao_objeto"]
    problemas = []
    if set(m) != TOPO:
        problemas.append("campos_do_manifesto_fora_da_lista")
        if not TOPO <= set(m):
            return problemas
    if not (isinstance(m["fonte"], str) and m["fonte"].strip() and isinstance(m["edicao"], str) and m["edicao"].strip()):
        problemas.append("fonte_ou_edicao_invalida")
    paginas = m["paginas"]
    if not isinstance(paginas, list) or not paginas:
        return problemas + ["paginas_invalidas"]
    numeros = []
    for p in paginas:
        if not isinstance(p, dict) or set(p) != PAGINA:
            problemas.append("pagina_fora_da_lista_fechada")
            continue
        if not (_inteiro(p["pagina"]) and p["pagina"] >= 1):
            problemas.append("numero_de_pagina_invalido")
            continue
        numeros.append(p["pagina"])
        if not (isinstance(p["sha256"], str) and _HEX64.fullmatch(p["sha256"])):
            problemas.append("hash_invalido")
        if not (_inteiro(p["palavras"]) and 0 <= p["palavras"] <= MAX_PALAVRAS_PAGINA):
            problemas.append("palavras_invalidas")
    if len(set(numeros)) != len(numeros):
        problemas.append("pagina_repetida")
    if numeros and sorted(set(numeros)) != list(range(1, max(numeros) + 1)):
        problemas.append("lacuna_de_pagina")
    if m["total_paginas"] != len(paginas) or not _inteiro(m["total_paginas"]):
        problemas.append("total_diverge_das_paginas")
    return sorted(set(problemas))


def suspeitas_de_truncamento(m) -> list[int]:
    """Páginas de sequências (≥2 seguidas) com menos de 20 palavras: o sintoma de um conector que devolveu só a ficha e o sumário."""
    if validar_manifesto(m):
        return []
    curtas = sorted(p["pagina"] for p in m["paginas"] if p["palavras"] < MIN_PALAVRAS_PAGINA)
    saida, corrente = [], []
    for n in curtas:
        if corrente and n == corrente[-1] + 1:
            corrente.append(n)
        else:
            if len(corrente) >= MIN_SEQUENCIA_TRUNCADA:
                saida += corrente
            corrente = [n]
    if len(corrente) >= MIN_SEQUENCIA_TRUNCADA:
        saida += corrente
    return saida


def _por_numero(m) -> dict:
    return {p["pagina"]: p for p in m["paginas"]}


def prova_de_leitura(m, abertas, exigidas) -> dict:
    """Uma página só conta como lida se o texto aberto bate com o hash do manifesto. `abertas`: {página: texto}; `exigidas`: lista de páginas."""
    r = {"ok": False, "faltando": [], "divergentes": [], "fora_do_manifesto": [], "problemas": []}
    problemas = validar_manifesto(m)
    if problemas:
        r["problemas"] = problemas
        return r
    if not (isinstance(exigidas, list) and exigidas and all(_inteiro(p) and p >= 1 for p in exigidas)) or not isinstance(abertas, dict):
        r["problemas"] = ["pedido_invalido"]
        return r
    paginas = _por_numero(m)
    for p in sorted(set(exigidas)):
        if p not in paginas:
            r["fora_do_manifesto"].append(p)
        elif p not in abertas or not isinstance(abertas[p], str):
            r["faltando"].append(p)
        elif hash_pagina(abertas[p]) != paginas[p]["sha256"]:
            r["divergentes"].append(p)  # truncada, alterada ou de outra edição
    r["ok"] = not (r["faltando"] or r["divergentes"] or r["fora_do_manifesto"])
    return r


def afirmar_leitura(abertas, afirmadas) -> list[int]:
    """Páginas que o Coach afirma ter lido SEM tê-las aberto (devem ser retiradas da afirmação)."""
    abertas = set(abertas)
    return sorted(p for p in afirmadas if p not in abertas)


def _palavras(texto: str) -> list[str]:
    return normalizar_pagina(texto).split()


def conferir_citacao(m, pagina, texto_da_pagina, citacao) -> dict:
    """Citação de 2 a 25 palavras, literal na página aberta, com a página conferida pelo hash do manifesto."""
    def r(ok, codigo=None):
        return {"ok": ok, "codigo": codigo, "pagina": pagina if ok else None}

    if validar_manifesto(m):
        return r(False, "MANIFESTO_INVALIDO")
    item = _por_numero(m).get(pagina) if _inteiro(pagina) else None
    if item is None:
        return r(False, "PAGINA_FORA_DO_MANIFESTO")
    if not isinstance(texto_da_pagina, str) or hash_pagina(texto_da_pagina) != item["sha256"]:
        return r(False, "PAGINA_DIVERGE_DO_MANIFESTO")
    if not isinstance(citacao, str) or not citacao.strip():
        return r(False, "CITACAO_VAZIA")
    n = len(_palavras(citacao))
    if n > MAX_PALAVRAS_CITACAO:
        return r(False, "CITACAO_ACIMA_DE_25_PALAVRAS")
    if n < MIN_PALAVRAS_CITACAO:
        return r(False, "CITACAO_CURTA_DEMAIS")
    if normalizar_pagina(citacao) not in normalizar_pagina(texto_da_pagina):
        return r(False, "CITACAO_FORA_DA_PAGINA")
    return r(True)
