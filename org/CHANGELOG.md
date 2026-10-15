# Conventions changelog

## hq/v2 — 2026-10-15

Added the epic type (`E`, `org/epics/`, schema epic/v1)
(P-20261015-1140-epic-type). No existing file changes.

## hq/v1 — 2026-10-15

First version: the README's rules, tree, branches and edge cases, and the
schemas in `org/schemas/` (item, task, evidence, experiment, cohort,
incident, waiver, decision, audit, version, change, role, run, brief, and
the config files).

Amended the same day, before any item used it: `evidence/v1` gained
`round`, `acceptance_sha256`, `outputs_changed` (yes / no / unverified) and
optional `merge_commit` and `runs`, with fixed body sections. No migration:
no evidence file existed yet.
