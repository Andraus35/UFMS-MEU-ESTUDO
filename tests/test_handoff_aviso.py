"""O aviso de defasagem do checkpoint não pode sumir do HANDOFF (lido em todo START)."""
import unittest
from pathlib import Path

HANDOFF = (Path(__file__).resolve().parents[1] / "memory" / "HANDOFF.md").read_text(encoding="utf-8")


class HandoffAvisoTests(unittest.TestCase):
    def test_aviso_de_defasagem_esta_presente(self):
        for trecho in ("Aviso de defasagem do checkpoint", "defasado", "python scripts/next_task.py", "já foi mesclado",
                       "record_merge_receipt.py"):
            self.assertIn(trecho, HANDOFF, trecho)

    def test_aviso_vem_depois_do_checkpoint_e_antes_do_ponto_de_retomada_detalhado(self):
        fim = HANDOFF.index("GOVERNANCE-CHECKPOINT:END")
        aviso = HANDOFF.index("Aviso de defasagem do checkpoint")
        detalhe = HANDOFF.index("**Em uma frase:**")
        self.assertLess(fim, aviso)
        self.assertLess(aviso, detalhe)


if __name__ == "__main__":
    unittest.main()
