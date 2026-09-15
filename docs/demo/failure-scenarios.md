# Failure Scenarios

Run each from a fresh `.env.demo` reset. These are controlled simulations, not
claims about live hospital or traffic feeds.

| Scenario | Trigger | Expected result |
|---|---|---|
| Hospital rejection | Reject the current acceptance request | Request closes with a reason; hospital is excluded; matching requests the next candidate |
| ICU failure | Mark the reserved ICU unavailable | Reservation is released once; capacity invariant remains valid; reassessment selects another feasible hospital or escalates |
| Ambulance failure | Mark the assigned ambulance unavailable | Assignment is superseded; a new eligible ambulance is selected; dispatcher is notified |
| Traffic change | Increase simulated route traffic | Route comparison runs; a changed destination/route is explained and audited |
| Unknown capacity | Remove or stale a resource reading | Hospital is excluded, never treated as available |
| No feasible candidate | Make all candidates ineligible | Incident becomes `ESCALATED`; no fabricated recommendation is shown |

Record the scenario name, trigger, visible result, and audit/event evidence in
the rehearsal notes. Do not repair a scenario by editing database rows by hand.
