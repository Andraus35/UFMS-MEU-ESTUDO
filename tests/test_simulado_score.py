"""Cenários SIM-01..04 e SIM-10 e contraprovas da pontuação ponderada de simulado."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from simulado_score import score_simulado  # noqa: E402

CONFIG = json.loads((ROOT / "config/concursos.json").read_text(encoding="utf-8"))


def area(name, correct, questions):
    return {"name": name, "correct": correct, "questions": questions}


FULL = [area("Português", 10, 15), area("Inglês", 3, 5), area("Legislação", 6, 10),
        area("Raciocínio Lógico", 7, 10), area("Conhecimentos Específicos", 12, 20)]


class SimuladoScoreTests(unittest.TestCase):
    def test_sim01_pontuacao_ponderada_63_de_100(self):
        r = score_simulado({"areas": FULL}, CONFIG)
        self.assertEqual(r["status"], "weighted_score")
        self.assertEqual(r["points_of_100"], 63)
        self.assertEqual(r["by_area"]["Legislação"]["points"], 12)
        self.assertEqual(r["by_area"]["Conhecimentos Específicos"]["points"], 24)
        self.assertTrue(r["official_equivalent"])
        self.assertEqual(r["approval_status"], "not_determined")

    def test_sim02_percentual_global_sem_areas_nao_gera_pontuacao(self):
        r = score_simulado({"total_correct": 48, "total_questions": 60}, CONFIG)
        self.assertEqual(r["status"], "unknown_weighted_score")
        self.assertIsNone(r["points_observed"])
        self.assertIsNone(r["points_of_100"])

    def test_sim03_simulado_parcial_nao_e_equivalente_a_100_pontos(self):
        r = score_simulado({"areas": [area("Português", 15, 15), area("Conhecimentos Específicos", 15, 20)]}, CONFIG)
        self.assertEqual(r["status"], "partial_weighted_observation")
        self.assertFalse(r["official_equivalent"])
        self.assertIsNone(r["points_of_100"])
        self.assertEqual(r["points_observed"], 45)
        self.assertEqual(r["max_points_covered"], 55)
        self.assertTrue(any(a.startswith("partial_exam") for a in r["alerts"]))

    def test_sim03_area_com_menos_questoes_tambem_e_parcial(self):
        rows = [dict(row) for row in FULL]
        rows[0]["questions"], rows[0]["correct"] = 10, 10
        r = score_simulado({"areas": rows}, CONFIG)
        self.assertEqual(r["status"], "partial_weighted_observation")
        self.assertIsNone(r["points_of_100"])

    def test_sim04_area_zerada_sinaliza_restricao_sem_declarar_reprovacao(self):
        rows = [area("Português", 15, 15), area("Inglês", 0, 5), area("Legislação", 10, 10),
                area("Raciocínio Lógico", 5, 10), area("Conhecimentos Específicos", 5, 20)]
        r = score_simulado({"areas": rows}, CONFIG)
        self.assertEqual(r["points_of_100"], 55)
        self.assertTrue(any(a.startswith("zero_area:Inglês") for a in r["alerts"]))
        self.assertEqual(r["approval_status"], "not_determined")
        self.assertEqual(r["minimum_points_status"], "reference_only_unverified")

    def test_sim10_regras_retificadas_invalidam_a_simulacao(self):
        r = score_simulado({"areas": FULL}, CONFIG, rectification_pending=True)
        self.assertEqual(r["status"], "invalidated_pending_edital_check")
        self.assertIsNone(r["points_observed"])
        self.assertIsNone(r["points_of_100"])

    def test_contraprovas_de_entrada_invalida(self):
        casos = {
            "acertos acima do total": [area("Português", 16, 15)],
            "questões acima da configuração": [area("Português", 10, 20)],
            "questões zero": [area("Português", 0, 0)],
            "área desconhecida": [area("Matemática", 1, 5)],
            "área duplicada": [area("Português", 1, 15), area("Português", 2, 15)],
            "bool como inteiro": [{"name": "Português", "correct": True, "questions": 15}],
            "negativo": [area("Português", -1, 15)],
            "float": [{"name": "Português", "correct": 1.5, "questions": 15}],
            "lista vazia": [],
        }
        for nome, rows in casos.items():
            with self.subTest(nome), self.assertRaises(ValueError):
                score_simulado({"areas": rows}, CONFIG)
        for report in (None, [], "x"):
            with self.subTest(report=report), self.assertRaises(ValueError):
                score_simulado(report, CONFIG)

    def test_contraprovas_de_configuracao_invalida(self):
        for bad in (None, {}, {"areas": []}, {"areas": [{"name": "A", "questions": 0, "points": 5}]},
                    {"areas": [{"name": "A", "questions": 5, "points": 5}, {"name": "A", "questions": 5, "points": 5}]}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                score_simulado({"areas": FULL}, bad)

    def test_config_do_repositorio_soma_100_pontos_e_60_questoes(self):
        r = score_simulado({"areas": [area(a["name"], a["questions"], a["questions"]) for a in CONFIG["areas"]]}, CONFIG)
        self.assertEqual(r["points_of_100"], 100)
        self.assertEqual(sum(a["questions"] for a in CONFIG["areas"]), CONFIG["shared_exam"]["questions"])

    def test_modulo_nao_faz_rede_nem_escreve(self):
        src = (ROOT / "scripts/simulado_score.py").read_text(encoding="utf-8")
        for proibido in ("urllib", "requests", "socket", "subprocess", "open(", "write_text", "os.environ"):
            self.assertNotIn(proibido, src)


if __name__ == "__main__":
    unittest.main()
