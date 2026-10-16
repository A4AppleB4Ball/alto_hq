# Handoff: T-20261016-2126-window-end-from-manifest

- Branch `eng/T-20261016-2126-window-end-from-manifest`, worktree `alto/.claude/worktrees/T-20261016-2126`.
- Base b893361 (main, includes f8db8c4). Commit 926dce1 (one item, local only).

## Acceptance
1. `grep -rn "WINDOW_END" backend` and `grep -rn "2026-10-15" backend/validation/scenarios --include='*.py' | grep -v tests`: both empty. (Two docstring examples in scenarios/selection/ used the date; changed to `YYYY-MM-DD`.)
2. New tests in backend/validation/scenarios/tests/test_catalog.py: `test_window_end_equal_to_manifest_as_of_passes`, `test_window_end_differs_from_manifest_as_of` (match "window.end 2026-10-14 differs from case manifest as_of 2026-10-15"), `test_cases_frozen_at_different_dates_validate_together` (2026-10-15 and 2026-11-20 in one catalog), `test_manifest_without_as_of_is_rejected`. Fixtures take `as_of`.
3. Real cases (read only; alto_testcases `git status` clean after): `python -m backend.validation.cases.load <alto_testcases>/cases/*` verified all five (628/385/520/347/347 files). Catalog's `load_case(root, case)` for each prints `as_of 2026-10-15` (window_start 2026-07-01, ARSSBL 2026-06-06). Acceptance says "both"; all five checked.
4. `pytest backend/validation`: 90 passed. Full suite: new 66 failed / 1523 passed; base 66 failed / 1519 passed; `comm -23 new base` empty; test_boundaries not among failures.

## Behaviour changes
- CaseManifest now requires `as_of`; a hand-written manifest lacking it is rejected by the catalog.
- No real scenarios exist yet in alto_testcases/scenarios, so the full catalog CLI was not run against real data.

## Found
- Four of five real cases record `prices_dhan_15min` with `past_as_of: true` (max_date 2026-10-16, a day after the freeze). The loader reports it, so it's known, but a replay that reads those prices without as-of filtering would see the future. Not in scope; worth a check in the replay.
