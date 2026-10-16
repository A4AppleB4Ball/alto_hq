---
schema: task/v1
id: T-20261016-2252-hq-generated-views
title: "alto_hq generated views: tasks by status and the owner's approval queue"
status: done
closed: 2026-10-16
merge_commit: 3b945ba
claimed_by:
lease_until: 2026-10-17T23:59+05:30
created: 2026-10-16T22:52+05:30
created_by: owner
kind: internal
related: []
friction: "the amendment changes org/schemas, which README routes through P- items; the task gave no P- path"
branch: eng/T-20261016-2252-hq-generated-views
approvals:
  - file: acceptance.md
    sha256: 9d7843814461396a597589c4480c5ec32cd703d6e11798656ec1ef29365302b1
    by: owner
    at: 2026-10-16T23:43+05:30
  - file: evidence.md
    sha256: 06bb61a9347c35a5c6d2f38abad34cd0c492bdde1c1e82bc2f91ef423cbe7fea
    by: owner
    at: 2026-10-16T23:55+05:30
---

## Goal

A command in alto_hq rebuilds `_generated/by_status.md` (every item grouped by status, with title and link) and `engineering/_generated/approvals.md` (every item with status awaiting_owner or needs_owner and its `waiting_on`) from the item files' frontmatter, per README rules 3–4. Items never move.

## Why

Owner 2026-10-16: tasks should be organised; folders stay put, so a generated view does it.

## Out of scope

Moving items; editing items; a UI.
