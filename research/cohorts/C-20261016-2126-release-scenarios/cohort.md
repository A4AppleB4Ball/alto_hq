---
schema: cohort/v1
id: C-20261016-2126-release-scenarios
title: Release-validation curated companies
status: active
created: 2026-10-16T21:26+05:30
created_by: owner
builder: "alto f8db8c4: python -m backend.validation.scenarios.selection --as-of 2026-10-15 (candidates); members picked by owner 2026-10-16"
sha256: fccd4097406a3235de9429c8ca19e39276bd99fd7897022e3cbd4644e327a190
size: 5
as_of: 2026-10-15
related: [E-20261015-1140-validation, T-20261016-1928-scenario-selection]
---

## How members are chosen

The selection command lists candidates per failure class from stored state,
with evidence. The owner picked one company per group of classes so that 3-5
companies cover the catalog, with one BSE-only healthy company. FC07 (late
macro) is applied to all; FCR is the random live company chosen per release.
FC02b has no member yet (needs the listed-but-not-ingested check, epic story 17).

## Why the selection does not use evaluated outcomes

The selection reads index, quarter states, intake failures and stance links
only; an AST test asserts it imports no P&L, returns, backtest or book store.
