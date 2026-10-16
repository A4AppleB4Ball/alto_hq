---
schema: task/v1
id: T-20261016-2252-hq-generated-views
title: "alto_hq generated views: tasks by status and the owner's approval queue"
status: in_progress
created: 2026-10-16T22:52+05:30
created_by: owner
kind: internal
related: []
friction: "the amendment changes org/schemas, which README routes through P- items; the task gave no P- path"
branch: eng/T-20261016-2252-hq-generated-views
approvals:
  - file: acceptance.md
    sha256: 58869235dc1826fba05edf7c5b485a3797beab9ad19a4759d5c66937b3bf6a1a
    by: owner
    at: 2026-10-16T23:29+05:30
---

## Goal

A command in alto_hq rebuilds `_generated/by_status.md` (every item grouped by status, with title and link) and `engineering/_generated/approvals.md` (every item with status awaiting_owner or needs_owner and its `waiting_on`) from the item files' frontmatter, per README rules 3–4. Items never move.

## Why

Owner 2026-10-16: tasks should be organised; folders stay put, so a generated view does it.

## Out of scope

Moving items; editing items; a UI.
