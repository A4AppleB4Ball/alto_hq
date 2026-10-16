---
schema: task/v1
id: T-20261016-2200-completeness-awaiting-state
title: "Completeness: a due quarter with no documents is Awaiting and does not block"
status: ready
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
claimed_by: claude-main-20261016-1900
lease_until: 2026-10-17T22:00+05:30
branch: eng/T-20261016-2200-completeness-awaiting-state
---

## Goal

Change `backend/validation/completeness` so the Due-with-nothing-in state becomes Awaiting (non-blocking) per D-20261016-2200-due-nothing-in-awaiting, bump the check version, update the design page and docs.

## Why

The proposal-gate build refuses on 261 of 485 stance companies, 259 only because of Due-with-nothing-in. Only 11 are Missing.

## Out of scope

Unavailable-at-source evidence; any change to Missing, Stale or the stance-without-chain-start violation.
