# Smart Ambulance Routing & Emergency Bed Allocation

Hackathon prototype: decision support on synthetic data, not a clinically
autonomous system. All data is simulated.

The build plan, setup commands and step-by-step exits are in
`docs/executable-plan.md`. Decisions on conflicts between the specs are in
`docs/spec-conflicts.md`.

## Current state

The repository contains an implemented S1-S8 backend foundation, realtime core,
selected S11/S12 services, and Alembic revisions through
`0018_decision_trace_fields`. It includes deterministic simulation seed data,
dispatcher/crew/hospital/demo-controller surfaces, authenticated realtime
events, and the reservation/sweeper lifecycle. The application uses
synthetic data and the mock routing provider for repeatable local
demonstrations. S13 ML and voice are intentionally not built.

## Setup

PowerShell from the repository root:

```powershell
docker compose up -d postgres
$py = ".\apps\api\.venv\Scripts\python.exe"
$env:ENV_FILE = ".env.test"
& $py scripts\reset_demo.py
& $py -m uvicorn app.main:app --app-dir apps\api
pnpm --dir apps/web dev
```

Use separate terminals for the API and web processes. The demo uses
`.env.demo`; tests use `.env.test` and never the demo database.

For the live browser smoke test, keep the API and Postgres running, reset the
test/demo database as appropriate, and run:

```powershell
$env:LIVE_E2E = "1"
pnpm --dir apps/web exec playwright test e2e/live-golden.spec.ts --reporter=list
```

## Verification commands

```powershell
$py = ".\apps\api\.venv\Scripts\python.exe"
& $py -m alembic -c apps\api\alembic.ini heads
& $py -m ruff check apps\api scripts
& $py -m pytest apps\api\tests -v
pnpm --dir apps/web build
$env:ENV_FILE = ".env.test"; & $py scripts\measure_decision_latency.py
```

The latency utility reads `LATENCY_SAMPLE_RUNS` (default `50`) and reports
p50/p95 for the deterministic matcher. It is a local decision-engine measure,
not a claim about production performance. Evidence and known gaps are tracked
in `docs/dod.md` and `docs/measurements.md`.

## Demo and pitch

Run the judge-facing golden scenario from `docs/demo/golden-scenario.md` and
use `docs/pitch/slides.md` for the concise story and judge answers. The demo
must visibly say `DEMO MODE` or `SIMULATED`; no simulated hospital feed is
presented as live clinical data.

## Not built

- S13 ML and voice: FR-023 arrival-time readiness and FR-032 voice control are
  intentionally skipped because no training data is available and no accuracy
  claim is made.
- Production hospital integrations, operational backup/restore, and clinical
  autonomy are outside this synthetic hackathon prototype.
