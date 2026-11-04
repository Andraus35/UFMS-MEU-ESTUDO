"""Checkpoint somente leitura; nunca afirma confirmação de commit remoto."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(root=ROOT):
    state = json.loads((Path(root) / "state/CURRENT.json").read_text(encoding="utf-8"))
    return {
        "event_cursor": state["event_cursor"],
        "event_count": state["event_count"],
        "persistencia_remota_confirmada": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
