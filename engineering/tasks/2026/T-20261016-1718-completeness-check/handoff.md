# Handoff: completeness-check

Branch `eng/T-20261016-1718-completeness-check`, worktree `.claude/worktrees/T-20261016-1718-completeness-check`. Base ab8a959.
Commits: f8058d9 (quarter_key_for_label in lib/quarter_policy), 7c45580 (verdicts), 3ad6d1c (completeness + design page). Acceptance hash verified (16c2b27a...) before starting.

## Acceptance (run from the worktree, read-only on product data)
Command: `PYTHONPATH=. python -m backend.validation.completeness.cli ARSSBL CHANDAN 20MICRONS ...`
1. Incident: all ten return `incomplete`, quarter Missing. ARSSBL Q1_FY27 + Q2_FY27 missing; CHANDAN Q1_FY27 missing; the other eight Q1_FY27 missing. fleet_scan.py (same date) lists 10 rows, latest chain quarter per company, consistent (its ARSSBL row is Q2_FY27 as the latest; the check also names Q1_FY27, which the scan does not print).
2. 20MICRONS: `complete`; Q3_FY26 final, Q4_FY26 final, Q1_FY27 open (transcript not in yet), Q2_FY27 unknown (no meeting on record); no Missing/Stale/violation.
3. `test_company_states.py` (tmp fixtures): no chain start -> `not_initiated`; with a stance -> violation `stance_without_chain_start`.
4. `test_quarter_states.py`: one test per state (final, open, not_released, due_nothing_in, expected, unknown, missing, stale) plus Open-stays-Open-until-newer-quarter.
5. `test_arssbl_validity.py` (tmp copy of ARSSBL's index, analyses written into tmp): unchanged -> current; touched doc -> not current and Q1 stale; new check version -> not current; backdated doc -> Q1 stale, company incomplete.
6. `test_calendar_read_only.py`: AST scan, no import of results_calendar.reader/capture (and none of dagster); stale calendar -> `calendar_stale` quarter state and tmp tree mtimes unchanged; "no meeting on record" reason. Real run: results_calendar.json mtime unchanged and `find data -newer` after the CLI run listed nothing.
7. **Not runnable as written**: `python -I -c "import backend.validation.completeness"` fails with ModuleNotFoundError for every backend module (e.g. `backend.raw.results_calendar.due` too): -I drops cwd and PYTHONPATH, backend is not installed. Ran `python -I -c "import sys; sys.path.insert(0,'.'); import backend.validation.completeness, backend.validation.completeness.cli"` -> ok, dagster not in sys.modules. `pip freeze` identical before/after (diffed); dagster not installed. Owner/QA: confirm this variant is acceptable; I did not change acceptance.md.
8. `lib/tests/test_quarter_key_for_label.py`: every label from Q1FY27 on converts via new `quarter_key_for_label` in `backend/lib/quarter_policy.py`.
9. `stores/tests/test_boundaries.py` 2 passed; entry points import (intake.runner, stance.runner, e2e.run, workflow.cli, raw.master_pipeline, backtest.replay). Full suite, base vs new (run from backend/): 66 failures new, 67 base (flaky), `comm -23` empty on a sequential run. A first concurrent run showed test_main_cockpit_middleware::test_health_is_exempt_without_session failing in new only; it passes alone twice and in the sequential rerun (concurrent runs share state).
Targeted: `pytest backend/validation backend/lib/tests/test_quarter_key_for_label.py` -> 30 passed.

## Behaviour / interpretations the owner should know
- Nothing is wired in: no gate, e2e or scheduler calls the check. New code only (plus one helper in lib).
- Newest quarter holding documents with both PPT and transcript is `open` (the table's Final needs a newer quarter holding a document; Open lists "one missing"). Interpretation, flagged in the design page header.
- Missing/Stale override Final/Open (they are states in the table). Stale = the quarter's newest document set has no valid stored analysis but some stored analysis exists (validity from `validate_versions`, so a rebuilt base or backdated document also reads Stale).
- Stale calendar (>20h since last_captured_at, or unstamped): quarters whose state turns on the calendar (Expected/Unknown) report `calendar_stale`, non-blocking. The 20h is `CALENDAR_STALE_AFTER_HOURS` duplicating `reader.REFRESH_HOURS`, because reader may not be imported (it captures). Suggest moving REFRESH_HOURS to results_calendar/policy.py.
- Fingerprint covers index versions, stored validity, chain, meeting dates, stance presence, due quarters and upcoming meetings, so a verdict also goes stale when a meeting date passes.
- Design page copied to `backend/validation/docs/completeness_design.md`; the alto_hq original is untouched (owner removes/redirects).

## Not done
- Stance-input-is-an-analysis-key structural check and "every indexed document extracted/analysed" (design page "Beyond quarters"): not in acceptance; no code.
- Known limits (BSE-only pre-2026-10-07 meetings, SME generic purposes) are not detected, only the stale-calendar case.
- Spike branch observers.py not reused verbatim: fingerprint/validity were re-expressed as verdicts/record.py (generic) and check.py.

## Found
Acceptance 7 wording (see above) cannot pass in any environment as written; future acceptance files should use `python -c` with the repo on PYTHONPATH and assert on `sys.modules`.
