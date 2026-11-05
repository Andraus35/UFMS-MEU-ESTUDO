"""Valida links e rótulos históricos do índice pedagógico."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "docs/pedagogia/README.md"


class PedagogicalIndexTests(unittest.TestCase):
    def test_todos_os_29_links_locais_continuam_validos(self):
        text = README.read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+)\)", text)
        self.assertEqual(len(links), 29)
        for link in links:
            with self.subTest(link=link):
                self.assertFalse(link.startswith(("http://", "https://", "/")))
                self.assertTrue((README.parent / link).is_file())

    def test_handoffs_e_prompt_antigos_estao_rotulados(self):
        index = README.read_text(encoding="utf-8")
        handoff = (README.parent / "HANDOFF.md").read_text(encoding="utf-8")
        prompt = (README.parent / "PROMPT_TRANSFERENCIA_TECNICA_v1.8.md").read_text(encoding="utf-8")
        self.assertIn("Handoff pedagógico — histórico", index)
        self.assertIn("ARQUIVO HISTÓRICO", handoff)
        self.assertIn("ARQUIVO HISTÓRICO", prompt)
        self.assertIn("PRs #1 e #2 foram integrados", prompt)


if __name__ == "__main__":
    unittest.main()
