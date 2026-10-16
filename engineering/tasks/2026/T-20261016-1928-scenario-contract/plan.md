# Plan (written alongside the code; the change was small and new-only)

- **Touches:** new `backend/validation/scenarios/{__init__,contract,catalog}.py`,
  `scenarios/tests/`, `backend/validation/docs/scenarios.md`. Reads
  `backend.validation.completeness.policy.CHECK_ID` for the default check
  registry. No existing function changes; no callers. No stores, no entry
  points besides the new CLI.
- **Money path?** No.
- **Change:** pydantic scenario/v1 (curated + random_live), closed edit
  vocabulary, timeline, expected verdicts, the case-manifest fields used;
  validator raising CatalogError with a reason on the first broken rule.
- **Checks:** (1)+(2) `pytest backend/validation/scenarios`, plus the CLI on
  a tmp catalog; (3) `test_no_writes.py`; (4) doc review; (5)
  `pytest backend/validation` and full suite vs base 79e66a7.
