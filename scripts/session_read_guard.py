"""Guarda OFFLINE da leitura de projeções por sessões do app Claude (S6-R9, ADR-013, consentimento v4).

Lógica pura e fail-closed: não faz rede, não lê credencial, não grava nada. Decide e não age. Autorização deste guarda é condição
NECESSÁRIA, nunca suficiente: hoje nenhuma sessão tem acesso ao estado pessoal e a flag `personal_results_writes_enabled` segue
false; ligar a leitura é a C6 (PR próprio, aprovação expressa do proprietário).

O que confere:
- `check_consent_v4`: consentimento v4 íntegro (versão, escopo, inclui a leitura de projeções, não revogado, data válida, texto cuja
  hash confere e que cita o app Claude e a leitura somente de projeções).
- `check_projection`: a projeção segue uma LISTA FECHADA PROPOSTA (níveis, pendências e revisões) e nunca traz texto de questão nem
  identificador de conta, e-mail, URL, segredo ou campo desconhecido. A lista é proposta para o proprietário aprovar na C6.
- `authorize_session_read`: junta as duas; recusa pedido de histórico bruto.
"""
import hashlib
import re
from datetime import datetime, timedelta, timezone

from private_persistence_guard import CONSENT_SCOPE, PersistenceBlocked

INCLUI_OBRIGATORIO = {"resultados_estudo", "plano_estudo", "leitura_projecoes_sessoes_app_claude"}
TEXTO_OBRIGATORIO = ("app Claude", "somente leitura", "projeções", "nunca o histórico bruto")
KINDS_PERMITIDOS = {"projecao"}  # histórico bruto, fila e arquivos de exportação nunca são lidos por sessão
TOPO = {"schema", "gerado_em", "niveis", "pendencias", "revisoes"}
ITENS = {"niveis": {"topico", "nivel"}, "pendencias": {"atividade_id", "tipo"}, "revisoes": {"topico", "vence_em"}}
NIVEIS = {"E0", "E1", "E2", "E3", "E4"}
TIPOS_PENDENCIA = {"caderno", "revisao", "simulado"}
_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_TOPICO = re.compile(r"^[\wÀ-ÿ .,;:()/-]{1,120}$")
_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_INSTANTE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
LIMITE_PRAZO_H, LIMITE_ORIENTACAO_H = 24, 72  # S15-R5, propostas ajustáveis pelo proprietário
_PROIBIDO = re.compile(r"@|https?:|www\.|\bgithub_pat_|\bghp_|\bsk-|cookie|senha|token|\bcpf\b|enunciado|alternativa|gabarito", re.I)
MAX_ITENS = 500


def _agora(now):
    return now or datetime.now(timezone.utc)


def check_consent_v4(consent, now=None):
    """Consentimento v4 íntegro; qualquer falha bloqueia."""
    if not isinstance(consent, dict):
        raise PersistenceBlocked("V4: consentimento ausente")
    if consent.get("version") != "v4":
        raise PersistenceBlocked("V4: a leitura por sessão exige o consentimento v4 (versão diferente)")
    if consent.get("scope") != CONSENT_SCOPE:
        raise PersistenceBlocked("V4: escopo do consentimento inválido")
    inclui = consent.get("inclui")
    if not isinstance(inclui, list) or not INCLUI_OBRIGATORIO.issubset(set(map(str, inclui))):
        raise PersistenceBlocked("V4: o consentimento não cobre a leitura de projeções por sessões do app Claude")
    if consent.get("revoked_at") is not None:
        raise PersistenceBlocked("V4: consentimento revogado")
    try:
        quando = datetime.fromisoformat(consent.get("granted_at"))
    except (TypeError, ValueError):
        raise PersistenceBlocked("V4: data do consentimento inválida") from None
    if quando.tzinfo is None:
        raise PersistenceBlocked("V4: data do consentimento sem fuso")
    if quando > _agora(now):
        raise PersistenceBlocked("V4: consentimento com data futura")
    texto = consent.get("text")
    if not isinstance(texto, str) or consent.get("text_sha256") != hashlib.sha256(texto.encode("utf-8")).hexdigest():
        raise PersistenceBlocked("V4: o texto do consentimento não confere com a hash")
    if not texto.endswith("Versão: v4.") or any(t not in texto for t in TEXTO_OBRIGATORIO):
        raise PersistenceBlocked("V4: o texto não é o do consentimento v4 (falta app Claude, somente leitura ou projeções)")
    return "v4"


def _texto_seguro(valor, rotulo):
    if not isinstance(valor, str) or _PROIBIDO.search(valor) or "\n" in valor or "\r" in valor:
        raise PersistenceBlocked(f"PROJECAO: {rotulo} com conteúdo proibido")
    return valor


def _tipo_gerado_em(valor):
    """"instante" (AAAA-MM-DDTHH:MM:SSZ real), "data" (AAAA-MM-DD real) ou None."""
    if not isinstance(valor, str):
        return None
    try:
        if _INSTANTE.fullmatch(valor):
            datetime.strptime(valor, "%Y-%m-%dT%H:%M:%SZ")
            return "instante"
        if _DATA.fullmatch(valor):
            datetime.strptime(valor, "%Y-%m-%d")
            return "data"
    except ValueError:
        return None
    return None


def conferir_idade(proj, agora_utc, uso, *, limite_prazo_h=LIMITE_PRAZO_H, limite_orientacao_h=LIMITE_ORIENTACAO_H):
    """Idade da projeção (S15-R5), com relógio injetado. `uso` "prazo": recusa acima do limite (padrão 24 h) e recusa data sem hora;
    "orientacao": avisa acima de 72 h, nunca recusa por idade. Sem `gerado_em` ou no futuro: recusa nos dois usos. Devolve
    {"decisao": OK|AVISO|RECUSA, "codigo", "horas"}."""
    def r(decisao, codigo=None, horas=None):
        return {"decisao": decisao, "codigo": codigo, "horas": horas}

    if not isinstance(agora_utc, datetime) or agora_utc.tzinfo is None:
        return r("RECUSA", "RELOGIO_AUSENTE")
    if uso not in ("prazo", "orientacao"):
        return r("RECUSA", "USO_DESCONHECIDO")
    valor = proj.get("gerado_em") if isinstance(proj, dict) else None
    tipo = _tipo_gerado_em(valor)
    if tipo is None:
        return r("RECUSA", "PROJECAO_SEM_GERADO_EM")
    agora = agora_utc.astimezone(timezone.utc)
    if tipo == "data":
        if uso == "prazo":
            return r("RECUSA", "PROJECAO_SEM_INSTANTE")  # só a data: não dá para provar 24 h
        gerado = datetime.strptime(valor, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if gerado.date() > agora.date():
            return r("RECUSA", "PROJECAO_NO_FUTURO")
        horas = (agora - gerado).total_seconds() / 3600  # COR-E, AC-9: só a data, vale a idade MÁXIMA possível (desde 00:00 UTC), nunca a mínima
    else:
        gerado = datetime.strptime(valor, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if gerado > agora:
            return r("RECUSA", "PROJECAO_NO_FUTURO")
        horas = (agora - gerado).total_seconds() / 3600
    if uso == "prazo":
        return r("RECUSA", "PROJECAO_VELHA_PARA_PRAZO", horas) if horas > limite_prazo_h else r("OK", None, horas)
    return r("AVISO", "PROJECAO_DEFASADA", horas) if horas > limite_orientacao_h else r("OK", None, horas)


def check_projection(proj):
    """A projeção segue a lista fechada e nunca traz texto de questão, identificador de conta, URL ou segredo."""
    if not isinstance(proj, dict):
        raise PersistenceBlocked("PROJECAO: não é um objeto")
    extra = set(proj) - TOPO
    if extra:
        raise PersistenceBlocked("PROJECAO: campo desconhecido no topo (" + ",".join(sorted(map(str, extra))) + ")")
    if proj.get("schema") != 1:
        raise PersistenceBlocked("PROJECAO: schema inválido")
    if _tipo_gerado_em(proj.get("gerado_em")) is None:  # data (legado) ou instante UTC (GB-2, S15-R5)
        raise PersistenceBlocked("PROJECAO: gerado_em inválido")
    for secao, campos in ITENS.items():
        itens = proj.get(secao, [])
        if not isinstance(itens, list) or len(itens) > MAX_ITENS:
            raise PersistenceBlocked(f"PROJECAO: {secao} inválido")
        for item in itens:
            if not isinstance(item, dict) or set(item) != campos:
                raise PersistenceBlocked(f"PROJECAO: item de {secao} com campos fora da lista fechada")
            for campo, valor in item.items():
                _texto_seguro(valor, f"{secao}.{campo}")
            if secao == "niveis" and item["nivel"] not in NIVEIS:
                raise PersistenceBlocked("PROJECAO: nível fora de E0 a E4")
            if secao == "pendencias" and (item["tipo"] not in TIPOS_PENDENCIA or not _ID.fullmatch(item["atividade_id"])):
                raise PersistenceBlocked("PROJECAO: pendência inválida")
            if secao in ("niveis", "revisoes") and not _TOPICO.fullmatch(item["topico"]):
                raise PersistenceBlocked("PROJECAO: tópico inválido")
            if secao == "revisoes" and not _DATA.fullmatch(item["vence_em"]):
                raise PersistenceBlocked("PROJECAO: data de revisão inválida")
    return proj


def eh_sintetico(registro):
    """True se o registro do histórico é de TESTE (C5) ou se a marca é ambígua. Fail-closed: só é real o registro cujo envelope
    é um objeto sem a chave `sintetico`; `sintetico` presente com qualquer valor (inclusive false, texto ou número), envelope
    ausente, malformado ou registro que não é objeto contam como sintético e saem da projeção."""
    if not isinstance(registro, dict):
        return True
    envelope = registro.get("envelope")
    if not isinstance(envelope, dict):
        return True
    return "sintetico" in envelope


def descartar_sinteticos(registros):
    """Entrada de TODA projeção feita a partir do histórico privado: devolve só os registros reais, na mesma ordem."""
    return [r for r in registros if not eh_sintetico(r)]


def authorize_session_read(consent, kind, projection, now=None):
    """Autoriza (ou bloqueia) UMA leitura de projeção por sessão; ordem fail-closed: tipo, consentimento v4, projeção."""
    if kind not in KINDS_PERMITIDOS:
        raise PersistenceBlocked("V4: sessões leem só projeções, nunca o histórico bruto nem a fila")
    versao = check_consent_v4(consent, now)
    check_projection(projection)
    return {"authorized": True, "consent_version": versao, "kind": kind}
