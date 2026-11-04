"""Bootstrap compacto, sem escrita e sem acesso externo."""
import json
import sys

try:
    from core import ROOT, load_json
except ModuleNotFoundError:
    from scripts.core import ROOT, load_json


def run(root=ROOT):
    cfg = load_json(root / "settings.json")
    missing = [p for p in cfg["bootstrap"]["mandatory"] if not (root / p).is_file()]
    if missing:
        raise ValueError("Arquivos obrigatórios ausentes: " + ", ".join(missing))
    state = load_json(root / "state/CURRENT.json")
    concursos = load_json(root / "config/concursos.json")
    return {
        "bootstrap": "verificado_localmente",
        "obrigatorios": cfg["bootstrap"]["mandatory"],
        "cargos": [c["codigo"] for c in concursos["cargos"]],
        "prova": concursos["prova_data"],
        "event_count": state["event_count"],
        "last_event": state["event_cursor"],
        "next": "Consultar regras de estudo, tópicos e eventos relevantes sob demanda",
        "warning": "Leitura local não comprova commit remoto nem execução automática de hooks",
    }


if __name__ == "__main__":
    try:
        print(json.dumps(run(), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as exc:
        print(f"FALHA: {exc}", file=sys.stderr)
        sys.exit(1)
