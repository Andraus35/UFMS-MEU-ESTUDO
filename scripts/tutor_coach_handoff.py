"""Registro de passagem Tutor↔Coach e âncora da norma (GAP-D, GD-1 e GD-4; S13-R3, T3; S10-R7).

GD-1: esquema FECHADO do registro de passagem, com validador e encaminhamento (tutor, coach, ambos ou diagnóstico complementar) conforme a
S13-R3, a taxonomia L-, P-, M- da S13-R4 e a assistência H0 a H5 da S13-R5. O registro leva REFERÊNCIAS, nunca o texto da questão; texto
livre é curto e passa pelos filtros de segredo, dado pessoal e texto de questão. Dado real mora só no repositório privado (D-24); este módulo é
função pura e sem E/S além de ler `config/topics.csv` e `config/norma_ancoras.json`.
O mapa código→destino é LEITURA da S13-R3 (proposta a confirmar): códigos que a regra não nomeia vão a diagnóstico complementar.

GD-4: conferência de citação contra âncoras locais da norma (artigo, página, fonte e SHA-256 do trecho). O arquivo de âncoras está VAZIO
(texto oficial pendente), então a conferência recusa com ANCORA_AUSENTE em vez de aprovar de memória.
"""
from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
from pathlib import Path

try:
    import agent_commands
    import content_filters
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import agent_commands, content_filters

ROOT = Path(__file__).resolve().parents[1]
ORIGENS = ("oficial", "banco", "adaptado", "sintetico")
RESPOSTAS = ("A", "B", "C", "D", "E", "certo", "errado", "em_branco")
CONFIANCAS = ("alta", "media", "baixa")
ASSISTENCIAS = ("H0", "H1", "H2", "H3", "H4", "H5", "desconhecido")
INDEPENDENCIA = {"H0": "independente", "H1": "guiada", "H2": "guiada", "H3": "assistida", "H4": "assistida", "H5": "assistida",
                 "desconhecido": "desconhecida"}  # só H0 é recuperação independente; não registrada nunca vira H0 (S13-R5)
CAMPOS = ("topico", "origem_item", "referencia_item", "resposta", "fundamento_ref", "confianca", "assistencia", "tempo_segundos",
          "codigos_erro", "objetivo", "reteste")
CAMPOS_ERRO = ("codigo", "evidencia", "hipotese")
CODIGOS = frozenset({"L-KNO", "L-COM", "L-REC", "L-RET", "L-DIS", "L-APP", "L-TRF", "L-HNT", "L-CAL",
                     "P-SEM", "P-QNT", "P-NEG", "P-EXT", "P-INS", "P-INV", "P-VIG", "P-CPT", "P-CON", "P-CNS", "P-TAN", "P-REL", "P-CAR",
                     "P-DEC", "P-TEM", "P-CMD", "P-EST", "M-SRC", "M-ITM"})
_TUTOR = frozenset({"L-KNO", "L-COM", "L-REC", "L-RET", "L-HNT"})  # conhecimento, compreensão, recuperação, esquecimento, dependência de pista
_COACH = frozenset({"P-CMD", "P-NEG", "P-QNT", "P-EXT", "P-DEC", "P-TEM"})  # comando, negação, quantificador, extrapolação, risco e estratégia, tempo
_AMBOS = frozenset({"L-DIS", "L-APP", "L-TRF"})  # confusão de conceitos, aplicação e transferência
_ID = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")
_FUNDAMENTO = re.compile(r"^[\wÀ-ÿ .,:/§º°-]{1,80}$")
MAX_TEXTO = 120
MAX_TEMPO = 36000
MAX_CODIGOS = 6
MIN_TRECHO = 12


def _topicos() -> frozenset:
    with (ROOT / "config" / "topics.csv").open(encoding="utf-8", newline="") as f:
        return frozenset(l["topic_id"] for l in csv.DictReader(f))


def _res(ok, codigo=None, campo=None, **extra):
    return {"ok": ok, "codigo": codigo, "campo": campo, **extra}


def _texto_livre_ok(valor, *, sem_resultado_pessoal=False) -> str | None:
    """None se o texto livre é curto e limpo; senão o código de recusa. COR-C, AT-6: sem URL, instrução embutida nem homóglifo;
    `sem_resultado_pessoal` (objetivo) recusa também contagem de acertos e erros de alguém."""
    if not isinstance(valor, str) or not valor.strip() or len(valor) > MAX_TEXTO or valor != valor.strip():
        return "TEXTO_LIVRE_INVALIDO"
    if agent_commands.scan_text(valor, html=True) or agent_commands.texto_de_questao(valor):
        return "TEXTO_DE_QUESTAO_OU_DADO_PESSOAL"
    if content_filters.tem_url(valor):
        return "TEXTO_COM_URL"
    if content_filters.instrucao_embutida(valor) or content_filters.mistura_de_scripts(valor):
        return "TEXTO_COM_INSTRUCAO_EMBUTIDA"
    if sem_resultado_pessoal and content_filters.desempenho_individual(valor):
        return "TEXTO_COM_RESULTADO_PESSOAL"
    return None


def encaminhar(codigos_erro) -> str:
    """tutor, coach, ambos ou diagnostico_complementar (S13-R3). Hipótese, lista vazia, código não nomeado ou causa mista vão a diagnóstico."""
    if not isinstance(codigos_erro, list) or not codigos_erro:
        return "diagnostico_complementar"
    destinos = set()
    for e in codigos_erro:
        if not isinstance(e, dict) or e.get("hipotese") is not False:
            return "diagnostico_complementar"
        c = e.get("codigo")
        destinos.add("tutor" if c in _TUTOR else "coach" if c in _COACH else "ambos" if c in _AMBOS else "outro")
    if "outro" in destinos:
        return "diagnostico_complementar"
    if len(destinos) == 1:
        return next(iter(destinos))
    return "ambos" if destinos == {"ambos", "tutor"} or destinos == {"ambos", "coach"} else "diagnostico_complementar"


def validar_registro(registro) -> dict:
    """Valida o registro de passagem. Nunca levanta exceção para entrada ruim e não altera a entrada.
    Devolve {"ok", "codigo", "campo"} e, se válido, `destino`, `independencia` e `prioridade` (alta confiança com erro, S12-R6)."""
    if not isinstance(registro, dict):
        return _res(False, "REGISTRO_NAO_OBJETO")
    for extra in sorted(set(registro) - set(CAMPOS), key=str):
        return _res(False, "CAMPO_FORA_DA_LISTA", str(extra))
    for campo in CAMPOS:
        if campo not in registro:
            return _res(False, "CAMPO_OBRIGATORIO_AUSENTE", campo)
    if registro["topico"] not in _topicos():
        return _res(False, "TOPICO_FORA_DO_EDITAL", "topico")
    for campo, lista in (("origem_item", ORIGENS), ("resposta", RESPOSTAS), ("confianca", CONFIANCAS), ("assistencia", ASSISTENCIAS)):
        if registro[campo] not in lista:
            return _res(False, "VALOR_FORA_DA_LISTA", campo)
    ref = registro["referencia_item"]
    if not (isinstance(ref, str) and _ID.fullmatch(ref)) or agent_commands.texto_de_questao(ref):
        return _res(False, "REFERENCIA_INVALIDA", "referencia_item")  # só identificador: nunca o texto da questão
    fund = registro["fundamento_ref"]
    if not (isinstance(fund, str) and _FUNDAMENTO.fullmatch(fund)) or agent_commands.scan_text(fund) or agent_commands.texto_de_questao(fund):
        return _res(False, "REFERENCIA_INVALIDA", "fundamento_ref")
    tempo = registro["tempo_segundos"]
    if type(tempo) is not int or not 0 <= tempo <= MAX_TEMPO:
        return _res(False, "TEMPO_INVALIDO", "tempo_segundos")
    codigos = registro["codigos_erro"]
    if not isinstance(codigos, list) or len(codigos) > MAX_CODIGOS:
        return _res(False, "CODIGOS_ERRO_INVALIDOS", "codigos_erro")
    for e in codigos:
        if not isinstance(e, dict) or set(e) != set(CAMPOS_ERRO) or e["codigo"] not in CODIGOS or type(e["hipotese"]) is not bool:
            return _res(False, "CODIGOS_ERRO_INVALIDOS", "codigos_erro")
        motivo = _texto_livre_ok(e["evidencia"])  # cada código com evidência (S13-R4)
        if motivo:
            return _res(False, motivo, "codigos_erro")
    for campo in ("objetivo",):
        motivo = _texto_livre_ok(registro[campo], sem_resultado_pessoal=True)
        if motivo:
            return _res(False, motivo, campo)
    reteste = registro["reteste"]
    if not (isinstance(reteste, dict) and set(reteste) == {"item_novo"} and reteste["item_novo"] is True):
        return _res(False, "RETESTE_SEM_ITEM_NOVO", "reteste")
    return _res(True, None, None, destino=encaminhar(codigos), independencia=INDEPENDENCIA[registro["assistencia"]],
                prioridade=registro["confianca"] == "alta" and bool(codigos))


def hash_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _norm(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto.lower())
    return re.sub(r"\s+", " ", "".join(c for c in base if not unicodedata.combining(c))).strip()


CAMPOS_ANCORA = frozenset({"norma", "artigo", "pagina", "fonte", "texto", "sha256"})


def conferir_citacao_norma(artigo, trecho, ancoras) -> dict:
    """GD-4 (S10-R7): o trecho citado precisa constar, literalmente, da âncora local do artigo, e a âncora precisa bater com o seu SHA-256.
    Sem âncora do artigo: recusa (ANCORA_AUSENTE); a conferência então continua externa."""
    if not isinstance(ancoras, list):
        return _res(False, "ANCORA_MALFORMADA")
    candidatas = []
    for a in ancoras:
        if not (isinstance(a, dict) and set(a) == CAMPOS_ANCORA and all(isinstance(v, str) and v for v in a.values())):
            return _res(False, "ANCORA_MALFORMADA")
        if a["artigo"] == artigo:
            candidatas.append(a)
    if not candidatas:
        return _res(False, "ANCORA_AUSENTE")
    if not isinstance(trecho, str) or len(_norm(trecho)) < MIN_TRECHO:
        return _res(False, "TRECHO_CURTO_DEMAIS")
    for a in candidatas:
        if hash_texto(a["texto"]) != a["sha256"]:
            return _res(False, "ANCORA_ADULTERADA")
        if _norm(trecho) in _norm(a["texto"]):
            return _res(True, None, None, fonte=a["fonte"], pagina=a["pagina"])
    return _res(False, "TRECHO_FORA_DA_ANCORA")
