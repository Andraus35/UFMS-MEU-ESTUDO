"""Hook opcional: imprime marcador de checkpoint, sem afirmar persistência GitHub."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    state = json.loads((ROOT / "state/CURRENT.json").read_text(encoding="utf-8"))
    print(json.dumps({"event_cursor": state["event_cursor"], "event_count": state["event_count"], "persistencia_remota_confirmada": False}, ensure_ascii=False))
