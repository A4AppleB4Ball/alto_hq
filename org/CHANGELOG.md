# Conventions changelog

## hq/v3 — proposed 2026-10-16, awaiting owner approval

`version/v1` extends `item/v1`, and `epic/v1` declares its sidecar files
(`E-….<topic>.md` and `E-….<topic>.py` beside an existing epic)
(P-20261016-2252-version-item-epic-sidecars). `python -m scripts.views.build`
rejects any other file under an item folder pattern, and version folders
other than `v<n>` or `v<n>.<m>`. No migration: no version exists, and the
existing sidecars already have the declared form.

## hq/v2 — 2026-10-15

Added the epic type (`E`, `org/epics/`, schema epic/v1)
(P-20261015-1140-epic-type). No existing file changes.

Amended the same day: `epic/v1` gained an optional `Findings` body section
and sibling evidence files (`E-….<topic>.md`), so investigations made while
planning reach the worker who picks up a story. No migration: the section is
optional.

## hq/v1 — 2026-10-15

First version: the README's rules, tree, branches and edge cases, and the
schemas in `org/schemas/` (item, task, evidence, experiment, cohort,
incident, waiver, decision, audit, version, change, role, run, brief, and
the config files).

Amended the same day, before any item used it: `evidence/v1` gained
`round`, `acceptance_sha256`, `outputs_changed` (yes / no / unverified) and
optional `merge_commit` and `runs`, with fixed body sections. No migration:
no evidence file existed yet.
