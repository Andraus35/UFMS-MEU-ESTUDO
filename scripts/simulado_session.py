"""Regras de sessão, independência e comparação de simulados (SIM-05..09), offline e sem inferência.

Funções puras: sem rede, sem escrita, sem arquivos. Seguem `PROTOCOLO_SIMULADOS_v1.4.md`.
Nunca somam provas de cargos distintos, nunca presumem independência, nunca afirmam
causa (fadiga) e nunca declaram tendência sustentada a partir de duas notas.
"""

CARGOS = frozenset({"523", "324"})
NOVELTY = frozenset({"new", "repeated", "mixed", "unknown"})


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} ausente")
    return value


def combine_session(first, second, combined_session_id):
    """SIM-05: duas tentativas distintas vinculadas; nunca nota conjunta oficial."""
    _text(combined_session_id, "combined_session_id")
    if not isinstance(first, dict) or not isinstance(second, dict):
        raise ValueError("Tentativas devem ser objetos")
    ids = (_text(first.get("simulation_id"), "simulation_id"), _text(second.get("simulation_id"), "simulation_id"))
    if ids[0] == ids[1]:
        raise ValueError("As tentativas precisam de identificadores distintos")
    cargos = (first.get("cargo_id"), second.get("cargo_id"))
    if set(cargos) != CARGOS:
        raise ValueError("Ensaio combinado exige uma tentativa do 523 e uma do 324")
    return {"combined_session_id": combined_session_id, "attempt_ids": list(ids),
            "points_by_attempt": {a["cargo_id"]: a.get("points_of_100") for a in (first, second)},
            "official_combined_score": None, "aggregated": False,
            "note": "duas tentativas distintas; nenhuma nota conjunta oficial"}


def diagnose_drop(first, second, reported_fatigue=None):
    """SIM-06: queda no segundo simulado não prova fadiga; lista hipóteses sem eleger causa."""
    for attempt in (first, second):
        if not isinstance(attempt, dict):
            raise ValueError("Tentativas devem ser objetos")
    hypotheses = ["content_difference", "specific_gaps", "sampling_conditions", "execution"]
    out = {"cause_inferred": None, "fatigue_proven": False, "hypotheses": hypotheses,
           "next_step": "comparar conteúdo e condições entre as provas antes de concluir"}
    if reported_fatigue is not None:
        out["hypotheses"] = hypotheses + ["reported_fatigue"]
        out["fatigue_note"] = "fadiga apenas relatada pelo estudante; não é prova de causa"
    return out


def classify_independence(attempt):
    """SIM-07: só é 'independent' com consulta ausente confirmada e itens inéditos; nunca presume."""
    if not isinstance(attempt, dict):
        raise ValueError("Tentativa deve ser objeto")
    mode, consulted, novelty = (attempt.get("independent_or_guided"), attempt.get("consulted_during"),
                                attempt.get("question_novelty"))
    if novelty is not None and novelty not in NOVELTY:
        raise ValueError("question_novelty inválido")
    if consulted is True or mode == "guided":
        return {"label": "guided", "independent": False, "reason": "consulta durante a tentativa"}
    if novelty in ("repeated", "mixed"):
        return {"label": "not_independent_repeated_items", "independent": False,
                "reason": "itens repetidos podem inflar a pontuação"}
    if mode == "independent" and consulted is False and novelty == "new":
        return {"label": "independent", "independent": True, "reason": "sem consulta e itens inéditos informados"}
    return {"label": "unknown", "independent": False, "reason": "dados insuficientes; independência não presumida"}


def compare_simulados(a, b):
    """SIM-08: nota sozinha não sustenta melhora ou piora; separa comparável, parcial e não comparável."""
    for attempt in (a, b):
        if not isinstance(attempt, dict):
            raise ValueError("Tentativas devem ser objetos")
    base = {"claim": "none", "sustained_claim_allowed": False}
    if a.get("cargo_id") != b.get("cargo_id") or a.get("source_edital_version") != b.get("source_edital_version") \
            or not a.get("cargo_id") or not a.get("source_edital_version"):
        return {**base, "comparability": "not_comparable", "delta_points": None, "by_area_delta": {},
                "reason": "cargo ou versão do edital diferentes ou ausentes; preservar resultados em separado"}
    equal = (a.get("format") == b.get("format") and a.get("question_count") == b.get("question_count")
             and a.get("question_novelty") == b.get("question_novelty") == "new"
             and classify_independence(a)["independent"] and classify_independence(b)["independent"])
    shared = {}
    for name, ra in (a.get("by_area") or {}).items():
        rb = (b.get("by_area") or {}).get(name)
        if rb and ra.get("questions") == rb.get("questions") and None not in (ra.get("correct"), rb.get("correct")):
            shared[name] = rb["correct"] - ra["correct"]
    if equal:
        pa, pb = a.get("points_of_100"), b.get("points_of_100")
        delta = None if None in (pa, pb) else pb - pa
        return {**base, "claim": "provisional_trend", "comparability": "comparable", "delta_points": delta,
                "by_area_delta": shared, "reason": "mudança observada é tendência provisória; sem causalidade"}
    if shared:
        return {**base, "comparability": "partially_comparable", "delta_points": None, "by_area_delta": shared,
                "reason": "amostras não equivalentes; afirmar apenas por área com mesma contagem"}
    return {**base, "comparability": "not_comparable", "delta_points": None, "by_area_delta": {},
            "reason": "amostras não equivalentes e sem área em comum; preservar resultados em separado"}


def plan_notebook(requested_questions, available_questions=None, availability_confirmed=False, full_questions=60):
    """SIM-09: sem estoque confirmado, oferecer versão parcial rotulada; nunca inventar disponibilidade."""
    for value, label in ((requested_questions, "requested_questions"), (full_questions, "full_questions")):
        if type(value) is not int or value <= 0:
            raise ValueError(f"{label} deve ser inteiro positivo")
    if available_questions is not None and (type(available_questions) is not int or available_questions < 0):
        raise ValueError("available_questions inválido")
    if not availability_confirmed or available_questions is None:
        return {"format": "simulado_parcial", "label": "simulado_parcial", "questions_offered": None,
                "availability_confirmed": False, "official_equivalent": False,
                "note": "disponibilidade não confirmada na plataforma; quantidade não afirmada"}
    if requested_questions >= full_questions and available_questions >= full_questions:
        return {"format": "completo", "label": "simulado_completo", "questions_offered": full_questions,
                "availability_confirmed": True, "official_equivalent": True, "note": "estoque confirmado"}
    offered = min(requested_questions, available_questions)
    return {"format": "simulado_parcial", "label": "simulado_parcial", "questions_offered": offered,
            "availability_confirmed": True, "official_equivalent": False,
            "note": "estoque insuficiente para o simulado completo; versão parcial rotulada"}
