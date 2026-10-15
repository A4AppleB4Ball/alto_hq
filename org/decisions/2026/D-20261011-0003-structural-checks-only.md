---
schema: decision/v1
id: D-20261011-0003-structural-checks-only
title: Checks are structural, never text-matching
status: in_force
created: 2026-10-11T00:00+05:30
created_by: owner
decided_by: owner
covers: ["action class: writing checks"]
standing: true
friction: "Imported from alto work/decisions.md on 2026-10-15; the time of day was not recorded, so HHMM is the entry's order."
---

## Decision

No brittle rules or text-matching checks (hooks, regexes on commands or code). Checks must be structural: parsed code, typed models, rules over real data, the test suite.

## Why

Owner ruling, 2026-10-11.
