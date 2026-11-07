"""A resposta da Zapia está transcrita de forma íntegra, sem segredos e sem testes executados."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/governanca/RESPOSTA_VERIFICACAO_ZAPIA_20261107.md").read_text(encoding="utf-8")
STATUS = {"OBSERVADO", "DOCUMENTADO", "DESCONHECIDO"}


def entries():
    block = re.search(r"```json\n(.*?)\n```", DOC, re.S).group(1)
    return json.loads(block)


class ZapiaRespostaTests(unittest.TestCase):
    def test_vinte_e_uma_respostas_validas_e_ordenadas(self):
        data = entries()
        self.assertEqual([e["id"] for e in data], [f"Q{n}" for n in range(1, 22)])
        for e in data:
            self.assertIn(e["status"], STATUS, e["id"])
            for campo in ("resposta", "evidencia", "risco"):
                self.assertTrue(e[campo].strip(), f"{e['id']}.{campo}")

    def test_contagem_de_status_confere_com_o_autorrelato(self):
        counts = {s: sum(e["status"] == s for e in entries()) for s in STATUS}
        self.assertEqual(counts, {"OBSERVADO": 15, "DOCUMENTADO": 3, "DESCONHECIDO": 3})

    def test_nenhum_segredo_nem_referencia_de_credencial(self):
        for padrao in (r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"gho_[A-Za-z0-9]{20,}",
                       r"sk-[A-Za-z0-9]{20,}", r"Bearer\\s+[A-Za-z0-9._-]{20,}", r"github_ufms_repo_token"):
            self.assertIsNone(re.search(padrao, DOC), padrao)
        self.assertIn("[nome da credencial omitido]", DOC)

    def test_testes_sinteticos_nao_foram_executados(self):
        self.assertIn("Testes T1, T2 e T3 não foram executados", DOC)
        self.assertIn("autorização literal", DOC)

    def test_registra_a_divergencia_sobre_mcp_e_a_ausencia_de_trava_tecnica(self):
        self.assertIn("a premissa de acesso por MCP", DOC)
        self.assertIn("Não há trava técnica", DOC)
        self.assertIn("**não distingue**", DOC)


if __name__ == "__main__":
    unittest.main()
