"""Gerador OFFLINE de projeções para sessões do app Claude (PROJ; S6-R9, consentimento v4).

Função pura e fail-closed: não faz rede, não lê credencial, não lê nem grava arquivo. Recebe registros do histórico JÁ LIDOS (por
quem tem a credencial, fora do modelo), os tópicos e o consentimento v4, e devolve UMA projeção na lista fechada de
`session_read_guard`: `schema`, `gerado_em`, `niveis` (E0 a E4), `pendencias` e `revisoes`.

Ordem (qualquer falha bloqueia com `PersistenceBlocked`, sem devolver nada parcial):
1. consentimento v4 íntegro (`check_consent_v4`), ANTES de olhar qualquer registro;
2. `descartar_sinteticos`: eventos de teste, marca ambígua e registro malformado saem;
3. validação e reconstrução dos eventos reais (`core.validate_events` e `core.rebuild`);
4. mapeamento para a lista fechada e `authorize_session_read` (que revalida consentimento e projeção).

Limites: o nível é a qualidade da INFORMAÇÃO (E0 a E4), nunca domínio nem chance de aprovação; o nível do tópico é o nível global da
evidência, só para tópicos com tentativa registrada (tópico ausente = E0). Os vencimentos de revisão são os já gravados nos
eventos (padrão 7, 15 e 30 dias, PRODUCT D-11); o gerador NÃO os calcula. Nada aqui liga a leitura por sessão: isso é a C6.
"""
from datetime import datetime, timezone

import core
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
    nivel = atual["evidence_level"]
    projecao = {
        "schema": 1,
        "gerado_em": agora.astimezone(timezone.utc).strftime("%Y-%m-%d"),
        "niveis": [{"topico": nome[l["topic_id"]], "nivel": nivel} for l in linhas if l["attempted"] > 0],
        "pendencias": [{"atividade_id": cid, "tipo": "caderno"} for cid in atual["pending_cadernos"]],
        "revisoes": [{"topico": nome[t], "vence_em": str(due)[:10]} for t, due in sorted(atual["pending_reviews"].items())],
    }
    authorize_session_read(consentimento, "projecao", projecao, agora)
    return projecao
