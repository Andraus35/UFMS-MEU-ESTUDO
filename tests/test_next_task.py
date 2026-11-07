import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import next_task  # noqa: E402

QUEUE = [
    {"id": "S1", "title": "um", "roadmap_task": "RM-08", "deliverable": "docs/especificacoes/S1_a.md",
     "depends_on": [], "blocking_inputs": [], "optional_inputs": []},
    {"id": "S2", "title": "dois", "roadmap_task": "RM-08", "deliverable": "docs/especificacoes/S2_b.md",
     "depends_on": ["S1"], "blocking_inputs": [], "optional_inputs": ["x"]},
]


def git(root, *a):
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                   check=True, capture_output=True)


class NextTaskTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)
        (self.root / "state").mkdir()
        (self.root / "docs/especificacoes").mkdir(parents=True)
        self.set_workflow(pr=5)

    def set_workflow(self, pr=5, queue=QUEUE):
        wf = {"active": {"task_id": "RM-08", "branch": "feat/x", "pr_number": pr}, "work_queue": queue}
        (self.root / "state/WORKFLOW.json").write_text(json.dumps(wf), encoding="utf-8")

    def init_git(self, *subjects):
        git(self.root, "init", "-q", "-b", "main")
        for n, subj in enumerate(subjects):
            (self.root / f"f{n}.txt").write_text(str(n))
            git(self.root, "add", "-A")
            git(self.root, "commit", "-q", "-m", subj)

    def test_pr_mesclado_detectado_pelo_historico(self):
        self.init_git("antes", "feat: coisa (#5)")
        c = next_task.compute(self.root)["ciclo"]
        self.assertEqual(c["estado"], "encerrado_recibo_pendente")
        self.assertEqual(len(c["merge_sha"]), 40)

    def test_numero_diferente_nao_conta_como_mesclado(self):
        self.init_git("feat: coisa (#50)", "feat: outra (#15)")
        self.assertEqual(next_task.compute(self.root)["ciclo"]["estado"], "em_andamento")

    def test_sem_git_fica_indeterminado(self):
        self.assertEqual(next_task.compute(self.root)["ciclo"]["estado"], "indeterminado")

    def test_sem_pr_registrado_e_andamento(self):
        self.set_workflow(pr=None)
        self.assertEqual(next_task.compute(self.root)["ciclo"]["estado"], "em_andamento")

    def test_proximo_item_respeita_entrega_e_dependencia(self):
        f = next_task.compute(self.root)["fila"]
        self.assertEqual(f["proximo"]["id"], "S1")
        (self.root / "docs/especificacoes/S1_a.md").write_text("x")
        f = next_task.compute(self.root)["fila"]
        self.assertEqual((f["feitos"], f["proximo"]["id"]), (["S1"], "S2"))
        self.assertEqual(f["proximo"]["insumos_que_melhoram"], ["x"])

    def test_dependencia_nao_atendida_nao_libera_item(self):
        (self.root / "docs/especificacoes/S2_b.md").write_text("x")  # S2 existe, S1 não
        f = next_task.compute(self.root)["fila"]
        self.assertEqual(f["proximo"]["id"], "S1")

    def test_fila_concluida(self):
        for i in QUEUE:
            (self.root / i["deliverable"]).write_text("x")
        f = next_task.compute(self.root)["fila"]
        self.assertIsNone(f["proximo"])
        self.assertIn("concluída", f["acao"])

    def test_repositorio_real_tem_proximo_item(self):
        r = next_task.compute(ROOT)
        self.assertIn(r["ciclo"]["estado"], {"em_andamento", "encerrado_recibo_pendente", "indeterminado"})
        self.assertTrue(r["fila"]["proximo"] is None or r["fila"]["proximo"]["procedimento"])


if __name__ == "__main__":
    unittest.main()
