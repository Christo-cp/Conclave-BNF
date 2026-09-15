from app.decision_engine.hospital import HospitalCandidate, evaluate_hospitals


def test_null_capacity_is_excluded():
    result = evaluate_hospitals([HospitalCandidate("H-007", 100, frozenset({"TRAUMA"}), {"ICU": None})], {"TRAUMA", "ICU"}, set(), {"ICU"})
    assert result[0].score is None
    assert "CAPACITY_UNKNOWN:ICU" in result[0].reasons
