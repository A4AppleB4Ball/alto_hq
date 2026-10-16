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

## Round v2 (Amendment v2, checks 8-10), 2026-10-16

Branch rebased onto main `9013baa`. Range `9013baa..8543946`:
- `8f3ced2` (was 16bc453), `ac12fe7` (0c2a56b), `218cae9` (488d3d6), `3cc84dc` (b1932d5): rebased, no conflicts.
- `8543946` Stance: poller cold-start date from lib/chain_start `stance_scan_start`; no SCAN_START fallback, no copy of the rule.

Main now requires `.alto_checkout.yaml`. The worktree declares a sandbox root `alto_sandboxes/T-20261016-2252-stance-cold-start-window/news_server` (same shape `backend.config.new_sandbox_worktree` creates; written by hand because the worktree already existed).

### 8. Window rule - PASS
`stance_scan_start = min(chain.start_date, FEED_START_DATE)` in `backend/lib/chain_start/policy.py` (unchanged, owner-confirmed). `pytest lib/chain_start stance/tests/test_cold_start_window_rule.py stance/tests/test_poller_cold_start_rule.py`: 17 passed. Covers pre-feed annual (06-06), legacy (01-01), after-feed start (08-13 -> 07-01), no start raises.

### 9. Poller - PASS
`backend/stance/poller.py`: `_cold_start_date` = `stance_scan_start(symbol, DataAccess.chain_start(...))`; `SCAN_START` import and `earliest_knowable_analysis_date` call removed. A company with no chain start (nothing filed) is logged `no chain start yet ... no cold-start work` and not scanned (before: scanned from SCAN_START; the runner already reports "nothing to walk" for it). Test `stance/tests/test_poller_cold_start_rule.py` (AST: no `SCAN_START`, no `earliest_knowable_analysis_date`, uses `stance_scan_start`; plus 4 behaviour cases). `test_poller_price_triggers.py` stub switched to `chain_start`. Poller tests: 22 passed.
Note: the runner's walk start (`backend/stance/runner.py:235`) still uses `DataAccess.earliest_knowable_analysis_date` (the walk, not the window; check 9 names only the poller). It is now the only caller of that function.

### 10. SHILPAMED pilot - NOT DONE (blocked, no spend)
Sandbox built by read-only copies from live: SHILPAMED index, hashes, financials, workflow caches (quarterly_update, annual_report_analysis), blob_index.duckdb + SHILPAMED blobs, BSE/NSE day files 2025-10..2026-10, raw_announcements, corporate_actions, system/{legacy_chain_starts,results_calendar,stockedge_securities,dhan_instruments}.json, SHILPAMED stance dir; empty user `workspace/u_sandbox`. Rewind through the product function `backend.stance.rewind.rewind(CompanyStore(), "SHILPAMED", "2026-02-06")` on the sandbox store (asserted the store resolved under alto_sandboxes): dropped 25 links, sidecar `rewound_2026-02-06.jsonl`.
- LLM-blocked dry pass: `WINDOW SHILPAMED 2026-01-01..2026-02-06 -> 9 announcement(s)` for the cold link (before: 2026-07-01..2026-02-06 -> 0); walk 2026-02-06..2026-10-15, 52 candidate dates; reached Agent A.
- Metered run (`$TMPDIR/sbx_runner/run_metered.py --symbols SHILPAMED --once`): Agent A to kimi-k3 failed 3/3 with HTTP 502; proxy says `ExpiredTokenException ... security token included in the request is expired` (Bedrock). Credentials are the owner's call; I stopped.
- **LLM cost of the pilot: 0** (3 requests, all 502, no usage returned). A full rerun rebuilds all 25 links (~52 candidate dates, Agents A/B/D per checkpoint, kimi-k3); I have no price table to estimate dollars.
- To finish: owner refreshes the Bedrock token, then from the worktree: `PYTHONPATH=. python $TMPDIR/sbx_runner/run_metered.py --symbols SHILPAMED --once` (usage to `$TMPDIR/sbx_runner/usage.jsonl`), then `python -m backend.validation.stance_chain.cli SHILPAMED`. Sandbox store is already rewound.

### Suite (v2)
Run with an empty sandbox data root on both sides (base worktree at `9013baa`). Base: 100 failed, 8 errors; branch: 100 failed, 8 errors, 16 more passed; `comm -23 new base` empty. `pytest stance validation lib stores/tests/test_boundaries.py`: 39 FAILED/ERROR on both base and branch, identical sets (tests that read live stores, e.g. `legacy_chain_starts.json not found` under the sandbox root). The v1 "420 passed" was against the live root, before main's checkout file. Entry points import: stance.runner/poller/reconcile/ready, validation.stance_chain.cli, e2e.run, intake.runner, workflow.cli, lib.asof.
No production write: `find` on live stances/SHILPAMED and workspace newer than the run start: none.

### Found (v2)
- No CLI rewinds an `inverted_window` chain: `stance.ready` rewinds only `skipped_input` (backend/stance/ready.py, `--fix-skipped-input-and-rewind`). The production repair of the 16 links needs either that flag widened or an owner-approved call of `backend.stance.rewind.rewind`.
- Since the checkout-file change, ~39 tests in stance/validation/lib need live data and fail in any sandbox worktree (e.g. validation/completeness/tests/test_arssbl_validity.py). They need fixtures, not the live root.

## Round v2, part 2 (coordinator: DeepSeek-only pilot; acceptance check 11, approved sha256 a8d0bf6c...)

New commit `c5f9853` Stance: runner cold-start walk opens at lib/chain_start stance_scan_start; no earliest_knowable_analysis_date copy. Range now `9013baa..c5f9853`.

### 11. Runner - PASS
`backend/stance/runner.py` cold start: `chain = ledger.chain_start(symbol)`; `walk_start = stance_scan_start(symbol, chain)`, or "nothing to walk: no chain start yet" when `chain.start_date` is None. Test `stance/tests/test_runner_cold_start_rule.py`: AST (no `earliest_knowable_analysis_date`, no `SCAN_START`, uses `stance_scan_start`) plus walk range for 06-06, legacy 01-01, 08-13 -> 07-01, and no start. 5 passed after; 5 failed with the runner change stashed. Runner and poller tests: all pass. `DataAccess.earliest_knowable_analysis_date` now has no production caller (backend/lib/data_access.py:300); not removed.

**Behaviour change the owner must know (check 11):** the cold walk now begins at the window start, not at the first knowable quarter version. SHILPAMED (legacy) now walks 2026-01-01..2026-10-15, 57 candidates, and its first evaluated day is 2026-01-06 (1 announcement), before its first quarter version (Q3_FY26, 2026-02-06). Before: the walk began 2026-02-06. Companies whose chain starts after the feed now walk from 2026-07-01 instead of from their first version. This departs from the old runner comment "before its first version stance knows nothing" (decision 6 in backend/docs/31_quarter_versions.md); the owner should confirm that is intended.

### 10. Pilot on DeepSeek - NOT DONE (blocked on credentials; no Kimi call made)
- Sandbox-only config `$TMPDIR/sbx_runner/sandbox_llm_deepseek.yaml` (not in the repo; llm_config.yaml untouched): default and stance agent_a, agent_b, agent_d, materiality_classifier, signal_extraction, er_extraction all `deepseek-v4.1-flash`, `foundry_project: hackit`, no aws_profile. Passed via `--llm-config` by `$TMPDIR/sbx_runner/run_deepseek.py`, which resolves every role first (printed: all deepseek-v4.1-flash, foundry=hackit, aws_profile=None) and aborts on any non-DeepSeek role or request.
- Run (before check 11): cold link 2026-02-06, Agent A answered (deepseek-v4.1-flash, 14s); then halted `BrokerNotConfiguredError: No active broker for user=scienceamit1`. The price read (`AsOfLedger` default `user_id="scienceamit1"`, backend/lib/asof.py:61 -> `DhanDailyStore` -> `_build_client`) always builds a live Dhan client from that user's credentials, and its cache is `~/NSE_BSE_Data/dhan_cache` (outside any sandbox root, written on refresh). Making it run means putting Dhan credentials into the sandbox, which is credentials, the owner's call. Stopped.
- **Token usage: 1 call, deepseek-v4.1-flash, 4,942 prompt + 1,259 completion = 6,201 tokens.** Kimi: 0 calls in this round; the earlier round's 3 kimi-k3 requests all returned 502 with no usage.
- stance_chain on sandbox SHILPAMED: `ValueError: SHILPAMED: stance log ... holds no link` (the chain is rewound and nothing was rebuilt). No link was written.
- After check 11, a dry pass with LLM calls blocked (DeepSeek config) shows walk 2026-01-01..2026-10-15, first day 2026-01-06.
- To finish: the owner decides how the sandbox gets prices (Dhan credentials for a sandbox user, or a sandbox price source). Then: `PYTHONPATH=. python $TMPDIR/sbx_runner/run_deepseek.py --symbols SHILPAMED --once` and `python -m backend.validation.stance_chain.cli SHILPAMED`.
- Sandbox hygiene: an earlier targeted pytest run under this sandbox created `workspace/u_test`; removed (the runner refused a two-user pass).

### Suite (part 2)
Empty sandbox root: 100 failed, 8 errors, 1574 passed; `comm -23 new base` (base 9013baa) empty.
No production write: nothing newer than the run start in live stances/SHILPAMED or workspace; `~/NSE_BSE_Data/dhan_cache/daily/SHILPAMED.parquet` unchanged (15 Oct).

## Round v4 (Amendment v4: checks 8', 11'), 2026-10-17

Branch rebased onto local main `0d07e40`. Range `0d07e40..103170e`:
- `a74d4fc` `b9719a7` `b53ff07` `151b391` `fe37389` `a4e4c22`: rebased, no conflicts.
- `63622da` Revert of c5f9853 (now a4e4c22): runner walk start back to `DataAccess.earliest_knowable_analysis_date`; `git diff main -- backend/stance/runner.py` is empty.
- `103170e` Stance: one cold-start rule. `stance_scan_start(symbol, chain, legacy, first_version_dates)` in `backend/lib/chain_start/policy.py`: legacy = earliest first version date of a quarter in its chain (raises if none); else min(chain start, FEED_START_DATE); raises with no chain start. Resolved in `backend/lib/chain_start/resolve.py:stance_cold_start`, exposed as `DataAccess.stance_cold_start` and `AsOfLedger.stance_cold_start`. Worker (`worker.py:445`) and poller (`poller.py:_cold_start_date`) call those; neither imports the policy function.

No LLM call this round (all LLM `_send` blocked); check 10 not run (waits for T-20261016-2336).

### 8'. Window rule - tests PASS
`lib/chain_start/tests/test_policy.py`: SHILPAMED-like legacy (first version Q3_FY26 2026-02-06 -> 02-06; versions before the legacy chain ignored; no version raises), ARSSBL-like (annual 06-06 -> 06-06), after-feed (08-13 -> 07-01), no chain start raises. `lib/chain_start/tests/test_resolve.py`: same three through `stance_cold_start`. Worker/poller rule tests updated (AST: no SCAN_START, no earliest_knowable_analysis_date in poller, uses `stance_cold_start`).

### Before/after dry comparison (LLM blocked)
Sandbox root (`alto_sandboxes/T-20261016-2252-.../news_server`), seeded this round with read-only copies from live of ARSSBL, DBOL, 3BBLACKBIO index, financials, attachment hashes and workflow caches (BSE blobs not copied). Base = detached worktree `T-20261016-2252-base4` at main `0d07e40`, same sandbox declaration. `PYTHONPATH=. python $TMPDIR/sbx_runner/run_blocked.py --symbols X --once --output-dir <empty tmp>`; logs in `$TMPDIR/cmp4/`. The second WINDOW of the first date is the cold-start Agent A window.
| company | walk (both) | before (base) | after |
|---|---|---|---|
| ARSSBL (annual 06-06) | 06-06.. | 06-06 day scan -> 0 (pre-feed clamp), no event, walks on with empty windows to 07-02 | `2026-06-06..2026-06-06 -> 3`, halts `MissingAnnouncementBody` bse_544530_9fce2b86 (FC09: backfill) |
| SHILPAMED (legacy) | 02-06.. | `2026-07-01..2026-02-06 -> 0` (inverted) | `2026-02-06..2026-02-06 -> 3`, reaches Agent A (blocked) |
| DBOL (chain start 07-01) | 07-01.. | `2026-07-01..07-01 -> 3` | identical |
| 3BBLACKBIO (after feed, 08-13) | 08-13.. | `2026-07-01..2026-08-13 -> 5` | identical |
DBOL/3BBLACKBIO halt on missing BSE blobs in the sandbox (both sides, after the window). Also: 3BBLACKBIO's poller reports 14 candidates on base, 18 on the branch (the poller now scans from 07-01, its cold-start window, not from 08-13); the runner walk is 21 dates on both.

### 4. Fleet inverted list
Live `alto_data/stances` copied into the sandbox (sandbox SHILPAMED rewound state moved aside and restored after), `python -m backend.validation.stance_chain.cli --fleet` -> exit 1, `fleet: 485 companies, failing links by reason {'inverted_window': 16}, 1 read error(s) ['BHADORA']`; same 16 as before (539730, 544440, 544451, 544563, ABDL, ALOKINDS, ARSSBL, DSFCL, EMUDHRA, HPTL, KRISHNADEF, MAWANASUG, PNGSREVA, RAYMOND, SHILPAMED, SMCGLOBAL).

### Suite (v4)
Sandbox root, sequential. Base 0d07e40: 61 failed, 1632 passed; branch: 61 failed, 1651 passed; `comm -23 new base` empty. `pytest stance validation lib stores/tests/test_boundaries.py`: 428 passed. Entry points import (stance runner/poller/worker/reconcile/ready, stance_chain.cli, e2e.run, intake.runner, workflow.cli, lib.asof).
No production write: `find` on live stances, triggers_custom, screener_announcements, -mmin -40: none.

### Behaviour change the owner must know (v4)
- Check 3's wording "uses its recorded legacy start; unchanged output" no longer holds under 8': a legacy company's cold window now opens at its first quarter version (SHILPAMED 02-06, not 01-01). RAJRATAN-like companies whose stored cold link covered from 01-01 would examine fewer days on a rebuild. QA should read check 3 through 8'.
- `DataAccess.earliest_knowable_analysis_date` is again used by the runner (11').

### Not done
Check 10 (pilot) and check 5 (repair) - wait for T-20261016-2336 and ARSSBL's body backfill.
