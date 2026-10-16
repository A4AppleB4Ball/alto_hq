---
schema: evidence/v1
task: T-20261016-2252-stance-cold-start-window
round: 1
qa: pass
qa_by: qa@alto_hq-22bf678
commits: 0d07e40..103170e
acceptance_sha256: 405229719e76c17e6f716d62f1967838a1b6aa2cb566737b17180e8e310f2799
outputs_changed: unverified
---

## Round 1 (2026-10-17)

Scope: PASS on every judged check. Checks 5 (repair) and 10 (SHILPAMED pilot) are
PENDING on T-20261016-2336 (caller's instruction), not run and not failed; check 3
struck (v5). This PASS does not cover 5 and 10; merge approval must wait for them.

Setup: worktrees `.claude/worktrees/T-20261016-2252-qa` (103170e) and `-qa-base`
(0d07e40), both declared `mode: sandbox`, data_root
`alto_sandboxes/T-20261016-2252-qa/news_server`, seeded with read-only copies of live
`1/screener_announcements`, `alto_data/stances`, `alto_data/system/legacy_chain_starts.json`,
and `1/daily_announcements` 2026-05..07. Live data was only read. No LLM call
(HTTP(S)_PROXY to a dead port; no workflow run). Logs: `news_server/verify_data/reports/<task>/qa/`.

### Acceptance checks
1. One rule - PASS. `stance/tests/test_cold_start_window_rule.py` (AST: no SCAN_START, uses
   stance_cold_start, no date literal) passes; `grep SCAN_START|2026-07-01 worker.py poller.py` -> none.
2. ARSSBL - PASS (dry). `AsOfLedger.stance_cold_start('ARSSBL')` = 2026-06-06 = covers_to of the
   06-06 link; `announcements_between(ARSSBL, 06-06, 06-06)` -> 3 announcements. EMUDHRA 05-25 -> 4.
   A missing day raises naming it (`MissingBseDayFile ... announcements_2026-02-06.json`, seen on SHILPAMED
   where the sandbox has no Feb files).
3. Struck (v5).
4. Inverted window fails - PASS. `python -m backend.validation.stance_chain.cli --fleet` on the byte copy
   of the live store -> rc=1, `fleet: 485 companies, failing links by reason {'inverted_window': 16}, 1 read
   error(s) ['BHADORA']`; list: 539730, 544440, 544451, 544563, ABDL, ALOKINDS, ARSSBL, DSFCL, EMUDHRA,
   HPTL, KRISHNADEF, MAWANASUG, PNGSREVA, RAYMOND, SHILPAMED, SMCGLOBAL. Reconciler `inspect`: ARSSBL,
   SHILPAMED, EMUDHRA -> state `inverted_window`, rebuild_from = the link's as_of, needs_run True.
5. Repair - PENDING (T-20261016-2336).
6. Unchanged elsewhere - PASS. Fleet before/after of the cold-start covers_from (base worker: SCAN_START
   = 2026-07-01; head: stance_cold_start) over all 485: 302 non-legacy companies with chain start >= 07-01
   -> 0 changed.
7. Suite - PASS. `pytest backend/stance backend/validation backend/lib` 426 passed; boundary test 2 passed;
   full suite base 66 FAILED/ERROR lines, head 65, `comm -23 new base` empty.
8'. Window rule - PASS. Independent recomputation for all 485 (legacy: min first version date of
   in-chain quarters; others: min(chain start, 2026-07-01)) vs `DataAccess.stance_cold_start`: 0 mismatches,
   0 raises. 164 legacy, 19 pre-feed cold (e.g. ARSSBL 06-06, EMUDHRA 05-25), 302 at 07-01.
9. Poller - PASS. `poller.py:_cold_start_date` calls `DataAccess.stance_cold_start`, same as worker via
   AsOfLedger; no SCAN_START import; `test_poller_cold_start_rule.py` passes.
10. Pilot - PENDING (T-20261016-2336).
11'. Runner - PASS. `git diff 0d07e40..103170e -- backend/stance/runner.py` empty.
12. No Kimi - not applicable until check 10 runs; no LLM was called in this round.

### Findings
None confirmed (no verifier needed). Observations, not findings:
- `lib/asof.py:293-299` `view()` clamps its lookback at SCAN_START, so for as_of before 2026-07-01 it now
  raises "inverted announcement window" where it returned []. `view`/`view_peers` have no production caller.
- Poller now scans an after-feed company from 07-01 while the runner walks from its first version (11'):
  more candidates (dev: 3BBLACKBIO 14 -> 18), same walk. Owner-intended by 8'/11'.
- Revert 63622da's message names c5f9853; the branch commit is a4e4c22 (rebase). Content reverted fully.

### Suite
base 0d07e40 / head 103170e, sandbox root, LLM blocked: no new failure.

### Dev claims not confirmed
Dev's runner-level before/after (run_blocked.py on ARSSBL/SHILPAMED/DBOL/3BBLACKBIO) was not rerun at
runner level; QA confirmed the same windows at function level fleet-wide and ARSSBL's 3-announcement read.
All else in handoff Round v4 matches.

### Automatic catch
`stance_chain --fleet` inverted_window rule, if added to a scheduled read-only check, catches this class.
Proposal: the qa skill should say how to judge a round with owner-deferred checks (schema has no `pending`).
