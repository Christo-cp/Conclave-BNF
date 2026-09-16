from app.decision_engine.hospital import HospitalCandidate, evaluate_hospitals


def test_null_capacity_excluded_capacity_unknown():
    result = evaluate_hospitals(
        [HospitalCandidate("H-007", 600, frozenset({"TRAUMA"}), {"ICU": None})],
        {"ICU"},
        set(),
        {"ICU"},
    )
    assert result[0].eligible is False
    assert result[0].reasons == ("CAPACITY_UNKNOWN:ICU",)


def test_stale_resource_is_excluded_by_service_input():
    result = evaluate_hospitals(
        [HospitalCandidate("H-008", 600, frozenset({"TRAUMA"}), {"ICU": 1}, stale_resources=frozenset({"ICU"}))],
        {"ICU"},
        set(),
        {"ICU"},
    )
    assert result[0].eligible is False
    assert result[0].reasons == ("STALE_DATA:ICU",)
