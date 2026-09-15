from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AmbulanceCandidate:
    code: str
    eta_s: int
    status: str
    gps_updated_at: datetime | None
    equipment: frozenset[str]
    active_mission: bool = False


@dataclass(frozen=True)
class AmbulanceDecision:
    code: str
    score: float | None
    rank: int | None
    eligible: bool
    reasons: tuple[str, ...]


def evaluate_ambulances(
    candidates: list[AmbulanceCandidate],
    required_equipment: set[str],
    preferred_equipment: set[str],
    now: datetime,
    stale_after_s: int = 60,
) -> list[AmbulanceDecision]:
    results: list[AmbulanceDecision] = []
    for candidate in candidates:
        reasons: list[str] = []
        if candidate.status != "AVAILABLE":
            reasons.append("UNAVAILABLE")
        if candidate.active_mission:
            reasons.append("ACTIVE_MISSION")
        if candidate.gps_updated_at is None or (now - candidate.gps_updated_at).total_seconds() > stale_after_s:
            reasons.append("GPS_STALE")
        missing = sorted(required_equipment - candidate.equipment)
        if missing:
            reasons.append(f"MISSING_EQUIPMENT:{','.join(missing)}")
        if reasons:
            results.append(AmbulanceDecision(candidate.code, None, None, False, tuple(reasons)))
            continue
        preferred_score = len(preferred_equipment & candidate.equipment) / len(preferred_equipment) if preferred_equipment else 1.0
        equipment_score = len(required_equipment & candidate.equipment) / len(required_equipment) if required_equipment else 1.0
        eta_score = 1 - min(candidate.eta_s, 3600) / 3600
        age = (now - candidate.gps_updated_at).total_seconds() if candidate.gps_updated_at else 10**9
        freshness = 1.0 if age <= 15 else 0.6
        score = 0.45 * eta_score + 0.25 * 1.0 + 0.15 * equipment_score + 0.10 * preferred_score + 0.05 * freshness
        results.append(AmbulanceDecision(candidate.code, round(score, 6), None, True, ()))
    eligible = sorted((item for item in results if item.eligible), key=lambda item: (-item.score, next(c.eta_s for c in candidates if c.code == item.code), item.code))
    ranks = {item.code: index for index, item in enumerate(eligible, 1)}
    return [item if not item.eligible else AmbulanceDecision(item.code, item.score, ranks[item.code], True, item.reasons) for item in results]
