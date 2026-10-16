---
schema: task/v1
id: T-20261016-1718-lib-regroup
title: "Regroup backend/lib into quarters/, filings/, prices/, resolvers/"
status: needs_owner
waiting_on: "Deferred by owner 2026-10-16: rearrangement only. Do not pick up until the owner sets status back to ready."
created: 2026-10-16T17:18+05:30
created_by: owner
kind: internal
spawned_from: T-20261015-1058-dagster-spike
related: [T-20261016-1718-completeness-check]
approvals:
  - file: acceptance.md
    sha256: 6bd85602eb8be8df29aac1dc003dea918f12b151726a573c8e60da13c6345372
    by: owner
    at: 2026-10-16T18:55+05:30
branch: eng/T-20261016-1718-lib-regroup
---

> Deferred by the owner, 2026-10-16. Acceptance stays approved; set status back to ready when the owner says go.

## Goal

Move the flat modules of `backend/lib/` into feature folders and update every import in one change, no shims. About 150 import lines (quarter_policy 30 files, data_access 29, company_resolver 29, announcement_key 28, concall_dates 22, filing_policy 18, events 16, quarter_versions 14).

## Why

`backend/lib/` is flat and growing; the repo CLAUDE.md prescribes the feature folders.

## Out of scope

Any behaviour change. Needs the owner's go-ahead on timing: it breaks the roughly 18 worktrees on old paths. Run when nothing else is mid-flight.
