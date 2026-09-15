from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import DecisionCandidate, DecisionReason, DecisionRun


def persist_decision(
    session: Session,
    incident_id: UUID,
    decision_type: str,
    algorithm_version: str,
    config_version: str,
    candidates: list[dict],
    freshness: dict | None = None,
) -> DecisionRun:
    run = DecisionRun(
        incident_id=incident_id,
        decision_type=decision_type,
        algorithm_version=algorithm_version,
        config_version=config_version,
        data_freshness=freshness or {},
    )
    session.add(run)
    session.flush()
    for item in candidates:
        candidate = DecisionCandidate(
            decision_run_id=run.id,
            candidate_id=str(item["candidate_id"]),
            eligible=bool(item["eligible"]),
            score=item.get("score"),
            rank=item.get("rank"),
        )
        session.add(candidate)
        session.flush()
        for reason in item.get("reasons", []):
            session.add(DecisionReason(decision_candidate_id=candidate.id, code=reason["code"], detail=reason["detail"]))
    session.commit()
    return run
