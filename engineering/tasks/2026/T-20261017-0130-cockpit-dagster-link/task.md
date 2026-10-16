---
schema: task/v1
id: T-20261017-0130-cockpit-dagster-link
title: "Cockpit: a button to Dagster's UI on the Queue and Pipeline pages, and a Pipeline card with the last chain run's per-company state"
status: ready
created: 2026-10-17T01:30+05:30
created_by: claude-main
kind: internal
depends_on: [T-20261016-1718-dagster-chain-wrap]
related: [T-20261016-1718-dagster-chain-wrap]
approvals:
  - file: acceptance.md
    sha256: 1755eedba85e1a4822c245c5f09e5de39b8687e4b563f7c7ef83e97e9ab8fc61
    by: owner
    at: 2026-10-17T01:35+05:30
---

## Goal

The owner opens Dagster's own UI from the cockpit in a new tab, and sees the last chain run's per-company state on the Pipeline page, without the cockpit importing Dagster.

## Why

Dagster runs on the Mac (compute); the cockpit is served from the thin server. Linking out keeps Dagster's run history and asset views as they are, and the cockpit shows only the stored per-company result.

## Out of scope

Embedding Dagster; changes to the intake funnel counts on the Queue page; auth for Dagster (it binds to localhost); running Dagster on the server.
