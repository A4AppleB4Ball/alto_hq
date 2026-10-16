---
schema: evidence/v1
task: T-20261016-2235-checks-stance-inputs-asof
round: 1
qa: fail
qa_by: qa@v1
commits: 9013baa..f653467
acceptance_sha256: ed0e83361368a9ca7287e9fbdd46e147c218f486bd152324f0deac794dc600f9
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
