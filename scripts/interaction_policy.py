"""Política determinística de efeitos para orientação e ferramentas externas.

Este módulo decide autorização; não envia mensagens, não chama conectores e
não concede credenciais. Integração indisponível nunca pode ser reportada como
ação executada.
"""

ORIENTATION = "orientation"
ROUTINE_AUTHORIZED = "routine_authorized"
SENSITIVE = "sensitive"

ALLOWED = "ALLOWED"
DENIED = "DENIED"
NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
NOT_SENT = "NOT_SENT"
PENDING_READBACK = "PENDING_READBACK"
CONFIRMED = "CONFIRMED"


def decide_action(
    action,
    *,
    integration_available=False,
    integration_verified=False,
    scope_authorized=False,
    explicit_approval=False,
):
    """Retorna decisão pura; orientação não herda gates de ferramentas."""
    if action == ORIENTATION:
        return {
            "allowed": True,
            "decision": ALLOWED,
            "effect": "NONE",
            "approval_required": False,
            "reason": "orientação cognitiva sem efeito externo",
        }

    if action not in (ROUTINE_AUTHORIZED, SENSITIVE):
        return {
            "allowed": False,
            "decision": DENIED,
            "effect": "NONE",
            "approval_required": True,
            "reason": "ação desconhecida; bloqueio fail-closed",
        }

    if not integration_available or not integration_verified:
        return {
            "allowed": False,
            "decision": NOT_IMPLEMENTED,
            "effect": "TOOL",
            "approval_required": action == SENSITIVE,
            "reason": "integração ausente ou não verificada",
        }

    if action == ROUTINE_AUTHORIZED:
        if not scope_authorized:
            return {
                "allowed": False,
                "decision": DENIED,
                "effect": "TOOL",
                "approval_required": False,
                "reason": "consentimento prévio de escopo ausente",
            }
        return {
            "allowed": True,
            "decision": ALLOWED,
            "effect": "TOOL",
            "approval_required": False,
            "reason": "rotina autorizada por escopo; sem aprovação por mensagem",
        }

    if not explicit_approval:
        return {
            "allowed": False,
            "decision": DENIED,
            "effect": "TOOL",
            "approval_required": True,
            "reason": "ação sensível exige aprovação humana explícita",
        }

    return {
        "allowed": True,
        "decision": ALLOWED,
        "effect": "TOOL",
        "approval_required": True,
        "reason": "ação sensível aprovada explicitamente",
    }


def delivery_status(
    *,
    integration_available=False,
    integration_verified=False,
    action_performed=False,
    readback_confirmed=False,
):
    """Só confirma entrega após ação real e readback; nunca simula envio."""
    if not integration_available or not integration_verified:
        return NOT_IMPLEMENTED
    if not action_performed:
        return NOT_SENT
    if not readback_confirmed:
        return PENDING_READBACK
    return CONFIRMED
