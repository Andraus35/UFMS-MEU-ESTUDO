"""E25: o registro das decisões do proprietário (22 e 23/11/2026) existe, traz as decisões-chave e o HANDOFF aponta para ele. Não é contrato."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "governanca" / "E25_REGISTRO_DE_DECISOES_DO_PROPRIETARIO_20261122_23.md"


class RegistroTeste(unittest.TestCase):
    def test_traz_as_decisoes_chave(self):
        t = DOC.read_text(encoding="utf-8")
        for trecho in ("Não é contrato", "Tutor e Coach dão prompts e instruções à Zapia", "recurso nativo de rotina agendada", "tanto o Tutor quanto o Coach emitem",
                       "não é garantível por código", "AUTORIZO rotina automática agora", "24 h, 5 d, 10 d, 20 d e 30 d", "top 10 de assuntos",
                       "dia 1 do ciclo da matéria", "ciclo independente", "Tutor decide caso a caso", "exclusivamente no Gemini Notebook",
                       "cadernos de acertos e erros feitos no TEC", "D-11", "Mesclar #184", "(PROPOSTA)", "citando PR e head", "E24"):
            self.assertIn(trecho, t, trecho)

    def test_nao_registra_dado_pessoal_nem_token(self):
        t = DOC.read_text(encoding="utf-8").lower()
        for ruim in ("souza.merchan", "ghp_", "github_pat_", "senha:"):
            self.assertNotIn(ruim, t)

    def test_o_handoff_aponta_para_o_registro(self):
        h = (ROOT / "memory" / "HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("E25_REGISTRO_DE_DECISOES_DO_PROPRIETARIO_20261122_23.md", h)
        self.assertLess(len(h.encode("utf-8")), 60 * 1024)


if __name__ == "__main__":
    unittest.main()
