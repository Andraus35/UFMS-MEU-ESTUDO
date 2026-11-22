"""Filtros de conteúdo compartilhados (COR-C; AT-3 a AT-6). Funções PURAS, sem rede, arquivo, relógio nem modelo.

Módulo-folha: não importa nenhum outro módulo de `scripts/`, para poder ser usado por `agent_commands`, `command_params_schema`,
`notebook_prompt_validator`, `tutor_coach_handoff` e `notebook_prescriber` sem ciclo de importação.

Todo filtro aqui é HEURÍSTICO: reduz, não elimina. Texto de terceiros e do próprio modelo é DADO; o filtro não prova ausência de
instrução embutida, de URL ou de texto de questão (S5-R4, S10-R3).
"""
from __future__ import annotations

import re
import unicodedata

TLDS = ("com|org|net|gov|edu|mil|int|info|biz|io|co|br|app|dev|ai|me|ly|tv|xyz|site|online|top|club|cloud|page|link|us|uk|ru|cn|de|fr|es|pt")
_DEFANG = re.compile(r"\s*(?:\[\s*\.\s*\]|\(\s*\.\s*\)|\{\s*\.\s*\}|\[\s*dot\s*\]|\(\s*dot\s*\)|\{\s*dot\s*\})\s*", re.I)
_ESQUEMA = re.compile(r"\b(?:h(?:tt|xx|\W{1,2}|\*{1,2}|tx|xt)ps?|ftp|sftp|file|data|javascript|vbscript|mailto|ws|wss)\s*:|\bwww\s*\.|//[a-z0-9.-]+\.[a-z]{2,}", re.I)
_DOMINIO = re.compile(r"(?<![\w@])(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:" + TLDS + r")(?![a-z0-9])", re.I)
_IPV4 = re.compile(r"(?<![\d.])\d{1,3}(?:\.\d{1,3}){3}(?![\d.])")

# Confusáveis comuns (cirílico e grego) → latino. Só as letras visualmente idênticas ou quase.
_CONFUSAVEIS = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i", "ј": "j", "ѕ": "s", "ԁ": "d", "ɡ": "g",
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X", "І": "I", "Ѕ": "S",
    "ο": "o", "ν": "v", "α": "a", "ε": "e", "ι": "i", "κ": "k", "ρ": "p", "τ": "t", "υ": "u", "χ": "x",
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I", "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P", "Τ": "T", "Χ": "X",
})
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "!": "i"})
_PALAVRA_COM_LETRA_E_SIMBOLO = re.compile(r"\b(?=\w*[a-z])[a-z0-9@$!]{3,}\b", re.I)
_SCRIPT_NAO_LATINO = re.compile(r"[\u0370-\u03ff\u0400-\u04ff]")
_LETRA_LATINA = re.compile(r"[A-Za-z]")
_LETRAS_SEPARADAS = re.compile(r"\b(?:[a-z][.\-_*]){3,}[a-z]\b")

_INSTRUCAO = re.compile(
    r"\bignor\w* (?:(?:all|todas?|as|os|the|your|suas?|seus?|any) )*(?:previous|prior|above|anteriores?|instruc\w*|instructions?|regras|rules)"
    r"|\bdisregard\b|\byou are now\b|\bvoce (?:e|eh) agora\b|\bvoce agora (?:e|eh)\b|\ba partir de agora\b|\bfrom now on\b|\bde agora em diante\b"
    r"|\bsystem prompt\b|\bprompt do sistema\b|\bnao (?:siga|obede\w+)\b|\bdo not follow\b|\bnovas? instruc\w*|\bnew instructions?\b"
    r"|\boverride\b|\bjailbreak\b|\bdeveloper mode\b|\bmodo desenvolvedor\b|\bnovo papel\b|\bnew role\b"
    r"|\bact as\b|\bpretend (?:to be|you)\b|\broleplay as\b|\bfinja (?:que|ser)\b|\baja como\b|\batue como\b|\bdo anything now\b"
    r"|\besquec\w* (?:tudo|todas?|as|os|suas?|seus?|o que)\b|\bforget (?:everything|all|your|the|previous)\b|\bdesconsidere?m?\b"
    r"|\breveal\b.{0,30}\b(?:prompt|instructions?|rules)\b|\brevel\w+\b.{0,30}\b(?:prompt|instruc\w*|regras)\b",
    re.S)
_DESEMPENHO = re.compile(
    r"\b(?:meu|minha|meus|minhas|my)\s+(?:desempenho|nota|notas|acertos?|erros?|resultados?|score|percentual)\b"
    r"|\b(?:acertei|errei|gabaritei)\b|\b(?:errou|acertou|gabaritou)\b|\b(?:teve|tive|tem|fez|com|totalizou|somou)\s+\d+\s*(?:acertos?|erros?)\b|\b\d+\s*%\s*(?:de\s+)?(?:acerto|erro|aproveitamento)")


def desconfundir(texto: str) -> str:
    """NFKC e troca de letras cirílicas e gregas confundíveis por latinas (`іgnore` com i cirílico vira `ignore`)."""
    return unicodedata.normalize("NFKC", texto).translate(_CONFUSAVEIS)


def mistura_de_scripts(texto) -> bool:
    """True se UMA palavra tem letras latinas e cirílicas/gregas juntas (homóglifo). Texto só cirílico ou só latino não casa."""
    if not isinstance(texto, str):
        return False
    return any(_SCRIPT_NAO_LATINO.search(p) and _LETRA_LATINA.search(p) for p in re.findall(r"\w+", texto))


def _ascii(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii").lower()


def normalizar(texto: str) -> str:
    """Forma para casar instrução: sem acento, homóglifo e ofuscação de letras (`i.g.n.o.r.e`); separadores viram espaço."""
    base = _ascii(desconfundir(texto))
    base = _LETRAS_SEPARADAS.sub(lambda m: re.sub(r"[.\-_*]", "", m.group(0)), base)
    return re.sub(r"[\s_\-.]+", " ", base).strip()


def _leet(norm: str) -> str:
    return _PALAVRA_COM_LETRA_E_SIMBOLO.sub(lambda m: m.group(0).translate(_LEET), norm)


def tem_url(texto) -> bool:
    """AT-3: URL com ou sem esquema, ofuscada (`hxxp://`, `example[.]com`, `h**p`), domínio nu (`google.com.br`), `www.` ou IPv4."""
    if not isinstance(texto, str):
        return False
    claro = _DEFANG.sub(".", desconfundir(texto))
    return bool(_ESQUEMA.search(claro) or _DOMINIO.search(claro) or _IPV4.search(claro))


def instrucao_embutida(texto) -> bool:
    """AT-4: ordem de esquecer, substituir regras, assumir papel ou revelar o sistema, também com homóglifo cirílico/grego e leet."""
    if not isinstance(texto, str):
        return False
    norm = normalizar(texto)
    return bool(_INSTRUCAO.search(norm) or _INSTRUCAO.search(_leet(norm)))


def desempenho_individual(texto) -> bool:
    """Contagem ou relato de acertos e erros de alguém (`errou 12`, `teve 12 erros`, `meu desempenho`, `40% de acerto`): resultado pessoal.
    Contagem solta ("os 3 erros comuns") não casa: sem falso positivo em orientação comum."""
    return isinstance(texto, str) and bool(_DESEMPENHO.search(normalizar(texto)))
