"""Measure deterministic ambulance matching latency over configured samples."""

from __future__ import annotations

import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from statistics import quantiles

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))

from app.decision_engine.ambulance import AmbulanceCandidate, evaluate_ambulances


def percentile(values: list[float], fraction: float) -> float:
    if len(values) == 1:
        return values[0]
    return quantiles(values, n=100, method="inclusive")[int(fraction * 100) - 1]


def main() -> None:
    samples = int(os.environ.get("LATENCY_SAMPLE_RUNS", "50"))
    if samples < 1:
        raise SystemExit("LATENCY_SAMPLE_RUNS must be at least 1")
    now = datetime.now(UTC)
    candidates = [
        AmbulanceCandidate("AMB-001", 600, "AVAILABLE", now, frozenset({"TRAUMA_KIT"})),
        AmbulanceCandidate("AMB-002", 420, "AVAILABLE", now, frozenset({"TRAUMA_KIT", "VENTILATOR"})),
        AmbulanceCandidate("AMB-003", 300, "DISPATCHED", now, frozenset({"TRAUMA_KIT", "VENTILATOR"})),
    ]
    elapsed_ms: list[float] = []
    for _ in range(samples):
        started = time.perf_counter()
        evaluate_ambulances(candidates, {"TRAUMA_KIT"}, {"VENTILATOR"}, now)
        elapsed_ms.append((time.perf_counter() - started) * 1000)
    print(f"samples={samples}")
    print(f"p50_ms={percentile(elapsed_ms, 0.50):.3f}")
    print(f"p95_ms={percentile(elapsed_ms, 0.95):.3f}")
    print("target=under 2000 ms; synthetic deterministic matcher; not a production benchmark")


if __name__ == "__main__":
    main()
