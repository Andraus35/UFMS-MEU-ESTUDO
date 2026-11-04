"""Configuração auditável da proteção da main, via GitHub CLI autenticado.

Uso:
  python scripts/protect_main.py --plan
  python scripts/protect_main.py --check
  python scripts/protect_main.py --apply --confirm Andraus35/UFMS-MEU-ESTUDO

A aplicação exige permissão administrativa real no GitHub; não é executada
pela CI. Por padrão, zero aprovações obrigatórias evita o deadlock de um único
mantenedor (autores não podem aprovar seus próprios PRs); o PR e a CI ainda
são obrigatórios. --approvals 1 só com revisor independente habilitado.
"""
import argparse
import json
import subprocess
from pathlib import Path

REPOSITORY = "Andraus35/UFMS-MEU-ESTUDO"
ENDPOINT = f"repos/{REPOSITORY}/branches/main/protection"
REQUIRED_CONTEXT = "validate"


def protection_policy(approvals=0):
    if type(approvals) is not int or approvals not in (0, 1):
        raise ValueError("Aprovações permitidas: 0 (manutenção individual) ou 1 (revisor independente)")
    return {
        "required_status_checks": {"strict": True, "contexts": [REQUIRED_CONTEXT]},
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": approvals,
            "require_last_push_approval": False,
        },
        "restrictions": None,
        "required_linear_history": False,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_conversation_resolution": True,
        "lock_branch": False,
        "block_creations": False,
        "allow_fork_syncing": False,
    }


def _enabled(response, key):
    value = response.get(key)
    return value.get("enabled") if isinstance(value, dict) else value


def verify_protection(response, minimum_approvals=0):
    """Valida a resposta autenticada, nunca confunde configuração com aprovação de PR."""
    if not isinstance(response, dict):
        raise ValueError("Resposta de proteção inválida")
    status = response.get("required_status_checks")
    if not isinstance(status, dict) or status.get("strict") is not True:
        raise ValueError("Check obrigatório não é estrito")
    checks = status.get("contexts", [])
    checks += [check.get("context") for check in status.get("checks", []) if isinstance(check, dict)]
    if REQUIRED_CONTEXT not in checks:
        raise ValueError("Check validate não é obrigatório")
    reviews = response.get("required_pull_request_reviews")
    if not isinstance(reviews, dict):
        raise ValueError("PR não é obrigatório")
    if reviews.get("required_approving_review_count", -1) < minimum_approvals:
        raise ValueError("Quantidade de revisões abaixo da política")
    if _enabled(response, "enforce_admins") is not True:
        raise ValueError("Administradores podem contornar a proteção")
    if _enabled(response, "required_conversation_resolution") is not True:
        raise ValueError("Conversas pendentes não estão bloqueadas")
    if _enabled(response, "allow_force_pushes") is not False:
        raise ValueError("Force push está permitido ou desconhecido")
    if _enabled(response, "allow_deletions") is not False:
        raise ValueError("Exclusão de main está permitida ou desconhecida")
    return True


def github_api(method, payload=None):
    cmd = ["gh", "api", "--method", method, ENDPOINT]
    if payload is not None:
        cmd += ["--input", "-"]
    try:
        proc = subprocess.run(
            cmd, input=json.dumps(payload) if payload is not None else None,
            capture_output=True, text=True, timeout=40, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("GitHub CLI indisponível ou sem resposta") from exc
    if proc.returncode != 0:
        raise RuntimeError("GitHub API recusou operação: " + (proc.stderr or "").strip()[:400])
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GitHub API respondeu com JSON inválido") from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm", help="Nome exato do repositório para aplicação administrativa")
    parser.add_argument("--approvals", type=int, choices=(0, 1), default=0)
    args = parser.parse_args()
    expected = protection_policy(args.approvals)
    if args.plan:
        print(json.dumps(expected, indent=2, ensure_ascii=False))
        return
    if args.check:
        verify_protection(github_api("GET"), args.approvals)
        print("OK: main protegida com PR obrigatório, validate estrito e sem bypass administrativo")
        return
    if args.confirm != REPOSITORY:
        parser.error("--apply exige --confirm " + REPOSITORY)
    github_api("PUT", expected)
    verify_protection(github_api("GET"), args.approvals)
    print("OK: proteção aplicada e confirmada por readback autenticado da GitHub API")


if __name__ == "__main__":
    main()
