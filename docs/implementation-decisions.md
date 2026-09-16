# Implementation Decisions

## 2026-09-16

### Deterministic Routing

`MockRoutingProvider` reads ambulance and hospital ETAs plus route estimates from
the `GOLDEN_2026` simulation scenario. It returns `SIMULATED` metadata and fails
with `ROUTING_PROVIDER_ERROR` when a route is not defined; the application does
not fabricate a constant route.

### Decision Persistence

Ambulance and hospital match runs persist `decision_runs`, candidates, reasons,
input snapshots, freshness configuration, algorithm version, and config version
inside the caller's transaction. The append-only migration protects the history.

### Role Mapping

Backend authorization keeps `HOSPITAL_STAFF` and `HOSPITAL_ADMIN` as canonical
role codes. The frontend may map both to the hospital workspace, but never uses
frontend visibility as authorization.

### Crew Scope

Crew users have a nullable `users.ambulance_id` association. Mission reads and
writes are allowed only when that association matches the mission ambulance;
dispatchers and system admins retain operational access.

### Acceptance And Expiration

Acceptance holds lock every required resource, fail closed on missing/stale/
unknown/unavailable capacity, and expire reservations without committing until
the request and all holds are closed together.

### Realtime Subscription

WebSocket clients must send a non-empty explicit subscription. Empty channels do
not mean subscribe-all. The server keeps the connection alive while handling
commands, events, and heartbeat timeouts; the browser resyncs via REST after
reconnect or version gaps.

### Verification Boundary

Automated backend, database, frontend build/unit, and non-live browser checks are
allowed during implementation. Live browser smoke testing is deliberately left
to the owner and is not run automatically.
