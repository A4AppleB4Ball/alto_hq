---
schema: decision/v1
id: D-20261016-2200-due-nothing-in-awaiting
title: A due quarter with no documents is Awaiting, not blocking, until the next quarter's data comes in
status: in_force
created: 2026-10-16T22:00+05:30
created_by: owner
decided_by: owner
covers: [T-20261016-2200-completeness-awaiting-state, T-20261016-1718-proposal-gate]
standing: true
---

## Decision

In the completeness definition (D-20261016-1718-completeness-definition) the state Due-with-nothing-in no longer blocks. A quarter that is due, holds no document, and has no later quarter holding one is Awaiting: reported, non-blocking, and it closes (to Not released) when a later quarter holds documents. Missing, Stale and a stance without a chain start still block.

## Why

On 2026-10-16 the check over the 485 stance companies found 261 incomplete, 259 of them only Due-with-nothing-in (245 Q1 FY27, 14 Q2 FY27) and 11 truly Missing. With the whole-proposal block, the 259 would stop every proposal. The source cannot tell not-yet from never; the owner's Open rule (open until the next quarter's data comes in) is applied to a quarter with no documents too.

## Conditions

Revisit when the results calendar plus a source check can show a document is unavailable at source (E-20261015-1140-validation story 7).
