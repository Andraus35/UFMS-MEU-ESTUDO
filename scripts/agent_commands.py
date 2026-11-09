#!/usr/bin/env python3
"""Validador OFFLINE dos comandos de Tutor e Coach para a Zapia (PR-013; S4-R1 a S4-R4).

Puro e fail-closed: sem rede, sem arquivo gravado, sem credencial real. O chamador injeta as
chaves de assinatura por origem e o relógio. Aceitar um comando aqui é condição NECESSÁRIA,
nunca suficiente: não executa nada, não autoriza gravação de resultado pessoal
(`personal_results_writes_enabled` segue falso) e não prova que a Zapia usa este validador.

Assinatura, por origem (o algoritmo é fixado pela configuração de chaves, nunca pela mensagem, o que
impede rebaixamento): `("ed25519", chave_pública_de_32_bytes)` é a recomendada, pois a Zapia só guarda
chave pública; `("hmac", segredo)` e a forma antiga `bytes` (HMAC) continuam aceitas.

Limites declarados:
- A assinatura só impede forja por quem NÃO tem a chave que assina (a privada, no Ed25519; o segredo, no
  HMAC); se ela estiver ao alcance do modelo, a restrição volta a ser protocolo (E-04, OPEN-09).
  Gestão de chaves está fora daqui.
- O filtro de dados pessoais é heurístico (CPF, e-mail, segredos, HTML, nomes de campo e tamanho);
  não detecta texto integral de questão escrito em prosa curta nem todo dado pessoal.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import ed25519_pure
    from agents_gate import COACH_ONLY, SHARED, TUTOR_ONLY
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import ed25519_pure
    from scripts.agents_gate import COACH_ONLY, SHARED, TUTOR_ONLY

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "config" / "agent_command_schema.json"
OPERATIONS = {"tutor": SHARED | TUTOR_ONLY, "coach": SHARED | COACH_ONLY}

ACCEPTED = "ACCEPTED"
DUPLICATE = "DUPLICATE"  # mesma operação já aceita: não executar de novo
DENIED = "DENIED"

_CPF_FMT = re.compile(r"(?<!\d)\d{3}\.\d{3}\.\d{3}-\d{2}(?!\d)")
_DIGITS11 = re.compile(r"(?<!\d)\d{11}(?!\d)")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_SECRET = re.compile(
    r"ghp_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{10,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}"
    r"|Bearer\s+[A-Za-z0-9._~+/=-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)
_HTML = re.compile(r"<\s*(?:!doctype|html|body|head|script|style|div|span|table|iframe|form)\b", re.I)


def load_schema(path: Path = SCHEMA_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _cpf_valid(digits: str) -> bool:
    if len(set(digits)) == 1:
        return False
    for size in (9, 10):
        total = sum(int(d) * w for d, w in zip(digits[:size], range(size + 1, 1, -1)))
        if (total * 10 % 11) % 10 != int(digits[size]):
            return False
    return True


def canonical_bytes(command: dict) -> bytes:
    """Bytes assinados: todos os campos exceto `signature`, em JSON canônico."""
    body = {k: v for k, v in command.items() if k != "signature"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sign(command: dict, key: bytes) -> str:
    return hmac.new(key, canonical_bytes(command), hashlib.sha256).hexdigest()


def sign_ed25519(command: dict, secret: bytes) -> str:
    """Assinatura Ed25519 em hexadecimal (128 caracteres). Para testes e para o código local do agente."""
    return ed25519_pure.sign(secret, canonical_bytes(command)).hex()


def _signature_ok(command: dict, entry) -> bool:
    """Confere a assinatura com o algoritmo FIXADO pela configuração da origem. Fail-closed."""
    signature = command.get("signature")
    if not isinstance(signature, str):
        return False
    if isinstance(entry, (bytes, bytearray)):
        entry = ("hmac", bytes(entry))
    if not (isinstance(entry, tuple) and len(entry) == 2):
        return False
    algorithm, key = entry
    if algorithm == "hmac" and isinstance(key, (bytes, bytearray)) and key:
        return hmac.compare_digest(signature, sign(command, bytes(key)))
    if algorithm == "ed25519" and isinstance(key, (bytes, bytearray)):
        try:
            raw = bytes.fromhex(signature)
        except ValueError:
            return False
        return ed25519_pure.verify(bytes(key), canonical_bytes(command), raw)
    return False


def params_hash(params) -> str:
    raw = json.dumps(params, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _parse_time(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("issued_at deve ser ISO 8601 UTC terminado em Z")
    return datetime.fromisoformat(value[:-1] + "+00:00").astimezone(timezone.utc)


def _scan_params(value, schema, depth=0):
    """Devolve o motivo de recusa ou None."""
    limits = schema["limits"]
    if depth > limits["max_param_depth"]:
        return "PARAMS_PROFUNDOS"
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                return "PARAMS_CHAVE_INVALIDA"
            if key.strip().lower() in schema["forbidden_param_keys"]:
                return "PARAMS_CAMPO_PROIBIDO"
            reason = _scan_params(item, schema, depth + 1)
            if reason:
                return reason
    elif isinstance(value, list):
        for item in value:
            reason = _scan_params(item, schema, depth + 1)
            if reason:
                return reason
    elif isinstance(value, str):
        if len(value) > limits["max_param_string_chars"]:
            return "PARAMS_TEXTO_LONGO"
        if _SECRET.search(value):
            return "PARAMS_SEGREDO"
        if _HTML.search(value):
            return "PARAMS_HTML_BRUTO"
        if _EMAIL.search(value):
            return "PARAMS_DADO_PESSOAL"
        for match in _CPF_FMT.findall(value):
            return "PARAMS_DADO_PESSOAL"
        for match in _DIGITS11.findall(value):
            if _cpf_valid(match):
                return "PARAMS_DADO_PESSOAL"
    elif value is not None and not isinstance(value, (bool, int, float)):
        return "PARAMS_TIPO_INVALIDO"
    return None


class CommandLedger:
    """Registro em memória de nonce e idempotência. Só avança quando o comando é aceito.

    Em produção o registro precisa ser durável e atômico (ver scripts/tool_gateway.py);
    aqui serve para provar a regra sem rede nem disco."""

    def __init__(self):
        self.nonces: set[str] = set()
        self.keys: dict[str, str] = {}

    def commit(self, nonce: str, key: str, body_hash: str) -> None:
        self.nonces.add(nonce)
        self.keys[key] = body_hash


def _deny(code, detail=""):
    return {"decision": DENIED, "code": code, "detail": detail}


def validate_command(command, *, keys: dict, now: datetime, ledger: CommandLedger, schema: dict | None = None) -> dict:
    """Valida um comando. Nunca levanta exceção para entrada ruim; nada é registrado em recusa."""
    schema = schema or load_schema()
    limits = schema["limits"]
    if not isinstance(command, dict):
        return _deny("COMANDO_NAO_OBJETO")
    try:
        size = len(json.dumps(command, ensure_ascii=False).encode("utf-8"))
    except (TypeError, ValueError):
        return _deny("COMANDO_NAO_SERIALIZAVEL")
    if size > limits["max_command_bytes"]:
        return _deny("COMANDO_GRANDE")
    required = set(schema["required_fields"])
    if set(command) != required:
        return _deny("CAMPOS_FORA_DO_ESQUEMA", ",".join(sorted(set(command) ^ required)))
    if command["schema_version"] != schema["schema_version"]:
        return _deny("VERSAO_DESCONHECIDA")
    origin = command["origin"]
    if origin not in schema["origins"] or origin not in keys:
        return _deny("ORIGEM_DESCONHECIDA")
    if not _signature_ok(command, keys[origin]):
        return _deny("ASSINATURA_INVALIDA")
    try:
        issued = _parse_time(command["issued_at"])
    except (ValueError, TypeError):
        return _deny("DATA_INVALIDA")
    if abs((now - issued).total_seconds()) > limits["time_window_seconds"]:
        return _deny("FORA_DA_JANELA")
    operation = command["operation"]
    if operation not in OPERATIONS[origin]:
        return _deny("OPERACAO_FORA_DO_PERFIL")
    if command["destination"] != schema["destinations"].get(operation):
        return _deny("DESTINO_NAO_DESIGNADO")
    key, nonce = command["idempotency_key"], command["nonce"]
    if not isinstance(key, str) or not re.fullmatch(limits["idempotency_key_pattern"], key):
        return _deny("CHAVE_IDEMPOTENCIA_INVALIDA")
    if not isinstance(nonce, str) or not re.fullmatch(limits["nonce_pattern"], nonce):
        return _deny("NONCE_INVALIDO")
    params = command["params"]
    if not isinstance(params, dict):
        return _deny("PARAMS_NAO_OBJETO")
    reason = _scan_params(params, schema)
    if reason:
        return _deny(reason)
    if nonce in ledger.nonces:
        return _deny("NONCE_REPETIDO")
    body_hash = params_hash({"operation": operation, "destination": command["destination"], "params": params})
    previous = ledger.keys.get(key)
    if previous is not None:
        if previous != body_hash:
            return _deny("CHAVE_REUTILIZADA_COM_OUTRO_CORPO")
        ledger.nonces.add(nonce)  # a repetição legítima consome o nonce, mas não executa de novo
        return {"decision": DUPLICATE, "code": "IDEMPOTENTE", "detail": ""}
    ledger.commit(nonce, key, body_hash)
    return {"decision": ACCEPTED, "code": "OK", "detail": ""}


def check(root: Path = ROOT) -> list[str]:
    """Consistência do esquema com os perfis; sem rede."""
    schema = load_schema(root / "config" / "agent_command_schema.json")
    errs = []
    declared = set(schema["destinations"])
    allowed = set().union(*OPERATIONS.values())
    if declared != allowed:
        errs.append(f"destinos divergem das operações dos perfis: {sorted(declared ^ allowed)}")
    if set(schema["origins"]) != set(OPERATIONS):
        errs.append("origens do esquema divergem dos perfis")
    if schema.get("signature", {}).get("recommended") != "ed25519":
        errs.append("esquema sem a assinatura recomendada (ed25519)")
    for field in ("signature", "nonce", "idempotency_key", "issued_at", "destination", "origin"):
        if field not in schema["required_fields"]:
            errs.append(f"campo obrigatório ausente no esquema: {field}")
    return errs


if __name__ == "__main__":
    problems = check()
    if "--check" in sys.argv[1:]:
        print("OK: esquema de comandos coerente com os perfis" if not problems else "FALHA: " + "; ".join(problems))
        sys.exit(1 if problems else 0)
    print(__doc__)
