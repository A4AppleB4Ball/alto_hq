---
schema: task/v1
id: T-20261016-2200-completeness-awaiting-state
title: "Completeness: a due quarter with no documents is Awaiting and does not block"
status: done
created: 2026-10-16T22:00+05:30
created_by: owner
kind: internal
spawned_from: T-20261016-1718-proposal-gate
related: [T-20261016-1718-completeness-check, T-20261016-1718-proposal-gate, D-20261016-2200-due-nothing-in-awaiting]
approvals:
  - file: acceptance.md
    sha256: 891784628abcc1d4c874db17848220c890d1d56fb386b4808066075ca74e7e88
    by: owner
    at: 2026-10-16T22:30+05:30
  - file: evidence.md
    sha256: 9e771acd34a2d9e2ae4ea46026912a99df4da5670267a1d5a8ad1120550de5aa
    by: owner
    at: 2026-10-16T23:20+05:30
closed: 2026-10-16T23:45+05:30
branch: eng/T-20261016-2200-completeness-awaiting-state
---

## Goal

Change `backend/validation/completeness` so the Due-with-nothing-in state becomes Awaiting (non-blocking) per D-20261016-2200-due-nothing-in-awaiting, bump the check version, update the design page and docs.

## Why

The proposal-gate build refuses on 261 of 485 stance companies, 259 only because of Due-with-nothing-in. Only 11 are Missing.

## Out of scope

Unavailable-at-source evidence; any change to Missing, Stale or the stance-without-chain-start violation.
