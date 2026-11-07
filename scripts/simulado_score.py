"""Pontuação ponderada de simulado (cenários SIM-01..04 e SIM-10), offline e sem inferência.

Função pura: não faz rede, não grava nada e não lê arquivos. Pesos e contagens vêm
de uma configuração explícita (`config/concursos.json`). Nunca declara aprovação ou
reprovação: apenas calcula pontos observados e sinaliza restrições a verificar no
edital vigente (as regras do cadastro não estão confirmadas contra retificações).
"""
from fractions import Fraction


def _int(value, label):
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} deve ser inteiro não negativo")
    return value


def _weights(exam_config):
    areas = exam_config.get("areas") if isinstance(exam_config, dict) else None
    if not isinstance(areas, list) or not areas:
        raise ValueError("Configuração sem áreas")
    table = {}
    for area in areas:
        name = area.get("name") if isinstance(area, dict) else None
        if not isinstance(name, str) or not name or name in table:
            raise ValueError("Área da configuração inválida ou duplicada")
        questions, points = _int(area.get("questions"), "questions"), _int(area.get("points"), "points")
        if questions == 0 or points == 0:
            raise ValueError("Área da configuração sem questões ou pontos")
        table[name] = (questions, Fraction(points, questions))
    return table


def _num(value):
    return int(value) if value.denominator == 1 else float(value)


def score_simulado(report, exam_config, *, rectification_pending=False):
    """Calcula pontos ponderados observados; nunca decide aprovação."""
    table = _weights(exam_config)
    max_total = _num(sum(q * w for q, w in table.values()))
    base = {"max_points": max_total, "approval_status": "not_determined",
            "minimum_points_reference": (exam_config.get("shared_exam") or {}).get("minimum_points"),
            "minimum_points_status": "reference_only_unverified"}
    if not isinstance(report, dict):
        raise ValueError("Relatório deve ser objeto")
    if rectification_pending:                                   # SIM-10
        return {**base, "status": "invalidated_pending_edital_check", "points_observed": None,
                "points_of_100": None, "official_equivalent": False,
                "alerts": ["rectification_pending: conferir o edital vigente antes de usar esta simulação"]}
    rows = report.get("areas")
    if rows is None:                                            # SIM-02
        return {**base, "status": "unknown_weighted_score", "points_observed": None,
                "points_of_100": None, "official_equivalent": False,
                "alerts": ["no_area_breakdown: pontuação ponderada desconhecida; nenhum limiar global aplicado"]}
    if not isinstance(rows, list) or not rows:
        raise ValueError("areas deve ser lista não vazia")
    seen, by_area, alerts = set(), {}, []
    points, covered_max, complete = Fraction(0), Fraction(0), True
    for row in rows:
        name = row.get("name") if isinstance(row, dict) else None
        if name not in table or name in seen:
            raise ValueError("Área desconhecida ou duplicada no relatório")
        seen.add(name)
        config_q, weight = table[name]
        questions, correct = _int(row.get("questions"), "questions"), _int(row.get("correct"), "correct")
        if questions == 0 or questions > config_q:
            raise ValueError(f"Contagem de questões incoerente com a configuração: {name}")
        if correct > questions:
            raise ValueError(f"Acertos acima do total de questões: {name}")
        got, cap = correct * weight, questions * weight
        points, covered_max = points + got, covered_max + cap
        complete = complete and questions == config_q
        by_area[name] = {"correct": correct, "questions": questions, "points": _num(got), "max_points": _num(cap)}
        if correct == 0:                                        # SIM-04
            alerts.append(f"zero_area:{name}: possível restrição eliminatória; verificar a regra vigente no edital")
    complete = complete and seen == set(table)
    if not complete:                                            # SIM-03
        alerts.append("partial_exam: não comparável a 100 pontos nem equivalente ao simulado oficial")
    return {**base, "status": "weighted_score" if complete else "partial_weighted_observation",
            "points_observed": _num(points), "max_points_covered": _num(covered_max),
            "points_of_100": _num(points) if complete else None, "official_equivalent": complete,
            "by_area": by_area, "alerts": alerts}
