"""Contraprovas adversariais da regra de uma branch/PR por tarefa."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from single_flow_gate import validate_local, validate_remote

class SingleFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live = validate_local(ROOT)

    def temp_root(self, mutation=None):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        for name in ("ROADMAP.md", "AGENTS.md", "memory/HANDOFF.md"):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / name).read_text(encoding="utf-8"), encoding="utf-8")
        data = copy.deepcopy(self.live)
        if mutation:
            mutation(data)
        state = root / "state/WORKFLOW.json"
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return temp, root

    def test_estado_unico_valido(self):
        self.assertEqual(validate_local(ROOT)["active"]["pr_number"], 9)

    def test_rejeita_varias_frentes_habilitadas(self):
        for key, mutation in (
            ("max_open_pull_requests", 2),
            ("max_active_work_branches", 2),
            ("allow_parallel_work", True),
            ("allow_concurrent_prs", True),
            ("require_previous_merge_before_next", False),
            ("require_head_ci", False),
            ("require_negative_tests_for_high_medium", False),
        ):
            with self.subTest(key=key):
                tmp, root = self.temp_root(lambda d: d["rules"].__setitem__(key, mutation))
                with tmp:
                    with self.assertRaisesRegex(ValueError, "enfraquecida"):
                        validate_local(root)

    def test_rejeita_pr_legado_sem_sha_ou_duplicado(self):
        for mutate in (
            lambda d: d["deferred_pull_requests"][0].__setitem__("sha", ""),
            lambda d: d["deferred_pull_requests"][0].__setitem__("number", 9),
            lambda d: d["deferred_pull_requests"][0].__setitem__("branch", d["active"]["branch"]),
            lambda d: d["deferred_pull_requests"][0].__setitem__("archived_without_merge", False),
        ):
            tmp, root = self.temp_root(mutate)
            with tmp:
                with self.assertRaises(ValueError):
                    validate_local(root)

    def test_rejeita_branch_main_ativa(self):
        tmp, root = self.temp_root(lambda d: d["active"].__setitem__("branch", "main"))
        with tmp:
            with self.assertRaisesRegex(ValueError, "Branch principal"):
                validate_local(root)

    def test_rejeita_tarefa_fora_do_roadmap(self):
        tmp, root = self.temp_root(lambda d: d["active"].__setitem__("task_id", "SIM-99"))
        with tmp:
            with self.assertRaisesRegex(ValueError, "ausente no roadmap"):
                validate_local(root)

    def test_rejeita_ausencia_de_fonte_unica_no_handoff(self):
        tmp, root = self.temp_root()
        with tmp:
            path = root / "memory/HANDOFF.md"
            path.write_text(path.read_text(encoding="utf-8").replace(
                "state/WORKFLOW.json", "estado_vago"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "sem estado único"):
                validate_local(root)

    def pr(self, n=9, branch=None):
        return {"number": n, "head": {"ref": branch or self.live["active"]["branch"]}}

    def check_remote(self, prs, event="pull_request", ref="9/merge", head=None):
        return validate_remote(self.live, prs, event, ref,
                               self.live["active"]["branch"] if head is None else head)

    def test_aceita_um_unico_pr(self):
        self.assertTrue(self.check_remote([self.pr()]))
        self.assertTrue(self.check_remote([self.pr()], event="push",
                                          ref=self.live["active"]["branch"], head=""))

    def test_rejeita_dois_prs_simultaneos(self):
        with self.assertRaisesRegex(ValueError, "Múltiplos PRs"):
            self.check_remote([self.pr(), self.pr(18, "fix/other")])

    def test_rejeita_pr_diferente(self):
        with self.assertRaisesRegex(ValueError, "PR remoto diferente"):
            self.check_remote([self.pr(18, "fix/other")])

    def test_rejeita_branch_de_pr_diferente(self):
        with self.assertRaisesRegex(ValueError, "Branch remota diferente"):
            self.check_remote([self.pr(9, "other/branch")])

    def test_rejeita_push_em_branch_legada(self):
        with self.assertRaisesRegex(ValueError, "fora da única frente"):
            self.check_remote([self.pr()], event="push", ref="fix/other", head="")

    def test_rejeita_pr_evento_de_outra_branch(self):
        with self.assertRaisesRegex(ValueError, "PR concorrente"):
            self.check_remote([self.pr()], head="other/branch")

    def test_rejeita_branch_sem_pr(self):
        with self.assertRaisesRegex(ValueError, "sem PR aberto"):
            self.check_remote([], event="push", ref=self.live["active"]["branch"], head="")

    def test_permite_main_sem_pr_apos_merge(self):
        self.assertTrue(self.check_remote([], event="push", ref="main", head=""))

    def test_rejeita_lista_invalida(self):
        with self.assertRaisesRegex(ValueError, "inválido"):
            self.check_remote(None)

if __name__ == "__main__":
    unittest.main()
