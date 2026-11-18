"""O HANDOFF é lido inteiro em todo START e o ponto de entrada recusa documento acima de 64 KiB: o orçamento fica fixado em teste."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = (ROOT / "memory" / "HANDOFF.md").read_text(encoding="utf-8")
ARQUIVO = (ROOT / "docs" / "governanca" / "ARQUIVO_HANDOFF_RODADAS_20261118.md").read_text(encoding="utf-8")
LIMITE_DO_BROKER = 64 * 1024
ORCAMENTO = 60 * 1024  # folga de 4 KiB abaixo do limite do ponto de entrada


class OrcamentoDoHandoffTests(unittest.TestCase):
    def test_o_limite_do_broker_e_o_que_este_teste_assume(self):
        fonte = (ROOT / "scripts" / "agent_entrypoint.py").read_text(encoding="utf-8")
        self.assertIn("len(raw) > 64 * 1024", fonte)

    def test_handoff_dentro_do_orcamento(self):
        tamanho = len(HANDOFF.encode("utf-8"))
        self.assertLessEqual(tamanho, ORCAMENTO, f"{tamanho} bytes: arquive rodadas antigas em docs/governanca")
        self.assertLess(ORCAMENTO, LIMITE_DO_BROKER)

    def test_so_as_duas_rodadas_mais_recentes_ficam_no_handoff(self):
        rodadas = re.findall(r"^\*\*Perguntas de fim de rodada, (\w+) \(", HANDOFF, re.M)
        self.assertLessEqual(len(rodadas), 4, rodadas)
        self.assertIn("ARQUIVO_HANDOFF_RODADAS_20261118.md", HANDOFF)

    def test_arquivo_guarda_as_rodadas_antigas_inteiras(self):
        paragrafos = [p for p in ARQUIVO.split("\n\n") if p.startswith("**Perguntas de fim de rodada")]
        self.assertGreaterEqual(len(paragrafos), 14)
        for p in paragrafos:
            self.assertGreater(len(p), 200)
        for trecho in ("reconfirmou o merge só da C3", "reconfirmou o merge só do runner", "hook Stop de perguntas",
                       "décima terceira", "décima sexta", "aceita a recomendação"):
            self.assertIn(trecho, ARQUIVO, trecho)
        self.assertIn("sem alteração", ARQUIVO.lower())


if __name__ == "__main__":
    unittest.main()
