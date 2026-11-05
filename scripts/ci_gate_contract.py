"""Gate offline de regressão da configuração CI do harness.

Detecta remoção acidental de etapas obrigatórias e amplia contraprovas.
Limite: o autor com write pode alterar este script junto ao workflow; apenas
proteção GitHub do branch/status de fonte confiável impede esse bypass.
"""
import json
import re
from pathlib import Path

try:
    from core import ROOT
except ModuleNotFoundError:
    from scripts.core import ROOT

REQUIRED_STEPS = (
    ("Validar contrato de segurança da CI", "python scripts/ci_gate_contract.py --check"),
    ("Verificar bloqueio de resultados pessoais", "python scripts/write_policy.py --check"),
    ("Validar roadmap e bootstrap", "python scripts/roadmap_gate.py --check"),
    ("Garantir trabalho serial e PR unico", "python scripts/single_flow_gate.py --remote"),
    ("Validar START controlado de engenharia", "python scripts/bootstrap.py --mode engineering"),
    ("Validar broker read-only com SHA de checkout", "python scripts/agent_entrypoint.py --role engineer --check"),
    ("Validar estrutura e dados", "python scripts/validate.py"),
    ("Testar regras de integridade", "python -m unittest discover -s tests -v"),
    ("Confirmar projeções reproduzíveis", "python scripts/rebuild.py --check"),
)

REDUNDANT_STEPS = (
    ("Validar integridade do edital", "python scripts/chunk_edital.py --check"),
    ("Validar linhas do quadro de vagas", "python scripts/index_vagas.py --check"),
    ("Validar atribuições literais do Anexo IV", "python scripts/index_atribuicoes.py --check"),
    ("Validar proveniência de fontes e alerta de cronograma", "python scripts/validate_fontes_oficiais.py --check"),
)
COMPOSITE_VALIDATIONS = (
    "chunks = check_edital(root)",
    "indexed_vagas = check_vagas(root)",
    "indexed_atribuicoes = check_atribuicoes(root)",
    "official_observations,verified_amendments,open_alerts = check_sources(root)",
)


def verify_composite_validation(root=ROOT, source=None):
    """Garante que validate.py continue executando as quatro validações consolidadas."""
    content = source if source is not None else (Path(root) / "scripts/validate.py").read_text(encoding="utf-8")
    for token in COMPOSITE_VALIDATIONS:
        if content.count(token) != 1:
            raise ValueError("Validação consolidada ausente/duplicada: " + token)
    return True


def verify_workflow(workflow):
    if not isinstance(workflow, str):
        raise ValueError("Workflow inválido")
    for expected in ("on:", "  push:", "  pull_request:",
                     "permissions:", "  contents: read", "  pull-requests: read"):
        if len(re.findall(r"(?m)^" + re.escape(expected) + r"\s*$", workflow)) != 1:
            raise ValueError("Workflow sem gatilho/permissão obrigatória: " + expected.strip())
    if re.search(r"(?m)^\s*contents:\s*write\s*$", workflow):
        raise ValueError("Permissão de escrita no workflow proibida")
    if re.search(r"(?m)^\s*(?:continue-on-error:\s*true|if:\s*(?:false|\$\{\{\s*false\s*\}\}))\s*$", workflow):
        raise ValueError("Bypass explícito de CI detectado")
    for name, command in REQUIRED_STEPS:
        pattern = "      - name: " + name + "\n        run: " + command
        if workflow.count(pattern) != 1:
            raise ValueError("Etapa de CI obrigatória ausente/duplicada: " + name)
    for name, command in REDUNDANT_STEPS:
        if command in workflow:
            raise ValueError("Validação já executada por scripts/validate.py: " + name)
    return True


def verify_security_contract(root=ROOT):
    root = Path(root)
    verify_workflow((root / ".github/workflows/validate.yml").read_text(encoding="utf-8"))
    verify_composite_validation(root)
    settings = json.loads((root / "settings.json").read_text(encoding="utf-8"))
    storage = settings.get("storage", {})
    if storage.get("personal_results_writes_enabled") is not False:
        raise ValueError("Flag de resultados pessoais precisa permanecer false")
    if storage.get("repository_must_be_private_for_personal_results") is not True:
        raise ValueError("Exigência de privacidade desabilitada")
    sources = {
        "scripts/validate.py": ("verify_write_policy(root)", "check_hook_contract(root)"),
        "scripts/rebuild.py": ("verify_write_policy(root)",),
        "scripts/roadmap_gate.py": ("def verify(", "check_bootstrap(root)"),
        "scripts/single_flow_gate.py": ("def validate_local(", "def validate_remote(", "def fetch_open_prs(", "def fetch_pr("),
        "scripts/bootstrap.py": ("def run(", "validate_local(root)", "state/WORKFLOW.json"),
        "scripts/agent_entrypoint.py": ("def verify_start(", "class ReadOnlyAgentBroker:", "def model_context("),
        "scripts/protect_main.py": ("def protection_policy(", "def verify_protection("),
        "scripts/write_policy.py": ("def verify_write_policy(",),
        "scripts/api_write_guard.py": ("def check_proposal(", "def check_readback("),
    }
    for file, tokens in sources.items():
        content = (root / file).read_text(encoding="utf-8")
        if not all(content.count(token) >= 1 for token in tokens):
            raise ValueError("Contrato de segurança ausente: " + file)
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    args = parser.parse_args()
    if args.check:
        verify_security_contract()
        print("OK: configuração básica de CI e bloqueios de privacidade presentes")


if __name__ == "__main__":
    main()
