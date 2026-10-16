---
schema: change/v1
id: P-20261016-2252-version-item-epic-sidecars
title: version/v1 extends item/v1; epic/v1 declares its sidecar files
status: awaiting_owner
created: 2026-10-16T23:55+05:30
created_by: dev
evidence: [T-20261016-2252-hq-generated-views]
migration: none
waiting_on: "owner approves this change and the hq/v3 CHANGELOG entry (they ship with T-20261016-2252-hq-generated-views)"
---

## Problem

T-20261016-2252-hq-generated-views builds the status views and the owner's
approval queue from every item schema that extends item/v1. QA round 1 found
two holes: version/v1 did not extend item/v1, so an awaiting_owner version
would never reach the approval queue; and the epic evidence files beside an
epic (`E-….<topic>.md`, with a script beside them, e.g.
`E-20261015-1140-data-storage.measure.py`) were not declared anywhere, so the
build could only skip them silently or fail on them.

## Change

- `version/v1` gains `extends: item/v1`. A version carries the item/v1 fields
  (title, created_by, approvals, closed when final). Its id stays `v<n>` or
  `v<n>.<m>`; the build rejects any other folder under `product/versions/`.
- `epic/v1` gains `sidecar:`, a list of the files allowed beside an epic:
  `org/epics/<year>/E-….<topic>.md` and `org/epics/<year>/E-….<topic>.py`,
  each starting with an existing epic's id.
- `python -m scripts.views.build` fails naming any file under an item folder
  pattern that is not an item, a declared sidecar beside an existing item, or
  a file inside an item's own folder.

Migration: none. No version exists yet; the four existing epic sidecars and
the one script already have the declared form.
