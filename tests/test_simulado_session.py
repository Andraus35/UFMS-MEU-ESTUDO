"""Cenários SIM-05..09 e contraprovas das regras de sessão e comparação de simulados."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from simulado_session import classify_independence, combine_session, compare_simulados, diagnose_drop, plan_notebook  # noqa: E402


def att(sim, cargo="523", points=63, **over):
    base = {"simulation_id": sim, "cargo_id": cargo, "points_of_100": points, "source_edital_version": "152/2026",
            "format": "full", "question_count": 60, "question_novelty": "new", "independent_or_guided": "independent",
            "consulted_during": False, "by_area": {"Português": {"correct": 10, "questions": 15},
                                                    "Inglês": {"correct": 3, "questions": 5}}}
    base.update(over)
    return base


class SessaoTests(unittest.TestCase):
    def test_sim05_duas_tentativas_distintas_sem_nota_conjunta(self):
        r = combine_session(att("S1", "523", 63), att("S2", "324", 55), "C1")
        self.assertEqual(r["attempt_ids"], ["S1", "S2"])
        self.assertIsNone(r["official_combined_score"])
        self.assertFalse(r["aggregated"])
        self.assertEqual(r["points_by_attempt"], {"523": 63, "324": 55})

    def test_sim05_contraprovas(self):
        with self.assertRaises(ValueError):
            combine_session(att("S1"), att("S1", "324"), "C1")            # mesmo id
        with self.assertRaises(ValueError):
            combine_session(att("S1"), att("S2", "523"), "C1")            # mesmo cargo
        with self.assertRaises(ValueError):
            combine_session(att("S1"), att("S2", "999"), "C1")            # cargo inválido
        with self.assertRaises(ValueError):
            combine_session(att("S1"), att("S2", "324"), "")              # sem sessão combinada
        with self.assertRaises(ValueError):
            combine_session(att("S1"), None, "C1")

    def test_sim06_queda_nao_prova_fadiga(self):
        r = diagnose_drop(att("S1", "523", 63), att("S2", "324", 40))
        self.assertIsNone(r["cause_inferred"])
        self.assertFalse(r["fatigue_proven"])
        self.assertNotIn("reported_fatigue", r["hypotheses"])
        r2 = diagnose_drop(att("S1"), att("S2", "324"), reported_fatigue="cansado")
        self.assertIn("reported_fatigue", r2["hypotheses"])
        self.assertFalse(r2["fatigue_proven"])
        self.assertIsNone(r2["cause_inferred"])

    def test_sim07_independencia_nunca_e_presumida(self):
        self.assertEqual(classify_independence(att("S"))["label"], "independent")
        casos = {
            "consultou": (att("S", consulted_during=True), "guided"),
            "guiado": (att("S", independent_or_guided="guided"), "guided"),
            "repetidas": (att("S", question_novelty="repeated"), "not_independent_repeated_items"),
            "mistas": (att("S", question_novelty="mixed"), "not_independent_repeated_items"),
            "consulta desconhecida": (att("S", consulted_during=None), "unknown"),
            "sem modo": (att("S", independent_or_guided=None), "unknown"),
            "novidade desconhecida": (att("S", question_novelty="unknown"), "unknown"),
        }
        for nome, (a, esperado) in casos.items():
            with self.subTest(nome):
                r = classify_independence(a)
                self.assertEqual(r["label"], esperado)
                self.assertEqual(r["independent"], esperado == "independent")
        with self.assertRaises(ValueError):
            classify_independence(att("S", question_novelty="inventado"))

    def test_sim08_amostras_equivalentes_dao_so_tendencia_provisoria(self):
        r = compare_simulados(att("A", points=63), att("B", points=70))
        self.assertEqual(r["comparability"], "comparable")
        self.assertEqual(r["claim"], "provisional_trend")
        self.assertEqual(r["delta_points"], 7)
        self.assertFalse(r["sustained_claim_allowed"])

    def test_sim08_amostras_nao_equivalentes_nao_afirmam_melhora_ou_piora(self):
        parcial = compare_simulados(att("A", points=63), att("B", points=80, question_novelty="repeated"))
        self.assertEqual(parcial["comparability"], "partially_comparable")
        self.assertIsNone(parcial["delta_points"])
        self.assertEqual(parcial["claim"], "none")
        self.assertIn("Português", parcial["by_area_delta"])
        formato = compare_simulados(att("A"), att("B", format="partial", question_count=30))
        self.assertIsNone(formato["delta_points"])
        self.assertEqual(formato["claim"], "none")
        for outra in (att("B", cargo_id="324"), att("B", source_edital_version="outra"),
                      att("B", source_edital_version=None)):
            r = compare_simulados(att("A"), outra)
            self.assertEqual(r["comparability"], "not_comparable")
            self.assertIsNone(r["delta_points"])
            self.assertEqual(r["claim"], "none")
        sem_area = compare_simulados(att("A", question_novelty="repeated"),
                                     att("B", by_area={"Legislação": {"correct": 5, "questions": 10}}))
        self.assertEqual(sem_area["comparability"], "not_comparable")
        for r in (parcial, formato, sem_area):
            self.assertFalse(r["sustained_claim_allowed"])

    def test_sim08_independencia_diferente_impede_comparacao_integral(self):
        r = compare_simulados(att("A"), att("B", consulted_during=True))
        self.assertNotEqual(r["comparability"], "comparable")
        self.assertIsNone(r["delta_points"])

    def test_sim09_nao_inventa_disponibilidade(self):
        r = plan_notebook(60)
        self.assertEqual(r["label"], "simulado_parcial")
        self.assertIsNone(r["questions_offered"])
        self.assertFalse(r["official_equivalent"])
        r = plan_notebook(60, 60, availability_confirmed=False)          # número sem confirmação
        self.assertIsNone(r["questions_offered"])
        r = plan_notebook(60, 35, availability_confirmed=True)
        self.assertEqual((r["label"], r["questions_offered"], r["official_equivalent"]), ("simulado_parcial", 35, False))
        r = plan_notebook(60, 60, availability_confirmed=True)
        self.assertEqual((r["label"], r["official_equivalent"]), ("simulado_completo", True))
        r = plan_notebook(30, 100, availability_confirmed=True)
        self.assertEqual((r["label"], r["questions_offered"]), ("simulado_parcial", 30))

    def test_sim09_entradas_invalidas(self):
        for args in ((0,), (-1,), (True,), (60, -1, True), (60, "x", True), (60, 1.5, True)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                plan_notebook(*args)

    def test_modulo_nao_faz_rede_nem_escreve(self):
        src = (ROOT / "scripts/simulado_session.py").read_text(encoding="utf-8")
        for proibido in ("urllib", "requests", "socket", "subprocess", "open(", "write_text", "os.environ"):
            self.assertNotIn(proibido, src)


if __name__ == "__main__":
    unittest.main()
