"""Gates G-MOT-01 a 22 da IMC do Coach que SÃO verificáveis por código (GAP-E, GE-2; S18-R11). Função pura, sem rede, arquivo, relógio nem modelo.

Três classes, sem fingir cobertura total:
- ESTRUTURAIS (10): conferem campos de um registro de intervenção em formato fechado PROPOSTO (hipótese com evidência e incerteza, dimensões
  separadas, alvo e indicador, base da eficácia, encaminhamentos, consentimento, revisão). Provam a PRESENÇA e a coerência dos campos, não a
  verdade do que o Coach registrou.
- LEXICAIS (10): padrões de frase proibida na mensagem ao candidato (diagnóstico clínico, promessa de aprovação, privação de sono...). É
  HEURÍSTICA: reduz, não elimina, e não pega paráfrase; negação na mesma oração ("não é um diagnóstico de...") não dispara.
- NÃO GATEÁVEIS (2): G-MOT-20 (preservar fontes, privacidade e contexto) e G-MOT-22 (persistência adaptativa x teimosia) dependem de juízo; ficam
  para a auditoria por amostra (S14-R14).
Não homologa o harness e NÃO está aplicado em `agents/COACH.md` (isso exige a aprovação expressa do texto e do merge do proprietário).
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date

try:
    import content_filters
except ModuleNotFoundError:  # uso como pacote
    from scripts import content_filters

TIPOS = frozenset({"motivacao", "conhecimento", "recuperacao", "capacidade", "oportunidade", "custo", "bem_estar"})
INCERTEZAS = frozenset({"baixa", "media", "alta"})
ORIGENS = frozenset({"estudante", "harness", "ia"})
DIMENSOES = ("capacidade", "oportunidade", "motivacao", "custo", "bem_estar")
ESTADOS_DIMENSAO = frozenset({"avaliada", "sem_dado"})
BASES_FRACAS = frozenset({"satisfacao", "relato_animo", "antes_depois_isolado"})
BASES = BASES_FRACAS | {"serie_n_of_1", "comparacao_controlada", "indicador_observavel_repetido", "resultado_de_ia"}
TOPO = frozenset({"hipotese", "intervencao", "eficacia", "sofrimento", "apoio_social", "encaminhado_ao_tutor"})
MAX_TEXTO = 120
MAX_MENSAGEM = 2000
TENTATIVAS_PARA_REVISAO = 3
ESTRUTURAIS = ("G-MOT-01", "G-MOT-02", "G-MOT-03", "G-MOT-06", "G-MOT-07", "G-MOT-13", "G-MOT-14", "G-MOT-17", "G-MOT-18", "G-MOT-19")
NAO_GATEAVEIS = ("G-MOT-20", "G-MOT-22")
LIMITE = ("Estruturais provam presença e coerência de campos, não a verdade do registro; lexicais são heurística (reduzem, não eliminam, e não pegam "
          "paráfrase); G-MOT-20 e G-MOT-22 dependem de juízo (auditoria por amostra). Não homologa e não está aplicado em agents/COACH.md.")


def _norm(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto.lower())
    return re.sub(r"\s+", " ", "".join(c for c in base if not unicodedata.combining(c))).strip()


_LEXICAIS = {
    "G-MOT-04": (r"\bescala (?:psicometrica )?validada\b", r"\bdiagnostico psicologico\b", r"\bteste psicologico\b"),
    "G-MOT-05": (r"\bvoce e (?:uma pessoa |do tipo |um tipo |um |uma )?(?:preguicos\w*|fraco|fraca|desorganizad\w*|procrastinador\w*|indisciplinad\w*|incapaz)\b",
                 r"\bseu perfil e (?:preguicos\w*|fraco|desorganizad\w*|procrastinador\w*)\b"),
    "G-MOT-08": (r"\b(?:tenha|ter) vergonha\b", r"\be uma vergonha\b", r"\bvoce nao tem escolha\b", r"\bvoce e obrigad[oa] a\b"),
    "G-MOT-09": (r"\bvai (?:fracassar|reprovar|perder tudo)\b", r"\bvoce vai se arrepender\b", r"\boutros candidatos estao estudando mais\b"),
    "G-MOT-10": (r"\bcompense\w* (?:todas|todo|integralmente|tudo)\b", r"\brecupere (?:todas as|todo o) horas?\b", r"\bdivida de (?:horas|estudo)\b"),
    "G-MOT-11": (r"\bdurma menos\b", r"\bpule (?:o |a )?(?:almoco|refeicao|refeicoes|jantar)\b", r"\bcorte (?:o )?sono\b",
                 r"\b(?:abandone|pare|interrompa|suspenda|largue|deixe de tomar) (?:de tomar )?(?:o |a |os |as |seu |sua |seus |suas )?(?:tratamento|medicacao|remedios?|exercicio)\b"),
    "G-MOT-12": (r"\blargue (?:o )?emprego\b", r"\bpeca demissao\b", r"\babandone (?:os |seus )?(?:filhos|dependentes)\b"),
    "G-MOT-15": (r"\bvoce (?:tem|esta com|sofre de|apresenta) (?:ansiedade|depressao|burnout|transtorno\w*|tdah|toc|bipolaridade|autismo|panico|fobia)\b",
                 r"\bdiagnostico de (?:ansiedade|depressao|burnout)\b", r"\bseu quadro e de (?:ansiedade|depressao|burnout)\b"),
    "G-MOT-16": (r"\bso eu (?:te )?entendo\b", r"\bnao precisa de (?:mais )?ninguem\b", r"\bfale so comigo\b"),
    "G-MOT-21": (r"\bgarant\w+ (?:sua |a )?(?:aprovacao|nomeacao)\b", r"\bvoce (?:vai|ira|sera) (?:passar|(?:ser )?aprovad\w+|(?:ser )?nomead\w+)\b",
                 r"\baprovacao (?:esta |e |ja e |fica )?garantida\b", r"\bgaranto que voce\b", r"\bgarantia de (?:aprovacao|nomeacao)\b"),
}
LEXICAIS = tuple(sorted(_LEXICAIS))
_COMPILADOS = {g: tuple(re.compile(p) for p in ps) for g, ps in _LEXICAIS.items()}
# AC-5: negação ou ressalva na mesma oração, janela de 40 caracteres ("não quero que você durma menos", "ninguém pode garantir aprovação")
_NEGACAO = re.compile(r"\b(?:nao|nunca|jamais|ninguem|nenhum|nenhuma|sem)\b[^.,;:!?]{0,40}$")


def cobertura() -> dict:
    return {"estruturais": list(ESTRUTURAIS), "lexicais": list(LEXICAIS), "nao_gateaveis": list(NAO_GATEAVEIS), "homologa": False, "limite": LIMITE}


def verificar_mensagem(texto) -> dict:
    """Gates lexicais sobre o texto enviado ao candidato. Nunca levanta; heurística."""
    base = {"ok": False, "falhas": [], "nao_verificados": list(NAO_GATEAVEIS) + list(ESTRUTURAIS), "limite": LIMITE}
    if not isinstance(texto, str) or len(texto) > MAX_MENSAGEM:
        return {**base, "falhas": [{"gate": "FORMA", "codigo": "TEXTO_INVALIDO_OU_LONGO"}]}
    n = _norm(texto)
    falhas = []
    for gate in LEXICAIS:
        for padrao in _COMPILADOS[gate]:
            if any(not _NEGACAO.search(n[:m.start()]) for m in padrao.finditer(n)):
                falhas.append({"gate": gate, "codigo": "FRASE_PROIBIDA"})
                break
    return {**base, "ok": not falhas, "falhas": falhas}


def _texto_ok(v) -> bool:
    return isinstance(v, str) and bool(v.strip()) and len(v) <= MAX_TEXTO


def _data_ok(v) -> bool:
    try:
        return isinstance(v, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", v)) and bool(date.fromisoformat(v))
    except ValueError:
        return False


def _forma(i) -> bool:
    return (isinstance(i, dict) and set(i) == TOPO and all(isinstance(i[k], dict) for k in TOPO - {"encaminhado_ao_tutor"})
            and isinstance(i["encaminhado_ao_tutor"], bool) and i["hipotese"].get("tipo") in TIPOS)


def verificar_intervencao(i) -> dict:
    """Gates estruturais sobre o registro de intervenção (formato fechado proposto). Nunca levanta e não altera a entrada."""
    base = {"ok": False, "falhas": [], "nao_verificados": list(NAO_GATEAVEIS), "limite": LIMITE}
    if not _forma(i):
        return {**base, "falhas": [{"gate": "FORMA", "codigo": "REGISTRO_FORA_DO_FORMATO"}]}
    falhas = []

    def falha(gate, codigo):
        falhas.append({"gate": gate, "codigo": codigo})

    h, iv, ef, so, ap = i["hipotese"], i["intervencao"], i["eficacia"], i["sofrimento"], i["apoio_social"]
    ev = h.get("evidencias")
    evidencias_ok = (isinstance(ev, list) and bool(ev) and all(isinstance(e, dict) and set(e) == {"data", "sinal", "origem"} and _data_ok(e["data"])
                                                                and _texto_ok(e["sinal"]) and e["origem"] in ORIGENS for e in ev))
    if not evidencias_ok or h.get("incerteza") not in INCERTEZAS:
        falha("G-MOT-03", "HIPOTESE_SEM_EVIDENCIA_OU_INCERTEZA")
    if h["tipo"] == "motivacao" and not (evidencias_ok and len(ev) >= 2 and len({e["data"] for e in ev}) >= 2):
        falha("G-MOT-01", "MOTIVACAO_INFERIDA_DE_UMA_OBSERVACAO_OU_UM_DIA")
    dim = h.get("dimensoes")
    if not (isinstance(dim, dict) and set(dim) == set(DIMENSOES) and all(v in ESTADOS_DIMENSAO for v in dim.values())):
        falha("G-MOT-02", "DIMENSOES_NAO_SEPARADAS")
    elif h["tipo"] == "motivacao" and not (dim["capacidade"] == "avaliada" and dim["oportunidade"] == "avaliada"):
        falha("G-MOT-02", "MOTIVACAO_SEM_DESCARTAR_CAPACIDADE_E_OPORTUNIDADE")
    if not (_texto_ok(iv.get("comportamento_alvo")) and _texto_ok(iv.get("indicador"))):
        falha("G-MOT-06", "INTERVENCAO_SEM_ALVO_OU_INDICADOR")
    elif not verificar_mensagem(iv["comportamento_alvo"] + ". " + iv["indicador"])["ok"] or content_filters.tem_url(iv["comportamento_alvo"] + " " + iv["indicador"]) \
            or content_filters.instrucao_embutida(iv["comportamento_alvo"] + " " + iv["indicador"]):
        falha("G-MOT-06", "ALVO_OU_INDICADOR_COM_CONTEUDO_PROIBIDO")  # AC-6: o alvo não é texto livre sem filtro
    base_ef = ef.get("base")
    if type(ef.get("declarada")) is not bool:
        falha("G-MOT-07", "EFICACIA_DECLARADA_NAO_BOOLEANA")  # AC-6: "true" em texto não pode passar como "sem eficácia declarada"
    if ef.get("declarada") is True:
        if not (isinstance(base_ef, list) and all(b in BASES for b in base_ef)) or not (set(base_ef) - BASES_FRACAS - {"resultado_de_ia"}):
            falha("G-MOT-07", "EFICACIA_SEM_BASE_ALEM_DE_SATISFACAO_RELATO_OU_ANTES_DEPOIS")
        if isinstance(base_ef, list) and "resultado_de_ia" in base_ef:
            falha("G-MOT-18", "RESULTADO_DE_IA_COMO_EVIDENCIA_DE_APRENDIZAGEM")
    if h["tipo"] in ("conhecimento", "recuperacao") and i["encaminhado_ao_tutor"] is not True:
        falha("G-MOT-13", "LACUNA_DE_CONHECIMENTO_NAO_ENCAMINHADA_AO_TUTOR")
    if type(so.get("intenso_ou_persistente")) is not bool:
        falha("G-MOT-14", "SOFRIMENTO_CAMPO_NAO_BOOLEANO")  # AC-6: tipo errado ("sim") não pode passar como "sem sofrimento"
    elif so["intenso_ou_persistente"] and so.get("encaminhado") is not True:
        falha("G-MOT-14", "SOFRIMENTO_SEM_ENCAMINHAMENTO_HUMANO")
    if type(ap.get("usado")) is not bool:
        falha("G-MOT-17", "APOIO_SOCIAL_CAMPO_NAO_BOOLEANO")
    elif ap["usado"] and ap.get("consentimento") is not True:
        falha("G-MOT-17", "APOIO_SOCIAL_SEM_CONSENTIMENTO")
    tentativas = iv.get("tentativas_sem_efeito")
    if type(tentativas) is not int or tentativas < 0 or (tentativas >= TENTATIVAS_PARA_REVISAO and iv.get("revisada") is not True):
        falha("G-MOT-19", "INTERVENCAO_SEM_EFEITO_NAO_REVISADA")
    return {**base, "ok": not falhas, "falhas": falhas}
