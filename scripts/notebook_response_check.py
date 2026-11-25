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


def conferir(resposta_bytes, esperado: dict, fonte_texto: str, contraprova: bool = False):
    """`esperado`: {nome, hash_corpo, fonte_nome}. Devolve None se a resposta pode seguir ao Tutor, senão um código."""
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
    return None
