# Smart Ambulance — topic index

Start lines are listed by topic across all six specs, so one lookup covers
every doc that discusses a topic. A range like `db:1261-1414` spans several
sections; a single number is one section's heading. To read, use
`Read file offset=<line> limit=60`, and read the next 60 only if the section
clearly continues. Built 2026-09-13.

| File | Lines | Notes |
|---|---|---|
| prd.md | 3159 | Sections §1–§72 |
| plan.md | 5673 | §0–§156 |
| appflow.md | 4120 | §1–§155 |
| database.md | 6400 | §1–§281 |
| design.md | 3828 | §1–§164 |
| techspec.md | 7075 | Two documents: master prompt §1–§83 (lines 1–2533), then the spec §1–§159 (2534–7075). Section numbers repeat — use lines |

If the heading at a listed line doesn't match, the spec has been edited. Grep
`^# ` in that file and fix this entry.

Prefixes: `prd`, `plan`, `flow` = appflow, `db` = database, `tech` = techspec, `design`.

---

**Scope, goals, non-goals, MVP** — prd:118, prd:200, prd:458, prd:2444, prd:2489 · plan:94, plan:200, plan:3539 · tech:5939-6009

**Roles, personas, permissions** — prd:285, prd:501 · plan:270, plan:2119 · flow:86, flow:3703 · db:511, db:3276, db:5692 · tech:4437-4475

**Build order, phases, milestones** — plan:3298, plan:3481, plan:3507, plan:4665, plan:4696, plan:5129 · flow:3621 · tech:1738, tech:1845, tech:1874, tech:6634, tech:6720

**Gates, DoD, acceptance** — prd:1849, prd:2398, prd:2856, prd:2924 · plan:4370, plan:4391, plan:5404, plan:5537 · db:4755, db:6127 · tech:1904, tech:2095, tech:2120, tech:2182, tech:6754, tech:6775 · design:3675, design:3711

**Principles, business rules, non-negotiables** — prd:238, prd:1128, prd:2765 · plan:5358, plan:5596 · flow:3974, flow:3991 · db:85, db:6309 · tech:347 (conflict rule), tech:570, tech:642, tech:2268, tech:6946

**Stack, architecture, folders** — prd:2623 · plan:1729, plan:1759, plan:1810, plan:1846, plan:1944, plan:3210 · db:203, db:4912, db:4973 · tech:448, tech:498, tech:1556, tech:2772-2870, tech:3427-3516, tech:5579, tech:6447

**Local dev, commands, env, config, flags** — plan:2595, plan:2633, plan:3066, plan:3182 · db:3411, db:3434, db:3455, db:3475, db:5415-5476 · tech:1622-1685, tech:4893-4933, tech:5523, tech:5551, tech:5805, tech:5823

**API endpoints, errors, idempotency** — prd:2164 · plan:1286-1432, plan:2233, plan:2517 · db:4090, db:4114 · tech:1544, tech:3520-3721, tech:4501-4533, tech:5078, tech:5108, tech:5639-5731

**Realtime, events, WebSocket** — prd:2185 · plan:1218, plan:1260, plan:1424 · flow:1598 (network failure by role), flow:2586, flow:2612 (reconnect, backoff), flow:2952 (offline ambulance), flow:3733 (refresh and reconnect), flow:3771 (multi-tab), flow:3783 (state versioning) · db:2895, db:2913, db:5230-5286 · tech:874, tech:896, tech:914, tech:4123-4207

**Patient requirements, severity, emergency creation** — prd:554, prd:2056 · plan:408 · flow:392-515 · db:593, db:613, db:696-746 · tech:4479

**Ambulance matching** — prd:611, prd:1226 · plan:459, plan:518 · flow:534-633 · db:764-935, db:2168 · tech:713, tech:3132, tech:3161

**Routing, ETA, GPS** — prd:1991, prd:2019 · plan:585, plan:2028 · flow:1176, flow:1198, flow:1215, flow:1542 (provider failure), flow:2718 (error UI), flow:3146 · db:869, db:1559-1653 · tech:759, tech:782, tech:3045-3128, tech:3915, tech:5397

**Hospital matching, capabilities** — prd:1271, prd:1461 · plan:656, plan:713, plan:909 · flow:718-803, flow:3166, flow:3341 · db:936-1053, db:2197, db:2222 · tech:736, tech:3205-3257, tech:3951, tech:5414

**Acceptance, rejection, timeout** — prd:1960 · plan:778 · flow:828-956 (§30–34), flow:916 (rejection reasons), flow:1352 (rejection during travel), flow:3458 (timeout) · db:1209-1260, db:4334 · tech:3264, tech:3618

**Hospital readiness, arrival, handover** — flow:1027, flow:1067, flow:1848, flow:1893, flow:1925 · db:4372, db:4398, db:4422, db:4434 · tech:3951 · design:1664, design:1695, design:2755

**Reservation, capacity, concurrency** — plan:827, plan:1674 · flow:956-1027, flow:2636, flow:3433 · db:1054-1208, db:1261-1414, db:2284-2369, db:2844-2937, db:4294-4531 · tech:802, tech:3302-3373, tech:4639, tech:5754-5801 · design:1234, design:2774-2799

**State machines** — prd:1090 · plan:476, plan:839 · flow:1634, flow:1674 · db:626-676, db:1448-1491, db:5795-5878 · tech:845, tech:5342, tech:5369

**Reassessment, failures, fallbacks** — prd:869, prd:1930-2019 · plan:1137, plan:2267, plan:2335 · flow:1276-1633, flow:3077-3225, flow:3383, flow:3409, flow:3482, flow:3583 · db:5621-5657 · tech:1521, tech:4537-4618

**Freshness, unknown data, confidence** — prd:1510 · plan:1695, plan:4054, plan:4086 · flow:1490, flow:1517, flow:2220, flow:2255 · db:1151, db:2640-2686 · tech:673, tech:4380, tech:4405, tech:4618, tech:6162, tech:6187 · design:1132, design:1158, design:2618, design:2872-2904, design:3582, design:3609

**Explainability, decision trace, override** — prd:885, prd:898 · plan:1097, plan:3988, plan:4027, plan:4823-4936 · flow:583, flow:1939, flow:1966, flow:2192 · db:1654-1789, db:3213, db:4535, db:4562 · tech:1213-1280, tech:3859, tech:4700, tech:6466-6556 · design:1039-1131, design:2519-2617, design:2978-3020

**Optimisation** — prd:1317 · plan:1177 · tech:3830

**AI / ML** — prd:1345 · plan:956-1096, plan:4575, plan:4602 · db:1790-1863 · tech:1163, tech:1187, tech:3898-4046, tech:6009

**Voice** — prd:1426 · plan:2054 · flow:1254, flow:2823-2887 · tech:1126, tech:4047-4122 · design:2709, design:2739

**Demo mode, simulation, seed data** — prd:1535, prd:2382, prd:3015 · plan:1405, plan:2663-2757, plan:3591-3757, plan:3889-3982, plan:5061, plan:5086, plan:5104 · flow:1986-2158, flow:3279, flow:3873, flow:3907, flow:3949 · db:1972-2126, db:2780-2843, db:4180-4235, db:5316-5386 · tech:1284-1410, tech:1685, tech:4211-4309, tech:5155, tech:6026-6124 · design:749, design:2649, design:3427-3514, design:3629

**Judges, pitch, claims, risks** — prd:2655, prd:2685, prd:2697, prd:2747, prd:2780 · plan:192, plan:3761-3867, plan:4277, plan:4329, plan:4355, plan:5178-5281 · flow:2158 · tech:6128 · design:3515, design:3544

**Security, privacy, audit** — prd:2204, prd:2227 · plan:2145-2232, plan:4640 · flow:2366 · db:1906-1971, db:3245-3363, db:4638-4683, db:5675 · tech:1411-1470, tech:4437-4475, tech:4664, tech:4871, tech:4949-4995, tech:6560-6630

**Notifications, alerts** — prd:2033 · plan:4940 · flow:1731, flow:2745-2822 · db:1864-1905, db:2757 · tech:4730, tech:4754 · design:2057-2150, design:3185, design:3371

**Testing** — plan:2759-2883, plan:2934, plan:3126 · db:3489-3668, db:3906-3962, db:4755-4911, db:5749-5794 · tech:1471-1543, tech:5188-5396

**Performance, monitoring, logging** — prd:981, prd:2319-2394 · plan:2437, plan:2457, plan:2504, plan:2539, plan:2573, plan:3154 · db:3787-3905, db:5498-5597 · tech:2035, tech:4772-4870, tech:5839, tech:5862

**Database schema, indexes, migrations** — plan:1451-1668, plan:4753-4819 · db:240-470 (conventions), db:474-2011 (core tables), db:4398 and db:4434 (optional readiness and handover tables), db:2127-2269 (spatial), db:2373-2606 (FKs, indexes, JSONB), db:2941-3190 (constraints, views), db:3364-3407 (migrations), db:5390, db:5997-6102 (minimal/MVP/priority), db:6154 (canonical schema) · tech:929-1024, tech:3379-3426, tech:5132

**UI screens, layout, states** — prd:2258-2294 · plan:4103-4276 · flow:119-341 (structure, nav, dashboard), flow:2662 (loading), flow:2690 (empty states), flow:2718 (error states, including routing unavailable), flow:2745 (critical alerts), flow:2902-2972 (responsive, offline), flow:3656 (route map) · tech:1025-1125, tech:1949-2034, tech:2932 · design:604-1321, design:1559-1876, design:2324-2476, design:3086-3134

**Map** — flow:1156 · tech:1969, tech:3012 · design:351, design:1322-1558, design:3169

**Design system, copy, i18n** — see `design-tokens.md` first · design:57-600, design:1923-1977 (motion), design:2151-2323 (components, tokens, icons), design:3221-3308 (themes), design:3309-3426 (i18n, copy)
