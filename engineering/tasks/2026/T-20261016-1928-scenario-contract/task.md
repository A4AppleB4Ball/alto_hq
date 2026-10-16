---
schema: task/v1
id: T-20261016-1928-scenario-contract
title: "Scenario contract (scenario/v1, edits, timeline, expected verdicts) and catalog validator"
status: done
created: 2026-10-16T19:28+05:30
created_by: owner
closed: 2026-10-17T00:20+05:30
merge_commit: 8bd1c6c
kind: internal
related: [E-20261015-1140-validation, T-20261016-1928-case-freezer]
approvals:
  - file: acceptance.md
    sha256: 689d3cff8618237d8d576a0d8fd9eae8681cbedc668d40272aeccfe1b3dfb9d5
    by: owner
    at: 2026-10-16T19:40+05:30
  - file: evidence.md
    sha256: 2a3896e19f94cebe061b97d15ba15d25ef8c66a8553c9b8aa44c8321161f09f3
    by: owner
    at: 2026-10-16T23:30+05:30
branch: eng/T-20261016-1928-scenario-contract
---

## Goal

`backend/validation/scenarios/contract.py` defines scenario/v1, the closed edit vocabulary, timeline checkpoints and expected-verdict files (pydantic). `python -m backend.validation.scenarios.catalog --root ../alto_testcases` validates every scenario and the release set's class coverage. Design: `org/epics/2026/E-20261015-1140-validation.scenario-catalog.md` (story 11).

## Why

Scenarios are data written by many agents; the contract is what stops them drifting from the cases and the checks.

## Out of scope

Applying edits (needs the sandbox from T-20261015-0321-checkout-data-root), writing scenarios, the check catalogue (story 5).
