"""START local de estudo ou engenharia, sem escrita e sem acesso externo.

O recibo demonstra bytes lidos pelo programa; nao comprova leitura por LLM,
mesma revisao remota do GitHub nem invocacao obrigatoria por qualquer agente.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from core import ROOT, load_json
except ModuleNotFoundError:
    from scripts.core import ROOT, load_json


def run(root=ROOT, mode="study"):
    root = Path(root)
    if mode not in ("study", "engineering"):
        raise ValueError("Modo de START invalido")
    cfg = load_json(root / "settings.json")
    try:
        from agent_gates import check_bootstrap, check_hook_contract
    except ModuleNotFoundError:
        from scripts.agent_gates import check_bootstrap, check_hook_contract
    digests = check_bootstrap(root)
    check_hook_contract(root)
    flow = None
    if mode == "engineering":
        try:
            from single_flow_gate import validate_local
        except ModuleNotFoundError:
            from scripts.single_flow_gate import validate_local
        flow = validate_local(root)
        raw = (root / "state/WORKFLOW.json").read_bytes()
        digests["state/WORKFLOW.json"] = hashlib.sha256(raw).hexdigest()
    state = load_json(root / "state/CURRENT.json")
    concursos = load_json(root / "config/concursos.json")
    result = {
        "bootstrap": "verificado_localmente",
        "modo": mode,
        "obrigatorios": list(digests),
        "sha256_dos_arquivos": digests,
        "roadmap_sha256": digests["ROADMAP.md"],
        "roadmap_bytes": "lidos localmente; compreensao semantica nao comprovada",
        "hooks_com_interface": ["before_write", "after_write", "checkpoint"],
        "cargos": [c["codigo"] for c in concursos["cargos"]],
        "prova": concursos["prova_data"],
        "event_count": state["event_count"],
        "last_event": state["event_cursor"],
        "next": ("Consultar estado remoto do PR registrado: se aberto, continuar a tarefa; se mesclado, aguardar a próxima tarefa."
                 if flow else "Orientar estudos com arquivos relevantes recuperados sob demanda"),
        "warning": "Leitura local nao comprova HEAD remoto ou passagem obrigatoria de agentes externos",
    }
    if flow:
        result.update({
            "tarefa_ativa": flow["active"]["task_id"],
            "pr_ativo": flow["active"]["pr_number"],
            "branch_ativa": flow["active"]["branch"],
            "proxima_apos_merge": flow["next_task_after_merge"],
            "situacao_remota": "nao_verificada_pelo_bootstrap_local",
        })
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("study", "engineering"), default="study")
    args = parser.parse_args()
    try:
        print(json.dumps(run(mode=args.mode), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"FALHA: {exc}", file=sys.stderr)
        sys.exit(1)
