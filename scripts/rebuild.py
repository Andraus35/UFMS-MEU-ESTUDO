"""Reconstrói projeções do histórico; por padrão, apenas verifica."""
import argparse
import csv
import io
import json
from pathlib import Path

try:
    from core import ROOT, event_rows, load_json, rebuild, topic_rows, validate_events
except ModuleNotFoundError:
    from scripts.core import ROOT, event_rows, load_json, rebuild, topic_rows, validate_events


def render_progress(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=["topic_id", "attempted", "correct", "accuracy", "revision_due_at"])
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def projected_files(root=ROOT):
    settings = load_json(root / "settings.json")
    try:
        from write_policy import verify_write_policy
    except ModuleNotFoundError:
        from scripts.write_policy import verify_write_policy
    verify_write_policy(root)
    topics = topic_rows(root)
    events = event_rows(root)
    validate_events(events, topics, allow_private=settings["storage"].get("personal_results_writes_enabled", False))
    state, rows = rebuild(events, topics, settings["schema_version"])
    return {
        root / "state/CURRENT.json": json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        root / "state/PROGRESS.csv": render_progress(rows),
    }


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="Conferir se as projeções coincidem com os eventos")
    group.add_argument("--write", action="store_true", help="Atualizar as projeções (requer aprovação operacional)")
    args = parser.parse_args()
    mismatches = []
    for path, expected in projected_files().items():
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current.replace("\r\n", "\n") != expected.replace("\r\n", "\n"):
            mismatches.append(str(path.relative_to(ROOT)))
            if args.write:
                path.write_text(expected, encoding="utf-8")
    if mismatches and not args.write:
        parser.error("Projeções desatualizadas: " + ", ".join(mismatches))
    print("OK: projeções verificadas" if not mismatches else "OK: projeções atualizadas: " + ", ".join(mismatches))


if __name__ == "__main__":
    main()
