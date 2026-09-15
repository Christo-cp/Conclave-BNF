# Pitch Support

## 1. The problem

Emergency coordination is not only a navigation problem. A dispatcher must
match a suitable ambulance, route it, identify a hospital that satisfies the
patient's mandatory requirements, obtain acceptance, and reserve scarce
resources while conditions change.

## 2. What this prototype demonstrates

The system connects those decisions into one auditable coordination loop. Hard
constraints filter candidates before scoring. Hospital capacity remains
unknown when its reading is missing or stale. Reservations are server-side and
transactional, and every critical transition leaves an event or audit record.

## 3. Demo arc

Create emergency -> reject unsuitable ambulance -> select capable ambulance ->
reject unsuitable hospital -> accept a compatible hospital -> reserve ICU ->
start mission -> trigger traffic change -> trigger ICU failure -> reassess ->
reserve a new resource -> complete handover.

## 4. Honest positioning

- Hospital capacity and acceptance are explicitly simulated in this prototype.
- The mock routing provider makes the demo deterministic and works offline.
- This is decision support on synthetic data, not clinical autonomy.
- ML and voice are not presented as production capabilities; S13 is skipped.
- The production path would use authenticated hospital integrations behind the
  same provider/service boundaries.

## 5. Judge answers

**Why not nearest hospital?** Proximity is only one scoring factor. A hospital
that lacks a mandatory capability or has unknown/stale capacity is not eligible.

**What if a bed disappears?** The reservation is released or invalidated under
the resource-loss rules, then the system reassesses and re-ranks feasible
destinations. A destination change is recorded and surfaced.

**Can the model override a hard constraint?** No. The deterministic eligibility
layer runs before scoring, and no recommendation is fabricated when nothing is
feasible.

**Is the data live?** No. The demo is labelled `DEMO MODE`/`SIMULATED`; the
architecture leaves a boundary for authenticated hospital feeds.

**How is double booking prevented?** The reservation path is server-authority,
uses a locked resource transaction, checks capacity, and has database
invariants plus idempotency keys.

**What is production-ready?** The safety-oriented service boundaries, audit
trail, constraints, and provider interfaces are the intended foundation. The
prototype itself still needs real integrations, operational resilience, and
deployment validation.
