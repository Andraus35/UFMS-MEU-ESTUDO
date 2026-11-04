"""Contraprovas dos contratos locais de abertura e fechamento."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from agent_gates import BOOTSTRAP_FILES, HOOK_FILES, check_bootstrap, check_hook_contract
from hooks import before_write, after_write, checkpoint


class AgentGateTests(unittest.TestCase):
    def test_bootstrap_do_repositorio_tem_nove_identidades(self):
        hashes = check_bootstrap(ROOT)
        self.assertEqual(list(hashes), list(BOOTSTRAP_FILES))
        self.assertTrue(all(len(x) == 64 for x in hashes.values()))

    def test_hooks_do_repositorio_tem_interfaces(self):
        self.assertEqual(set(check_hook_contract(ROOT)), set(HOOK_FILES))

    def test_hooks_efetivamente_executam_validacao(self):
        self.assertTrue(before_write.run(ROOT))
        self.assertTrue(after_write.run(ROOT))
        marker = checkpoint.run(ROOT)
        self.assertFalse(marker["persistencia_remota_confirmada"])
        self.assertEqual(marker["event_count"], 0)

    def test_hook_nao_aprova_raiz_ausente(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises((ValueError, OSError, KeyError)):
                before_write.run(Path(tmp))

    def test_bootstrap_rejeita_arquivo_vazio(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = {
                "bootstrap": {"mandatory": list(BOOTSTRAP_FILES)},
                "hooks": {"native_registration_required": True, **HOOK_FILES},
            }
            for name in BOOTSTRAP_FILES:
                file = root / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("fixture", encoding="utf-8")
            (root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
            (root / "AGENTS.md").write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "vazio"):
                check_bootstrap(root)

    def test_hook_sem_interface_run_falha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = {"hooks": {"native_registration_required": True, **HOOK_FILES}}
            (root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
            for name in HOOK_FILES.values():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("print('sem run')\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "sem interface run"):
                check_hook_contract(root)

    def test_configuracao_de_hook_divergente_falha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = {"hooks": {"native_registration_required": True,
                                   **HOOK_FILES, "checkpoint": "hooks/other.py"}}
            (root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
            for name in HOOK_FILES.values():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("def run(): pass\\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "divergente"):
                check_hook_contract(root)


if __name__ == "__main__":
    unittest.main()
