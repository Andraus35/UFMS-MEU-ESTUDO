"""Gate local determinístico de roadmap. Não prova leitura semântica por IA."""
import argparse
from pathlib import Path
try:
    from agent_gates import BOOTSTRAP_FILES, check_bootstrap
    from core import ROOT
except ModuleNotFoundError:
    from scripts.agent_gates import BOOTSTRAP_FILES, check_bootstrap
    from scripts.core import ROOT

REFERENCES = (
    "AGENTS.md", "README.md", "rules/CORE.md", "memory/INDEX.md",
    "docs/OPERACAO.md", ".github/copilot-instructions.md",
)

def verify(root=ROOT):
    root = Path(root)
    hashes = check_bootstrap(root)
    if len(BOOTSTRAP_FILES) != 10 or BOOTSTRAP_FILES[1] != "ROADMAP.md":
        raise ValueError("Ordem do roadmap divergente")
    for path in REFERENCES:
        if "ROADMAP.md" not in (root / path).read_text(encoding="utf-8"):
            raise ValueError("Referência ao roadmap ausente: " + path)
    return hashes["ROADMAP.md"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    try:
        print("OK: ROADMAP obrigatório; SHA-256=" + verify())
    except (ValueError, OSError, KeyError) as exc:
        raise SystemExit("FALHA: roadmap gate: " + str(exc))
