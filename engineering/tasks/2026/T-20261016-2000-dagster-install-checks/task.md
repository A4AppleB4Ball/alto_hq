---
schema: task/v1
id: T-20261016-2000-dagster-install-checks
title: "Dagster launchd install and the checks that need the Mac"
status: draft
created: 2026-10-16T20:00+05:30
created_by: owner
kind: internal
spawned_from: T-20261016-1718-dagster-environment
related: [T-20261016-1718-dagster-environment, E-20261015-1140-orchestration-and-ops]
branch: eng/T-20261016-2000-dagster-install-checks
---

## Goal

Install the daemon and webserver agents on the Mac and prove they stay up through a kill, a sleep and a reboot.

## Why

Split from T-20261016-1718-dagster-environment so its merge does not wait on checks only the owner can run on the Mac.

## Out of scope

Wrapping the chain (T-20261016-1718-dagster-chain-wrap).
