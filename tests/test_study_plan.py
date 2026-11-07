"""Contraprovas do plano de estudos (Método 4.2 + revisão em 7, 15 e 30 dias)."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from study_plan import generate_plan, load_defaults, load_topics  # noqa: E402

DEFAULTS = load_defaults(ROOT)
TOPICS = load_topics(ROOT, cargo="523")
START, EXAM = "2026-11-09", "2027-01-17"        # segunda-feira; prova prevista no edital
BASE = dict(start_date=START, exam_date=EXAM, topics=TOPICS, daily_minutes=240, rest_weekday=6, defaults=DEFAULTS)


def plan(**over):
    args = dict(BASE)
    args.update(over)
    return generate_plan(**args)


def first_study_dates(result):
    out = {}
    for day in result["days"]:
        for item in day["items"]:
            if item["activity"] == "teoria_com_grifos_e_anotacoes":
                out.setdefault(item["topic_id"], date.fromisoformat(day["date"]))
    return out


class StudyPlanTests(unittest.TestCase):
    def test_padrao_do_proprietario_vem_do_settings(self):
        self.assertEqual(DEFAULTS["intervals"], [7, 15, 30])
        self.assertEqual(DEFAULTS["cap"], 120)
        self.assertEqual(DEFAULTS["cycle"], {"theory_days": 4, "review_days": 2, "rest_days": 1})

    def test_deterministico(self):
        self.assertEqual(plan(), plan())

    def test_ciclo_4_2_cada_semana_completa_tem_4_teoria_2_revisao_1_descanso(self):
        result = plan(final_phase_days=0)
        days = result["days"]
        for start in range(0, 7 * 4, 7):                     # quatro primeiras semanas
            kinds = [d["kind"] for d in days[start:start + 7]]
            self.assertEqual(kinds.count("descanso"), 1, kinds)
            self.assertEqual(kinds.count("revisao_semanal"), 2, kinds)
            self.assertEqual(sum(k in ("teoria", "consolidacao") for k in kinds), 4, kinds)
        for d in days:
            if d["kind"] == "descanso":
                self.assertEqual(d["weekday"], 6)
                self.assertEqual(d["items"], [])

    def test_no_maximo_2h_por_disciplina_e_disciplinas_distintas_por_dia_de_teoria(self):
        for d in plan()["days"]:
            if d["kind"] != "teoria":
                continue
            teoria = [i for i in d["items"] if i["activity"] == "teoria_com_grifos_e_anotacoes"]
            disc = [i["disciplina"] for i in teoria]
            self.assertEqual(len(disc), len(set(disc)), d["date"])
            for i in teoria:
                self.assertLessEqual(i["minutes"], DEFAULTS["cap"])

        def teoria_de(minutos):
            dia = next(d for d in plan(daily_minutes=minutos)["days"] if d["kind"] == "teoria")
            return [i["minutes"] for i in dia["items"] if i["activity"] == "teoria_com_grifos_e_anotacoes"]
        self.assertEqual(teoria_de(240), [120, 120])
        self.assertEqual(teoria_de(120), [120])
        self.assertEqual(teoria_de(60), [60])

    def test_revisoes_espacadas_ocorrem_depois_de_7_15_e_30_dias(self):
        result = plan(final_phase_days=0)
        studied = first_study_dates(result)
        found = Counter()
        for d in result["days"]:
            for i in d["items"]:
                if i["activity"] != "revisao_espacada":
                    continue
                n = int(i["interval"].split("+")[1])
                found[i["interval"]] += 1
                self.assertGreaterEqual(date.fromisoformat(d["date"]), studied[i["topic_id"]] + timedelta(days=n))
                self.assertNotEqual(d["kind"], "descanso")
        for label in ("D+7", "D+15", "D+30"):
            self.assertGreater(found[label], 0, label)
        self.assertEqual(found["D+7"], len(studied))        # todo tópico estudado recebe a revisão de 7 dias

    def test_nada_em_descanso_nem_no_dia_da_prova_e_revisoes_antes_da_prova(self):
        result = plan(final_phase_days=14)
        exam = date.fromisoformat(EXAM)
        for d in result["days"]:
            if d["kind"] in ("descanso", "prova"):
                self.assertEqual(d["items"], [], d["date"])
        self.assertEqual(result["days"][-1]["kind"], "prova")
        for d in result["days"]:
            for i in d["items"]:
                if i["activity"] == "revisao_espacada":
                    self.assertLess(date.fromisoformat(d["date"]), exam)

    def test_fase_final_nao_tem_teoria_nem_revisao_espacada(self):
        result = plan(final_phase_days=14)
        final_start = date.fromisoformat(EXAM) - timedelta(days=14)
        for d in result["days"]:
            if date.fromisoformat(d["date"]) >= final_start and d["kind"] not in ("descanso", "prova"):
                self.assertEqual(d["kind"], "revisao_final")
                self.assertTrue(all(i["activity"] != "revisao_espacada" for i in d["items"]))
        self.assertTrue(any(u["reason"].startswith("absorvida") for u in plan(final_phase_days=40)["unscheduled_reviews"]))

    def test_prioridade_antecipa_o_topico(self):
        sem = first_study_dates(plan())
        com = first_study_dates(plan(priorities={TOPICS[-1]["topic_id"]: 5}))
        self.assertLess(com[TOPICS[-1]["topic_id"]], sem[TOPICS[-1]["topic_id"]])

    def test_topicos_ja_estudados_nao_voltam_a_teoria_e_vencidas_sao_sinalizadas(self):
        tid = TOPICS[0]["topic_id"]
        result = plan(completed={tid: "2026-10-20"})
        self.assertNotIn(tid, first_study_dates(result))
        vencidas = [u for u in result["unscheduled_reviews"] if u["reason"] == "vencida_antes_do_inicio"]
        self.assertEqual({(u["topic_id"], u["interval"]) for u in vencidas}, {(tid, "D+7"), (tid, "D+15")})
        agendadas = [(d["date"], i["interval"]) for d in result["days"] for i in d["items"]
                     if i["activity"] == "revisao_espacada" and i["topic_id"] == tid]
        self.assertEqual(agendadas[0][1], "D+30")

    def test_meta_de_questoes_so_aparece_se_informada(self):
        self.assertTrue(all("question_target" not in d for d in plan()["days"]))
        alvo = [d["question_target"] for d in plan(weekly_question_target=200)["days"] if d["kind"] == "revisao_semanal"]
        self.assertTrue(alvo and set(alvo) == {100})

    def test_entradas_invalidas(self):
        casos = {
            "prova antes do início": dict(exam_date="2026-11-01"),
            "data inválida": dict(start_date="09/11/2026"),
            "tempo diário curto": dict(daily_minutes=10),
            "tempo diário não inteiro": dict(daily_minutes=120.5),
            "descanso inválido": dict(rest_weekday=7),
            "fase final negativa": dict(final_phase_days=-1),
            "meta inválida": dict(weekly_question_target=0),
            "sem tópicos": dict(topics=[]),
            "tópico duplicado": dict(topics=[TOPICS[0], TOPICS[0]]),
            "prioridade fora da faixa": dict(priorities={TOPICS[0]["topic_id"]: 9}),
            "prioridade de tópico desconhecido": dict(priorities={"X-99": 3}),
            "estudado desconhecido": dict(completed={"X-99": "2026-10-01"}),
            "estudado depois do início": dict(completed={TOPICS[0]["topic_id"]: "2026-11-10"}),
        }
        for nome, over in casos.items():
            with self.subTest(nome), self.assertRaises(ValueError):
                plan(**over)

    def test_settings_adulterado_e_rejeitado(self):
        for mutacao in (lambda p: p.__setitem__("method", "5.1"),
                        lambda p: p["cycle"].__setitem__("theory_days", 5),
                        lambda p: p.__setitem__("review_intervals_days", [30, 15, 7]),
                        lambda p: p.__setitem__("review_intervals_days", [7, 7]),
                        lambda p: p.__setitem__("review_intervals_days", []),
                        lambda p: p.__setitem__("max_minutes_per_discipline_theory", 0)):
            with self.subTest(mutacao=mutacao), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                cfg = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
                mutacao(cfg["study"]["owner_default_plan"])
                (root / "settings.json").write_text(json.dumps(cfg), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_defaults(root)

    def test_sem_efeitos_externos(self):
        src = (ROOT / "scripts/study_plan.py").read_text(encoding="utf-8")
        for proibido in ("urllib", "requests", "socket", "subprocess", "write_text", "os.environ"):
            self.assertNotIn(proibido, src)

    def test_topicos_do_repositorio_cobrem_os_dois_cargos(self):
        self.assertGreater(len(load_topics(ROOT, cargo="324")), 0)
        self.assertGreater(len(load_topics(ROOT)), len(load_topics(ROOT, cargo="523")) - 1)


if __name__ == "__main__":
    unittest.main()
