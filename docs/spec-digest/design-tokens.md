# Smart Ambulance — design tokens and UI rules

Condensed from design.md on 2026-09-13; conflicts in C28. Look: an operational
command centre — calm, dense, trustworthy. Not futuristic, neon, gamified or
generic SaaS (design:147-170).

## Colour (design:214-338, CSS design:2247-2279)

| Token | Hex | Meaning |
|---|---|---|
| `--color-primary` | #2563EB | Navigation, controls, selection, active route, primary CTA |
| `--color-primary-dark` | #1D4ED8 | Pressed / hover |
| navy / `--color-text` | #0F172A | App shell, header, map overlays; light-theme text |
| `--color-surface` | #FFFFFF | Cards, forms, panels |
| `--color-bg` | #F8FAFC | Page background |
| `--color-critical` | #DC2626 | Critical emergency, resource failure, urgent alert |
| `--color-warning` | #D97706 | Pending, stale, caution |
| `--color-success` | #16A34A | Confirmed, accepted, reserved, ready |
| `--color-info` | #0891B2 | System info, ETA, informational events |
| `--color-text-muted` | #64748B | Secondary text |

- **Dark dispatcher theme** (design:3236-3257): bg #0B1120, surface #111827,
  panel #1E293B, text #F8FAFC, muted #94A3B8.
- **Light hospital theme** (design:3261-3274). Semantic colours never change
  between themes (design:3280-3292).
- **Semantics** (design:323-338): ready/confirmed green · active blue ·
  pending/warning amber · critical/failed red · **unknown grey** · stale
  amber/grey · unavailable red/grey.
- **Never rely on colour alone:** "🟢 CONFIRMED", not a green dot.

## Type, spacing, shape, motion

- **Fonts** (design:417-481): Manrope for headings, big metrics and CTAs; Inter
  for body, forms and tables. Uppercase only for status and system labels.
- **Type scale:**

  | Style | Size / weight |
  |---|---|
  | Display | 32–40 / 700 |
  | H1 | 28–32 / 700 |
  | H2 | 22–24 / 700 |
  | H3 | 18–20 / 650 |
  | Body L | 16 / 500 |
  | Body | 14–15 / 400–500 |
  | Small | 12–13 |
  | Caption | 11–12 / 500 |

- **Spacing** (design:501-534): 4 px base — 4, 8, 12, 16, 20, 24, 32, 40, 48, 64.
  Card padding 20–24, section 24–32, page margin 24–32. Tokens `--space-1`…`--space-6` and `--space-8` (4–32; there is no `--space-7`).
- **Radius** (design:538-550): controls 8 · cards 12 · major panels 14 · modal
  16 · pills 999. Tokens sm 8 / md 12 / lg 16.
- **Shadow** (design:554-576): only `0 2px 8px` soft. Build hierarchy from
  spacing, type and contrast.
- **Borders** (design:580-600): 1 px neutral; 1 px critical; selected 2 px primary.
- **Motion** (design:1923-1974): micro 120–180 ms, card 200–250, panel 250–300,
  map route 300–500. Critical alerts appear instantly. Reduced motion = no
  marker interpolation, no pulsing.

## Layout (design:604-781, design:1738-1873)

- **Dispatcher desktop:** top bar + sidebar (240–260) + flexible map + right
  context panel (360–420) + mission timeline at the bottom.
- **Dashboard priority:** 1 critical alerts · 2 active emergency · 3 current
  decision · 4 map · 5 hospital/ambulance state · 6 timeline · 7 secondary metrics.
- **Top bar:** "EMERGENCY COMMAND", always-visible system health (DB, routing,
  decision engine, WebSocket, ML, voice), DEMO MODE badge, active count, user.
- **Breakpoints:** < 768 mobile · 768–1023 tablet · 1024–1279 small desktop · 1280+.
- **Touch targets:** ≥ 44 px, prefer 48.
- **Ambulance UI** is low distraction: destination, ETA, acceptance, resource,
  navigate, alerts. On mobile the map fills 55–65% with a bottom sheet
  (design:3086-3134).
- **Hospital UI** answers: who is coming, when, what they need, can we accept,
  what to prepare.
- **One-glance rule** (design:3657-3671): the active emergency view shows
  severity, requirements, ambulance, ETA, destination, acceptance, reservation,
  route and critical warnings without navigating.

## Map (design:351-411, design:1322-1558)

- **Ambulance:** blue; selected bright blue + halo; unavailable muted grey.
- **Emergency:** red pin; pulses only when new.
- **Hospital:** selected green + halo; alternatives grey/blue; failure red; unknown grey.
- **Routes:** selected primary blue 5–7 px; alternatives grey dashed 3–4 px;
  congestion amber, severe red.
- **Focus mode:** on selecting an emergency, zoom to bounds, highlight its
  ambulance, hospital and route, and dim everything else.
- Marker movement is interpolated visually only; true coordinates are never altered.

## Components (design:2151-2226)

- **Core:** Button, Input, Select, Badge, Tooltip, Modal, Drawer, Tabs,
  Dropdown, Toast, Alert.
- **Operational:** EmergencyCard, AmbulanceCard, HospitalCard, ResourceCard,
  ReservationCard, DecisionCard, StatusBadge, ConfidenceBadge, FreshnessBadge,
  Timeline.
- **Geospatial:** Map, AmbulanceMarker, HospitalMarker, EmergencyMarker,
  RouteLayer, MapLegend, MapControls.
- **Naming:** domain names (HospitalRecommendationCard), never BlueCard2.

## Required UI behaviours

- **Freshness badge** "● Fresh · 18 sec" / "⚠ Stale · 15 min" / "? Unknown"
  (design:1158-1176).
- **Decision card** shows WHY; raw scores go in a hidden drawer
  (design:1039-1131).
- **Hospital switch** shows "Hospital C → Hospital D" plus the reason, with no
  dramatic animation (design:2568-2595).
- **Readiness** is a checklist, not a gauge. The reservation timer ("Expires in
  08:42") turns to warning near expiry. No "67% complete" bars
  (design:2755-2836).
- **Critical failures** are persistent alerts or modals, never just a toast.
  No modals for routine updates (design:2057-2150).
- **Error copy** = icon + title + what happened + recovery actions, e.g.
  "ROUTING UNAVAILABLE … using last confirmed route [RETRY] [MANUAL MODE]".
  Never "WebSocket error 1006", "SYSTEM ERROR!!!", "No data." or "AI says
  Hospital C." (design:2031-2053, design:3341-3426).
- **Simulated labels** are prominent; AI output is labelled "AI PREDICTION";
  never "[AI MAGIC]" (design:2649-2708).
- **i18n:** English, Malayalam, Hindi; no hardcoded strings; layouts fit longer
  labels (design:3309-3337).
- **Accessibility:** keyboard operation, visible focus, contrast, text
  alternatives, screen-reader labels (design:1877-1919).
- **Before calling a screen done:** run the validation checklist
  (design:3675-3707) and design acceptance criteria (design:3711-3729).
