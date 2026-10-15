---
schema: decision/v1
id: D-20261011-0001-news-server-local-only
title: news_server data is local-machine only; agents never write server data
status: in_force
created: 2026-10-11T00:00+05:30
created_by: owner
decided_by: owner
covers: ["action class: writing production data"]
standing: true
friction: "Imported from alto work/decisions.md on 2026-10-15; the time of day was not recorded, so HHMM is the entry's order."
---

## Decision

`news_server` data is local-machine only. Real server data is synced into `../alto_workspace/workspace/<uid>/` and `../alto_data/` (intake/, system/). Agents never write to either.

## Why

Owner ruling, 2026-10-11.
