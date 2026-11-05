"""Fail-closed contract tests for scheduled FAPEC single-page monitor.

No live requests, no runner secrets and no scheduling side effects.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/monitor-fapec.yml"

def validate_workflow(text):
    if not isinstance(text, str):
        raise ValueError("Workflow missing")
    for required in (
        "name: Monitorar retificações FAPEC (sonda)",
        "on:\n  schedule:\n    - cron: '17 12 * * *'\n  workflow_dispatch:",
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "timeout-minutes: 8",
        "python scripts/monitor_fapec.py --live",
        "result=$?",
        "if [ \"$result\" -eq 0 ]; then",
        "elif [ \"$result\" -eq 2 ]; then",
        "elif [ \"$result\" -eq 3 ]; then",
        "echo \"::warning::",
    ):
        if text.count(required) != 1 and required != "echo \"::warning::":
            raise ValueError("Required schedule contract missing: " + required)
        if required == "echo \"::warning::" and text.count(required) != 2:
            raise ValueError("Expected manual-review and inconclusive warnings")
    for bad in (
        "contents: write", "pull-requests: write", "issues: write",
        "continue-on-error: true", "git push", "gh issue create",
        "gh pr merge", "repository_dispatch", "curl -X POST",
        "GITHUB_TOKEN:", "secrets.", "actions/upload-artifact",
    ):
        if bad in text:
            raise ValueError("Unexpected privilege or outward write: " + bad)
    if len(re.findall(r"(?m)^\s+exit 1$", text)) != 3:
        raise ValueError("Must fail for needs_review, unverifiable and unknown")
    if re.search(r"(?m)^  push:|^  pull_request:", text):
        raise ValueError("Online monitor must not execute on normal CI")
    if "Acesso" in text or "RETIFICACAO_VERIFICADA" in text:
        raise ValueError("No normative promotion in monitor")
    return True


class FapecScheduleTests(unittest.TestCase):
    def setUp(self):
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_valid_contract_is_read_only(self):
        self.assertTrue(validate_workflow(self.workflow))

    def test_schedule_dropped_rejected(self):
        with self.assertRaisesRegex(ValueError, "Required schedule"):
            validate_workflow(self.workflow.replace("  schedule:", "  disabled:"))

    def test_write_permission_rejected(self):
        with self.assertRaisesRegex(ValueError, "Required schedule|privilege"):
            validate_workflow(self.workflow.replace("contents: read", "contents: write"))

    def test_failure_status_suppression_rejected(self):
        with self.assertRaisesRegex(ValueError, "Must fail"):
            validate_workflow(self.workflow.replace("exit 1", "exit 0", 1))

    def test_secret_or_issue_publishing_rejected(self):
        for injected in ("secrets.GH_TOKEN", "gh issue create", "git push",
                         "contents: write", "continue-on-error: true"):
            with self.subTest(injected=injected):
                with self.assertRaises(ValueError):
                    validate_workflow(self.workflow + "\n" + injected)

    def test_missing_manual_warning_rejected(self):
        with self.assertRaisesRegex(ValueError, "Expected manual"):
            validate_workflow(self.workflow.replace(
                "::warning::Possível publicação FAPEC",
                "::notice::Possível publicação FAPEC"))

    def test_missing_unverifiable_branch_rejected(self):
        with self.assertRaisesRegex(ValueError, "Required schedule"):
            validate_workflow(self.workflow.replace(
                "elif [ \"$result\" -eq 3 ]; then",
                "elif [ \"$result\" -eq 999 ]; then"))

    def test_trigger_push_rejected(self):
        with self.assertRaisesRegex(ValueError, "Online monitor must not execute"):
            validate_workflow(self.workflow + "\n  push:\n")


if __name__ == "__main__":
    unittest.main()
