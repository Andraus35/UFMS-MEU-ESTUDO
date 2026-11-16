"""Contrato da S12: pesquisa, requisitos pareados a prova, portas sem volta e nenhuma promessa de eficácia."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S12_CICLO_RETENCAO_RECUPERACAO_PROVA.md").read_text(encoding="utf-8")
TEXTO = DOC.lower()


class SpecS12Tests(unittest.TestCase):
    def test_requisitos_r1_a_r13_cada_um_com_criterio(self):
        linhas = [l for l in DOC.splitlines() if re.match(r"\| S12-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S12-R\d+) ", l).group(1) for l in linhas], [f"S12-R{i}" for i in range(1, 14)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3, l[:30])

    def test_pesquisa_com_confianca_lacunas_e_sem_afirmar_o_que_nao_leu(self):
        pesquisa = DOC.split("## Pesquisa", 1)[1].split("## Ciclo completo", 1)[0]
        self.assertGreaterEqual(len(re.findall(r"https?://", pesquisa)), 15)
        self.assertIn("- **Lacunas:**", pesquisa)
        for trecho in ("não li o artigo original", "hipóteses", "regra de penalidade", "E0, zero eventos"):
            self.assertIn(trecho, pesquisa.replace("**", ""))

    def test_a_regra_de_chute_fica_suspensa_ate_conferir_o_edital(self):
        self.assertIn("a confirmar no edital", TEXTO)
        self.assertIn("suspensa", TEXTO)

    def test_portas_sem_volta_e_flag_de_resultados(self):
        porta = DOC.split("## Portas sem volta", 1)[1].split("## Aceite", 1)[0]
        for trecho in ("D-11", "personal_results_writes_enabled=false", "AGENTS.md"):
            self.assertIn(trecho, porta)
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')

    def test_nao_ha_dado_pessoal_nem_promessa_de_eficacia(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"github_pat_|ghp_")
        self.assertIn("não prova", TEXTO)
        self.assertNotIn("garante aprovação", TEXTO)

    def test_esta_na_fila_com_entrega_existente(self):
        item = next(i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"] if i["id"] == "S12")
        self.assertEqual(item["depends_on"], ["S1", "S2", "S3"])
        self.assertTrue((ROOT / item["deliverable"]).exists())


if __name__ == "__main__":
    unittest.main()
