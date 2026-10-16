# Plan: T-20261016-2235-checks-stance-inputs-asof

**Touches (new code only; no product behaviour changes):**
- `backend/validation/stance_inputs_asof/` (policy, inputs, check, cli, tests): new check.
- `backend/validation/cases/install.py` (+ test): copy a hash-verified case into the
  data root of the current checkout, refusing unless `paths.CHECKOUT.mode == "sandbox"`,
  and refusing to overwrite a different existing file. Targets come from
  `cases.roots.production_roots()` (which, in a sandbox, resolves the sandbox root).
- `backend/validation/docs/stance_checks.md`: section for the new check.
- No caller of any existing function changes. Not a money path.

**Resolution (only lib):** links from `stores.stance.CompanyStore.history`.
- quarterly key -> `DataAccess.quarter_versions` + `lib.quarter_versions.find_version` -> `version_date`.
- annual docid -> `DataAccess.list_annual_analyses` entry with that docid -> `filed_at`.
- trigger docid -> `AsOfLedger.announcement_key` (CompanyResolver + NSE-only set; both exchanges)
  then `AsOfLedger.announcements_between(key, FEED_START_DATE, through)` -> `date`.
  `through` is a required CLI argument (the last day the feed is read to; case mode: the case's as_of).
- Not found -> `input_not_in_index`; dated after the link's as_of -> `input_after_as_of`. Never skipped.
- AST test: the package calls no `open`/`read_text`/`json.load`/`glob`, imports no
  `backend.config.paths`, `lib.events`, `raw.*` day-file helper.

**Acceptance runs (from the sandbox worktree `.claude/worktrees/T-20261016-2235`, root
`alto_sandboxes/T-20261016-2235`):**
1. `python -m backend.validation.cases.install <case>` for 511144, ARSSBL, CHANDAN; then
   `python -m backend.validation.stance_inputs_asof.cli 511144 --through 2026-10-15`.
2. Planted defect: test on a tmp tree + a planted copy in a second sandbox (trigger moved to
   a later day file).
3. AST test; CLI on ARSSBL, CHANDAN, 511144.
4. Test: unknown trigger docid -> `input_not_in_index`.
5. Verdict test (check_id, version, fingerprint).
6. `pytest backend/validation backend/stance`, full suite vs base 9013baa, boundary test.
