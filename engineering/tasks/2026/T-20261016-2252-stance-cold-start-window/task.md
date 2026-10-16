---
schema: task/v1
id: T-20261016-2252-stance-cold-start-window
title: "Stance cold-start window starts at the company's chain start (lib/chain_start), not a fixed 2026-07-01"
status: ready
claimed_by:
lease_until: 2026-10-17T23:59+05:30
waiting_on: owner - the SHILPAMED sandbox pilot needs prices; AsOfLedger always builds a live Dhan client from scienceamit1's credentials (backend/lib/asof.py:61). Decide how a sandbox gets prices. Also confirm check 11's walk-start change (cold walk begins before the first quarter version)
friction: main's .alto_checkout.yaml landed mid-task, so an existing worktree needed a hand-written sandbox declaration and a hand-copied input set (no seed command beyond the index)
created: 2026-10-16T22:52+05:30
created_by: owner
kind: decision
related: [E-20261015-1140-validation, T-20261016-2147-checks-stance-chain]
evidence_route: "owner 2026-10-16: shadow is parked; this fix restores the owner's stated chain-start rule, so a before/after sandbox comparison (ARSSBL, one legacy, one 2026-07-01 company) replaces research+shadow"
approvals:
  - file: acceptance.md
    sha256: c426d632267169f8af51e08c48b6289f93bed8694328742cabe72b1fe1ce0faf
    by: owner
    at: 2026-10-17T01:43+05:30
---

## Goal

- The stance worker's cold-start link scans from the company's chain start resolved through `backend/lib/chain_start` (whichever came first: FY26 annual filing or first Q1FY27+ version; legacy companies keep their recorded start), not `SCAN_START` (`backend/stance/worker.py:441-445`, `backend/stance/config.py:23`). No second copy of the rule.
- Announcements before `FEED_START_DATE` (2026-07-01) the stores do not hold are handled the FC09 way: fetched, or recorded missing with evidence; the worker raises rather than scanning an empty range.
- `stance_chain` (`backend/validation/stance_chain`) adds the rule: a link's `covers_from` must not be after its `covers_to` (rule in `backend/stance/chain/continuity.py`, shared with the reconciler).
- Existing bad cold-start links (ARSSBL 2026-06-06: covers_from 2026-07-01 > covers_to) are found by the reconciler and rebuilt only through the stance reconciler / rerun commands.

## Why

Owner rule 2026-10-16: the start is min(2026-07-01, FY26 annual publish date). QA of T-20261016-2147-checks-stance-chain (finding F2) found ARSSBL's cold-start window inverted, so announcements 06-06..07-01 were never examined.

## Out of scope

Changing the chain-start rule itself; FC09 body fetching beyond what exists.
