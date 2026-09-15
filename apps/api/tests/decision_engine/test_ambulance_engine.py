from datetime import UTC, datetime

from app.decision_engine.ambulance import AmbulanceCandidate, evaluate_ambulances


def test_ineligible_candidate_has_no_score_or_rank():
    now = datetime.now(UTC)
    result = evaluate_ambulances([AmbulanceCandidate("AMB-001", 100, "AVAILABLE", now, frozenset())], {"VENTILATOR"}, set(), now)
    assert result[0].eligible is False
    assert result[0].score is None
    assert result[0].rank is None


def test_unknown_equipment_is_not_available():
    now = datetime.now(UTC)
    result = evaluate_ambulances([AmbulanceCandidate("AMB-001", 100, "AVAILABLE", now, frozenset())], {"VENTILATOR"}, set(), now)
    assert "MISSING_EQUIPMENT:VENTILATOR" in result[0].reasons


def test_tie_break_eta_then_code():
    now = datetime.now(UTC)
    candidates = [AmbulanceCandidate("AMB-002", 100, "AVAILABLE", now, frozenset({"VENTILATOR"})), AmbulanceCandidate("AMB-001", 100, "AVAILABLE", now, frozenset({"VENTILATOR"}))]
    result = evaluate_ambulances(candidates, {"VENTILATOR"}, set(), now)
    assert [item.code for item in sorted(result, key=lambda item: item.rank or 99)] == ["AMB-001", "AMB-002"]
