from datetime import UTC, datetime

from app.decision_engine.ambulance import AmbulanceCandidate, evaluate_ambulances


def test_same_input_same_output():
    now = datetime(2026, 9, 12, tzinfo=UTC)
    candidates = [AmbulanceCandidate("AMB-002", 420, "AVAILABLE", now, frozenset({"VENTILATOR"}))]
    first = evaluate_ambulances(candidates, {"VENTILATOR"}, set(), now)
    second = evaluate_ambulances(candidates, {"VENTILATOR"}, set(), now)
    assert first == second


def test_unknown_requirement_neither_filters_nor_scores():
    now = datetime(2026, 9, 12, tzinfo=UTC)
    candidate = AmbulanceCandidate("AMB-002", 420, "AVAILABLE", now, frozenset({"VENTILATOR"}))
    result = evaluate_ambulances([candidate], set(), {"UNKNOWN"}, now)
    assert result[0].eligible is True
