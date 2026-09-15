# Golden Demo Scenario

This is a human-run guide for the synthetic, deterministic demonstration. Use a
fresh demo reset and keep the `DEMO MODE` or `SIMULATED` labels visible.

## Before the demo

1. Start Docker Desktop and run `docker compose up -d postgres`.
2. In a PowerShell terminal run `$env:ENV_FILE = ".env.demo"; & .\apps\api\.venv\Scripts\python.exe scripts\reset_demo.py`.
3. Start the API with `& .\apps\api\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir apps\api`.
4. Start the web app with `pnpm --dir apps/web dev`.
5. Log in with the synthetic demo users from `app/simulation/seed.py`; the shared password is `demo-password-change-me`.

## Wow sequence

1. Dispatcher creates an emergency with trauma and ventilator requirements.
2. Show the nearest unsuitable ambulance excluded with a reason.
3. Show the eligible ambulance selected and confirm the assignment.
4. Calculate the route and show the route result.
5. Show the nearest hospital excluded because it lacks a mandatory capability or resource.
6. Show the suitable hospital selected with freshness and simulated-data labels.
7. Show ICU and ventilator holds, then have hospital staff accept.
8. Show the confirmed destination without a page reload.
9. Start the mission and trigger the traffic-change simulation event.
10. Show the alternative route and the associated mission/audit event.
11. Trigger ICU failure and show the current reservation released before reassessment.
12. Show hospital re-ranking and the new ICU reservation.
13. Trigger an ambulance failure and show reassignment to an eligible ambulance.
14. Complete the handover and show the final audit trail.

The application must never display unknown capacity as confirmed, select an
ineligible ambulance or hospital, silently change a destination, or present
simulated hospital data as live.

## Expected evidence

- Candidate exclusions include explicit reasons.
- Reservation state changes are visible as `HELD`, `CONFIRMED`, `IN_USE`, or
  `RELEASED` and never exceed capacity.
- A destination change has a mission event, notification, and audit record.
- The UI remains visibly marked `DEMO MODE` or `SIMULATED`.
- The failure path completes without manual database edits.
