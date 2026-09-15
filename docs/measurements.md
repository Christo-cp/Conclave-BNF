# Measurements

## Decision latency

Measurement date: 2026-09-15. The command below measures the pure deterministic
ambulance matcher with the configured `LATENCY_SAMPLE_RUNS` count. It does not
include database, HTTP, routing-provider, browser, or network latency.

```powershell
$env:ENV_FILE = ".env.test"
$env:LATENCY_SAMPLE_RUNS = "50"
& .\apps\api\.venv\Scripts\python.exe scripts\measure_decision_latency.py
```

Recorded output from the final verification run:

```text
samples=50
p50_ms=0.009
p95_ms=0.012
target=under 2000 ms; synthetic deterministic matcher; not a production benchmark
```

The sub-millisecond values are rounded to three decimal places and should not
be represented as an end-to-end service SLA. The approved target is decision
calculation under two seconds under demo load. HTTP/database/browser latency was
not measured by this utility.
