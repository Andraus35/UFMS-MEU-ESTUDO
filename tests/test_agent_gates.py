"""Contraprovas dos contratos locais de abertura e fechamento."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from agent_gates import BOOTSTRAP_FILES, HOOK_FILES, check_bootstrap, check_hook_contract, validate_roadmap_text
from hooks import before_write, after_write, checkpoint


class AgentGateTests(unittest.TestCase):
    def test_bootstrap_do_repositorio_tem_dez_identidades(self):
        hashes = check_bootstrap(ROOT)
        self.assertEqual(len(hashes), 10)
        self.assertEqual(BOOTSTRAP_FILES[1], 'ROADMAP.md')
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

    def test_roadmap_ausente_vazio_placeholder_falham(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in BOOTSTRAP_FILES:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture", encoding="utf-8")
            (root / "settings.json").write_text(json.dumps({"bootstrap": {"mandatory": list(BOOTSTRAP_FILES)}}), encoding="utf-8")
            (root / "ROADMAP.md").unlink()
            with self.assertRaisesRegex(ValueError, "ausente"):
                check_bootstrap(root)
            (root / "ROADMAP.md").write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "vazio"):
                check_bootstrap(root)
            (root / "ROADMAP.md").write_text("placeholder", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "truncado/placeholder"):
                check_bootstrap(root)

    def test_roadmap_omitido_ou_fora_de_ordem_falha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ordered = list(BOOTSTRAP_FILES)
            for variant in ([x for x in ordered if x != "ROADMAP.md"],
                            [ordered[0], ordered[2], ordered[1], *ordered[3:]]):
                (root / "settings.json").write_text(json.dumps({"bootstrap": {"mandatory": variant}}), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "ordem"):
                    check_bootstrap(root)

    def test_roadmap_fila_real_integra_e_e_valida(self):
        contents = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertTrue(validate_roadmap_text(contents))

    def test_mutantes_de_fila_nao_podem_passar(self):
        original = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        mutants = (
            original.replace("| RM-10 |", "| RM-09 |"),
            original.replace("| RM-04 |", "| RM-99 |"),
            original.replace("| RM-03 | P1 |", "| RM-03 | P9 |"),
            original.replace("| RM-03 | P1 |", "| RM-03 | P1 |", 1).replace(
                "| planejado |", "| ESTADO_FALSO |", 1),
            original.split("## Fila de execução")[0],
        )
        for mutation in mutants:
            with self.subTest(length=len(mutation)):
                with self.assertRaises(ValueError):
                    validate_roadmap_text(mutation)

    def test_alteracao_estrategica_sem_baseline_rejeitada(self):
        original = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        line = next(line for line in original.splitlines() if line.startswith("| RM-02 |"))
        fields = line.split("|")
        self.assertEqual(fields[4].strip(), "bloqueado")
        variants = []
        for index, value in (
            (2, "P2"),
            (4, "homologado"),
            (5, "Critério aprovado sem resultados, provas ou testes suficientes"),
        ):
            changed = fields.copy()
            changed[index] = " " + value + " "
            variants.append(original.replace(line, "|".join(changed), 1))
        for variant in variants:
            with self.subTest(changed=variant != original):
                with self.assertRaisesRegex(ValueError, "baseline auditada"):
                    validate_roadmap_text(variant)

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
                p.write_text("def run(): pass\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "divergente"):
                check_hook_contract(root)


if __name__ == "__main__":
    unittest.main()
