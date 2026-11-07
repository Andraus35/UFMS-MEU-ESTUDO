"""Guard OFFLINE de persistência privada (ADR-013, controles P1-P3, P5, P6).

Lógica pura e fail-closed: não faz rede, não grava nada e não lê credenciais.
A visibilidade do repositório de destino é obtida por um leitor injetado pelo
chamador (em produção, leitura autenticada fora do LLM). Autorização deste guard
é condição NECESSÁRIA, nunca suficiente: a flag `personal_results_writes_enabled`
do settings.json permanece false e só muda por PR próprio com aprovação humana.
"""
import re
from datetime import datetime, timezone

PUBLIC_REPOSITORY = "Andraus35/UFMS-MEU-ESTUDO"
CONSENT_SCOPE = "resultados_estudo"
_REPO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9._-]{1,100}$")
_SHA = re.compile(r"^[0-9a-f]{40}$")


class PersistenceBlocked(ValueError):
    """Escrita pessoal bloqueada; a mensagem indica o controle que falhou."""


def _repo(value, label):
    if not isinstance(value, str) or not _REPO.fullmatch(value):
        raise PersistenceBlocked(f"P2: {label} inválido")
    return value


def _same(a, b):
    return a.casefold() == b.casefold()


def check_destination(target, configured):
    """P2: destino fixo, igual ao configurado e nunca o repositório público."""
    target = _repo(target, "destino")
    configured = _repo(configured, "destino configurado")
    if _same(target, PUBLIC_REPOSITORY) or _same(configured, PUBLIC_REPOSITORY):
        raise PersistenceBlocked("P2: o repositório público não pode receber dados pessoais")
    if not _same(target, configured):
        raise PersistenceBlocked("P2: destino diferente do repositório privado configurado")
    return target


def check_consent(consent, now=None):
    """P3: consentimento explícito, versionado, no escopo e não revogado."""
    if not isinstance(consent, dict):
        raise PersistenceBlocked("P3: consentimento ausente")
    version, scope = consent.get("version"), consent.get("scope")
    if not isinstance(version, str) or not version.strip():
        raise PersistenceBlocked("P3: versão do consentimento ausente")
    if scope != CONSENT_SCOPE:
        raise PersistenceBlocked("P3: escopo do consentimento inválido")
    if consent.get("revoked_at") is not None:
        raise PersistenceBlocked("P3: consentimento revogado")
    granted = consent.get("granted_at")
    try:
        when = datetime.fromisoformat(granted)
    except (TypeError, ValueError):
        raise PersistenceBlocked("P3: data do consentimento inválida") from None
    if when.tzinfo is None:
        raise PersistenceBlocked("P3: data do consentimento sem fuso")
    if when > (now or datetime.now(timezone.utc)):
        raise PersistenceBlocked("P3: consentimento com data futura")
    return version


def check_visibility(target, visibility_reader):
    """P1: leitura autenticada imediata com private=true; qualquer falha bloqueia."""
    try:
        info = visibility_reader(target)
    except Exception:
        raise PersistenceBlocked("P1: leitura de visibilidade indisponível") from None
    if not isinstance(info, dict):
        raise PersistenceBlocked("P1: resposta de visibilidade malformada")
    if info.get("private") is not True:
        raise PersistenceBlocked("P1: repositório de destino não é privado")
    if info.get("visibility") not in (None, "private"):
        raise PersistenceBlocked("P1: visibilidade diferente de private")
    name = info.get("full_name")
    if not isinstance(name, str) or not _same(name, target):
        raise PersistenceBlocked("P1: identidade do repositório divergente")
    return True


def authorize_private_write(target, configured, consent, visibility_reader,
                            writes_enabled, now=None):
    """Autoriza (ou bloqueia) UMA escrita pessoal; ordem fail-closed."""
    if writes_enabled is not True:
        raise PersistenceBlocked("Escrita pessoal desabilitada pela política (flag false)")
    target = check_destination(target, configured)
    version = check_consent(consent, now)
    check_visibility(target, visibility_reader)
    return {"authorized": True, "target": target, "consent_version": version}


def check_new_event(event_id, existing_ids):
    """P5: event_id único (idempotência)."""
    if not isinstance(event_id, str) or not event_id.strip():
        raise PersistenceBlocked("P5: event_id ausente")
    if event_id in set(existing_ids):
        raise PersistenceBlocked("P5: event_id já processado")
    return True


def check_expected_head(expected_head, observed_head):
    """P5: escrita condicional (CAS); HEAD divergente exige reconciliação."""
    for value in (expected_head, observed_head):
        if not isinstance(value, str) or not _SHA.fullmatch(value):
            raise PersistenceBlocked("P5: SHA de HEAD inválido")
    if expected_head != observed_head:
        raise PersistenceBlocked("P5: HEAD divergente; reconciliar sem force-push")
    return True


def confirm_readback(committed_sha, observed_head_sha, expected_content_sha, observed_content_sha):
    """P6: só 'confirmed' com SHA do commit e conteúdo conferidos; senão 'pending'."""
    values = (committed_sha, observed_head_sha, expected_content_sha, observed_content_sha)
    if not all(isinstance(v, str) and _SHA.fullmatch(v) for v in values):
        return "pending"
    if committed_sha != observed_head_sha or expected_content_sha != observed_content_sha:
        return "pending"
    return "confirmed"
