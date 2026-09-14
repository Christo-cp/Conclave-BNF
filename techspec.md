# MASTER INTEGRATION PROMPT

## Smart Ambulance Routing & Emergency Bed Allocation System

You are the **Lead Software Architect, Senior Full-Stack Engineer, AI/ML Engineer, Database Architect, DevOps Engineer, Security Engineer, QA Engineer, and Technical Product Engineer** responsible for implementing this entire project.

The repository contains the following six specification documents:

```text
plan.md
appflow.md
design.md
prd.md
database.md
techspec.md
```

Your job is to **integrate all six documents into one internally consistent, production-structured hackathon application**.

Do not treat these documents as six unrelated documents.

Treat them as six layers of the same system.

---

# 1. PRIMARY OBJECTIVE

Build the complete:

> **Smart Ambulance Routing & Emergency Bed Allocation System**

The system must demonstrate this complete emergency coordination loop:

```text
Emergency
    ↓
Patient Requirement Assessment
    ↓
Suitable Ambulance Selection
    ↓
Traffic-Aware Routing
    ↓
Hospital Capability Matching
    ↓
Hospital Capacity / Readiness Verification
    ↓
Hospital Acceptance
    ↓
Emergency Resource Reservation
    ↓
Hospital Preparation
    ↓
Live Ambulance Tracking
    ↓
Dynamic ETA / Route Updates
    ↓
Patient Arrival
    ↓
Emergency Handover
```

The system is NOT merely an:

* ambulance tracker
* hospital finder
* map application
* bed dashboard
* chatbot
* AI demo

It is an:

> **End-to-end emergency coordination and decision-support platform.**

---

# 2. DOCUMENT HIERARCHY

You must read and understand all six documents before making architecture or code decisions.

The documents have different responsibilities.

## 2.1 `prd.md`

Treat this as the **product requirements source**.

It defines:

* product vision
* problem
* goals
* users
* requirements
* business rules
* user stories
* acceptance criteria
* non-functional requirements
* product scope
* priorities

---

# 3. `plan.md`

Treat this as the **implementation and project architecture plan**.

It defines:

* implementation phases
* modules
* system architecture
* technical approach
* build order
* API structure
* development strategy
* testing strategy
* deployment strategy
* demo plan

---

# 4. `appflow.md`

Treat this as the **behavioral workflow specification**.

It defines:

* user journeys
* role flows
* screen transitions
* mission lifecycle
* emergency lifecycle
* ambulance workflow
* hospital workflow
* acceptance workflow
* reservation workflow
* failure workflow
* realtime workflow
* voice workflow
* simulation workflow

---

# 5. `design.md`

Treat this as the **UI/UX source of truth**.

It defines:

* visual language
* layout
* dashboard structure
* typography
* colors
* spacing
* cards
* maps
* alerts
* responsive behavior
* accessibility
* loading/error states
* presentation mode

Do not redesign the UI arbitrarily unless a technical constraint requires it.

---

# 6. `database.md`

Treat this as the **database and persistence source of truth**.

It defines:

* entities
* tables
* relationships
* constraints
* indexes
* transactions
* reservations
* audit logs
* event history
* PostGIS requirements
* state persistence
* data freshness
* simulation data
* migration strategy

Never invent a competing database architecture.

---

# 7. `techspec.md`

Treat this as the **technical implementation source of truth**.

It defines:

* technology stack
* backend structure
* frontend structure
* API architecture
* realtime architecture
* decision engine
* optimization
* ML
* voice
* routing
* security
* deployment
* testing
* failure handling
* performance
* environment configuration

---

# 8. INTEGRATION RULE

You must combine the documents into:

```text
Product Requirements
        +
Application Behavior
        +
UI/UX
        +
Database
        +
Technical Architecture
        +
Implementation Plan
```

Result:

```text
ONE SYSTEM
```

Not:

```text
Six partially connected systems
```

---

# 9. FIRST TASK — SPECIFICATION ANALYSIS

Before writing application code:

1. Read all six documents.
2. Extract all requirements.
3. Build an internal unified specification.
4. Identify:

   * duplicated requirements
   * contradictions
   * missing dependencies
   * ambiguous requirements
   * technically incompatible requirements
   * features referenced by one document but missing from another
5. Determine the canonical implementation for each feature.

Do NOT immediately start coding.

First understand the complete system.

---

# 10. REQUIREMENT TRACEABILITY

Create an internal traceability matrix.

For every major feature determine:

```text
Feature
↓
PRD requirement
↓
App flow
↓
UI design
↓
Database model
↓
API
↓
Backend service
↓
Frontend implementation
↓
Tests
```

Example:

```text
Hospital Resource Reservation

PRD
↓
Reservation requirement

Appflow
↓
Hospital accepts
↓
Resource reservation
↓
Mission continues

Database
↓
resources
reservations
resource_events

Techspec
↓
ReservationService
↓
transaction
↓
row lock

Design
↓
Reservation status card

API
↓
POST /reservations

Tests
↓
concurrent reservation test
```

Every important feature should have this kind of end-to-end traceability.

---

# 11. CONFLICT RESOLUTION RULE

When documents appear to disagree, do not silently choose randomly.

Use this priority:

```text
1. Safety / correctness
2. prd.md
3. techspec.md
4. database.md
5. plan.md
6. appflow.md
7. design.md
```

However:

> Never silently overwrite a requirement.

Document every meaningful conflict in:

```text
docs/spec-conflicts.md
```

Format:

```markdown
## Conflict: Example

### Document A
...

### Document B
...

### Resolution
...

### Reason
...

### Implementation Impact
...
```

If the conflict does not materially affect implementation, select the least complex compatible interpretation.

---

# 12. DO NOT OVERENGINEER

This is a hackathon project.

The architecture must be:

```text
small
modular
testable
explainable
deployable
demonstrable
```

Do NOT introduce unnecessary:

* microservices
* Kubernetes
* Kafka
* service mesh
* distributed databases
* blockchain
* event sourcing everywhere
* complex MLOps
* unnecessary LLM agents
* deep-learning pipelines
* unnecessary computer vision
* unnecessary hardware

Prefer:

```text
React
+
FastAPI
+
PostgreSQL/PostGIS
+
WebSockets
+
Routing API
+
Decision Engine
+
Optional ML
```

---

# 13. CANONICAL SYSTEM ARCHITECTURE

The final architecture should conceptually be:

```text
                    USERS
                     │
        ┌────────────┼─────────────┐
        │            │             │
   Dispatcher      EMT        Hospital
        │            │             │
        └────────────┼─────────────┘
                     │
                     ▼
            React + TypeScript
                     │
             REST + WebSocket
                     │
                     ▼
                FastAPI
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
   Domain      Decision Engine   Realtime
   Services        │
       │       ┌───┼────┐
       │       │   │    │
       │       ▼   ▼    ▼
       │    Rules  ML  Optimization
       │
       └─────────────┬──────────────
                     │
                     ▼
             PostgreSQL + PostGIS
                     │
           ┌─────────┼─────────┐
           │         │         │
           ▼         ▼         ▼
      Ambulances  Hospitals  Missions
                     │
                     ▼
             External Integrations
           ┌─────────┼───────────┐
           │         │           │
         Maps      Voice    Hospital APIs
```

---

# 14. TECHNOLOGY STACK

Use the stack defined by `techspec.md`.

## Frontend

```text
React
TypeScript
Vite
Tailwind CSS
TanStack Query
Zustand
React Router
React Hook Form
Zod
Lucide React
Recharts
```

## Backend

```text
Python
FastAPI
Pydantic
SQLAlchemy
Alembic
WebSockets
```

## Database

```text
PostgreSQL
PostGIS
```

## Optimization

```text
Google OR-Tools
```

Use only where actually useful.

## ML

```text
XGBoost / LightGBM
scikit-learn
```

ML is optional for MVP decision safety.

## Testing

```text
Pytest
Vitest
React Testing Library
Playwright
```

## Deployment

Use practical hackathon-friendly hosting.

Do not introduce unnecessary infrastructure.

---

# 15. CORE ARCHITECTURAL PRINCIPLE

The architecture must separate:

```text
Deterministic Rules
        +
Optimization
        +
Predictive Intelligence
```

Never combine them into one opaque AI function.

---

# 16. DECISION ENGINE

Create a standalone decision engine.

Recommended structure:

```text
decision_engine/
├── constraints.py
├── ambulance_matcher.py
├── hospital_matcher.py
├── scoring.py
├── optimizer.py
├── explanations.py
├── confidence.py
└── models.py
```

The decision engine must be independently testable.

---

# 17. DECISION PIPELINE

Implement:

```text
Emergency
    ↓
Requirements
    ↓
Hard Constraints
    ↓
Eligible Ambulances
    ↓
Route Calculation
    ↓
Ambulance Ranking
    ↓
Eligible Hospitals
    ↓
Hospital Capability Check
    ↓
Resource Check
    ↓
Hospital Acceptance
    ↓
ETA / Readiness / Reliability Scoring
    ↓
Final Recommendation
    ↓
Human Confirmation
```

---

# 18. HARD CONSTRAINTS

Hard constraints must be evaluated BEFORE soft scoring.

Example:

```text
Patient requires ICU
Hospital has no ICU
→ INELIGIBLE
```

Example:

```text
Patient requires ventilator
Hospital ventilator availability = 0
→ INELIGIBLE
```

Example:

```text
Ambulance lacks required equipment
→ INELIGIBLE
```

Do not allow soft scoring to override these conditions.

---

# 19. UNKNOWN DATA

Important:

```text
0 ≠ UNKNOWN
```

For example:

```text
ICU availability = 0
```

means confirmed unavailable.

Whereas:

```text
ICU availability = UNKNOWN
```

means the system does not know.

Unknown must never automatically become:

```text
available
```

or:

```text
unavailable
```

unless the configured policy explicitly says so.

---

# 20. AMBULANCE MATCHING

The matching service must consider:

```text
availability
distance
ETA
equipment
capability
GPS freshness
current assignment
operational status
```

The system should not blindly choose the geographically nearest ambulance.

The objective is:

> **Nearest suitable ambulance**, not merely nearest ambulance.

---

# 21. HOSPITAL MATCHING

Hospital matching must consider:

```text
clinical capability
resource availability
hospital operational status
hospital acceptance
route ETA
traffic
ETA uncertainty
readiness
resource margin
reliability
```

The system should answer:

> Which hospital is the fastest suitable hospital that is capable, likely ready, and willing to accept the patient?

---

# 22. ROUTING

Routing must be abstracted.

Create:

```text
RoutingProvider
```

with implementations such as:

```text
GoogleRoutingProvider
MapboxRoutingProvider
OSRMProvider
MockRoutingProvider
```

The core decision engine must not depend directly on a specific provider.

---

# 23. ROUTE FAILURE

Implement fallback:

```text
Primary Provider
      ↓
Failure?
      ↓
Secondary Provider
      ↓
Failure?
      ↓
Cached route / manual intervention
```

Always expose uncertainty.

---

# 24. RESOURCE RESERVATION

Resource reservation must be server authoritative.

Never trust:

```text
frontend availability
```

as final truth.

Use:

```text
transaction
+
FOR UPDATE / row locking
+
capacity validation
+
reservation record
```

Example:

```text
ICU:
Total = 10
Occupied = 7
Reserved = 1
Available = 2

Reserve 1

Available = 1
Reserved = 2
```

Concurrent reservations must be safe.

---

# 25. MISSION STATE MACHINE

Implement the mission state machine defined across the specifications.

Core states:

```text
CREATED
TRIAGED
AMBULANCE_RECOMMENDED
AMBULANCE_ASSIGNED
EN_ROUTE_TO_PATIENT
PATIENT_ONBOARD
HOSPITAL_SELECTION
ACCEPTANCE_PENDING
HOSPITAL_ACCEPTED
RESOURCE_RESERVED
EN_ROUTE_TO_HOSPITAL
HOSPITAL_READY
ARRIVED
HANDOVER_COMPLETE
CANCELLED
FAILED
```

Reject invalid transitions.

---

# 26. EVENT MODEL

Important state transitions should generate events.

Examples:

```text
mission.created
mission.assigned
ambulance.location.updated
hospital.acceptance.requested
hospital.accepted
hospital.rejected
resource.reserved
route.updated
hospital.ready
mission.arrived
mission.completed
```

---

# 27. REALTIME SYSTEM

Use WebSockets.

Frontend must react to realtime events rather than constantly polling everything.

Use channels such as:

```text
mission:{id}
incident:{id}
ambulance:{id}
hospital:{id}
dispatcher:{id}
```

---

# 28. REALTIME FAILURE STATES

The frontend must explicitly show:

```text
LIVE
RECONNECTING
STALE
OFFLINE
```

Never silently display old realtime data as current.

---

# 29. DATABASE INTEGRATION

Use `database.md` as the database source of truth.

Implement all essential entities:

```text
users
roles
user_roles

incidents
patient_requirements

ambulances
ambulance_equipment
ambulance_locations
ambulance_assignments

hospitals
hospital_capabilities
hospital_resources
resource_events

acceptance_requests
reservations

missions
mission_events

routes
route_alternatives

decision_runs
decision_candidates
decision_reasons

prediction_records
model_registry

notifications
audit_logs

simulation_scenarios
simulation_events
```

Do not create duplicate versions of these concepts.

---

# 30. POSTGIS

Use PostGIS for:

```text
ambulance location
incident location
hospital location
distance calculations
nearest-object queries
geospatial indexing
```

Use spatial indexes where necessary.

---

# 31. DATABASE INTEGRITY

Enforce:

```text
available_capacity >= 0
reserved_capacity >= 0
occupied_capacity >= 0
```

And:

```text
available
+
reserved
+
occupied
<=
total
```

Enforce uniqueness rules for active ambulance assignments.

Use transactions for critical updates.

---

# 32. FRONTEND INTEGRATION

The frontend must follow `design.md` rather than becoming a generic admin dashboard.

Primary visual character:

```text
Emergency Command Center
Operational
High information density
Clear hierarchy
Professional
Medical/mission-critical
Map-centric
Responsive
```

Do not make it look like a generic SaaS CRM.

---

# 33. DISPATCHER EXPERIENCE

The dispatcher should be able to:

```text
create emergency
↓
see patient requirements
↓
see recommended ambulances
↓
confirm ambulance
↓
see route
↓
see hospital ranking
↓
request acceptance
↓
see hospital decision
↓
reserve resources
↓
monitor mission
↓
respond to route changes
↓
see arrival
↓
complete handover
```

---

# 34. AMBULANCE EXPERIENCE

The EMT interface must prioritize:

```text
current mission
route
ETA
destination
patient requirements
hospital readiness
rerouting
connection status
voice assistance
```

Avoid clutter.

---

# 35. HOSPITAL EXPERIENCE

Hospital staff must be able to:

```text
receive incoming emergency
↓
see patient requirements
↓
view ETA
↓
view requested resources
↓
accept / reject / request information
↓
reserve/confirm resources
↓
mark readiness
↓
receive ambulance arrival
↓
complete handover
```

---

# 36. VOICE

Voice is an enhancement, not the core dependency.

If voice fails:

```text
system continues normally
```

Support:

```text
English
Malayalam
Hindi
```

Critical actions must require confirmation.

Example:

```text
"Reroute to City Hospital."

System:
"Confirm rerouting ambulance AMB-004 to City Hospital?"

User:
"Confirm."

System:
Reroute submitted.
```

---

# 37. AI/ML INTEGRATION

AI/ML must remain modular.

Possible components:

```text
ETA prediction
hospital readiness prediction
resource-demand forecasting
```

Do NOT make ML mandatory for:

```text
hard eligibility
resource reservation
authorization
state transitions
safety constraints
```

---

# 38. ML FALLBACK

Whenever:

```text
ML unavailable
model timeout
low confidence
missing features
stale features
```

use deterministic fallback.

Example:

```text
ML ETA
   ↓
unavailable
   ↓
Routing provider ETA
```

---

# 39. EXPLAINABILITY

Every recommendation must expose:

```text
score
eligibility
reasons
confidence
data freshness
```

Example:

```text
Hospital H-003
------------------------------
✓ ICU available
✓ Trauma capability
✓ Ventilator available
✓ Emergency surgery
✓ Hospital accepted
✓ Resource reserved
ETA: 12 min
Readiness: High
Confidence: High
```

---

# 40. REJECTION EXPLANATION

Show why candidates were rejected.

Example:

```text
Hospital H-001
❌ No ICU

Hospital H-002
❌ No trauma capability

Hospital H-003
✓ Suitable
✓ Accepted
✓ Resources reserved
```

This is essential for judge understanding.

---

# 41. HUMAN OVERRIDE

The dispatcher must be able to override recommendations when authorized.

Every override must store:

```text
user
timestamp
previous decision
new decision
reason
```

Never hide manual overrides.

---

# 42. SIMULATION

The project must have a dedicated simulation mode.

Simulation must support:

```text
start
pause
resume
reset
inject event
change traffic
hospital reject
resource unavailable
GPS failure
route blocked
hospital ready
```

---

# 43. GOLDEN DEMO

Build the primary demo around:

```text
Severe road traffic trauma
```

Requirements:

```text
Trauma
ICU
Ventilator
Emergency surgery
```

Scenario:

```text
Closest ambulance
→ unsuitable

Second ambulance
→ suitable

Closest hospital
→ no ICU

Second hospital
→ no trauma

Third hospital
→ suitable + accepts

Resource reserved
↓
Ambulance travelling
↓
Traffic changes
↓
Route changes
↓
ETA updates
↓
Hospital receives update
↓
Hospital becomes ready
↓
Ambulance arrives
↓
Handover complete
```

This scenario must be reproducible.

---

# 44. FAILURE DEMONSTRATION

At least one live failure must be demonstrated.

Preferred:

```text
Hospital H-003 rejects patient
```

Then visibly show:

```text
H-003 rejected
        ↓
Decision engine re-evaluates
        ↓
H-004 becomes best candidate
        ↓
Dispatcher notified
        ↓
New acceptance request
        ↓
Mission updated
```

This demonstrates that the system is a dynamic coordination system rather than a static dashboard.

---

# 45. DATA MODE

Every dynamic/simulated record must clearly indicate:

```text
LIVE
SIMULATED
REPLAY
MOCK
UNKNOWN
STALE
```

Never misrepresent simulation data as real healthcare infrastructure.

---

# 46. SECURITY

Implement:

```text
authentication
RBAC
authorization
HTTPS
input validation
secure cookies/tokens
rate limiting
audit logs
secret management
```

Backend authorization is mandatory.

Do not rely on frontend hiding UI buttons.

---

# 47. PRIVACY

For the hackathon:

Use:

```text
synthetic patients
synthetic medical information
synthetic contact details
```

Never use real patient health information in development/demo data.

Minimize stored sensitive data.

---

# 48. AUDIT

Audit:

```text
login
logout
incident creation
ambulance assignment
hospital acceptance
hospital rejection
resource reservation
route override
manual override
mission completion
simulation actions
```

---

# 49. TESTING STRATEGY

Use three levels.

## Unit

Test:

```text
constraint engine
scoring
hospital matching
ambulance matching
reservation logic
state transitions
permissions
ML fallback
```

## Integration

Test:

```text
API
database
WebSocket
transactions
routing adapter
decision engine
```

## E2E

Test:

```text
Create emergency
→ assign ambulance
→ choose hospital
→ accept
→ reserve
→ mission
→ reroute
→ arrival
→ handover
```

---

# 50. TEST THE FAILURE PATH

Do not only test successful flows.

Test:

```text
hospital rejection
no suitable ambulance
no suitable hospital
resource unavailable
GPS failure
routing provider failure
hospital API unavailable
duplicate reservation
invalid state transition
unauthorized action
WebSocket disconnect
ML failure
```

---

# 51. API CONTRACT

Use FastAPI OpenAPI as the API contract.

Frontend should consume typed API models.

Avoid random `fetch()` calls inside UI components.

Centralize API access.

---

# 52. CODE ORGANIZATION

Frontend:

```text
features/
components/
hooks/
stores/
lib/
schemas/
types/
```

Backend:

```text
api/
services/
models/
schemas/
decision_engine/
integrations/
ml/
realtime/
simulation/
core/
```

Do not put business logic inside route controllers or React components.

---

# 53. INTEGRATION ADAPTERS

External providers must be isolated.

Examples:

```text
integrations/routing/
integrations/voice/
integrations/hospital/
```

Create interfaces.

Example:

```python
class RoutingProvider:
    ...
```

Then:

```text
GoogleRoutingProvider
MapboxRoutingProvider
MockRoutingProvider
```

The rest of the application should depend on the interface, not vendor-specific code.

---

# 54. CONFIGURATION

Operational parameters must be configurable.

Examples:

```text
decision weights
GPS freshness threshold
hospital freshness threshold
reservation TTL
routing provider
ML enabled
simulation enabled
voice enabled
```

Do not scatter constants across the codebase.

---

# 55. ENVIRONMENT CONFIGURATION

Create:

```text
.env.example
```

Include:

```text
DATABASE_URL
JWT_SECRET
CORS_ORIGINS
MAP_PROVIDER
MAPBOX_TOKEN
GOOGLE_MAPS_API_KEY
ROUTING_PROVIDER
ML_ENABLED
VOICE_ENABLED
SIMULATION_ENABLED
```

Never commit actual secrets.

---

# 56. DEVELOPMENT ENVIRONMENTS

Support:

```text
development
test
demo
production
```

The demo environment must contain deterministic seeded data.

---

# 57. SEED DATA

Create realistic synthetic data for:

```text
ambulances
hospitals
capabilities
resources
users
incidents
demo missions
```

Seed deliberately conflicting hospitals so the decision engine's intelligence is visible.

---

# 58. DEMO DATA EXAMPLE

Example hospitals:

```text
H-001
Distance: 3.2 km
ICU: No
Trauma: Yes
Ventilator: Yes

H-002
Distance: 4.8 km
ICU: Yes
Trauma: No
Ventilator: Yes

H-003
Distance: 7.1 km
ICU: Yes
Trauma: Yes
Ventilator: Yes
Emergency Surgery: Yes
```

Expected:

```text
H-003
```

must be selected despite being farther away.

---

# 59. IMPLEMENTATION ORDER

Implement in this order.

## Step 1

Repository foundation.

```text
frontend
backend
database
environment
linting
testing
```

## Step 2

Authentication and RBAC.

## Step 3

Core database schema.

## Step 4

Incident creation.

## Step 5

Patient requirements.

## Step 6

Ambulance management.

## Step 7

Ambulance matching.

## Step 8

Routing.

## Step 9

Hospital management.

## Step 10

Hospital matching.

## Step 11

Acceptance workflow.

## Step 12

Resource reservation.

## Step 13

Mission state machine.

## Step 14

WebSockets.

## Step 15

Dispatcher dashboard.

## Step 16

Ambulance interface.

## Step 17

Hospital interface.

## Step 18

Simulation.

## Step 19

Failure injection.

## Step 20

AI/ML.

## Step 21

Voice.

## Step 22

Testing.

## Step 23

Deployment.

---

# 60. DO NOT BUILD ADVANCED FEATURES TOO EARLY

Do not begin with:

```text
ML
voice
analytics
optimization
advanced dashboards
```

before the core vertical slice works.

First prove:

```text
Emergency
→ Ambulance
→ Route
→ Hospital
→ Acceptance
→ Reservation
→ Mission
→ Arrival
```

---

# 61. VERTICAL SLICE REQUIREMENT

The first complete working slice must be:

```text
POST /incidents
        ↓
Patient Requirements
        ↓
Ambulance Matcher
        ↓
Route Provider
        ↓
Hospital Matcher
        ↓
Acceptance
        ↓
Reservation
        ↓
Mission
        ↓
WebSocket
        ↓
Dispatcher UI
```

Only after this works should optional AI features expand.

---

# 62. BUILD QUALITY RULE

Do not generate huge placeholder structures and claim completion.

Every completed feature must:

```text
work
be connected
be testable
handle errors
handle loading
handle failure
persist state
```

No fake buttons.

If a UI element exists but backend behavior is not implemented, clearly mark it as:

```text
Coming soon
Demo-only
Mocked
```

and do not pretend it is production functionality.

---

# 63. NO DEAD FEATURES

Every visible major feature must map to:

```text
API
Database
Backend Service
Frontend Behavior
```

Do not add decorative UI without functional purpose.

---

# 64. UI REQUIREMENTS

The UI must prioritize:

```text
Emergency state
Patient requirements
Ambulance
Hospital
ETA
Resource readiness
Alerts
Route
Decision reasons
```

Do not bury critical information in nested menus.

---

# 65. MAP REQUIREMENTS

Map should visually communicate:

```text
Emergency location
Ambulance
Selected hospital
Alternate hospitals
Current route
Traffic
ETA
Route changes
```

Selected and rejected hospitals should be visually distinguishable.

---

# 66. STATUS SEMANTICS

Use consistent states.

Example:

```text
GREEN  = ready / accepted / available
YELLOW = warning / stale / pending
RED    = critical / rejected / unavailable
BLUE   = active mission / information
GRAY   = inactive / unknown
```

Use the exact visual system specified in `design.md`.

---

# 67. RESPONSIVE DESIGN

Minimum important surfaces:

```text
Dispatcher desktop
Hospital desktop/tablet
Ambulance mobile
```

The ambulance interface must prioritize touch targets and minimal interaction.

---

# 68. ACCESSIBILITY

Implement:

```text
keyboard accessibility
semantic labels
good contrast
focus states
screen-reader-friendly status messages
non-color-only status indicators
```

---

# 69. PERFORMANCE

Prioritize:

```text
fast dashboard loading
efficient map rendering
limited unnecessary WebSocket traffic
efficient database queries
indexed spatial queries
small API responses
```

Do not optimize prematurely.

Measure before replacing simple solutions.

---

# 70. DOCUMENTATION TO CREATE

After implementation, maintain:

```text
README.md
docs/spec-conflicts.md
docs/architecture.md
docs/api.md
docs/database.md
docs/demo.md
docs/deployment.md
```

---

# 71. SPEC-CONFLICT DOCUMENT

Whenever you detect an actual specification conflict, document it.

Do not silently resolve significant conflicts.

Example:

```markdown
# Specification Conflict Log

## SC-001 — Routing Provider

### Source
techspec.md allows Google/Mapbox/OSRM.

### Resolution
MVP uses one provider behind RoutingProvider interface.

### Reason
Avoid coupling core logic to vendor implementation.
```

---

# 72. FINAL ARCHITECTURAL CHECK

Before declaring implementation complete, verify:

```text
[ ] PRD requirements mapped
[ ] Application flows implemented
[ ] Design implemented
[ ] Database schema implemented
[ ] Technical architecture implemented
[ ] API contracts implemented
[ ] Decision engine working
[ ] Resource reservation transactional
[ ] Realtime updates working
[ ] Failure scenarios handled
[ ] Simulation working
[ ] Audit logging working
[ ] Authentication working
[ ] RBAC working
[ ] Tests passing
[ ] Golden demo working
```

---

# 73. FINAL GOLDEN-PATH TEST

Run exactly this scenario:

```text
1. Create critical emergency.

2. Set:
   Trauma = true
   ICU = true
   Ventilator = true
   Emergency Surgery = true

3. System evaluates ambulances.

4. Nearest unsuitable ambulance is filtered out.

5. Suitable ambulance is recommended.

6. Dispatcher confirms.

7. Route is calculated.

8. System evaluates hospitals.

9. Hospital A rejected because ICU missing.

10. Hospital B rejected because trauma capability missing.

11. Hospital C selected.

12. Acceptance request sent.

13. Hospital accepts.

14. ICU + ventilator reserved.

15. Mission starts.

16. Ambulance location updates.

17. Traffic changes.

18. Route recalculates.

19. ETA updates.

20. Hospital receives updated ETA.

21. Hospital marks patient as ready.

22. Ambulance arrives.

23. Handover completed.

24. Mission marked complete.

25. Full audit trail exists.
```

---

# 74. FAILURE TEST

Then test:

```text
Hospital C rejects.
```

Expected:

```text
Hospital C
      ↓
REJECTED
      ↓
Decision engine runs again
      ↓
Hospital candidates re-evaluated
      ↓
Best valid alternative selected
      ↓
Dispatcher alerted
      ↓
New acceptance requested
```

---

# 75. FINAL DEMONSTRATION STANDARD

A judge should understand the system within seconds.

The UI should make this obvious:

```text
PATIENT NEED
      ↓
AMBULANCE
      ↓
ROUTE
      ↓
HOSPITAL
      ↓
ACCEPTED
      ↓
RESOURCES RESERVED
      ↓
HOSPITAL READY
      ↓
ARRIVAL
```

And the system should visibly answer:

> **Why this ambulance?**

> **Why this hospital?**

> **Why not the nearest hospital?**

> **What happens when conditions change?**

---

# 76. FINAL IMPLEMENTATION RULE

The goal is NOT to implement every possible feature described in the documents immediately.

The goal is:

> **Build a coherent, working, defensible end-to-end emergency coordination system first.**

Then add:

```text
ML
Voice
Advanced optimization
Analytics
Interoperability
```

incrementally.

---

# 77. AGENT BEHAVIOR

When working in this repository:

### You MUST

* inspect existing files before changing architecture
* reuse existing working code
* preserve existing functionality
* follow the six specifications
* keep APIs typed
* keep database migrations clean
* write tests
* document significant decisions
* use real error handling
* maintain clear separation of concerns
* distinguish mock/simulated/live data
* implement safety-critical logic deterministically
* keep decisions explainable

### You MUST NOT

* rewrite the entire repository unnecessarily
* change stack without strong reason
* introduce random libraries
* add unnecessary infrastructure
* create fake AI
* create fake realtime behavior
* create fake database logic
* hardcode business decisions in UI
* silently ignore specification conflicts
* remove requirements because they are inconvenient
* claim incomplete features are complete

---

# 78. WHEN YOU FIND MISSING INFORMATION

Do not immediately ask unnecessary questions.

Instead:

1. determine whether the missing information blocks implementation;
2. use the smallest reasonable assumption if it does not;
3. record the assumption in:
   `docs/implementation-decisions.md`;
4. continue implementation.

Format:

```markdown
## DEC-001

### Decision
Use PostgreSQL/PostGIS.

### Reason
Required for spatial ambulance/hospital queries.

### Alternatives
MySQL
SQLite

### Why not
PostGIS provides stronger geospatial support.
```

Only stop when a genuinely blocking decision cannot be safely inferred.

---

# 79. WHEN EXISTING CODE CONFLICTS WITH THE DOCUMENTS

Do not blindly overwrite existing code.

First determine:

```text
Does current implementation satisfy the requirement?
```

If yes:

```text
preserve it
```

If no:

```text
modify minimally
```

If architectural refactoring is necessary:

```text
make the smallest safe refactor
```

Preserve working functionality whenever possible.

---

# 80. DEVELOPMENT PHILOSOPHY

Always favor:

```text
simple
+
correct
+
observable
+
testable
```

over:

```text
complex
+
impressive-looking
+
fragile
```

The system must impress judges through:

```text
real problem understanding
+
strong coordination logic
+
dynamic decisions
+
explainability
+
working realtime behavior
```

not through unnecessary technology count.

---

# 81. FINAL SYSTEM PRINCIPLE

The entire project must embody this concept:

> **The fastest hospital is not necessarily the nearest hospital. The best emergency decision is the hospital that can actually accept and treat the patient with the required resources when the ambulance arrives.**

Likewise:

> **The best ambulance is not necessarily the closest ambulance. It is the closest suitable ambulance capable of handling the patient's requirements.**

Therefore the system must optimize the complete emergency journey rather than one isolated component.

---

# 82. FINAL SUCCESS CRITERIA

The project is successful when the running application can prove:

```text
                PATIENT NEED
                     ↓
          SUITABLE AMBULANCE
                     ↓
             RELIABLE ROUTE
                     ↓
           SUITABLE HOSPITAL
                     ↓
               ACCEPTANCE
                     ↓
          RESOURCE RESERVATION
                     ↓
             HOSPITAL READY
                     ↓
             LIVE MONITORING
                     ↓
             DYNAMIC RESPONSE
                     ↓
              PATIENT ARRIVAL
                     ↓
             EMERGENCY HANDOVER
```

The final product must be:

```text
coherent
working
explainable
auditable
realtime
failure-aware
secure
testable
hackathon-demo-ready
```

and architecturally capable of evolving toward real healthcare integrations.

---

# 83. START HERE

Before modifying or creating code:

````text
1. Read:
   prd.md
   plan.md
   appflow.md
   design.md
   database.md
   techspec.md

2. Build the internal unified specification.

3. Inspect the repository structure.

4. Compare current code against the specification.

5. Identify:
   - implemented
   - partially implemented
   - missing
   - conflicting

6. Create:
   docs/spec-conflicts.md
   docs/implementation-decisions.md

7. Create or update the architecture structure.

8. Implement the minimum complete vertical slice.

9. Test it.

10. Expand feature-by-feature.

11. Run the golden-path demo.

12. Run failure scenarios.

13. Verify the final system against all six documents.

Do not claim completion until the end-to-end workflow actually works.

### Best way to use this

Put the six files in the project root:

```text
/plan.md
/appflow.md
/design.md
/prd.md
/database.md
/techspec.md
````

Then put the prompt above into your coding agent as the **master implementation instruction**.

One important correction: the filename should be **`techspec.md`**, not `techsecp.md`, so all references stay consistent.
# Smart Ambulance Routing & Emergency Bed Allocation System
## Technical Specification (`techspec.md`)

**Document Version:** 1.0  
**Project Type:** AI / Healthcare Hackathon  
**Primary Goal:** Build a real-time emergency coordination platform that connects emergency reporting, ambulance selection, traffic-aware routing, hospital capability matching, hospital acceptance, resource reservation, and live mission coordination.

---

# 1. Technical Specification Purpose

This document defines the technical implementation requirements for the Smart Ambulance Routing & Emergency Bed Allocation System.

It converts the product requirements into concrete engineering decisions covering:

- system architecture
- technology stack
- application boundaries
- frontend architecture
- backend architecture
- database architecture
- API contracts
- realtime communication
- decision engine
- ambulance assignment
- route optimization
- hospital matching
- resource reservation
- AI/ML integration
- voice interface
- authentication and authorization
- validation
- error handling
- observability
- testing
- deployment
- environment configuration
- demo/simulation architecture
- security
- performance
- implementation constraints

The implementation must prioritize:

> **Correct emergency coordination over unnecessary technical complexity.**

The system must be:

- demonstrable
- explainable
- deterministic where safety requires determinism
- realtime
- auditable
- failure-aware
- modular
- extensible toward real healthcare integrations

---

# 2. Product Technical Definition

## 2.1 Core System Statement

The platform must coordinate:

```text
Emergency
   ↓
Patient Requirement Assessment
   ↓
Suitable Ambulance Selection
   ↓
Traffic-Aware Routing
   ↓
Hospital Capability Matching
   ↓
Capacity / Resource Verification
   ↓
Hospital Acceptance
   ↓
Resource Reservation
   ↓
Hospital Preparation
   ↓
Live Ambulance Tracking
   ↓
Dynamic ETA / Route Updates
   ↓
Patient Arrival
   ↓
Emergency Handover
```

The system is not simply:

- an ambulance tracker
- a map application
- a hospital directory
- a bed management system
- a chatbot

It is an:

> **End-to-end emergency coordination and decision-support platform.**

---

# 3. Engineering Principles

## 3.1 Core Principles

### Principle 1 — Hard constraints before optimization

A hospital that cannot satisfy a mandatory clinical requirement must not be ranked as a valid option simply because it is geographically close.

Example:

```text
Patient requires:
- Trauma capability
- ICU
- Ventilator
- Emergency surgery

Hospital A:
- 3 km
- No ICU

Hospital B:
- 7 km
- ICU available
- Trauma capability
- Emergency surgery
- Ventilator available

Hospital B is preferred.
```

---

## 3.2 Principle 2 — AI supports decisions, not blindly controls them

The system must separate:

```text
Deterministic Rules
        +
Optimization
        +
Predictive ML
```

AI/ML must not override mandatory medical or operational constraints.

---

## 3.3 Principle 3 — Every important decision must be explainable

The system must be able to answer:

> Why was this ambulance selected?

> Why was this hospital selected?

> Why was this hospital rejected?

> Why was the route changed?

Example:

```text
Hospital H-003 selected because:

✓ ICU required
✓ ICU available
✓ Trauma capability available
✓ Emergency surgery available
✓ Ventilator available
✓ Hospital accepted patient
✓ Estimated arrival: 14 min
✓ Predicted readiness: high
✓ Route reliability: high
```

---

## 3.4 Principle 4 — Current state + event history

The system must maintain both:

```text
Current State
+
Immutable Event History
```

Example:

```text
Mission status:
EN_ROUTE

Events:
17:41 Incident created
17:42 Ambulance AMB-04 assigned
17:43 Hospital H-003 contacted
17:44 Hospital H-003 accepted
17:45 ICU reserved
17:48 Route changed
17:55 Hospital readiness confirmed
```

---

## 3.5 Principle 5 — Real vs simulated data must be explicit

Hackathon implementation may use:

- simulated ambulance GPS
- simulated hospital capacity
- synthetic emergency cases
- mocked hospital acceptance
- replayed incidents

The UI must clearly distinguish:

```text
LIVE
SIMULATED
REPLAY
STALE
UNKNOWN
```

Never present simulated values as real clinical infrastructure.

---

# 4. Recommended Technology Stack

## 4.1 Frontend

| Component | Technology |
|---|---|
| Framework | React |
| Language | TypeScript |
| Build tool | Vite |
| Styling | Tailwind CSS |
| UI primitives | Custom components + accessible primitives |
| Routing | React Router |
| Server state | TanStack Query |
| Client state | Zustand |
| Validation | Zod |
| Icons | Lucide React |
| Maps | Mapbox GL JS / Google Maps |
| Realtime | Native WebSocket client |
| Charts | Recharts |
| Forms | React Hook Form + Zod |
| Testing | Vitest + React Testing Library |
| E2E | Playwright |

---

# 5. Frontend Architecture

## 5.1 Frontend Responsibilities

The frontend is responsible for:

- authentication interface
- role-based dashboard rendering
- emergency creation
- patient requirement selection
- ambulance selection
- map rendering
- live ambulance tracking
- route visualization
- hospital ranking display
- hospital acceptance workflow
- resource reservation status
- mission timeline
- alerts
- notifications
- voice controls
- simulation controls
- decision explanations
- audit/event visibility

The frontend must not implement authoritative business decisions.

---

# 6. Frontend Architecture Pattern

Use a feature-oriented architecture.

```text
apps/web/
│
├── src/
│   │
│   ├── app/
│   │   ├── router/
│   │   ├── providers/
│   │   ├── layouts/
│   │   └── app.tsx
│   │
│   ├── components/
│   │   ├── ui/
│   │   ├── forms/
│   │   ├── maps/
│   │   ├── charts/
│   │   ├── alerts/
│   │   └── status/
│   │
│   ├── features/
│   │   ├── auth/
│   │   ├── incidents/
│   │   ├── ambulances/
│   │   ├── hospitals/
│   │   ├── missions/
│   │   ├── routing/
│   │   ├── reservations/
│   │   ├── notifications/
│   │   ├── voice/
│   │   └── simulation/
│   │
│   ├── hooks/
│   ├── lib/
│   ├── stores/
│   ├── types/
│   ├── schemas/
│   ├── constants/
│   └── styles/
│
└── tests/
```

---

# 7. Frontend State Architecture

Separate state into three categories.

## 7.1 Server State

Use TanStack Query for:

- incidents
- ambulances
- hospitals
- routes
- missions
- reservations
- notifications
- decision results
- resource availability

Example:

```typescript
useQuery({
  queryKey: ["mission", missionId],
  queryFn: () => api.getMission(missionId)
});
```

---

## 7.2 Client UI State

Use Zustand for:

- selected mission
- sidebar state
- map layer visibility
- selected hospital
- active modal
- simulation mode
- UI preferences
- temporary filters

---

## 7.3 URL State

Use URL parameters for:

```text
/dispatcher?mission=MSN-00012
/hospitals?status=available
/ambulances?status=available
```

This makes dashboards shareable and refresh-safe.

---

# 8. Frontend Role-Based Interfaces

## 8.1 Dispatcher Dashboard

Primary view:

```text
┌─────────────────────────────────────────────┐
│ Emergency Command Center                   │
├───────────────────┬─────────────────────────┤
│ Active Incidents  │                         │
│                   │                         │
│ INC-0042          │        LIVE MAP         │
│ Critical          │                         │
│ 11 min            │   🚑 → 🏥              │
│                   │                         │
├───────────────────┴─────────────────────────┤
│ Ambulances | Hospitals | Alerts | Timeline │
└─────────────────────────────────────────────┘
```

---

## 8.2 Ambulance / EMT Interface

Mobile-first.

Must show:

- current mission
- destination
- ETA
- patient requirements
- route
- reroute notification
- hospital readiness
- voice control
- emergency status
- connection status

---

## 8.3 Hospital Interface

Hospital dashboard must show:

- incoming emergency
- patient requirements
- ambulance ETA
- requested resources
- acceptance control
- reservation status
- readiness checklist
- current emergency capacity
- route information

Example:

```text
INCOMING TRAUMA PATIENT

ETA: 08 min

Required:
✓ Trauma
✓ ICU
✓ Ventilator
✓ Emergency Surgery

Resources:
ICU Bed       2 available
Ventilator    1 available
Trauma Team   Ready
OR            Available

[ ACCEPT ] [ REJECT ] [ REQUEST INFO ]
```

---

# 9. Map Technology

The map layer must support:

- ambulance position
- incident position
- hospital locations
- route line
- alternate routes
- traffic condition
- ETA
- hospital capability overlays
- selected hospital
- geofencing where required

Preferred architecture:

```text
React
 ↓
Map SDK
 ↓
Routing Provider
 ↓
FastAPI
 ↓
Decision Engine
```

The browser must not contain provider-specific business logic.

---

# 10. Routing Architecture

Routing must be provider-independent.

Create an internal interface:

```python
class RoutingProvider(Protocol):

    async def calculate_route(
        self,
        origin: Coordinate,
        destination: Coordinate,
        departure_time: datetime | None = None
    ) -> RouteResult:
        ...

    async def calculate_matrix(
        self,
        origins: list[Coordinate],
        destinations: list[Coordinate]
    ) -> MatrixResult:
        ...
```

Supported implementations may include:

```text
GoogleRoutingProvider
MapboxRoutingProvider
OSRMProvider
GraphHopperProvider
MockRoutingProvider
```

---

# 11. Route Data Model

Each route must contain:

```json
{
  "route_id": "RTE-001",
  "provider": "google",
  "distance_m": 6200,
  "duration_s": 840,
  "traffic_duration_s": 960,
  "eta": "2026-09-12T18:21:00Z",
  "confidence": 0.91,
  "source_timestamp": "2026-09-12T18:05:00Z"
}
```

---

# 12. Route Selection

Do not automatically use:

```text
shortest distance
```

Use:

```text
lowest emergency travel cost
```

Possible cost:

```text
RouteCost =
    0.55 * normalized_eta
  + 0.20 * congestion_penalty
  + 0.10 * route_risk
  + 0.10 * ETA_uncertainty
  + 0.05 * route_change_penalty
```

Weights must be configurable.

These are engineering defaults, not medical standards.

---

# 13. Ambulance Matching Engine

Ambulance selection happens in two phases.

## Phase 1 — Hard Filtering

Example:

```text
Ambulance must:

✓ be active
✓ be available
✓ be within operational radius
✓ have required equipment
✓ support required patient type
✓ have valid GPS
```

If an ambulance fails a mandatory rule:

```text
eligible = false
```

It must not be ranked using soft scores.

---

# 14. Ambulance Scoring

For eligible ambulances:

```text
AmbulanceScore =
    W1 * ETA
  + W2 * capability_match
  + W3 * equipment_match
  + W4 * reliability
  + W5 * operational_distance
```

Lower is better for cost-based components.

Example:

```text
AMB-01
ETA: 6 min
Capability: 100%
Equipment: 100%
GPS: Fresh
Score: 0.91

AMB-02
ETA: 4 min
Capability: 60%
Equipment: 50%
Score: invalid

AMB-03
ETA: 8 min
Capability: 100%
Equipment: 100%
Score: 0.82
```

The system may select AMB-03 depending on configured objective weights.

The explanation must always be visible.

---

# 15. Hospital Matching Engine

Hospital selection must follow:

```text
1. Clinical hard constraints
2. Resource feasibility
3. Hospital acceptance
4. Route / ETA
5. Predicted readiness
6. Operational reliability
```

---

# 16. Hospital Hard Constraints

Example:

```python
mandatory_requirements = [
    "ICU",
    "TRAUMA",
    "VENTILATOR"
]
```

Hospital passes only if:

```text
all required capabilities exist
AND
required resource status is available
AND
hospital operational status is active
```

Unknown must not automatically mean available.

---

# 17. Hospital Soft Scoring

Example:

```text
HospitalScore =
    W1 * ETA
  + W2 * ETA_uncertainty
  + W3 * readiness_prediction
  + W4 * acceptance_probability
  + W5 * resource_margin
  + W6 * hospital_reliability
```

Weights must be configurable.

---

# 18. Hospital Acceptance Workflow

The workflow must be:

```text
Dispatcher
    ↓
Hospital Candidate Generated
    ↓
Acceptance Request
    ↓
Hospital Receives Request
    ↓
Hospital Reviews
    ↓
ACCEPT / REJECT / REQUEST INFO
    ↓
Decision Engine Updated
```

If hospital rejects:

```text
Hospital rejected
      ↓
Candidate removed
      ↓
Remaining hospitals re-ranked
      ↓
New recommendation
      ↓
Dispatcher confirmation
      ↓
Ambulance destination updated
```

---

# 19. Resource Reservation Architecture

Resource reservation is transactional.

Examples:

- ICU bed
- ventilator
- operating room
- trauma team
- emergency bed

---

# 20. Resource Reservation Rules

Reservation must guarantee:

```text
available >= requested
```

When reservation succeeds:

```text
available_capacity -= amount
reserved_capacity += amount
```

When reservation expires:

```text
reserved_capacity -= amount
available_capacity += amount
```

When consumed:

```text
reserved_capacity -= amount
occupied_capacity += amount
```

All changes must be transactional.

---

# 21. Database Transaction Requirement

Use row-level locking for high-contention resources.

Conceptual SQL:

```sql
BEGIN;

SELECT *
FROM hospital_resources
WHERE id = :resource_id
FOR UPDATE;

-- validate capacity

UPDATE hospital_resources
SET reserved_capacity = reserved_capacity + :amount,
    available_capacity = available_capacity - :amount
WHERE id = :resource_id;

INSERT INTO reservations (...);

COMMIT;
```

Never trust a client-side availability check as the final authority.

---

# 22. PostgreSQL + PostGIS

Database:

```text
PostgreSQL
PostGIS
```

PostGIS will support:

- ambulance coordinates
- hospital coordinates
- incident coordinates
- spatial queries
- nearest ambulance search
- nearest hospital search
- geofencing
- spatial indexing

---

# 23. Spatial Indexing

Spatial fields:

```sql
geometry(Point, 4326)
```

Indexes:

```sql
CREATE INDEX idx_ambulance_location_geom
ON ambulance_locations
USING GIST(location);
```

Use spatial queries such as:

```sql
ST_DWithin(...)
ST_Distance(...)
ST_MakePoint(...)
```

---

# 24. Backend Technology

Use:

```text
Python
FastAPI
Pydantic
SQLAlchemy
Alembic
WebSockets
PostgreSQL
PostGIS
```

Optional:

```text
Redis
```

Redis is not mandatory for MVP.

---

# 25. Backend Architecture

```text
apps/api/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── logging.py
│   │   └── errors.py
│   │
│   ├── models/
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │   ├── incident_service.py
│   │   ├── ambulance_service.py
│   │   ├── hospital_service.py
│   │   ├── routing_service.py
│   │   ├── reservation_service.py
│   │   ├── mission_service.py
│   │   ├── notification_service.py
│   │   └── voice_service.py
│   │
│   ├── decision_engine/
│   │   ├── constraints.py
│   │   ├── ambulance_matcher.py
│   │   ├── hospital_matcher.py
│   │   ├── scoring.py
│   │   ├── optimizer.py
│   │   ├── explanations.py
│   │   └── confidence.py
│   │
│   ├── ml/
│   │   ├── eta.py
│   │   ├── readiness.py
│   │   ├── demand.py
│   │   └── registry.py
│   │
│   ├── integrations/
│   │   ├── routing/
│   │   ├── maps/
│   │   ├── voice/
│   │   └── hospital/
│   │
│   ├── realtime/
│   │   ├── manager.py
│   │   ├── channels.py
│   │   └── events.py
│   │
│   └── simulation/
│       ├── scenarios.py
│       ├── replay.py
│       └── controller.py
│
└── tests/
```

---

# 26. API Architecture

Base URL:

```text
/api/v1
```

All APIs must be versioned.

---

# 27. Authentication APIs

```http
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/me
POST /api/v1/auth/refresh
```

---

# 28. Incident APIs

```http
POST   /api/v1/incidents
GET    /api/v1/incidents
GET    /api/v1/incidents/{incident_id}
PATCH  /api/v1/incidents/{incident_id}
POST   /api/v1/incidents/{incident_id}/requirements
```

---

# 29. Ambulance APIs

```http
GET  /api/v1/ambulances
GET  /api/v1/ambulances/{id}
POST /api/v1/ambulances/{id}/location
POST /api/v1/ambulances/{id}/assign
POST /api/v1/ambulances/{id}/status
```

---

# 30. Ambulance Matching APIs

```http
POST /api/v1/dispatch/ambulances/match
POST /api/v1/dispatch/ambulances/{id}/confirm
```

Response:

```json
{
  "incident_id": "INC-00042",
  "recommendations": [
    {
      "ambulance_id": "AMB-003",
      "score": 0.91,
      "eta_seconds": 360,
      "eligible": true,
      "reasons": [
        "Required equipment available",
        "Closest suitable ambulance",
        "GPS signal fresh"
      ]
    }
  ]
}
```

---

# 31. Hospital APIs

```http
GET  /api/v1/hospitals
GET  /api/v1/hospitals/{id}
GET  /api/v1/hospitals/{id}/capabilities
GET  /api/v1/hospitals/{id}/resources
POST /api/v1/hospitals/{id}/status
```

---

# 32. Hospital Matching APIs

```http
POST /api/v1/dispatch/hospitals/match
GET  /api/v1/dispatch/hospitals/{id}/recommendation
```

---

# 33. Acceptance APIs

```http
POST /api/v1/acceptance-requests
GET  /api/v1/acceptance-requests/{id}
POST /api/v1/acceptance-requests/{id}/accept
POST /api/v1/acceptance-requests/{id}/reject
POST /api/v1/acceptance-requests/{id}/request-info
```

---

# 34. Reservation APIs

```http
POST   /api/v1/reservations
GET    /api/v1/reservations/{id}
POST   /api/v1/reservations/{id}/confirm
POST   /api/v1/reservations/{id}/release
POST   /api/v1/reservations/{id}/consume
```

---

# 35. Mission APIs

```http
GET   /api/v1/missions
GET   /api/v1/missions/{id}
POST  /api/v1/missions
PATCH /api/v1/missions/{id}
POST  /api/v1/missions/{id}/reroute
POST  /api/v1/missions/{id}/complete
```

---

# 36. Routing APIs

```http
POST /api/v1/routes/calculate
POST /api/v1/routes/matrix
POST /api/v1/routes/compare
```

Example:

```json
{
  "origin": {
    "lat": 9.9312,
    "lng": 76.2673
  },
  "destination": {
    "lat": 9.9975,
    "lng": 76.2996
  }
}
```

---

# 37. Decision Engine API

Central decision endpoint:

```http
POST /api/v1/decision/evaluate
```

Input:

```json
{
  "incident_id": "INC-00042",
  "requirements": {
    "icu": true,
    "trauma": true,
    "ventilator": true,
    "emergency_surgery": true
  }
}
```

Output:

```json
{
  "decision_id": "DEC-00091",
  "ambulance": {
    "selected": "AMB-004"
  },
  "hospital": {
    "selected": "H-003"
  },
  "confidence": 0.89,
  "reasons": [
    "Hospital meets mandatory clinical requirements",
    "Hospital accepted patient",
    "Expected travel time is within target",
    "Required resources can be reserved"
  ]
}
```

---

# 38. Decision Engine Architecture

```text
Incident
   ↓
Requirement Parser
   ↓
Hard Constraint Filter
   ├── Ambulances
   └── Hospitals
   ↓
Routing Matrix
   ↓
Prediction Layer
   ↓
Optimization / Scoring
   ↓
Confidence Evaluation
   ↓
Recommendation
   ↓
Human Confirmation
```

---

# 39. Decision Engine Components

## 39.1 Requirement Parser

Converts emergency information into structured requirements.

Example:

```json
{
  "severity": "critical",
  "trauma": true,
  "icu": true,
  "ventilator": true,
  "emergency_surgery": true
}
```

---

## 39.2 Constraint Engine

Determines:

```text
eligible / not eligible
```

Must never silently transform unknown into true.

---

## 39.3 Routing Layer

Computes:

```text
ambulance → incident
ambulance → hospital
incident → hospital
```

---

## 39.4 Prediction Layer

Optional ML predictions:

```text
ETA
Hospital readiness
Resource demand
Emergency congestion
```

---

## 39.5 Optimization Layer

Possible implementation:

```text
Google OR-Tools
```

Use it when assignment involves multiple simultaneous emergency requests or additional optimization complexity.

For MVP:

```text
rule filtering + weighted scoring
```

is acceptable.

Do not introduce OR-Tools solely for appearance.

---

# 40. Optimization Objective

Generic formulation:

```text
Minimize:

λ1 * travel_time
+ λ2 * travel_time_uncertainty
+ λ3 * route_risk
+ λ4 * hospital_readiness
+ λ5 * rejection_risk
+ λ6 * resource_shortage_risk
```

Subject to:

```text
ambulance.available = true
required equipment available = true
hospital capability satisfied = true
required resource available = true
hospital operational = true
```

Weights must be configurable.

---

# 41. Explainability Engine

Every decision must produce structured reasons.

Example:

```json
{
  "entity": "H-003",
  "decision": "selected",
  "reasons": [
    {
      "type": "hard_constraint",
      "status": "passed",
      "text": "ICU capability available"
    },
    {
      "type": "resource",
      "status": "passed",
      "text": "Ventilator available"
    },
    {
      "type": "acceptance",
      "status": "passed",
      "text": "Hospital accepted emergency"
    },
    {
      "type": "routing",
      "status": "positive",
      "text": "ETA 12 minutes"
    }
  ]
}
```

This data must be persisted through `decision_runs` and `decision_candidates`.

---

# 42. AI / ML Architecture

AI/ML must be modular.

```text
ml/
├── eta/
├── readiness/
├── demand/
├── feature_store/
├── registry/
├── inference/
└── evaluation/
```

---

# 43. ML Model 1 — ETA Prediction

Possible model:

```text
XGBoost
LightGBM
```

Inputs may include:

- route provider ETA
- distance
- traffic level
- time of day
- day of week
- historical route time
- weather if legitimately available
- road congestion
- ambulance class

Output:

```text
predicted ETA
confidence interval
```

Fallback:

```text
routing provider ETA
```

---

# 44. ML Model 2 — Hospital Readiness

Potential features:

- current resource availability
- historical response time
- current emergency load
- recent acceptance rate
- resource volatility
- incoming patient queue

Output:

```text
readiness_probability
```

Example:

```text
H-003

Predicted readiness: 0.92
Confidence: 0.81
```

This must never override a mandatory resource constraint.

---

# 45. ML Model 3 — Demand Forecasting

Potential future module:

```text
hospital demand forecast
```

Use cases:

- expected ED crowding
- ICU demand
- staffing pressure
- resource allocation

Not required for MVP unless time allows.

---

# 46. ML Safety Rules

ML prediction must include:

```text
prediction
model_version
timestamp
confidence
feature_version
fallback_used
```

Example:

```json
{
  "prediction": 0.89,
  "model_version": "readiness-v1.0",
  "confidence": 0.81,
  "fallback_used": false
}
```

---

# 47. ML Fallback

If:

```text
model unavailable
confidence low
features stale
prediction timeout
```

then:

```text
use deterministic scoring
```

The system must continue operating.

---

# 48. Voice Interface

Supported languages for the hackathon:

```text
English
Malayalam
Hindi
```

Voice should primarily support:

- hands-free status queries
- destination confirmation
- mission information
- ETA query
- route status
- hospital readiness
- informational commands

High-impact actions require confirmation.

---

# 49. Voice Safety

Unsafe:

```text
"Cancel ambulance."
```

Do not immediately execute.

Safe flow:

```text
User:
"Cancel mission."

System:
"Cancel Mission INC-0042?"

User:
"Confirm."

System:
Mission cancellation submitted.
```

---

# 50. Voice Architecture

```text
Microphone
   ↓
Speech Recognition
   ↓
Language Detection
   ↓
Intent Parser
   ↓
Authorization Check
   ↓
Confirmation if required
   ↓
Command Handler
   ↓
Application API
   ↓
TTS Response
```

---

# 51. WebSocket Architecture

Use WebSockets for realtime operations.

Connection:

```text
/ws
```

Channels:

```text
mission:{mission_id}
incident:{incident_id}
hospital:{hospital_id}
ambulance:{ambulance_id}
dispatcher:{user_id}
```

---

# 52. Realtime Events

Examples:

```text
ambulance.location.updated
ambulance.status.changed
mission.created
mission.assigned
mission.route.updated
hospital.acceptance.requested
hospital.accepted
hospital.rejected
resource.reserved
resource.released
hospital.readiness.changed
mission.alert.created
mission.completed
```

---

# 53. Event Payload

Example:

```json
{
  "event": "ambulance.location.updated",
  "timestamp": "2026-09-12T18:11:43Z",
  "mission_id": "MSN-0042",
  "ambulance_id": "AMB-004",
  "location": {
    "lat": 9.9312,
    "lng": 76.2673
  },
  "mode": "SIMULATED"
}
```

---

# 54. WebSocket Reliability

Client must handle:

```text
connected
reconnecting
stale
disconnected
```

Show explicit UI state:

```text
● Live
◐ Reconnecting
⚠ Data stale
○ Offline
```

The UI must not silently show stale realtime data as current.

---

# 55. Simulation Architecture

The hackathon environment requires deterministic demo scenarios.

Simulation engine must support:

```text
create scenario
start scenario
pause scenario
resume scenario
inject event
accelerate time
reset scenario
```

---

# 56. Golden Demo Scenario

Scenario:

```text
Severe road traffic accident
        ↓
Critical trauma patient
        ↓
Needs:
- Trauma
- ICU
- Ventilator
- Emergency surgery
        ↓
Ambulance matching
        ↓
Closest ambulance rejected
because capability mismatch
        ↓
Suitable ambulance selected
        ↓
Route calculated
        ↓
Hospital matching
        ↓
Hospital 1 rejected:
No ICU
        ↓
Hospital 2 rejected:
No trauma capability
        ↓
Hospital 3:
✓ ICU
✓ Trauma
✓ Ventilator
✓ Surgery
        ↓
Hospital accepts
        ↓
Resources reserved
        ↓
Ambulance starts mission
        ↓
Live tracking
        ↓
Traffic increases
        ↓
Route changes
        ↓
ETA updated
        ↓
Hospital receives updated ETA
        ↓
Patient arrives
        ↓
Emergency handover
```

---

# 57. Simulation Data Rules

Every simulated object must contain:

```text
data_mode = SIMULATED
```

Examples:

```text
LIVE
SIMULATED
REPLAY
MOCK
UNKNOWN
```

---

# 58. Database Entities

Core entities:

```text
users
roles
user_roles

incidents
patient_requirements

ambulances
ambulance_equipment
ambulance_locations
ambulance_assignments

hospitals
hospital_capabilities
hospital_resources
resource_events

acceptance_requests
reservations

missions
mission_events

routes
route_alternatives

decision_runs
decision_candidates
decision_reasons

prediction_records
model_registry

notifications
audit_logs

simulation_scenarios
simulation_events
```

---

# 59. Identifier Convention

Internal database IDs:

```text
UUID
```

Human-friendly identifiers:

```text
INC-000001
AMB-001
H-001
MSN-000042
RES-000091
DEC-000071
```

Never expose sequential internal IDs where security risk exists.

---

# 60. Data Freshness

Every operational state must carry:

```text
updated_at
source
confidence
data_mode
```

Example:

```json
{
  "available_icu_beds": 2,
  "updated_at": "2026-09-12T18:12:00Z",
  "source": "hospital_simulator",
  "confidence": 1.0,
  "data_mode": "SIMULATED"
}
```

---

# 61. Unknown vs Zero

Critical rule:

```text
0 = confirmed zero

NULL / UNKNOWN = not known
```

Never treat:

```text
unknown ICU availability
```

as:

```text
ICU unavailable
```

or:

```text
ICU available
```

Use explicit data states.

---

# 62. Authentication

Recommended MVP:

```text
JWT or secure HttpOnly session
```

Roles:

```text
DISPATCHER
AMBULANCE_OPERATOR
HOSPITAL_STAFF
HOSPITAL_ADMIN
SYSTEM_ADMIN
DEMO_CONTROLLER
```

---

# 63. Role Permissions

Example:

| Action | Dispatcher | EMT | Hospital | Admin |
|---|---:|---:|---:|---:|
| Create incident | ✓ | | | ✓ |
| Assign ambulance | ✓ | | | ✓ |
| View mission | ✓ | ✓ | ✓ | ✓ |
| Update GPS | | ✓ | | |
| Accept patient | | | ✓ | ✓ |
| Reserve resource | ✓ | | ✓ | ✓ |
| Edit hospital capability | | | | ✓ |
| Run simulation | | | | ✓ |

Backend must enforce authorization.

Frontend role hiding is not security.

---

# 64. API Validation

Use Pydantic for backend validation.

Use Zod for frontend validation.

Example backend:

```python
class CreateIncidentRequest(BaseModel):
    latitude: float
    longitude: float
    severity: Literal["LOW", "MODERATE", "SEVERE", "CRITICAL"]
    trauma: bool
    icu_required: bool
    ventilator_required: bool
```

Reject malformed input before business logic.

---

# 65. Error Handling

Standard response:

```json
{
  "error": {
    "code": "HOSPITAL_RESOURCE_UNAVAILABLE",
    "message": "Required ICU capacity is no longer available.",
    "request_id": "req_abc123"
  }
}
```

---

# 66. Error Categories

```text
VALIDATION_ERROR
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
NOT_FOUND
CONFLICT
RESOURCE_UNAVAILABLE
ROUTING_PROVIDER_ERROR
HOSPITAL_API_ERROR
GPS_STALE
ML_FAILURE
VOICE_FAILURE
NETWORK_ERROR
INTERNAL_ERROR
```

---

# 67. Failure-Safe Behavior

## GPS Failure

```text
GPS stale
↓
Mark ambulance location stale
↓
Reduce confidence
↓
Notify dispatcher
↓
Do not rely blindly on stale location
↓
Fallback to last known position
```

---

## Hospital API Failure

```text
Hospital integration unavailable
↓
mark data source unavailable
↓
prevent unsafe automatic assumption
↓
use last known state only within configured freshness window
↓
request manual confirmation if necessary
```

---

## Hospital Rejection

```text
Reject
↓
Remove from eligible preferred candidates
↓
Recalculate hospital ranking
↓
Notify dispatcher
↓
Request confirmation for new destination
```

---

## Route API Failure

```text
Routing provider fails
↓
Try secondary provider
↓
If unavailable:
use cached route
↓
mark route confidence low
↓
human intervention
```

---

## ML Failure

```text
ML unavailable
↓
deterministic scoring
↓
continue mission
```

---

# 68. Stale Data Policy

Example configurable thresholds:

```text
Ambulance GPS:
≤ 15 sec = fresh
15–60 sec = aging
> 60 sec = stale

Hospital resource state:
≤ configured threshold = current
> threshold = stale
```

Thresholds must be configurable.

Do not present these values as clinical standards.

---

# 69. Reservation Concurrency

Reservation must prevent:

```text
Hospital ICU = 1 available

Mission A reserves 1
Mission B simultaneously reserves 1
```

Both cannot succeed.

Use:

```text
transaction
+
row lock
+
capacity validation
```

---

# 70. Audit Logging

Record important actions:

```text
login
logout
incident.created
incident.updated
ambulance.assigned
hospital.accepted
hospital.rejected
reservation.created
reservation.released
route.changed
decision.executed
manual.override
simulation.started
simulation.reset
```

Audit record:

```json
{
  "actor": "USR-003",
  "action": "HOSPITAL_ACCEPTED",
  "entity_id": "H-003",
  "timestamp": "...",
  "metadata": {},
  "source": "UI"
}
```

---

# 71. Human Override

Authorized dispatcher/admin can override:

- ambulance recommendation
- hospital recommendation
- route recommendation

Override must require:

```text
user
timestamp
reason
previous decision
new decision
```

Example:

```text
Manual override:
Dispatcher selected H-004.

Reason:
Receiving hospital requested direct coordination.
```

---

# 72. Notification Architecture

Notification types:

```text
IN_APP
WEBSOCKET
EMAIL
SMS
PUSH
VOICE
```

For MVP prioritize:

```text
WebSocket
In-app
```

External SMS/email integrations are optional.

---

# 73. Notification Events

Examples:

```text
AMBULANCE_ASSIGNED
HOSPITAL_ACCEPTANCE_REQUEST
HOSPITAL_ACCEPTED
HOSPITAL_REJECTED
RESOURCE_RESERVED
ROUTE_UPDATED
ETA_CHANGED
HOSPITAL_READY
CRITICAL_ALERT
```

---

# 74. Observability

Backend must implement structured logging.

Each request should have:

```text
request_id
user_id
route
duration
status
```

Every emergency mission should have:

```text
mission_id
incident_id
```

in logs.

---

# 75. Metrics

Track:

```text
ambulance_assignment_latency
hospital_matching_latency
decision_engine_latency
route_calculation_latency
reservation_latency
websocket_event_latency
API_error_rate
stale_data_rate
```

Mission metrics:

```text
incident_to_ambulance_assignment
assignment_to_departure
departure_to_hospital_acceptance
acceptance_to_arrival
resource_reservation_time
total coordination time
```

Do not invent performance numbers in presentations.

Measure the actual implementation.

---

# 76. Performance Targets

Initial engineering goals:

```text
Typical API request:
< 500 ms

Decision engine:
< 2 sec for normal MVP scenario

Hospital ranking:
< 2 sec

WebSocket event propagation:
near realtime

Map update:
smooth enough for operational dashboard

Page load:
fast enough for desktop/mobile demo
```

These are engineering targets, not medical guarantees.

---

# 77. Caching

Safe cache candidates:

- hospital metadata
- capability definitions
- static map metadata
- ambulance equipment definitions
- routing configuration

Do not blindly cache highly dynamic resource availability.

---

# 78. Rate Limiting

Protect:

```text
/auth/*
/decision/*
/routes/*
/acceptance/*
/simulation/*
```

Especially:

```text
simulation reset
decision execution
route requests
```

---

# 79. Environment Variables

Backend:

```env
APP_ENV=development
DATABASE_URL=
JWT_SECRET=
CORS_ORIGINS=

ROUTING_PROVIDER=google
GOOGLE_MAPS_API_KEY=
MAPBOX_ACCESS_TOKEN=

REDIS_URL=

ML_MODEL_PATH=
ML_ENABLED=true

VOICE_PROVIDER=
VOICE_API_KEY=

SIMULATION_ENABLED=true
```

Frontend:

```env
VITE_API_BASE_URL=
VITE_WS_URL=
VITE_MAP_PROVIDER=
VITE_MAPBOX_TOKEN=
VITE_GOOGLE_MAPS_KEY=
VITE_ENV=
```

Never commit secrets.

---

# 80. Environment Separation

Provide:

```text
.env.example
.env.development
.env.test
.env.demo
.env.production
```

Production secrets must be injected by deployment platform.

---

# 81. API Security

Required:

```text
HTTPS
secure authentication
RBAC
input validation
SQL injection prevention
CORS configuration
rate limiting
audit logging
secret management
```

Never log:

- passwords
- tokens
- API secrets
- unnecessary patient identifiers

---

# 82. Privacy

The system must minimize patient data.

For hackathon demo use:

```text
synthetic patient identifiers
synthetic medical information
```

Avoid real patient data.

Do not include unnecessary:

- Aadhaar
- phone numbers
- full medical history
- identity documents

---

# 83. External Integrations

Architecture:

```text
                    ┌───────────────┐
                    │ Routing API   │
                    └───────┬───────┘
                            │
┌─────────────┐     ┌───────▼────────┐
│ Hospital    │────▶│ Integration    │
│ Systems     │     │ Layer           │
└─────────────┘     └───────┬────────┘
                            │
┌─────────────┐             │
│ Voice       │─────────────┤
└─────────────┘             │
                            ▼
                    ┌────────────────┐
                    │ FastAPI Core   │
                    └────────────────┘
```

Business logic must not directly depend on third-party SDKs.

---

# 84. Adapter Pattern

Use interfaces.

Example:

```python
class HospitalIntegration(Protocol):

    async def get_capabilities(
        self,
        hospital_id: str
    ) -> HospitalCapabilities:
        ...

    async def get_resources(
        self,
        hospital_id: str
    ) -> HospitalResources:
        ...

    async def request_acceptance(
        self,
        request: AcceptanceRequest
    ) -> AcceptanceResponse:
        ...
```

Implement:

```text
MockHospitalIntegration
RealHospitalIntegration
```

---

# 85. Healthcare Interoperability Readiness

Architecture must allow future integration with:

```text
HL7 FHIR
ABDM ecosystem
Hospital Information Systems
eHospital-like systems
Emergency response infrastructure
```

MVP does not need to implement every interoperability standard.

The system must expose domain boundaries so they can be added later.

---

# 86. Frontend API Client

Never call `fetch()` randomly from components.

Use:

```text
src/lib/api/
```

Example:

```typescript
api.incidents.create()
api.ambulances.match()
api.hospitals.rank()
api.missions.get()
api.reservations.create()
```

Centralize:

- auth headers
- retry behavior
- errors
- serialization
- request IDs

---

# 87. Type Safety

Generate or manually maintain shared API types.

Preferred:

```text
OpenAPI
    ↓
generated TypeScript types
```

FastAPI automatically exposes OpenAPI.

Use:

```text
/api/v1/openapi.json
```

as source of truth.

---

# 88. Database Migration

Use:

```text
Alembic
```

Migration naming:

```text
0001_initial_schema
0002_add_patient_requirements
0003_add_resource_reservations
...
```

Never modify old applied migrations.

Create a new migration.

---

# 89. Seed Data

Seed:

```text
10–30 ambulances
8–15 hospitals
multiple capabilities
hospital resources
demo users
simulation scenarios
routing mock data
```

Include intentionally conflicting cases.

Example:

```text
Hospital A:
near but no ICU

Hospital B:
ICU but no trauma

Hospital C:
complete match
```

This ensures the intelligence is visible during demo.

---

# 90. Test Data

Test cases must cover:

### Ambulance

```text
closest suitable
closest unsuitable
no ambulance
stale GPS
equipment missing
ambulance becomes unavailable
```

### Hospital

```text
closest suitable
closest unsuitable
no ICU
no trauma
resource becomes unavailable
hospital rejects
hospital accepts
hospital API stale
```

### Routing

```text
normal route
traffic change
provider failure
fallback provider
```

### Reservations

```text
successful reservation
concurrent reservation
resource unavailable
release
consume
expiration
```

---

# 91. Unit Testing

Backend:

```text
pytest
```

Test:

```text
constraint logic
scoring
ranking
reservation
state transitions
permission checks
prediction fallback
failure handling
```

Example:

```python
def test_hospital_without_icu_is_ineligible():
    ...
```

---

# 92. Frontend Testing

Use:

```text
Vitest
React Testing Library
```

Test:

- hospital cards
- ambulance ranking
- alerts
- mission timeline
- form validation
- role-based UI
- route updates
- realtime state

---

# 93. End-to-End Testing

Use:

```text
Playwright
```

Critical test:

```text
Create emergency
→ requirements generated
→ ambulance matched
→ hospital matched
→ acceptance
→ reservation
→ mission started
→ live update
→ route update
→ arrival
```

---

# 94. Critical E2E Scenario

Automate the full golden path.

Expected:

```text
INC-TEST-001

↓
AMB-TEST-03

↓
H-TEST-03

↓
RES-TEST-001

↓
MSN-TEST-001

↓
COMPLETED
```

---

# 95. State Machines

Mission states:

```text
CREATED
TRIAGED
AMBULANCE_RECOMMENDED
AMBULANCE_ASSIGNED
EN_ROUTE_TO_PATIENT
PATIENT_ONBOARD
HOSPITAL_SELECTION
ACCEPTANCE_PENDING
HOSPITAL_ACCEPTED
RESOURCE_RESERVED
EN_ROUTE_TO_HOSPITAL
HOSPITAL_READY
ARRIVED
HANDOVER_COMPLETE
CANCELLED
FAILED
```

Invalid transitions must be rejected.

---

# 96. Example State Transition

Valid:

```text
CREATED
→ TRIAGED
→ AMBULANCE_ASSIGNED
→ EN_ROUTE_TO_PATIENT
→ PATIENT_ONBOARD
→ HOSPITAL_ACCEPTED
→ RESOURCE_RESERVED
→ EN_ROUTE_TO_HOSPITAL
→ ARRIVED
→ HANDOVER_COMPLETE
```

Invalid:

```text
CREATED
→ HANDOVER_COMPLETE
```

must fail.

---

# 97. Route Recalculation Trigger

Recalculate when:

```text
traffic changes materially
route becomes unavailable
hospital changes
ambulance changes
major ETA deviation
dispatcher requests reroute
```

Do not recalculate continuously without need.

---

# 98. Hospital Reranking Trigger

Recalculate hospital recommendations when:

```text
resource availability changes
hospital rejects
hospital acceptance expires
ETA changes materially
new higher-priority hospital becomes available
hospital operational status changes
required patient condition changes
```

---

# 99. Priority Handling

For multiple incidents:

```text
CRITICAL
SEVERE
MODERATE
LOW
```

Higher-priority cases may preempt lower-priority recommendation queues.

Any preemption must:

```text
be logged
be explainable
not silently cancel an existing mission
```

---

# 100. Emergency Resource Allocation

Optional advanced optimization:

```text
Incident A:
critical
ICU + ventilator

Incident B:
severe
trauma

Incident C:
moderate
normal ED
```

Optimizer should assign limited ambulances/resources using:

```text
priority
clinical requirements
distance
resource availability
estimated response
```

For MVP, support one active emergency first and multiple emergencies second.

---

# 101. Background Jobs

Optional background processing:

```text
ETA prediction refresh
stale data detection
reservation expiration
notification retries
simulation events
analytics aggregation
```

For MVP these can run using lightweight worker/background tasks.

Do not introduce Kubernetes.

---

# 102. Queue Technology

Do not require Kafka for MVP.

Preferred progression:

```text
MVP:
FastAPI background tasks / lightweight worker

Scale:
Redis Queue / Celery / managed queue

Large production:
event streaming architecture
```

---

# 103. Docker

Provide:

```text
Dockerfile
docker-compose.yml
```

Local services:

```text
frontend
backend
postgres
optional redis
```

Example:

```text
docker compose up
```

must start the development stack.

---

# 104. Local Development

Expected workflow:

```bash
pnpm install

pnpm dev
```

Backend:

```bash
cd apps/api
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Database:

```bash
docker compose up postgres
alembic upgrade head
```

---

# 105. Monorepo Structure

Recommended:

```text
smart-ambulance/
│
├── apps/
│   ├── web/
│   └── api/
│
├── packages/
│   ├── shared-types/
│   ├── config/
│   └── ui/
│
├── infra/
│   ├── docker/
│   └── deployment/
│
├── docs/
│   ├── plan.md
│   ├── prd.md
│   ├── techspec.md
│   ├── database.md
│   ├── appflow.md
│   └── design.md
│
├── scripts/
├── tests/
├── docker-compose.yml
├── README.md
└── .env.example
```

---

# 106. Shared Types

Shared domain concepts:

```text
Incident
PatientRequirement
Ambulance
Hospital
Capability
Resource
Reservation
Mission
Route
Decision
Prediction
Notification
```

Do not duplicate incompatible definitions in multiple layers.

---

# 107. API Versioning

Current:

```text
/api/v1
```

Future:

```text
/api/v2
```

Do not break existing clients silently.

---

# 108. Response Pagination

List endpoints must support:

```text
page
page_size
cursor
```

depending on endpoint requirements.

Example:

```http
GET /api/v1/hospitals?page=1&page_size=20
```

---

# 109. Filtering

Hospital:

```text
status
capability
resource_status
distance
```

Ambulance:

```text
status
equipment
type
availability
```

Mission:

```text
status
severity
date
```

---

# 110. Sorting

Default sorting:

```text
operational relevance
```

not arbitrary database order.

Example hospital ranking:

```text
decision score ASC
```

or:

```text
priority DESC
```

---

# 111. API Idempotency

Critical operations should support idempotency.

Examples:

```text
reservation creation
acceptance
assignment
mission completion
```

Use:

```text
Idempotency-Key
```

where required.

---

# 112. Concurrency

Protect against:

```text
two dispatchers assigning same ambulance
two users reserving same ICU bed
hospital acceptance changing during ranking
ambulance becoming unavailable
```

Use:

```text
transactions
optimistic locking
status checks
row locks
```

---

# 113. Optimistic Locking

Important resources may include:

```text
version
updated_at
```

Example:

```text
resource.version = 5
```

Update:

```sql
WHERE version = 5
```

then increment:

```text
version = 6
```

---

# 114. Configuration Management

Configurable:

```text
decision weights
freshness thresholds
route provider
ML enable/disable
simulation speed
reservation TTL
notification policy
```

Do not hardcode operational parameters throughout application logic.

---

# 115. Feature Flags

Potential flags:

```text
ENABLE_VOICE
ENABLE_ML
ENABLE_SECONDARY_ROUTING
ENABLE_SIMULATION
ENABLE_AUTO_RERANK
ENABLE_RESOURCE_RESERVATION
ENABLE_MULTI_INCIDENT_OPTIMIZATION
```

---

# 116. Logging Policy

Use structured logs.

Bad:

```text
print("something happened")
```

Good:

```json
{
  "event": "hospital_reranked",
  "mission_id": "MSN-001",
  "hospital_id": "H-003",
  "reason": "resource_changed"
}
```

---

# 117. Monitoring Alerts

Alert when:

```text
API error rate spikes
database unavailable
routing provider failing
WebSocket failure rate increases
hospital data stale
reservation conflicts increase
ML service unavailable
```

---

# 118. Deployment Architecture

Recommended hackathon deployment:

```text
                Internet
                   │
          ┌────────▼─────────┐
          │ Frontend Hosting │
          │ Vercel / CF      │
          └────────┬─────────┘
                   │ HTTPS
          ┌────────▼─────────┐
          │ FastAPI Backend  │
          │ Render / Fly /   │
          │ Cloud Run        │
          └───────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │ PostgreSQL +       │
        │ PostGIS            │
        └────────────────────┘
```

External:

```text
Routing Provider
Voice Provider
Optional Notification Provider
```

---

# 119. Production Evolution

Future architecture:

```text
API Gateway
     ↓
Auth Service
     ↓
Emergency Coordination Service
     ├── Dispatch Service
     ├── Routing Service
     ├── Hospital Service
     ├── Resource Service
     ├── ML Service
     ├── Notification Service
     └── Audit Service
           ↓
    Event Infrastructure
           ↓
    PostgreSQL / Redis / Analytics
```

Do not implement this microservice architecture for the hackathon unless required.

---

# 120. MVP Boundary

## Must Have

```text
✓ Authentication
✓ Dispatcher dashboard
✓ Emergency creation
✓ Patient requirement assessment
✓ Ambulance matching
✓ Hospital matching
✓ Routing
✓ Hospital acceptance
✓ Resource reservation
✓ Live mission tracking
✓ Realtime events
✓ Decision explanation
✓ Simulation mode
✓ Golden demo scenario
```

---

# 121. Should Have

```text
✓ ML ETA prediction
✓ ML hospital readiness
✓ Voice interface
✓ Multi-incident support
✓ Route fallback provider
✓ Advanced analytics
```

---

# 122. Could Have

```text
- Demand forecasting
- Advanced OR-Tools optimization
- FHIR integration
- ABDM integration
- SMS
- Email
- Push notifications
- advanced geofencing
```

---

# 123. Must Not Become

Do not transform the project into:

```text
❌ generic chatbot
❌ blockchain project
❌ AR/VR project
❌ drone system
❌ robotics platform
❌ social network
❌ generic hospital finder
❌ simple ambulance GPS tracker
❌ unnecessary computer vision system
❌ LLM wrapper
```

---

# 124. AI Architecture Boundary

The system must remain:

```text
Emergency Coordination Platform
with AI-Assisted Decision Support
```

not:

```text
AI chatbot for hospitals
```

---

# 125. Data Source Strategy

## Hackathon

Use:

```text
synthetic hospital database
synthetic ambulance fleet
simulated GPS
real public map/routing provider
synthetic emergency cases
replayed traffic events
```

## Future Production

Replace with:

```text
real ambulance AVL
hospital APIs
verified hospital resources
real emergency response systems
real-time traffic
health information systems
authorized interoperability infrastructure
```

---

# 126. Demo Controller

The demo controller should expose controls such as:

```text
[Start Scenario]

[Traffic +50%]

[Hospital H-003 Reject]

[ICU becomes unavailable]

[Ambulance GPS Lost]

[Route Blocked]

[Hospital Ready]

[Hospital Not Ready]

[Reset]
```

This makes system intelligence visible to judges.

---

# 127. Demo Event Architecture

Example:

```text
Judge clicks:
"Hospital H-003 Reject"

        ↓

Simulation Event

        ↓

Hospital State Updated

        ↓

WebSocket Event

        ↓

Decision Engine

        ↓

Hospital Re-ranking

        ↓

New Recommendation

        ↓

Dispatcher Dashboard Updated

        ↓

Ambulance Destination Updated
```

---

# 128. Judge-Facing Intelligence

The UI must visually show:

```text
WHY?
```

Example:

```text
Why not the nearest hospital?

H-001
3.2 km
❌ No ICU

H-002
4.8 km
❌ No trauma capability

H-003
7.1 km
✓ ICU
✓ Trauma
✓ Ventilator
✓ Accepted
✓ Resource Reserved
```

This is more important than adding flashy AI effects.

---

# 129. Confidence Model

Every dynamic recommendation may include:

```text
HIGH
MEDIUM
LOW
```

Example:

```text
Hospital recommendation:
HIGH confidence

Reason:
- fresh resource data
- confirmed hospital acceptance
- current route available
- high-quality ETA
```

---

# 130. Uncertainty Handling

The system must distinguish:

```text
Known available
Known unavailable
Unknown
Stale
Predicted
```

This is essential for safe decision support.

---

# 131. Data Contract Example

Hospital resource:

```json
{
  "resource_type": "ICU_BED",
  "total_capacity": 10,
  "available_capacity": 2,
  "reserved_capacity": 1,
  "occupied_capacity": 7,
  "status": "AVAILABLE",
  "updated_at": "2026-09-12T18:10:00Z",
  "data_mode": "SIMULATED",
  "confidence": 1.0
}
```

---

# 132. Mission Snapshot

A mission snapshot should contain:

```json
{
  "mission_id": "MSN-0042",
  "incident_id": "INC-0042",
  "ambulance_id": "AMB-004",
  "hospital_id": "H-003",
  "status": "EN_ROUTE_TO_HOSPITAL",
  "patient_requirements": {
    "trauma": true,
    "icu": true,
    "ventilator": true
  },
  "eta_seconds": 540,
  "route_confidence": 0.93,
  "hospital_readiness": 0.91
}
```

---

# 133. API Request Correlation

Every API request should include:

```text
X-Request-ID
```

Every emergency workflow should preserve:

```text
incident_id
mission_id
decision_id
```

across services and logs.

---

# 134. Database Integrity Rules

Important constraints:

```text
available_capacity >= 0
reserved_capacity >= 0
occupied_capacity >= 0

available + reserved + occupied
<= total_capacity
```

Active ambulance assignment must be unique.

Active mission must reference:

```text
valid incident
valid ambulance
valid hospital
```

where required by state.

---

# 135. Soft Delete

Operational historical records should generally not be hard-deleted.

Prefer:

```text
is_active
deactivated_at
archived_at
```

Critical mission and audit history must remain.

---

# 136. Backup

Production database must support:

```text
automatic backups
point-in-time recovery where available
migration backups
restore testing
```

For hackathon:

```text
seed script
database dump
```

is sufficient.

---

# 137. API Documentation

FastAPI OpenAPI documentation must be enabled.

Expected:

```text
/docs
/redoc
/openapi.json
```

Use descriptions and examples for critical endpoints.

---

# 138. Developer Documentation

Repository must contain:

```text
README.md
CONTRIBUTING.md
.env.example
docs/architecture.md
docs/api.md
docs/demo.md
```

---

# 139. Code Quality

Backend:

```text
Black
Ruff
Pytest
MyPy where practical
```

Frontend:

```text
ESLint
Prettier
TypeScript strict mode
Vitest
```

---

# 140. TypeScript Rules

Use:

```json
{
  "compilerOptions": {
    "strict": true
  }
}
```

Avoid:

```typescript
any
```

unless explicitly justified.

Prefer:

```typescript
unknown
```

with validation.

---

# 141. Python Rules

Prefer:

```text
type hints
Pydantic models
service boundaries
dependency injection
small modules
explicit exceptions
```

Avoid giant route files.

Bad:

```text
routes.py
= 3000 lines
```

Good:

```text
routers/
services/
decision_engine/
```

---

# 142. Business Logic Placement

Do not put decision logic in:

```text
React components
SQL queries
FastAPI route functions
```

Put it in:

```text
decision_engine/
services/
```

---

# 143. Decision Engine Testability

The decision engine must accept:

```text
incident
ambulances
hospitals
routes
resource state
configuration
```

and return:

```text
recommendations
scores
reasons
confidence
```

without requiring the frontend.

This allows deterministic automated testing.

---

# 144. Example Decision Function

Conceptually:

```python
decision = decision_engine.evaluate(
    incident=incident,
    ambulances=ambulances,
    hospitals=hospitals,
    routes=routes,
    configuration=config
)
```

Return:

```python
DecisionResult(
    ambulance=...,
    hospital=...,
    confidence=...,
    reasons=...,
)
```

---

# 145. Decision Determinism

Given the same:

```text
input state
configuration
model version
```

the deterministic portion should produce the same decision.

Record:

```text
decision_version
config_version
model_version
```

---

# 146. Versioning Decisions

Decision record:

```json
{
  "decision_id": "DEC-1001",
  "engine_version": "1.0.0",
  "config_version": "1.2.0",
  "model_versions": {
    "eta": "1.0"
  }
}
```

---

# 147. Security Threat Model

Potential threats:

```text
unauthorized dispatcher
fake ambulance location
fake hospital capacity
resource reservation abuse
API abuse
token theft
data leakage
replay attacks
malicious simulation access
```

---

# 148. Security Mitigations

Use:

```text
RBAC
HTTPS
JWT/session security
request validation
rate limiting
audit logs
strict simulation access
server-authoritative state
transactional updates
secret management
```

---

# 149. Simulation Security

Simulation endpoints:

```text
/admin/simulation/*
```

must require:

```text
SYSTEM_ADMIN
DEMO_CONTROLLER
```

Never expose unrestricted simulation controls publicly.

---

# 150. Production Safety Boundary

This hackathon prototype is:

```text
decision-support software
```

It must not claim:

```text
autonomous medical decision making
```

Final patient-care decisions remain with authorized professionals.

---

# 151. Recommended Implementation Order

## Phase 1 — Foundation

```text
Repository
Frontend
FastAPI
PostgreSQL
Alembic
Auth
RBAC
```

---

## Phase 2 — Core Entities

```text
Incident
Patient Requirements
Ambulance
Hospital
Resources
Mission
```

---

## Phase 3 — Core Intelligence

```text
Ambulance matcher
Routing
Hospital matcher
Scoring
Explanations
```

---

## Phase 4 — Coordination

```text
Acceptance
Resource reservation
Mission lifecycle
WebSockets
Notifications
```

---

## Phase 5 — Demo

```text
Simulation
Golden scenario
Failure injection
Demo dashboard
```

---

## Phase 6 — AI

```text
ETA prediction
Readiness prediction
Confidence
Fallback
```

---

## Phase 7 — Voice

```text
ASR
Intent
Confirmation
TTS
```

---

# 152. Minimum Vertical Slice

Before adding advanced features, the team must make this path work:

```text
Create Incident
       ↓
Assess Requirements
       ↓
Find Ambulance
       ↓
Calculate Route
       ↓
Find Hospital
       ↓
Hospital Accepts
       ↓
Reserve Resource
       ↓
Start Mission
       ↓
Live Tracking
       ↓
Hospital Ready
       ↓
Arrival
       ↓
Handover
```

This is the most important engineering milestone.

---

# 153. Definition of Done

A feature is not complete until:

```text
✓ Backend implemented
✓ Database migration implemented
✓ Validation implemented
✓ Authorization implemented
✓ Frontend implemented
✓ Error state implemented
✓ Loading state implemented
✓ Realtime state implemented if applicable
✓ Audit event implemented where relevant
✓ Tests written
✓ Demo data added
✓ README/documentation updated
```

---

# 154. Acceptance Criteria

The system is considered MVP-complete when it can demonstrate:

### Emergency

```text
Emergency created successfully.
```

### Ambulance

```text
Suitable ambulance selected using requirements and ETA.
```

### Routing

```text
Real or simulated traffic-aware route generated.
```

### Hospital

```text
Hospital candidates filtered by mandatory requirements.
```

### Acceptance

```text
Hospital can accept or reject.
```

### Resource

```text
Required resource can be reserved transactionally.
```

### Realtime

```text
Ambulance mission updates appear in dashboard.
```

### Failure

```text
Hospital rejection/resource loss triggers reranking.
```

### Explainability

```text
System explains why recommendation was selected.
```

### Demo

```text
Full golden scenario runs from start to completion.
```

---

# 155. Core Architecture Diagram

```text
                         ┌─────────────────────┐
                         │      USERS          │
                         │ Dispatcher / EMT /  │
                         │ Hospital / Admin    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ React + TypeScript  │
                         │ Vite + Tailwind     │
                         └──────────┬──────────┘
                                    │
                         REST + WebSocket
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │ API / Auth / RBAC   │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
      │ Decision     │      │ Routing      │      │ ML Layer     │
      │ Engine       │      │ Engine       │      │ ETA / Ready  │
      └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │ PostgreSQL +        │
                         │ PostGIS             │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    ▼               ▼                ▼
              Hospital         Ambulance        Mission State
              Resources        Locations        & Events
```

---

# 156. Final Technical Architecture

The final MVP architecture should be:

```text
Frontend
React
TypeScript
Vite
Tailwind
TanStack Query
Zustand
React Router
Zod

             ↓

API
FastAPI
Python
Pydantic
SQLAlchemy
Alembic
WebSockets

             ↓

Core Intelligence
Constraint Engine
Weighted Scoring
OR-Tools
XGBoost / LightGBM

             ↓

Data
PostgreSQL
PostGIS

             ↓

External
Google Routes / Mapbox
Voice Services
Optional Hospital APIs

             ↓

Simulation
Synthetic Ambulances
Synthetic Hospitals
Synthetic Resources
Synthetic Emergencies
Event Replay
```

---

# 157. Non-Negotiable Technical Rules

The implementation team must follow these rules:

1. **Never select an unsuitable ambulance because it is closer.**

2. **Never select a hospital that violates a mandatory clinical requirement.**

3. **Never treat unknown data as confirmed availability.**

4. **Never allow client-side code to be the source of truth for resource reservations.**

5. **Never allow AI prediction to override hard constraints.**

6. **Never hide stale or simulated data from users.**

7. **Never allow two missions to reserve the same finite resource incorrectly.**

8. **Never make critical actions silently irreversible.**

9. **Never put core decision logic inside UI components.**

10. **Never claim the prototype is a clinically autonomous system.**

11. **Every important recommendation must have an explanation.**

12. **Every critical operational transition must be auditable.**

---

# 158. Final Engineering Goal

The implementation succeeds when the following statement is visibly true:

> **The system can receive an emergency, understand what the patient needs, identify the nearest suitable ambulance, choose a reliable route, identify the fastest suitable hospital, confirm hospital acceptance, reserve required resources, track the ambulance in realtime, react to changing conditions, and keep all parties synchronized until patient arrival and handover.**

The system should demonstrate:

```text
                EMERGENCY
                    │
                    ▼
            PATIENT REQUIREMENTS
                    │
                    ▼
        ┌────────────────────────┐
        │ SUITABLE AMBULANCE     │
        └────────────┬───────────┘
                     │
                     ▼
              RELIABLE ROUTE
                     │
                     ▼
        ┌────────────────────────┐
        │ SUITABLE HOSPITAL      │
        └────────────┬───────────┘
                     │
                     ▼
               ACCEPTANCE
                     │
                     ▼
            RESOURCE RESERVATION
                     │
                     ▼
             HOSPITAL READY
                     │
                     ▼
              LIVE TRACKING
                     │
                     ▼
               PATIENT ARRIVAL
                     │
                     ▼
              EMERGENCY HANDOVER
```

---

# 159. Final Rule for AI Coding Agents

Any AI coding agent working on this repository must treat:

```text
prd.md
plan.md
appflow.md
design.md
database.md
techspec.md
```

as the project's primary engineering specifications.

When documents conflict:

```text
Safety / correctness
        ↓
prd.md
        ↓
techspec.md
        ↓
database.md
        ↓
plan.md
        ↓
appflow.md
        ↓
design.md
```

However, the agent must flag conflicts rather than silently changing requirements.

The agent must:

- avoid speculative features
- avoid unnecessary dependencies
- avoid unnecessary microservices
- avoid unnecessary AI
- preserve deterministic emergency constraints
- maintain testability
- maintain explainability
- maintain auditability
- distinguish simulated from real data
- preserve future interoperability boundaries
- implement the smallest defensible architecture first

**Primary implementation objective:**

> **Build the smallest reliable system that proves Emergency → Suitable Ambulance → Reliable Route → Suitable Hospital → Acceptance → Resource Reservation → Hospital Ready → Patient Arrival.**