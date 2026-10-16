---
schema: task/v1
id: T-20261016-2252-hq-generated-views
title: "alto_hq generated views: tasks by status and the owner's approval queue"
status: awaiting_owner
waiting_on: "review evidence.md and approve the merge"
created: 2026-10-16T22:52+05:30
created_by: owner
kind: internal
related: []
branch: eng/T-20261016-2252-hq-generated-views
approvals:
  - file: acceptance.md
    sha256: d7feba4c53927eea9883253f08332f575d0848acd0a26b2fcbea71af4545ef94
    by: owner
    at: 2026-10-16T23:11+05:30
---

## Goal

A command in alto_hq rebuilds `_generated/by_status.md` (every item grouped by status, with title and link) and `engineering/_generated/approvals.md` (every item with status awaiting_owner or needs_owner and its `waiting_on`) from the item files' frontmatter, per README rules 3–4. Items never move.

## Why

Owner 2026-10-16: tasks should be organised; folders stay put, so a generated view does it.

## Out of scope

Moving items; editing items; a UI.
