"""Plano de estudos determinístico: Método 4.2 + revisão espaçada (padrão do proprietário, D-11).

Função pura e offline: não faz rede, não grava nada e não decide pedagogia. Os padrões vêm de
`settings.json` (`study.owner_default_plan`); tudo o que depende do estudante (datas, tempo
diário, dia de descanso, tópicos, prioridades) é parâmetro explícito, nunca presumido. O Tutor
pode ajustar o plano com justificativa; este módulo só calcula o padrão.
"""
import csv
import json
import math
from datetime import date, timedelta
from pathlib import Path

try:
    from core import ROOT
except ModuleNotFoundError:
    from scripts.core import ROOT

CYCLE_DAYS = 7


def load_defaults(root=ROOT):
    cfg = json.loads((Path(root) / "settings.json").read_text(encoding="utf-8"))
    plan = (cfg.get("study") or {}).get("owner_default_plan")
    if not isinstance(plan, dict) or plan.get("method") != "4.2":
        raise ValueError("Padrão do proprietário ausente ou diferente do Método 4.2")
    cycle = plan.get("cycle")
    if cycle != {"theory_days": 4, "review_days": 2, "rest_days": 1}:
        raise ValueError("Ciclo do Método 4.2 alterado")
    intervals = plan.get("review_intervals_days")
    if (not isinstance(intervals, list) or not intervals or any(type(i) is not int or i <= 0 for i in intervals)
            or intervals != sorted(set(intervals))):
        raise ValueError("Intervalos de revisão inválidos")
    cap = plan.get("max_minutes_per_discipline_theory")
    if type(cap) is not int or cap <= 0:
        raise ValueError("Limite por disciplina inválido")
    return {"cycle": cycle, "intervals": intervals, "cap": cap}


def load_topics(root=ROOT, cargo=None):
    path = Path(root) / "config/topics.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    out = []
    for row in rows:
        if cargo is not None and cargo not in row["cargo_ids"].split("|"):
            continue
        out.append({"topic_id": row["topic_id"], "disciplina": row["disciplina"], "titulo": row["titulo"]})
    return out


def _day(value, label):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(label + " deve ser data ISO (AAAA-MM-DD)") from None


def _validate(topics, daily_minutes, rest_weekday, final_phase_days, weekly_question_target, priorities):
    if type(daily_minutes) is not int or daily_minutes < 30:
        raise ValueError("daily_minutes deve ser inteiro de pelo menos 30")
    if type(rest_weekday) is not int or not 0 <= rest_weekday <= 6:
        raise ValueError("rest_weekday deve ser 0 (segunda) a 6 (domingo)")
    if type(final_phase_days) is not int or final_phase_days < 0:
        raise ValueError("final_phase_days deve ser inteiro não negativo")
    if weekly_question_target is not None and (type(weekly_question_target) is not int or weekly_question_target <= 0):
        raise ValueError("weekly_question_target deve ser inteiro positivo ou None")
    if not isinstance(topics, list) or not topics:
        raise ValueError("topics deve ser lista não vazia")
    seen = set()
    for t in topics:
        if not isinstance(t, dict) or not all(isinstance(t.get(k), str) and t[k] for k in ("topic_id", "disciplina")):
            raise ValueError("Tópico inválido")
        if t["topic_id"] in seen:
            raise ValueError("Tópico duplicado: " + t["topic_id"])
        seen.add(t["topic_id"])
    for tid, p in (priorities or {}).items():
        if tid not in seen or type(p) is not int or not 1 <= p <= 5:
            raise ValueError("Prioridade inválida ou de tópico desconhecido: " + str(tid))
    return seen


def generate_plan(*, start_date, exam_date, topics, daily_minutes, rest_weekday, defaults,
                  final_phase_days=0, weekly_question_target=None, priorities=None, completed=None):
    start, exam = _day(start_date, "start_date"), _day(exam_date, "exam_date")
    if exam <= start:
        raise ValueError("A prova deve ser posterior ao início")
    ids = _validate(topics, daily_minutes, rest_weekday, final_phase_days, weekly_question_target, priorities)
    completed = completed or {}
    first_study = {}
    for tid, when in completed.items():
        if tid not in ids:
            raise ValueError("Tópico já estudado desconhecido: " + str(tid))
        first_study[tid] = _day(when, "completed[" + tid + "]")
        if first_study[tid] >= start:
            raise ValueError("Tópico já estudado deve ter data anterior ao início do plano")
    cap, intervals = defaults["cap"], defaults["intervals"]
    slots = max(1, daily_minutes // cap)
    minutes_per_slot = min(cap, daily_minutes // slots)
    order = sorted(range(len(topics)), key=lambda i: (-(priorities or {}).get(topics[i]["topic_id"], 3), i))
    queue = [topics[i] for i in order if topics[i]["topic_id"] not in first_study]
    final_start = exam - timedelta(days=final_phase_days) if final_phase_days else None

    days, by_date = [], {}
    d = start
    while d <= exam:
        entry = {"date": d.isoformat(), "weekday": d.weekday(), "kind": None, "items": []}
        days.append(entry)
        by_date[d] = entry
        d += timedelta(days=1)

    cycle_topics = {}
    final_pool = list(topics)
    final_cursor = 0
    study_position = {}                       # índice do dia de estudo dentro de cada ciclo de 7 dias
    for index, entry in enumerate(days):
        d = date.fromisoformat(entry["date"])
        cycle = index // CYCLE_DAYS
        if d == exam:
            entry["kind"] = "prova"
            continue
        if d.weekday() == rest_weekday:
            entry["kind"] = "descanso"
            continue
        position = study_position.get(cycle, 0)
        study_position[cycle] = position + 1
        if final_start is not None and d >= final_start:
            entry["kind"] = "revisao_final"
            for _ in range(slots):
                topic = final_pool[final_cursor % len(final_pool)]
                final_cursor += 1
                entry["items"].append({"topic_id": topic["topic_id"], "disciplina": topic["disciplina"],
                                       "activity": "recuperacao_ativa_e_questoes", "minutes": minutes_per_slot})
            continue
        if position < 4:                         # dias de teoria
            used, items = set(), []
            for topic in list(queue):
                if len(items) == slots:
                    break
                if topic["disciplina"] in used:
                    continue
                used.add(topic["disciplina"])
                queue.remove(topic)
                items.append({"topic_id": topic["topic_id"], "disciplina": topic["disciplina"],
                              "activity": "teoria_com_grifos_e_anotacoes", "minutes": minutes_per_slot})
                first_study[topic["topic_id"]] = d
                cycle_topics.setdefault(cycle, []).append(topic)
            entry["kind"] = "teoria" if items else "consolidacao"
            entry["items"] = items
        else:                                    # dias de revisão da semana
            week = cycle_topics.get(cycle, [])
            half = math.ceil(len(week) / 2)
            part = week[:half] if position == 4 else week[half:]
            entry["kind"] = "revisao_semanal"
            entry["items"] = [{"topic_id": t["topic_id"], "disciplina": t["disciplina"],
                               "activity": "recuperacao_das_anotacoes_e_questoes", "minutes": None} for t in part]
            if weekly_question_target:
                entry["question_target"] = math.ceil(weekly_question_target / 2)

    unscheduled = []
    for tid in sorted(first_study):
        base = first_study[tid]
        topic = next(t for t in topics if t["topic_id"] == tid)
        for n in intervals:
            target = base + timedelta(days=n)
            label = f"D+{n}"
            if target < start:
                unscheduled.append({"topic_id": tid, "interval": label, "reason": "vencida_antes_do_inicio"})
                continue
            when = target
            while when < exam and by_date[when]["kind"] in ("descanso",):
                when += timedelta(days=1)
            if when >= exam or (final_start is not None and when >= final_start):
                unscheduled.append({"topic_id": tid, "interval": label, "reason": "absorvida_pela_revisao_final_ou_fora_da_janela"})
                continue
            by_date[when]["items"].append({"topic_id": tid, "disciplina": topic["disciplina"],
                                           "activity": "revisao_espacada", "interval": label, "minutes": None})
    return {
        "parameters": {"method": "4.2", "review_intervals_days": intervals,
                       "max_minutes_per_discipline_theory": cap, "start_date": start.isoformat(),
                       "exam_date": exam.isoformat(), "daily_minutes": daily_minutes,
                       "rest_weekday": rest_weekday, "final_phase_days": final_phase_days,
                       "weekly_question_target": weekly_question_target},
        "days": days,
        "unscheduled_reviews": unscheduled,
        "topics_not_reached": [t["topic_id"] for t in queue],
        "note": "Plano padrão (D-11). O Tutor pode ajustá-lo com justificativa; nada aqui é conclusão sobre domínio.",
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True)
    parser.add_argument("--exam", required=True)
    parser.add_argument("--daily-minutes", type=int, required=True)
    parser.add_argument("--rest-weekday", type=int, required=True)
    parser.add_argument("--cargo", default=None)
    parser.add_argument("--final-phase-days", type=int, default=0)
    args = parser.parse_args()
    out = generate_plan(start_date=args.start, exam_date=args.exam, topics=load_topics(cargo=args.cargo),
                        daily_minutes=args.daily_minutes, rest_weekday=args.rest_weekday, defaults=load_defaults(),
                        final_phase_days=args.final_phase_days)
    print(json.dumps(out, ensure_ascii=False, indent=2))
