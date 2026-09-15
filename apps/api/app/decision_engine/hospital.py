from dataclasses import dataclass


@dataclass(frozen=True)
class HospitalCandidate:
    code: str
    eta_s: int
    capabilities: frozenset[str]
    resources: dict[str, int | None]
    active: bool = True
    stale_resources: frozenset[str] = frozenset()


@dataclass(frozen=True)
class HospitalDecision:
    code: str
    score: float | None
    rank: int | None
    eligible: bool
    reasons: tuple[str, ...]


def evaluate_hospitals(
    candidates: list[HospitalCandidate],
    required: set[str],
    preferred: set[str],
    capacity_requirements: set[str],
) -> list[HospitalDecision]:
    results: list[HospitalDecision] = []
    for candidate in candidates:
        reasons: list[str] = []
        if not candidate.active:
            reasons.append("HOSPITAL_INACTIVE")
        for code in sorted(required):
            if code in capacity_requirements:
                capacity = candidate.resources.get(code)
                if capacity is None:
                    reasons.append(f"CAPACITY_UNKNOWN:{code}")
                elif capacity < 1:
                    reasons.append(f"RESOURCE_UNAVAILABLE:{code}")
                elif code in candidate.stale_resources:
                    reasons.append(f"STALE_DATA:{code}")
            elif code not in candidate.capabilities:
                reasons.append(f"MISSING_CAPABILITY:{code}")
        if reasons:
            results.append(HospitalDecision(candidate.code, None, None, False, tuple(reasons)))
            continue
        preferred_score = len(preferred & candidate.capabilities) / len(preferred) if preferred else 1.0
        eta_score = 1 - min(candidate.eta_s, 3600) / 3600
        score = 0.30 * eta_score + 0.20 * 1.0 + 0.20 * 0.5 + 0.15 * min((min(candidate.resources.get(code, 1) or 0 for code in capacity_requirements) / 3), 1) + 0.10 * 0.5 + 0.05 * preferred_score
        results.append(HospitalDecision(candidate.code, round(score, 6), None, True, ()))
    eligible = sorted((item for item in results if item.eligible), key=lambda item: (-item.score, next(c.eta_s for c in candidates if c.code == item.code), item.code))
    ranks = {item.code: index for index, item in enumerate(eligible, 1)}
    return [item if not item.eligible else HospitalDecision(item.code, item.score, ranks[item.code], True, item.reasons) for item in results]
