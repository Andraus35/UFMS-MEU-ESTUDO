"""Canaries de abstenção e fidelidade (E43): a conferência em três partes classifica o conjunto versionado como esperado. Offline."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import notebook_response_check as nrc  # noqa: E402

FIX = json.loads((ROOT / "tests/fixtures/canaries_notebook_n1.json").read_text(encoding="utf-8"))
FONTE = FIX["fonte_texto"]


def resposta(caso):
    return json.dumps({"texto_literal": caso["texto_literal"], "citacao_trecho": caso["citacao_trecho"]}, ensure_ascii=False).encode("utf-8")


class CanariesTest(unittest.TestCase):
    def test_cada_caso_do_conjunto_tem_o_codigo_esperado(self):
        for c in FIX["casos"]:
            av = nrc.avaliar(resposta(c), FONTE, c["prompt"])
            self.assertEqual(nrc.codigos_da_avaliacao(av, c["contraprova"]), c["esperado"], c["id"])

    def test_o_conjunto_cobre_respondivel_e_nao_respondivel_com_casos_reais_e_sinteticos(self):
        casos = FIX["casos"]
        self.assertGreaterEqual(len(casos), 8)
        self.assertTrue(any(c["contraprova"] for c in casos) and any(not c["contraprova"] for c in casos))
        self.assertEqual({c["origem"] for c in casos}, {"real", "sintetico"})
        self.assertEqual(len({c["id"] for c in casos}), len(casos))
        self.assertTrue(any(c["esperado"] == [] and c["contraprova"] for c in casos))  # há abstenção correta no conjunto

    def test_a_avaliacao_nao_devolve_texto_do_notebook(self):
        for c in FIX["casos"]:
            av = nrc.avaliar(resposta(c), FONTE, c["prompt"])
            self.assertTrue(all(isinstance(v, (bool, int)) for v in av.values()), c["id"])

    def test_entrada_ruim_nao_e_avaliavel(self):
        for ruim in (b"nao e json", b"[]", b'{"texto_literal": 5, "citacao_trecho": ""}', b'{"texto_literal": "x"}'):
            self.assertEqual(nrc.codigos_da_avaliacao(nrc.avaliar(ruim, FONTE), False), ["RESPOSTA_NAO_AVALIAVEL"])

    def test_abstencao_com_conteudo_nao_e_confundida_com_abstencao_limpa(self):
        limpa = next(c for c in FIX["casos"] if c["id"] == "SINT-ABSTENCAO-LIMPA")
        suja = next(c for c in FIX["casos"] if c["id"] == "SINT-ABSTENCAO-COM-NUMERO")
        self.assertEqual(nrc.codigos_da_avaliacao(nrc.avaliar(resposta(limpa), FONTE, limpa["prompt"]), True), [])
        self.assertIn("ABSTENCAO_COM_CONTEUDO_EXTERNO", nrc.codigos_da_avaliacao(nrc.avaliar(resposta(suja), FONTE, suja["prompt"]), True))


if __name__ == "__main__":
    unittest.main()
