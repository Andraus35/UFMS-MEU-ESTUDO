"""Bootstrap compacto, sem escrita e sem acesso externo."""
import json
import sys

try:
    from core import ROOT, load_json
except ModuleNotFoundError:
    from scripts.core import ROOT, load_json


def run(root=ROOT):
    cfg = load_json(root / "settings.json")
    try:
        from agent_gates import check_bootstrap, check_hook_contract
    except ModuleNotFoundError:
        from scripts.agent_gates import check_bootstrap, check_hook_contract
    digests = check_bootstrap(root)
    check_hook_contract(root)
    state = load_json(root / "state/CURRENT.json")
    concursos = load_json(root / "config/concursos.json")
    return {
        "bootstrap": "verificado_localmente",
        "obrigatorios": cfg["bootstrap"]["mandatory"],
        "sha256_dos_arquivos": digests,
        "roadmap_sha256": digests["ROADMAP.md"],
        "roadmap_bytes": "lidos localmente; compreensão semântica não comprovada",
        "hooks_com_interface": ["before_write", "after_write", "checkpoint"],
        "cargos": [c["codigo"] for c in concursos["cargos"]],
        "prova": concursos["prova_data"],
        "event_count": state["event_count"],
        "last_event": state["event_cursor"],
        "next": "Interpretar ROADMAP.md do HEAD e escolher item RM, depois consultar contexto relevante",
        "warning": "Leitura local não comprova commit remoto nem execução automática de hooks",
    }


if __name__ == "__main__":
    try:
        print(json.dumps(run(), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as exc:
        print(f"FALHA: {exc}", file=sys.stderr)
        sys.exit(1)
