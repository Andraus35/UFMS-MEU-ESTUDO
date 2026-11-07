import json
import shutil
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import record_merge_receipt as rec  # noqa: E402

SHA = "a" * 40


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()) / "repo"
        self.addCleanup(shutil.rmtree, self.root.parent, True)
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
        wf = json.loads((self.root / "state/WORKFLOW.json").read_text(encoding="utf-8"))
        self.pr = wf["active"]["pr_number"]
        self.task = wf["active"]["task_id"]

    def args(self, **kw):
        base = dict(merged_pr=self.pr, merged_sha=SHA, new_task="RM-00", new_scope="x", new_branch="feat/n", new_pr=self.pr + 1)
        base.update(kw)
        return Namespace(**base)

    def test_atualiza_so_o_bloco_vigente(self):
        out = rec.plan(self.root, self.args())
        wf = json.loads(out["state/WORKFLOW.json"])
        self.assertEqual(wf["last_merged"], {"task_id": self.task, "pr_number": self.pr, "merge_commit_sha": SHA})
        self.assertEqual(wf["active"]["pr_number"], self.pr + 1)
        for rel in rec.DOCS:
            novo = out[rel]
            antigo = (self.root / rel).read_text(encoding="utf-8")
            self.assertIn(f"Último merge comprovado: PR #{self.pr}; SHA {SHA}", novo)
            self.assertIn(f"PR #{self.pr + 1}**; branch `feat/n`", novo)
            # linhas históricas fora do bloco permanecem idênticas
            fora = lambda t: rec.BLOCK_RE.sub("", t)  # noqa: E731
            self.assertEqual(fora(novo), fora(antigo))

    def test_rejeita_pr_que_nao_e_o_ativo(self):
        with self.assertRaises(ValueError):
            rec.plan(self.root, self.args(merged_pr=self.pr + 40))

    def test_rejeita_sha_invalido(self):
        with self.assertRaises(ValueError):
            rec.plan(self.root, self.args(merged_sha="abc"))

    def test_rejeita_bloco_ausente(self):
        p = self.root / "memory/HANDOFF.md"
        p.write_text(p.read_text(encoding="utf-8").replace("GOVERNANCE-CHECKPOINT:START", "X"), encoding="utf-8")
        with self.assertRaises(ValueError):
            rec.plan(self.root, self.args())

    def test_sem_apply_nao_grava(self):
        antes = (self.root / "ROADMAP.md").read_bytes()
        rc = rec.main(["--root", str(self.root), "--merged-pr", str(self.pr), "--merged-sha", SHA, "--new-task", "RM-00",
                       "--new-scope", "x", "--new-branch", "feat/n", "--new-pr", str(self.pr + 1)])
        self.assertEqual(rc, 0)
        self.assertEqual((self.root / "ROADMAP.md").read_bytes(), antes)


if __name__ == "__main__":
    unittest.main()
