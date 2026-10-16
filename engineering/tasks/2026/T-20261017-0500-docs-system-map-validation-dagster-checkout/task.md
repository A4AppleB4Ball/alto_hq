---
schema: task/v1
id: T-20261017-0500-docs-system-map-validation-dagster-checkout
title: "High-level docs: the system map and CLAUDE.md describe the Dagster chain, validation, the checkout modes and the price cache"
status: ready
created: 2026-10-17T05:00+05:30
created_by: claude-main
kind: internal
depends_on: [T-20261016-2259-test-data-guard, T-20261017-0130-cockpit-dagster-link]
approvals:
  - file: acceptance.md
    sha256: 9c673af876165cc59cadbd4dc41d183632d7d20a2937c6c0c2efa825e1a3daf0
    by: owner
    at: 2026-10-17T05:05+05:30
---

## Goal

A new reader (human or agent) learns from the system map and CLAUDE.md that the compute chain runs under Dagster, that validation gates a company's stance, how a checkout declares live, sandbox or test, and how prices and holidays are read.

## Why

`backend/docs/00_system_map.md` does not mention Dagster or the validation package; CLAUDE.md's Data paths section predates `.alto_checkout.yaml`. Agents hit the checkout declaration first and nothing points them to it.

## Out of scope

Code changes; docs for trading and executor (still missing, tracked elsewhere).
