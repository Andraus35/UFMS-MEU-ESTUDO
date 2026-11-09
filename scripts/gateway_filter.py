"""Filtro de conteúdo sensível na frente do `ToolGateway` (S4-R4), sem alterar o gateway.

`scripts/tool_gateway.py` e seu teste têm SHA pinado na composição aprovada do GQ-D; por isso o filtro
fica aqui, como invólucro: `guarded_execute(gateway, request, token, ...)` recusa parâmetros com segredo, dado
pessoal heurístico, HTML bruto, campo proibido ou texto longo ANTES de o gateway ver o token ou chamar o
adaptador. Offline, sem estado. Limites: heurístico; só protege quem chamar por aqui (não é trava no gateway).
"""
try:
    import agent_commands
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import agent_commands

SENSITIVE = "SENSITIVE_PARAMETERS"


def check_request(request, schema=None):
    """Devolve o motivo (código do filtro) ou None."""
    if not isinstance(request, dict) or not isinstance(request.get("parameters"), dict):
        return None  # a forma inválida é recusada pelo próprio gateway
    return agent_commands._scan_params(request["parameters"], schema or agent_commands.load_schema())


def guarded_execute(gateway, request, token, **kwargs):
    reason = check_request(request)
    if reason:
        event = request.get("event_id") if isinstance(request, dict) else None
        receipt = {"event_id": event, "decision": "DENIED", "reason_codes": [SENSITIVE], "filter_reason": reason,
                   "effect_performed": False}
        return {"status": "DENIED", "exit_code": 1, "receipt": receipt}
    return gateway.execute(request, token, **kwargs)
