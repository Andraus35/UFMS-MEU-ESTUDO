"""Gerador OFFLINE de projeções para sessões do app Claude (PROJ; S6-R9, consentimento v4).

Função pura e fail-closed: não faz rede, não lê credencial, não lê nem grava arquivo. Recebe registros do histórico JÁ LIDOS (por
quem tem a credencial, fora do modelo), os tópicos e o consentimento v4, e devolve UMA projeção na lista fechada de
`session_read_guard`: `schema`, `gerado_em`, `niveis` (E0 a E4), `pendencias` e `revisoes`.

Ordem (qualquer falha bloqueia com `PersistenceBlocked`, sem devolver nada parcial):
1. consentimento v4 íntegro (`check_consent_v4`), ANTES de olhar qualquer registro;
2. `descartar_sinteticos`: eventos de teste, marca ambígua e registro malformado saem;
3. validação e reconstrução dos eventos reais (`core.validate_events` e `core.rebuild`);
4. mapeamento para a lista fechada e `authorize_session_read` (que revalida consentimento e projeção).

Limites: o nível é a qualidade da INFORMAÇÃO (E0 a E4), nunca domínio nem chance de aprovação; o nível de cada tópico é derivado só
das tentativas daquele tópico (tópico sem tentativa fica fora da lista = E0). Os vencimentos de revisão são os já gravados nos
eventos (padrão 7, 15 e 30 dias, PRODUCT D-11) e saem em data UTC; o gerador NÃO os calcula. `gerado_em` também é a data UTC.
Registro real com envelope ausente ou malformado conta como sintético e SAI da projeção (fail-closed de `descartar_sinteticos`):
a projeção pode subestimar, nunca inventar. `core.rebuild` guarda só os 10 últimos cadernos pendentes. Nada aqui liga a leitura por
sessão: isso é a C6.
"""
import copy
from datetime import datetime, timezone

import core
from evidence_projection import derive_evidence_level
from private_persistence_guard import PersistenceBlocked
from session_read_guard import authorize_session_read, check_consent_v4, descartar_sinteticos

MAX_REGISTROS = 100_000


def _eventos(registros):
    if not isinstance(registros, list) or len(registros) > MAX_REGISTROS:
        raise PersistenceBlocked("PROJ: registros inválidos")
    reais = descartar_sinteticos(registros)
    eventos = []
    for registro in reais:
        evento = registro.get("evento")
        if not isinstance(evento, dict):
            raise PersistenceBlocked("PROJ: registro real sem evento")
        eventos.append(evento)
    return eventos


def _data_utc(valor):
    return core.iso_date(valor, "due_at").astimezone(timezone.utc).strftime("%Y-%m-%d")


def _nivel_do_topico(eventos, topico):
    """Nível E0 a E4 só com as tentativas do tópico: cada evento de resultado leva apenas a linha desse tópico."""
    recorte = []
    for evento in eventos:
        linhas = [l for l in evento.get("topic_results", []) if isinstance(l, dict) and l.get("topic_id") == topico]
        if linhas:
            copia = copy.deepcopy(evento)
            copia["topic_results"] = linhas
            recorte.append(copia)
    return derive_evidence_level(recorte)["level"]


def gerar_projecao(registros, topicos, consentimento, agora=None):
    """Projeção fechada a partir de `registros` ({"evento", "envelope"}); levanta PersistenceBlocked ao menor problema."""
    agora = agora or datetime.now(timezone.utc)
    if agora.tzinfo is None:
        raise PersistenceBlocked("PROJ: horário sem fuso")
    check_consent_v4(consentimento, agora)
    eventos = _eventos(registros)
    try:
        core.validate_events(eventos, topicos, allow_private=True)
        atual, linhas = core.rebuild(eventos, topicos)
    except (ValueError, KeyError, TypeError):
        raise PersistenceBlocked("PROJ: eventos reais inválidos") from None
    nome = {t["topic_id"]: t["titulo"] for t in topicos}
    projecao = {
        "schema": 1,
        "gerado_em": agora.astimezone(timezone.utc).strftime("%Y-%m-%d"),
        "niveis": [{"topico": nome[l["topic_id"]], "nivel": _nivel_do_topico(eventos, l["topic_id"])} for l in linhas if l["attempted"] > 0],
        "pendencias": [{"atividade_id": cid, "tipo": "caderno"} for cid in atual["pending_cadernos"]],
        "revisoes": [{"topico": nome[t], "vence_em": due} for due, t in sorted((_data_utc(d), t) for t, d in atual["pending_reviews"].items())],
    }
    authorize_session_read(consentimento, "projecao", projecao, agora)
    return projecao
