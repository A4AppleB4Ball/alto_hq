# Handoff: T-20261016-2252-stance-cold-start-window

Branch `eng/T-20261016-2252-stance-cold-start-window`, worktree `alto/.claude/worktrees/T-20261016-2252-stance-cold-start-window`. Base `4c44dbf` (main; already has `backend/stance/chain/continuity.py` and `backend/validation/stance_chain`). Commits:
- `16bc453` Stance: cold-start window from lib/chain_start; ledger reads pre-feed days, raises on inverted window
- `0c2a56b` Validation: inverted window fails stance_chain (CHECK_VERSION 2) and the reconciler (state `inverted_window`, a rewind state in `stance.ready`)
- `488d3d6` Validation: `stance_chain.cli --fleet`
- `b1932d5` Stance: test made independent of suite order

## Decision the owner must confirm (read first)
The goal text says "scans from the company's chain start"; the owner rule it cites says "min(2026-07-01, FY26 annual publish date)". These differ for the 300 of 485 companies whose chain start is after 2026-07-01 (e.g. 3BBLACKBIO, start 2026-08-13): the literal chain start would shrink their first window and drop every announcement from 2026-07-01 up to the start, which they examine today. I implemented the owner rule: `stance_scan_start = min(chain.start_date, FEED_START_DATE)` in `backend/lib/chain_start/policy.py` (one place; the worker imports it). Legacy (2026-01-01) and ARSSBL (2026-06-06) get their chain start; companies starting after the feed keep 2026-07-01. If the owner wants the literal chain start, it is a one-line change there plus the 300-company behaviour change.

## Acceptance checks
1. **One rule** - PASS. `stance/tests/test_cold_start_window_rule.py`: worker has no `SCAN_START` name/import, uses `stance_scan_start`, and has no YYYY-MM-DD literal. `lib/chain_start/tests/test_policy.py` pins the rule (pre-feed annual, legacy, after-feed, no start raises).
2. **ARSSBL** - PASS on the "raises" branch. Sandbox runner (`--symbols ARSSBL --once --output-dir <tmp> --end-date 2026-06-06`, LLM calls patched to raise, ledger windows logged; wrapper `$TMPDIR/sbx_runner/run_blocked.py`):
   - before (base): `WINDOW ARSSBL 2026-07-01..2026-06-06 -> 0`, then went on to Agent A (stopped only by the LLM block) - i.e. it would write the inverted link again.
   - after: `WINDOW ARSSBL 2026-06-06..2026-06-06 -> 3 announcement(s)`, then `halted: MissingAnnouncementBody: bse_544530_9fce2b86-... (2026-06-06, bse:40871418-....pdf): no stored body; backfill the filing`. The window equals the chain start (2026-06-06 <= covers_to) and holds 3 filings never examined before; their bodies are not stored, so the worker raises naming the filing (FC09 route). No link was rebuilt: that needs the bodies backfilled first.
3. **Legacy (RAJRATAN)** - PASS. Stored cold link 2026-01-21 covers 2026-01-01, n=6. after: `WINDOW RAJRATAN 2026-01-01..2026-01-21 -> 6` (identical to the stored link). before (base) would now give `2026-07-01..2026-01-21 -> 0` (inverted) - base code had silently broken every legacy cold start.
4. **Inverted window fails** - PASS. Tests in `validation/stance_chain/tests/test_stance_chain.py` (check and reconciler, naming the link; one shared `continuity.inverted_window`). Live read-only fleet: `python -m backend.validation.stance_chain.cli --fleet` -> `fleet: 485 companies, failing links by reason {'inverted_window': 16}, 1 read error(s) ['BHADORA']` (exit 1). Links: 539730 06-08, 544440 01-27, 544451 06-01, 544563 05-29, ABDL 06-12, ALOKINDS 06-29, ARSSBL 06-06, DSFCL 06-20, EMUDHRA 05-25, HPTL 06-29, KRISHNADEF 06-20, MAWANASUG 06-11, PNGSREVA 06-04, RAYMOND 06-23, SHILPAMED 02-06, SMCGLOBAL 06-04 (all 2026, all cold-start links with covers_from 2026-07-01). An independent scan of the logs found the same 16. `python -m backend.stance.reconcile --companies ARSSBL SHILPAMED` -> both `inverted_window`, rebuild_from the cold link.
5. **Repair path** - NOT DONE. Rebuilding needs `stance.ready --fix...`-style rewind plus a stance rerun, i.e. LLM spend, and a sandbox copy of the stance store. Not run (brief: ask before LLM spend). ARSSBL cannot be rebuilt anyway until its 3 bodies of 2026-06-06 are backfilled. Note `stance.ready` only auto-rewinds `skipped_input`; `inverted_window` reports NOT READY and needs the human-approved rewind (backend/stance/ready.py:56). Proposed pilot: SHILPAMED (legacy, all 9 bodies stored) in a sandbox stance dir, rewind from 2026-02-06 and rerun; ARSSBL after body backfill.
6. **Unchanged elsewhere** - PASS. DBOL (chain start 2026-07-01): `WINDOW DBOL 2026-07-01..2026-07-01 -> 3` before and after. Also 3BBLACKBIO (start after feed): `2026-07-01..2026-08-13 -> 5` before and after.
7. **Suite** - PASS. `pytest stance validation lib stores/tests/test_boundaries.py`: 420 passed. Full suite (`--continue-on-collection-errors`): base 66 FAILED/ERROR, branch 66, `comm -23 new base` empty. Entry points import: stance.runner/reconcile/ready/worker, validation.stance_chain.cli, e2e.run, intake.runner, workflow.cli, lib.asof.

No production write: the runner ran with `--output-dir` in a temp dir; `find` on alto_data/stances/ARSSBL, triggers, intake newer than the run marker: none.

## Behaviour changes the owner must know
- `AsOfLedger.announcements_between` no longer returns [] for pre-feed windows: it reads the day files and raises on a missing day, on a body-less attachment (in the worker), on start > end, and on start before 2026-01-01. Any rerun touching pre-feed windows (16 inverted companies, and non-cold links before 2026-07-01 such as ARSSBL 06-07..06-19, which were also scanned empty) will now examine those filings or halt naming what is missing.
- `stance_chain` CHECK_VERSION 1 -> 2: recorded verdicts read stale.
- `AsOfLedger.view` on an as_of before 2026-07-01 now raises (its lookback floor is SCAN_START); it has no production caller.

## Found
- `StancePoller` (backend/stance/poller.py:346) chooses the cold-start date from `DataAccess.earliest_knowable_analysis_date`, a near-copy of the chain-start rule, with `or SCAN_START` as a fallback. Not changed (the walk start, not the window); worth one rule later.
- BHADORA has an empty `log.jsonl` (stance_chain read error).

## Not done
Acceptance 5 (rebuild on sandbox + stance_chain passing for rebuilt links): waits on owner approval for an LLM pilot, and ARSSBL on a body backfill of 3 filings of 2026-06-06.
