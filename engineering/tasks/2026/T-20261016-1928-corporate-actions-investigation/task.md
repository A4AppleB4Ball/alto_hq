---
schema: task/v1
id: T-20261016-1928-corporate-actions-investigation
title: "Investigate how splits and bonuses flow through prices, stance and positions today (FC12)"
status: awaiting_owner
created: 2026-10-16T19:28+05:30
created_by: owner
kind: internal
related: [E-20261015-1140-validation]
waiting_on: "Approve acceptance.md"
---

## Goal

A findings note answering, with file:line evidence: where corporate actions enter (if anywhere), whether Dhan and cached prices are adjusted, what the stance agents see across a split, how book positions and target quantities change, and which real company in the window had a split or bonus. Ends with the FC12 edit op and expected verdicts to propose. Design: `org/epics/2026/E-20261015-1140-validation.scenario-catalog.md` (story 15).

## Why

FC12 is in the catalog but the owner does not know how the product handles corporate actions; the scenario cannot be written before that is known.

## Out of scope

Any code change.
