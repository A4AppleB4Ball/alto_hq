---
schema: evidence/v1
task: T-20261016-2235-checks-stance-inputs-asof
round: 2
qa: pass
qa_by: qa@v1
commits: 1665a1c..25a9b8d
merge_commit: a6d2315
acceptance_sha256: 7f537bc157acc293cfe5937fc7006fc5085e82b2f7302cf9f9d3961c42ba7e73
outputs_changed: unverified
---

## Round 1

Setup: sandbox checkout `python -m backend.config.new_sandbox_worktree t2235-qa --base f653467` (root alto_sandboxes/t2235-qa). I placed the cases 511144, ARSSBL and CHANDAN @2026-10-15 with `python -m backend.validation.cases.install <case> --store` for each of the 7 STORES_READ (223/271/221 files). The three cases installed together without conflict. I did NOT copy legacy_chain_starts.json. Production was not written.

### Acceptance check results
1. Frozen cases: PASS. `python -m backend.validation.stance_inputs_asof.cli 511144 ARSSBL CHANDAN --through 2026-10-15` gives 511144 as_of_clean (35 inputs/14 links), ARSSBL as_of_clean (13/12), CHANDAN as_of_clean (11/6), exit 0. By-hand check of link 2026-08-27 in 511144 log.jsonl: quarterly Q1_FY27/2026-08-05 (2026-08-05 <= 08-27). Annual screener_511144_annual_report_financialyear2026frombse has index filed_at 2026-08-27 (<=). Trigger 02e0698a… is in announcements_2026-08-27.json (DissemDT 2026-08-27). All consistent.
2. Planted defect: PASS. In the sandbox log only (backed up, restored, cmp identical), I added trigger 4ed443ba… (filed 2026-10-07) to link 2026-10-06. Output: `leaked (link 2026-10-06: trigger_docids bse_511144_4ed443ba-… input_after_as_of (input dated 2026-10-07, link as_of 2026-10-06) ...)`.
3. One path, both exchanges: PASS. The AST test passes (test_package_reads_no_file_itself). On ARSSBL (NSE), CHANDAN and 511144 the check returns verdicts and never raises.
4. Unresolvable input: PASS. In the same plant, `bse_511144_doesnotexist` gives `input_not_in_index`.
5. Verdict contract: PASS. Verdict(CHECK_ID, CHECK_VERSION, state, reason, fingerprint), the same shape as completeness/index_dates/stance_chain.
6. Suite: FAIL as written. `pytest backend/validation backend/stance` in the sandbox: 34 failed, 221 passed, 5 errors. 39 of those are FileNotFoundError for alto_data/system/legacy_chain_starts.json (backend/lib/chain_start/store.py:21). At base the same 34F/5E (verifier confirmed), so they are pre-existing. The check passes only after a live file is copied into the sandbox, which changes the input, so it counts as a fail. Full suite (sandboxes, head vs base): 100F/8E both, no new failures (`comm -23` empty). Boundary test: 2 passed. Entry points import.

### Findings (verifier-confirmed)
- BLOCK: acceptance check 6 does not pass as written in the mandated sandbox. Cause: the sandbox lacks legacy_chain_starts.json (T-20261016-2311). The code in this range does not cause it. The fix belongs either to T-2311 (freeze it into cases, or let the sandbox install it) or to the owner re-scoping check 6 to "no new failures vs base".
- ALERT: backend/validation/stance_inputs_asof/inputs.py `AsOfInputs.to_record` includes `through`. The fingerprint changes with --through alone: 511144 at 10-15 gives fp 77456dbe…, at 10-14 gives fp 55c2785c…, with identical reason, links and dates. A recorded verdict will read stale every day even when nothing changed.

### Review judgements asked for
1. filings_between (backend/lib/asof.py:238) reads the same `scan_announcements` that `announcements_between` filters through `company_announcements`. It is a superset view of one reader, not a second reader, so it stays one resolution path. Trigger dating matches the worker: worker.py:341 takes trigger_docids from `announcements_between(ann_key, as_of, as_of)`, whose `date` comes from the same scan row that filings_between returns.
2. cases/install.py: install_into_sandbox refuses a non-sandbox checkout (tested). It hash-verifies through load_case and raises on different bytes (no overwrite). Targets come from cases.roots.production_roots/CaseRoots, so it does not build its own paths. Note: the `install()` library function itself has no guard (only install_into_sandbox does). Low risk, not a finding.
3. legacy_chain_starts.json: dev copied the live file into both sandboxes (handoff line 52). That is the input change that check 6 needed. See the BLOCK above.

### Dev claims not confirmed
- handoff check 6 "262 passed": reproducible only with the copied live file.

### Check that would catch this class
A sandbox-readiness preflight: the acceptance runner lists the production-only state files the suite needs, and a case freezes them.


## Round 2

The approval sha256 7f537bc1... matches acceptance.md as it is now. Range 1665a1c..25a9b8d.

Setup: fresh sandboxes `python -m backend.config.new_sandbox_worktree t2235-qa2 --base 25a9b8d` and `t2235-qa2-base --base 1665a1c`. Into each I ran `python -m backend.validation.cases.install ../alto_testcases/cases/<c>@2026-10-15 --store <s>` for c in 511144, ARSSBL, CHANDAN and s in index, workflow_cache, quarter_versions, stances, bse_day_files, nse_day_files, exchange_attachment_hashes, legacy_chain_starts. Nothing was copied from live. Logs: news_server/verify_data/reports/T-20261016-2235-checks-stance-inputs-asof/r2_*.log.

1. Frozen cases: PASS. `python -m backend.validation.stance_inputs_asof.cli 511144 ARSSBL CHANDAN --through 2026-10-15` gives 511144 as_of_clean (35 inputs over 14 links), ARSSBL as_of_clean (13 over 12) and CHANDAN as_of_clean (11 over 6), exit 0. By-hand check of 511144 link 2026-10-06: its trigger bse_511144_b2357e73... is in BSE day file announcements_2026-10-06.json, and its quarterly Q1_FY27/2026-08-05 has version_date 2026-08-05 (workflow_outputs/cache/quarterly_update/511144/Q1_FY27/2026-08-05.json). Both dates are on or before 2026-10-06.
2. Planted defect: PASS. I edited the sandbox log only (backed up first; after restore, cmp identical). Adding trigger 4ed443ba... (filed 2026-10-07) to link 2026-10-06 gives `leaked (link 2026-10-06: trigger_docids bse_511144_4ed443ba-... input_after_as_of (input dated 2026-10-07, link as_of 2026-10-06); ...)` with exit 1.
3. One resolution path, both exchanges: PASS. test_package_reads_no_file_itself passes. All three cases, including ARSSBL on NSE, return verdicts without raising. filings_between is a superset view on the same scan_announcements reader.
4. Unresolvable input: PASS. In the same plant, `bse_511144_doesnotexist` gives `input_not_in_index`, exit 1. test_unresolvable_input_fails_as_not_in_index also passes.
5. Verdict contract: PASS. Verdict(CHECK_ID, CHECK_VERSION, state, reason, fingerprint) is unchanged from round 1. test_verdict_carries_id_version_and_fingerprint passes.
6. Suite: PASS. `pytest -q backend/validation backend/stance` in the fresh head sandbox gives 322 passed, 0 failed. Full suite with `pytest -q backend --continue-on-collection-errors`: head has 61 failed, 1705 passed and 3 errors; base (cases installed the same way) has 61 failed, 1688 passed and 3 errors. `comm -23 head base` is empty, so there is no new failure. test_boundaries gives 2 passed. Entry imports (validation cli, lib.asof) work. `backend.api.main_cockpit` needs SESSION_SECRET in the environment; that is environment setup, not this change.
7. Fingerprint independent of --through: PASS. test_fingerprint_independent_of_through passes. Live check: 511144 at --through 2026-10-15 and at 2026-10-14 both give fp d781266f...
8. PASS. T-2311 has landed (1665a1c is in base), and check 6 above ran in a fresh sandbox holding only what cases.install placed.

### Findings
None at BLOCK or ALERT. Note: a trigger filed after `--through` resolves to None and is reported as input_not_in_index rather than input_after_as_of. It still fails, never passes. Because there were no findings, I did not run a verifier.

### Dev claims not confirmed
None. Dev's 61-failed-both-sides claim matches my run. The round 1 handoff mentions copying the live legacy_chain_starts.json; round 2 needs no copy, because the case installs it.

### Check that would catch this class
A sandbox-readiness preflight in the acceptance runner. It now exists in effect: cases.install --store legacy_chain_starts.
