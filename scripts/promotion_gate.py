"""Portão de promoção (S6-R4, tarefa C1): decide, em código e sem modelo, se uma ENTRADA da fila vira evento no histórico.

Biblioteca OFFLINE e fail-closed. Não faz rede, não lê credencial e não escolhe onde gravar: tudo o que toca o mundo
(leitura de visibilidade, do consentimento e do histórico, e a criação do arquivo) entra por **objetos injetados** pelo
chamador. Em produção o chamador será o fluxo de GitHub Actions do repositório `entrada` (tarefa C2); aqui só há fakes.

Etapas, em ordem fixa (S6-R4); a primeira que falhar PARA e devolve só um **código de motivo** (nunca eco do conteúdo):
  0 validador fixado por SHA · 1 forma e tamanho · 2 esquema do evento e id · 3 filtro de dado pessoal e segredo ·
  4 P2 destino fixo · 5 P1 repositório privado · 6 P3 consentimento · 7 flag de escrita pessoal · 8 idempotência ·
  9 escrita de UM arquivo novo · 10 P6 readback.
Com `escritas_habilitadas` diferente de True (hoje `personal_results_writes_enabled=false`) NADA é gravado: o resultado é
`NOT_IMPLEMENTED`. Estados: COMMITTED, DENIED, NOT_IMPLEMENTED, PENDENTE (S5-R7, S7-R6).

Limites: não prova que o fluxo real execute este código nem que o GitHub se comporte como o fake; o filtro é heurístico;
o hash do corpo prova integridade do arquivo, não a origem do comando (S6-R7: a origem Tutor ou Coach NÃO é provada).
"""
import hashlib
import json
import re
from datetime import datetime, timezone

try:
    import agent_commands
    import gp1_ingestion
    import private_persistence_guard as guard
except ModuleNotFoundError:  # uso como pacote
    from scripts import agent_commands, gp1_ingestion
    from scripts import private_persistence_guard as guard

ENTRY_VERSION = 1
MAX_ENTRY_BYTES = 16384
ENTRY_KEYS = frozenset({"entrada_versao", "evento", "origem"})
ORIGIN_KEYS = frozenset({"agente", "escritor", "comando_hash"})
AGENTS = frozenset({"tutor", "coach"})
DELIVERER = "zapia"
EVENT_TYPES = frozenset({"caderno_recomendado"}) | frozenset(gp1_ingestion.ATTEMPT_TYPES)
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_EVENT_ID = re.compile(r"^(\d{8})-[0-9a-f]{12}$")
_PATH = re.compile(r"^eventos/\d{4}-\d{2}/\d{8}-[0-9a-f]{12}\.json$")
_RUN = re.compile(r"^[A-Za-z0-9._-]{1,40}$")
_ENTRY_NAME = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
STEPS = ("validador", "forma", "esquema", "filtro", "p2", "p1", "p3", "flag", "idempotencia", "escrita", "readback")


class Recusa(Exception):
    """Interrompe o portão com um estado e um código de motivo (sem conteúdo)."""

    def __init__(self, status, codigo, etapa):
        super().__init__(codigo)
        self.status, self.codigo, self.etapa = status, codigo, etapa


def canonical(value):
    """JSON canônico: chaves ordenadas, sem espaços, UTF-8."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data):
    """SHA-1 de blob do Git (o `sha` que a API de conteúdo devolve)."""
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _event_date(evento):
    raw = evento.get("recorded_at") or evento.get("timestamp")
    try:
        when = datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        raise Recusa("DENIED", "ID_DATA_INVALIDA", "esquema") from None
    return when.strftime("%Y%m%d")


def derive_event_id(evento):
    """AAAAMMDD mais 12 caracteres do hash canônico do evento SEM o próprio event_id (decisão do proprietário)."""
    corpo = {k: v for k, v in evento.items() if k != "event_id"}
    return f"{_event_date(evento)}-{sha256_hex(canonical(corpo))[:12]}"


def event_path(event_id):
    match = _EVENT_ID.fullmatch(event_id)
    if not match:
        raise Recusa("DENIED", "ID_INVALIDO", "esquema")
    data = match.group(1)
    return f"eventos/{data[:4]}-{data[4:6]}/{event_id}.json"


def _no_duplicate_keys(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError("chave duplicada")
        seen[key] = value
    return seen


def parse_entry(raw):
    """Etapa 1: forma e tamanho. Devolve o dicionário da entrada ou levanta Recusa."""
    if not isinstance(raw, (bytes, bytearray)):
        raise Recusa("DENIED", "ENTRADA_TIPO", "forma")
    if len(raw) > MAX_ENTRY_BYTES:
        raise Recusa("DENIED", "ENTRADA_GRANDE", "forma")
    try:
        entry = json.loads(bytes(raw).decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise Recusa("DENIED", "ENTRADA_INVALIDA", "forma") from None
    if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
        raise Recusa("DENIED", "ENTRADA_CAMPOS", "forma")
    if entry["entrada_versao"] != ENTRY_VERSION or isinstance(entry["entrada_versao"], bool):
        raise Recusa("DENIED", "ENTRADA_VERSAO", "forma")
    origem, evento = entry["origem"], entry["evento"]
    if not isinstance(origem, dict) or set(origem) != ORIGIN_KEYS:
        raise Recusa("DENIED", "ORIGEM_CAMPOS", "forma")
    if origem["agente"] not in AGENTS or origem["escritor"] != DELIVERER:
        raise Recusa("DENIED", "ORIGEM_INVALIDA", "forma")
    if not isinstance(origem["comando_hash"], str) or not _HEX64.fullmatch(origem["comando_hash"]):
        raise Recusa("DENIED", "ORIGEM_HASH", "forma")
    if not isinstance(evento, dict):
        raise Recusa("DENIED", "EVENTO_TIPO", "forma")
    return entry


def check_schema(evento, existing_events, topics):
    """Etapa 2: tipo suportado, esquema validado do projeto (com o contexto já gravado) e id derivado do corpo."""
    if evento.get("type") not in EVENT_TYPES:
        raise Recusa("DENIED", "TIPO_NAO_SUPORTADO", "esquema")
    event_id = evento.get("event_id")
    if not isinstance(event_id, str):
        raise Recusa("DENIED", "ID_AUSENTE", "esquema")
    contexto = [e for e in existing_events if isinstance(e, dict) and e.get("event_id") != event_id]
    try:
        gp1_ingestion.validate_attempt_events(contexto + [evento], topics, allow_private=True)
    except (ValueError, KeyError, TypeError):
        raise Recusa("DENIED", "ESQUEMA_INVALIDO", "esquema") from None
    if derive_event_id(evento) != event_id:
        raise Recusa("DENIED", "ID_DIVERGENTE", "esquema")
    return event_path(event_id)


def check_filter(entry, schema=None):
    """Etapa 3: segredo, dado pessoal, HTML bruto, campo proibido, texto longo e profundidade."""
    reason = agent_commands._scan_params(entry, schema or agent_commands.load_schema())
    if reason:
        raise Recusa("DENIED", "FILTRO_" + reason, "filtro")


def _guarded(etapa, codigo, fn):
    try:
        return fn()
    except Recusa:
        raise
    except guard.PersistenceBlocked:
        raise Recusa("DENIED", codigo, etapa) from None
    except Exception:  # leitura indisponível, resposta malformada, tempo esgotado: fecha
        raise Recusa("DENIED", codigo, etapa) from None


def build_stored(evento, entry, contexto, hash_corpo):
    """Arquivo do histórico: o evento intacto mais o envelope de autoria (S6-R3, S7-R10); sem dado fora do evento."""
    envelope = {
        "origem": entry["origem"]["agente"], "entregue_por": entry["origem"]["escritor"],
        "comando_hash": entry["origem"]["comando_hash"], "escritor": "fluxo",
        "execucao": contexto["execucao"], "validador_sha": contexto["validador_sha"],
        "hash_corpo": hash_corpo,
    }
    return canonical({"evento": evento, "envelope": envelope})


def _existing_same(repo, path, evento):
    atual = repo.ler(path)
    if atual is None:
        return None
    try:
        gravado = json.loads(bytes(atual).decode("utf-8")).get("evento")
    except (UnicodeDecodeError, ValueError, AttributeError):
        raise Recusa("DENIED", "CONFLITO_ID", "idempotencia") from None
    if canonical(gravado) != canonical(evento):
        raise Recusa("DENIED", "CONFLITO_ID", "idempotencia")
    return True


def promover(raw, contexto):
    """Aplica as etapas à entrada `raw` (bytes). `contexto` traz o que é injetado; devolve o resultado, nunca levanta.

    Chaves de `contexto`: agora, alvo, configurado, leitor_visibilidade, leitor_consentimento, escritas_habilitadas,
    repositorio (ler, existentes, criar, ler_de_volta), topicos, validador_sha, validador_sha_fixado, execucao,
    entrada_id (nome do arquivo na fila, só para o registro de rejeição).
    """
    entrada_id = contexto.get("entrada_id")
    entrada_id = entrada_id if isinstance(entrada_id, str) and _ENTRY_NAME.fullmatch(entrada_id) else "invalido"
    agora = contexto.get("agora") or datetime.now(timezone.utc)
    try:
        return _executar(raw, contexto, agora)
    except Recusa as recusa:
        return {"status": recusa.status, "codigo": recusa.codigo, "etapa": recusa.etapa,
                "mantem_na_fila": recusa.status == "NOT_IMPLEMENTED",  # flag desligada: a entrada espera, não é rejeitada
                "rejeicao": rejection_record(entrada_id, recusa.status, recusa.codigo, agora)}
    except Exception:  # defesa final: erro inesperado nunca vira escrita
        return {"status": "DENIED", "codigo": "ERRO_INTERNO", "etapa": "interno",
                "rejeicao": rejection_record(entrada_id, "DENIED", "ERRO_INTERNO", agora)}


def _executar(raw, ctx, agora):
    # 0. o validador em execução é exatamente o fixado
    sha, fixado = ctx.get("validador_sha"), ctx.get("validador_sha_fixado")
    if not (isinstance(sha, str) and isinstance(fixado, str) and _SHA40.fullmatch(sha) and sha == fixado):
        raise Recusa("DENIED", "VALIDADOR_DIVERGENTE", "validador")
    if not (isinstance(ctx.get("execucao"), str) and _RUN.fullmatch(ctx["execucao"])):
        raise Recusa("DENIED", "EXECUCAO_INVALIDA", "validador")
    repo = ctx.get("repositorio")
    if repo is None:
        raise Recusa("DENIED", "REPOSITORIO_AUSENTE", "validador")
    # 1 a 3: forma, esquema e filtro (a entrada inteira passa pelo filtro)
    entry = parse_entry(raw)
    existentes = _guarded("esquema", "HISTORICO_ILEGIVEL", repo.existentes)
    path = check_schema(entry["evento"], existentes, ctx.get("topicos") or [])
    check_filter(entry)
    # 4 a 6: destino, visibilidade e consentimento
    alvo = _guarded("p2", "P2_DESTINO", lambda: guard.check_destination(ctx.get("alvo"), ctx.get("configurado")))
    _guarded("p1", "P1_VISIBILIDADE", lambda: guard.check_visibility(alvo, ctx["leitor_visibilidade"]))
    _guarded("p3", "P3_CONSENTIMENTO", lambda: guard.check_consent(ctx["leitor_consentimento"](), agora))
    # 7. flag: desligada ⇒ nada é promovido
    if ctx.get("escritas_habilitadas") is not True:
        raise Recusa("NOT_IMPLEMENTED", "FLAG_DESLIGADA", "flag")
    # 8. idempotência
    evento = entry["evento"]
    hash_corpo = sha256_hex(canonical(evento))
    ja = _guarded("idempotencia", "LEITURA_FALHOU", lambda: _existing_same(repo, path, evento))
    if ja:
        return {"status": "COMMITTED", "ja_registrado": True, "event_id": evento["event_id"], "path": path,
                "recibo": receipt(evento["event_id"], path, None, hash_corpo, ctx, "COMMITTED")}
    # 9. escrita de UM arquivo novo
    dados = build_stored(evento, entry, ctx, hash_corpo)
    try:
        criado = repo.criar(path, dados)
        commit = criado["commit_sha"]
    except Exception:
        raise Recusa("DENIED", "ESCRITA_FALHOU", "escrita") from None
    # 10. readback: só COMMITTED com SHA do commit e conteúdo conferidos
    try:
        lido = repo.ler_de_volta(path)
        confirmado = (guard.confirm_readback(commit, lido["head_sha"], git_blob_sha(dados), lido["blob_sha"]) == "confirmed"
                      and bytes(lido["conteudo"]) == dados)
    except Exception:
        confirmado = False
    if not confirmado:
        return {"status": "PENDENTE", "codigo": "READBACK_DIVERGENTE", "etapa": "readback", "event_id": evento["event_id"],
                "path": path, "recibo": receipt(evento["event_id"], path, commit, hash_corpo, ctx, "PENDENTE")}
    return {"status": "COMMITTED", "ja_registrado": False, "event_id": evento["event_id"], "path": path,
            "recibo": receipt(evento["event_id"], path, commit, hash_corpo, ctx, "COMMITTED")}


def receipt(event_id, path, commit_sha, hash_corpo, ctx, status):
    """Recibo sem dado do evento: só ids, caminho, SHAs e hash."""
    return {"event_id": event_id, "path": path, "commit_sha": commit_sha, "hash_corpo": hash_corpo, "status": status,
            "validador_sha": ctx["validador_sha"], "execucao": ctx["execucao"]}


def rejection_record(entrada_id, status, codigo, agora):
    """Registro de rejeição: SÓ o código do motivo e o id da entrada (decisão do proprietário)."""
    quando = agora.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if isinstance(agora, datetime) else None
    return {"entrada_id": entrada_id, "status": status, "codigo": codigo, "quando": quando}
