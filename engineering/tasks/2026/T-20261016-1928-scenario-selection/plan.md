# Plan: scenario-selection

**Touches:** new package `backend/validation/scenarios/selection/` only
(`policy.py`, `inputs.py`, `classes.py`, `run.py`, `__main__.py`, `tests/`).
Empty `backend/validation/scenarios/__init__.py` (the contract task creates
the real one; merge note in handoff). Reads, never writes: shared index via
`DataAccess`, completeness via `backend.validation.completeness.inputs.read_company_inputs`
+ `check.evaluate`, intake `failed/` via `backend.stores.intake.repository.read_stage_records`,
stance log via `CompanyStore.history`, listing via `CompanyResolver`.
No existing function changes behaviour; no callers to update. Entry point:
`python -m backend.validation.scenarios.selection`.

**Money path?** No. Reads no book, P&L, returns or backtest store (AST test).

**Change.** One pure predicate per real-state class over per-company facts:
- FC01: completeness `complete`, every window quarter `final`/`open`, FY26 annual
  stored with `filed_at`, stance log present and continuous (each link's
  `prior_as_of` = previous `as_of`), no intake `failed/` record. Flags BSE-only
  (resolver row with nsecode == numeric bsecode).
- FC02: a quarter `missing` or `due_nothing_in` (catalog: "Due/Missing").
- FC03: an intake failed record whose `last_error` equals the product's
  reporting-period refusal (exact string from `backend/raw/utils/reporting_period.py:187`,
  pinned by a test against that function).
- FC08: a stance link dated on/after the first version of a `missing`/`stale` quarter.
- FC09: chain `start_date` before `FEED_START_DATE`.
- FC10: completeness `not_initiated`.
Edit-only classes and FC12 out of scope. Companies whose inputs raise are
listed under `errors` (never dropped). `now` = as-of 23:59 IST; stance links
after the as-of are ignored. Output JSON (sorted keys) to a required `--out`,
with alto and news_server HEAD commits. Owner notices: nothing in production.

**Acceptance, command by command** (from worktree, output in $TMPDIR):
1-3. `touch $TMPDIR/marker; python -m backend.validation.scenarios.selection --as-of 2026-10-15 --out $TMPDIR/sel1.json`, then inspect ARSSBL FC02/FC08, CHANDAN FC03, FC01 (BSE-only present), FC10 via jq-like python.
4. `pytest backend/validation/scenarios/selection/tests` (AST test).
5. second run to sel2.json; `cmp`; commits present.
6. `find ../news_server/data -newer $TMPDIR/marker` (scoped) empty; full suite vs base.
