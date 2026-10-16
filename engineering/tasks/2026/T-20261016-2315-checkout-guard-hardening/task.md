---
schema: task/v1
id: T-20261016-2315-checkout-guard-hardening
title: "The checkout guard resolves every data path, refuses links to the live root or its parents at any depth, and costs no import-time walk"
status: done
closed: 2026-10-16
merge_commit: 35e1342
created: 2026-10-16T23:15+05:30
created_by: claude-main
kind: internal
spawned_from: T-20261015-0321-checkout-data-root
related: [T-20261015-0321-checkout-data-root]
approvals:
  - file: acceptance.md
    sha256: 14188b83700eae249e7ab86999d89a0295ccdd634669fcc761b927db69123ba4
    by: owner
    at: 2026-10-16T23:20+05:30
  - file: evidence.md
    sha256: 544749b490e061059ddcbe5565de912d7c4f1b0a4f0decaa3e5856d992d350ba
    by: owner
    at: 2026-10-16
---

## Goal

Close the three QA round 2 ALERTs of checkout-data-root in `backend/config/checkout.py`.

## Why

`_refuse_symlinks_into` resolves each link's own target only: a two-hop link (`data` to a dir whose `alto_data` links into live) and a link to a parent of the live root are accepted. It walks the whole sandbox root on every import (~30 s on a ~450k-file seeded root). `mode: live` is accepted in any clone with a `.git` directory.

## Out of scope

Chat and dashboard cwd-relative paths; Dhan caches (accepted as shared).
