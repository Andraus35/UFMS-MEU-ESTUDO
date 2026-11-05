"""Contraprovas documentais: autonomia cognitiva != bypass de efeitos externos.

Não testa Zapia, gateway ou eficácia pedagógica em produção.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ("ROADMAP.md", "AGENTS.md", "docs/OPERACAO.md")


class AutonomiaContratoTests(unittest.TestCase):
    def test_todos_contratos_distinguem_cognicao_de_efeitos(self):
        for rel in FILES:
            with self.subTest(path=rel):
                content = (ROOT / rel).read_text(encoding="utf-8")
                self.assertIn("## Autonomia cognitiva e gates proporcionais", content)
                for marker in ("ORIENTACAO", "ROTINA_AUTORIZADA", "SENSIVEL"):
                    self.assertIn(marker, content)

    def test_orientacao_nao_exige_aprovacao_individual(self):
        for rel in FILES:
            with self.subTest(path=rel):
                content = (ROOT / rel).read_text(encoding="utf-8").lower()
                self.assertIn("sem aprovação humana por mensagem", content)

    def test_zapia_nao_e_alegada_como_ativa(self):
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("não constitui integração real com Zapia", roadmap)

    def test_rm00_prioriza_gates_de_entrega_sem_estrutura_corporativa(self):
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        row = next(line for line in roadmap.splitlines() if line.startswith("| RM-00 |"))
        self.assertIn("gates automáticos de entrega", row)
        self.assertNotIn("gate independente de workflow alterável", row)
        self.assertIn("O antigo gate P0 de duas Apps", roadmap)

    def test_privacidade_permanece_bloqueada(self):
        import json
        config = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        storage = config["storage"]
        self.assertIs(storage["personal_results_writes_enabled"], False)
        self.assertIs(storage["repository_must_be_private_for_personal_results"], True)


if __name__ == "__main__":
    unittest.main()
