"""Conferência OFFLINE da resposta do Gemini Notebook devolvida pela Zapia (S10-R6, R7, R11; teste N1).

A resposta é DADO NÃO CONFIÁVEL: este módulo só decide se ela pode seguir ao Tutor para verificação. Confere forma fechada, vínculo com o comando (id e
hash), ausência de instrução embutida, URL, HTML e dado pessoal, e a CITAÇÃO ABERTA: o trecho devolvido tem de ser cópia literal (espaços normalizados)
do texto-fonte, com no máximo 2 frases. Na contraprova (a fonte não traz a resposta), a saída correta é "não consta nas fontes", sem citação.
Devolve só um CÓDIGO (None = pode seguir ao Tutor). NÃO verifica a afirmação contra o edital: isso é a verificação do Tutor (S10-R7b), humana e heurística.
Limites: não prova que a resposta veio do Notebook nem que a Zapia não a editou (autorrelato); a citação literal prova só que o trecho existe na fonte dada.
"""
from __future__ import annotations

import json
import re
import unicodedata

try:
    import agent_commands
    import content_filters
    import notebook_prompt_validator as npv
except ModuleNotFoundError:  # uso como pacote
    from scripts import agent_commands, content_filters
    from scripts import notebook_prompt_validator as npv

CAMPOS = frozenset({"entrada_id", "hash_corpo", "estado", "texto_literal", "citacao_trecho", "fonte_nome", "interface"})
CAMPO_PARADA = "codigo_parada"
MAX_TEXTO, MAX_CITACAO = 6000, 400
SEM_FONTE = "nao consta nas fontes"
_HASH64 = re.compile(r"^[0-9a-f]{64}$")
_PARADA = re.compile(r"^[A-Z0-9_]{3,40}$")
_FRASE = re.compile(r"[.!?;:](?:\s|$)")


def _norm(texto: str) -> str:
    sem = unicodedata.normalize("NFKD", texto.casefold())
    return re.sub(r"\s+", " ", "".join(c for c in sem if not unicodedata.combining(c))).strip()


def _limpo(texto: str) -> bool:
    return not (agent_commands.scan_text(texto, html=True) or content_filters.tem_url(texto) or content_filters.instrucao_embutida(texto)
                or npv.instrucao_embutida(texto) or content_filters.mistura_de_scripts(texto))


_EXTERNO = re.compile(r"\b\d+\b|\b(?:um|dois|tres|quatro|cinco|seis|sete|oito|nove|dez)\b|\binciso\b|\bparagrafo\b|§|\blei\s+n\b|\b(?:anos?|meses|dias)\b")
_MNEMONICO = re.compile(r"(?:\b[A-Z]\.){3,}")  # acrônimo com pontos, como L.I.M.P.E.
_ITEM_DE_LISTA = re.compile(r"(?m)^\s*\d+[.)]\s")


def avaliar(resposta_bytes, fonte_texto: str, prompt_texto: str = "") -> dict:
    """Conferência em TRÊS PARTES da resposta (pesquisa de 25/11/2026: medir a abstenção separada da sustentação das afirmações; heurística).

    (a) `disse_nao_consta`: a resposta traz a recusa "não consta nas fontes"? (b) `conteudo_externo`: quantas palavras de valor factual (número, número por
    extenso, inciso, parágrafo, "lei n", anos, meses, dias) aparecem na resposta e NÃO estão na fonte nem no prompt, e se há mnemônico com pontos; numeração
    de lista não conta. (c) `citacao_nao_vazia`. Devolve só booleanos e contagem, NUNCA o texto do Notebook. Limites: lista fixa de marcadores, sem
    semântica; não acha conteúdo externo escrito com palavras comuns; é triagem para o Tutor, não prova de fidelidade."""
    try:
        r = json.loads(bytes(resposta_bytes).decode("utf-8"))
        texto, citacao = r["texto_literal"], r["citacao_trecho"]
    except (UnicodeDecodeError, ValueError, TypeError, KeyError, AttributeError):
        return {"avaliavel": False}
    if not isinstance(texto, str) or not isinstance(citacao, str):
        return {"avaliavel": False}
    conhecido = _norm(fonte_texto) + " " + _norm(prompt_texto or "")
    sem_lista = _ITEM_DE_LISTA.sub("", texto)
    externos = [m for m in _EXTERNO.findall(_norm(sem_lista)) if m not in conhecido]
    return {"avaliavel": True, "disse_nao_consta": SEM_FONTE in _norm(texto), "conteudo_externo_n": len(externos),
            "mnemonico": bool(_MNEMONICO.search(texto)), "citacao_nao_vazia": bool(citacao.strip())}


def codigos_da_avaliacao(av: dict, contraprova: bool) -> list:
    """Códigos finos: separam o 'disse que não consta' do 'mas completou com conteúdo de fora' e da citação solta."""
    if not av.get("avaliavel"):
        return ["RESPOSTA_NAO_AVALIAVEL"]
    cod = []
    if contraprova:
        if not av["disse_nao_consta"]:
            cod.append("CONTRAPROVA_SEM_ABSTENCAO")
        if av["disse_nao_consta"] and (av["conteudo_externo_n"] or av["mnemonico"]):
            cod.append("ABSTENCAO_COM_CONTEUDO_EXTERNO")
        if av["citacao_nao_vazia"]:
            cod.append("ABSTENCAO_COM_CITACAO")
    elif av["conteudo_externo_n"] or av["mnemonico"]:
        cod.append("CONTEUDO_EXTERNO_NA_RESPOSTA")
    return cod


def conferir(resposta_bytes, esperado: dict, fonte_texto: str, contraprova: bool = False, ancora_gabarito: str | None = None):
    """`esperado`: {nome, hash_corpo, fonte_nome}. Devolve None se a resposta pode seguir ao Tutor, senão um código.

    `ancora_gabarito` (C1): trecho da FONTE que sustenta o gabarito da questão (registrado pelo Tutor); a citação devolvida precisa contê-lo, senão
    `CITACAO_NAO_SUSTENTA_GABARITO`. Confere que o Notebook citou a passagem certa; NÃO prova que a resposta do Notebook acertou."""
    try:
        r = json.loads(bytes(resposta_bytes).decode("utf-8"))
    except (UnicodeDecodeError, ValueError, TypeError):
        return "RESPOSTA_ILEGIVEL"
    if not isinstance(r, dict) or not (set(r) == CAMPOS or set(r) == CAMPOS | {CAMPO_PARADA}):
        return "RESPOSTA_FORA_DO_FORMATO"
    if not all(isinstance(r[c], str) for c in r):
        return "RESPOSTA_CAMPO_NAO_TEXTO"
    if r["entrada_id"] != esperado.get("nome") or r["hash_corpo"] != esperado.get("hash_corpo") or not _HASH64.fullmatch(r["hash_corpo"]):
        return "RESPOSTA_DE_OUTRO_COMANDO"
    if r["interface"] != "gemini_notebook" or r["fonte_nome"] != esperado.get("fonte_nome"):
        return "RESPOSTA_DE_OUTRA_FONTE_OU_INTERFACE"
    if r["estado"] == "PARADO":
        return None if _PARADA.fullmatch(r.get(CAMPO_PARADA, "")) and not r["texto_literal"] and not r["citacao_trecho"] else "PARADA_MAL_FORMADA"
    if r["estado"] != "RESPONDIDO" or CAMPO_PARADA in r:
        return "ESTADO_INVALIDO"
    texto, citacao = r["texto_literal"], r["citacao_trecho"]
    if not texto.strip() or len(texto) > MAX_TEXTO or len(citacao) > MAX_CITACAO:
        return "TEXTO_VAZIO_OU_GRANDE_DEMAIS"
    if not _limpo(texto) or not _limpo(citacao):
        return "CONTEUDO_PERIGOSO"  # URL, HTML, dado pessoal, segredo ou instrução embutida: só é relatado ao proprietário, nunca executado
    if contraprova:
        if SEM_FONTE not in _norm(texto) or citacao.strip():
            return "CONTRAPROVA_FALHOU"  # a fonte não traz a resposta: o Notebook devia dizer que não consta, sem inventar citação
        return None
    if not citacao.strip():
        return "SEM_CITACAO_ABERTA"
    if len(_FRASE.findall(citacao.strip() + " ")) > 2:
        return "CITACAO_LONGA_DEMAIS"
    if _norm(citacao) not in _norm(fonte_texto):
        return "CITACAO_NAO_ESTA_NA_FONTE"
    if ancora_gabarito is not None and (not isinstance(ancora_gabarito, str) or not ancora_gabarito.strip() or _norm(ancora_gabarito) not in _norm(citacao)):
        return "CITACAO_NAO_SUSTENTA_GABARITO"
    return None
