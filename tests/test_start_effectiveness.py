"""Testes adversariais do START real: leitura de arquivos nao e leitura do modelo."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from bootstrap import run

BASIC = ("AGENTS.md", "ROADMAP.md", "memory/HANDOFF.md", "state/CURRENT.json")
ENGINEERING = BASIC + ("state/WORKFLOW.json",)
FIXTURES = ENGINEERING + ("settings.json", "config/concursos.json",
                         "hooks/before_write.py", "hooks/after_write.py", "hooks/checkpoint.py")


class StartEffectivenessTests(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        for rel in FIXTURES:
            to = root / rel
            to.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, to)
        return temp, root

    def test_estudo_le_exatamente_quatro_arquivos(self):
        receipt = run(ROOT, mode="study")
        self.assertEqual(receipt["obrigatorios"], list(BASIC))
        self.assertEqual(list(receipt["sha256_dos_arquivos"]), list(BASIC))
        self.assertNotIn("state/WORKFLOW.json", receipt["sha256_dos_arquivos"])

    def test_engenharia_le_cinco_arquivos_em_ordem(self):
        receipt = run(ROOT, mode="engineering")
        self.assertEqual(receipt["obrigatorios"], list(ENGINEERING))
        self.assertEqual(list(receipt["sha256_dos_arquivos"]), list(ENGINEERING))
        self.assertEqual(receipt["tarefa_ativa"], "SIM-04")
        self.assertEqual(receipt["pr_ativo"], 9)
        self.assertEqual(receipt["proxima_apos_merge"], "SIM-01")

    def test_receipt_prova_bytes_de_cada_arquivo(self):
        receipt = run(ROOT, mode="engineering")
        for path, digest in receipt["sha256_dos_arquivos"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_missing_workflow_bloqueia_apenas_engenharia(self):
        temp, root = self.fixture()
        with temp:
            (root / "state/WORKFLOW.json").unlink()
            with self.assertRaises((ValueError, OSError)):
                run(root, mode="engineering")
            self.assertEqual(run(root, mode="study")["modo"], "study")

    def test_workflow_corrompido_bloqueia_engenharia(self):
        temp, root = self.fixture()
        with temp:
            (root / "state/WORKFLOW.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                run(root, mode="engineering")

    def test_tarefa_nao_presente_roadmap_bloqueia(self):
        temp, root = self.fixture()
        with temp:
            p = root / "state/WORKFLOW.json"
            data = json.loads(p.read_text(encoding="utf-8"))
            data["active"]["task_id"] = "SIM-99"
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ausente no roadmap"):
                run(root, mode="engineering")

    def test_arquivo_obrigatorio_vazio_bloqueia(self):
        temp, root = self.fixture()
        with temp:
            (root / "memory/HANDOFF.md").write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "vazio"):
                run(root, mode="study")

    def test_ordem_bootstrap_trocada_bloqueia(self):
        temp, root = self.fixture()
        with temp:
            p = root / "settings.json"
            data = json.loads(p.read_text(encoding="utf-8"))
            data["bootstrap"]["mandatory"][0:2] = list(reversed(data["bootstrap"]["mandatory"][0:2]))
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ordem"):
                run(root, mode="engineering")

    def test_modo_desconhecido_nao_autoriza_start(self):
        with self.assertRaisesRegex(ValueError, "Modo"):
            run(ROOT, mode="admin")

    def test_estudo_nao_necessita_estado_de_engenharia(self):
        temp, root = self.fixture()
        with temp:
            (root / "state/WORKFLOW.json").unlink()
            receipt = run(root, mode="study")
            self.assertEqual(receipt["modo"], "study")
            self.assertEqual(len(receipt["sha256_dos_arquivos"]), 4)


if __name__ == "__main__":
    unittest.main()
