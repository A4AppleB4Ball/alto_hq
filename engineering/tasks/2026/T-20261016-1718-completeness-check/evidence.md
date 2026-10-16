---
schema: evidence/v1
task: T-20261016-1718-completeness-check
round: 1
qa: pass
outputs_changed: unverified
---

# QA evidence, round 1 (ab8a959..3ad6d1c)

Acceptance hash verified: sha256 61464ed9...8750c matches task.md. Run in a detached worktree at 3ad6d1c (`.claude/worktrees/T-20261016-1718-completeness-check-qa`). Data root resolved to production; only read-only commands and tmp-dir tests were run.

## Acceptance checks
1. PASS. `PYTHONPATH=. python /…/I-20261015-1058…/fleet_scan.py` lists the 10 companies. `python -m backend.validation.completeness.cli ABDL ARSSBL CHANDAN EMUDHRA FAIRCHEMOR KRISHNADEF PNGSREVA RAYMOND SMCGLOBAL TAC` returns `incomplete` with a Missing quarter for all ten. ARSSBL has Q1_FY27 and Q2_FY27 missing, CHANDAN has Q1_FY27 missing, and the other eight have Q1_FY27 missing.
2. PASS. 20MICRONS is `complete`: Q3_FY26 final, Q4_FY26 final, Q1_FY27 open, Q2_FY27 unknown. No violations.
3. PASS. `test_company_states.py` (tmp fixtures): not_initiated, and the violation `stance_without_chain_start` when a stance exists.
4. PASS. `test_quarter_states.py`: one test per state plus Open-stays-Open. Each asserts state and reason.
5. PASS. `test_arssbl_validity.py` covers unchanged, touched document, new version and backdated document, on a tmp copy of the real ARSSBL index.
6. PASS. The grep finds only a comment mention of `reader` in policy.py. The AST test shows no import of reader or capture. The stale-calendar test sees `calendar_stale` and tmp mtimes unchanged. The "no meeting on record" test passes. `read_meetings` and `last_captured_at` only read (code read). The real-data CLI run touched nothing in the code path.
7. PASS as written: `python -I -c "import sys; sys.path.insert(0, '.'); import backend.validation.completeness"` prints ok, rc=0. `pip freeze` is identical before and after, and dagster is not installed.
8. PASS. `test_quarter_key_for_label.py` covers every label from the cutoff.
9. PASS. `test_boundaries.py` passes. The CLI entry point imports. The validation, quarter-label and boundary tests give 32 passed. Full backend suite, committed trees, run from backend/ (command in the dev skill): head 66 failed, base 67 failed. `comm -23` of head-only failures is empty. The only base-only failure is test_partitioned_storage (flaky). No new failure.

## Review
Rules: no fallbacks, no relative imports, no shims, tests in `<feature>/tests/`, data path via `backend.config.paths` (calendar_source default). The commits carry no attribution lines. Logic: quarter precedence (Missing/Stale over Final/Open, Due before CalendarStale before Expected/Unknown) is consistent with the design table. The 20h constant equals `reader.REFRESH_HOURS`; they are duplicated, which would drift silently.

## Confirmed findings
None (no BLOCK, no ALERT confirmed; no verifier needed).

Observations, not findings:
- `CalendarRead.is_stale` treats a `last_captured_at` in the future as fresh.
- `CALENDAR_STALE_AFTER_HOURS` duplicates `REFRESH_HOURS`. An invariant test asserting equality would catch drift.

## Dev claims
All confirmed. The handoff says the hash was 16c2b27a..., the earlier approval; the current hash matches the re-approved one.
