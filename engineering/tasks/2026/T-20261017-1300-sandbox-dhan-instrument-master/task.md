---
schema: task/v1
id: T-20261017-1300-sandbox-dhan-instrument-master
title: "A new sandbox gets a read-only copy of the live Dhan instrument master; readers raise when the copy is older than the read's date"
status: done
closed: 2026-10-17
merge_commit: 4fefe71
waiting_on:
claimed_by:
lease_until:
friction: check 7's CLI form cannot run before merge (the CLI requires the live main checkout, which has the old code); ran create() from the branch against main instead.
created: 2026-10-17T13:00+05:30
created_by: claude-main
kind: internal
spawned_from: T-20261016-2336-daily-price-store-everywhere
related: [T-20261016-2336-daily-price-store-everywhere, T-20261017-1200-nse-holiday-calendar-store, T-20261016-2252]
approvals:
  - file: acceptance.md
    sha256: a38f8586911b941e325cfcd6d50216773d3d1b478f657ca5b8d36592c186138f
    by: owner
    at: 2026-10-17T13:30+05:30
  - file: evidence.md
    sha256: ea3d8908afcc5b6fe7c520f22517a6c1f1e18f1ae029dd1d8c4af281179ac554
    by: owner
    at: 2026-10-17T18:00+05:30
---

## Goal

`backend.config.new_sandbox_worktree` copies the live checkout's stored Dhan instrument master for named users into the new sandbox, reading the live file only and never calling Dhan. The sandbox reader (`DhanInstrumentMapper.load_stored`) checks the copy's recorded date against the date the read is for, and raises when the copy is older.

## Why

T-2336 QA findings A2 and A3 (evidence.md lines 100-101).

- **A2.** On branch `eng/T-20261016-2336-daily-price-store-everywhere`, `backend/executor/broker_factory/daily_series.py` `_stored_exchange_of` calls `mapper.load_stored()`. That method reads `WorkspacePaths(user_id).system_dir / "dhan_instruments.json"`. In a sandbox, `WORKSPACE_ROOT` is `<sandbox data_root>/data/alto_data/workspace` (paths.py:245). No sandbox has that file and nothing installs it, so every NSE-only exchange check on the sandbox price path raises `FileNotFoundError`. This blocks the SHILPAMED pilot (T-20261016-2252 check 10).
- **A3.** `load_stored` accepts a master of any date. The file already records its date: `_fetch_and_cache` writes `"date": str(date.today())` (dhan_instruments.py:240 on the branch), and `_cache_is_fresh` reads it. If a symbol's exchange listing changed after that date, the reader returns the old segment without raising.

## Proposed design (dev confirms in plan.md)

- **Source.** The live file is `<live data_root>/data/alto_data/workspace/<user_id>/system/dhan_instruments.json`. On the local Mac this is where `load()` writes it (for example, `scienceamit1` is dated 2026-10-16 today). The copy is read-only from the live root, like `seed_index`. Dhan is never fetched.
- **Install.** `new_sandbox_worktree` gets `--seed-instrument-master USER_ID` (repeatable) and a `seed_instrument_master(live_root, sandbox_root, user_id)` function next to `seed_index`. It copies the file byte for byte to the same relative path under the sandbox root. Before creating the worktree it checks that the live file exists, has the six required keys (`instruments, exchanges, ticks, lots, securities, listings`) and a `date`, and raises otherwise, naming the path. The `date` field travels with the file, so the sandbox records the master's date with no new field.
- **Freshness, exact.** `load_stored(as_of: date)` takes the date the read needs, and the reader passes it. In `daily_series` this is the series `end`, which `CachedDailySeries` already receives. `load_stored` raises if `date` is missing, or if `date(cached["date"]) < as_of`. The message names the path, the stored date and `as_of`. No tolerance window and no fallback to fetch. Any other `load_stored` caller is listed in plan.md and passes its own as-of date.
- **Refresh.** A stale sandbox copy is refreshed by re-running the seed from a live master that `load()` has refreshed on a live checkout. The sandbox never refreshes it itself.

## Out of scope

- Point-in-time masters for historical as-of dates. A newer master can disagree with an older listing, for example after a later NSE delisting. That needs a dated master archive. If it matters, park it in `backend/docs/25_future_ideas.md` for the owner.
- The holiday file (T-20261017-1200).
- Fetching the master on the server.

## Notes

- `load_stored` and `_stored_exchange_of` exist only on the T-2336 branch. This task bases on that branch, or lands after it.
- The master is per user. The pilot needs the user id that the sandbox stance run passes to `daily_series` (scienceamit1 per QA). The dev confirms it in plan.md.
