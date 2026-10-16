# Handoff: T-20261016-2147-checks-stance-chain

- Branch `eng/T-20261016-2147-checks-stance-chain`, worktree
  `alto/.claude/worktrees/T-20261016-2147-checks-stance-chain`, base `9950df7`.
- Commits (one per item, local only):
  - `74f18dc` Stance: continuity rule moved to `backend/stance/chain/continuity.py`; reconcile imports it
  - `9fc6cdc` Validation: `stance_chain` check
  - `d79734f` Events: `_scan_bse` reads through new public `bse_rows_between(dir, code, start, end)` (behaviour unchanged)
  - `6c97bee` Validation: `stance_inputs_asof` check
  - `f538c5e` Validation docs: `backend/validation/docs/stance_checks.md`

## Acceptance checks

1. Frozen cases (run from the worktree root, `PYTHONPATH=.`; cases hash-verified by `load_case` first):
   ```
   $ python -m backend.validation.stance_chain.cli --case $C/511144@2026-10-15 --case $C/ARSSBL@2026-10-15
   511144: continuous (14 link(s) continuous through 2026-10-07) check=stance_chain@1 fp=35ec1616...
   ARSSBL: continuous (12 link(s) continuous through 2026-10-13) check=stance_chain@1 fp=a63eb4b8...
   exit 0
   $ python -m backend.validation.stance_inputs_asof.cli --case $C/511144@2026-10-15
   511144: as_of_clean (35 input(s) over 14 link(s) dated on or before their as_of) check=stance_inputs_asof@1 fp=cc0851ea...
   exit 0
   ```
   ($C = /Users/kmrh581/personal/projects/workspace/alto_testcases/cases.) QA's hand check of one link is QA's.
2. Planted defects on tmp copies: `backend/validation/stance_chain/tests/test_stance_chain.py`
   (one-day gap, overlap, covers_to != as_of each fail naming the link; cold-start link is not a gap;
   link without chain fails) and `backend/validation/stance_inputs_asof/tests/test_stance_inputs_asof.py`
   (trigger filed after as_of fails naming link, input, both dates; also annual and quarterly after as_of).
3. One rule: `StanceReconciler._chain_gap` deleted; reconcile calls `chain_gap`, and `gap_from`
   (reconcile.py, a second copy of the same rule) now calls `link_gap`; `stance_chain.check` calls `link_gap`.
   `test_reconcile_and_the_check_share_one_rule` asserts identity. `git diff main -- backend/stance/tests` is empty;
   `pytest backend/stance/tests`: 117 passed.
4. Unresolvable input: trigger, annual and quarterly ids absent each fail with `input_not_in_index` (parametrized test).
   An annual in the index with no `filed_at` fails `input_undated`. A missing day file raises.
5. Verdict contract: both checks return `backend.validation.verdicts.record.Verdict(check_id, check_version, state, reason,
   fingerprint(inputs.to_record()))`; tests assert id/version, unchanged inputs stay current, a touched input or new version reads stale.
6. `pytest backend/validation backend/stance backend/stores/tests/test_boundaries.py`: 228 passed.
   Full suite: base 66 failed / 1544 passed; new 66 failed / 1563 passed; `comm -23 new base` empty.
   Entry points import: stance.reconcile, stance.ready, stance.runner, e2e.run, intake.runner, workflow.cli, both CLIs.

## Interpretation the owner must check

- **Triggers are not in the index.** `trigger_docids` are BSE announcements (`bse_<scrip>_<newsid>`), absent from
  `{SYMBOL}_index.json`. The check resolves them in the announcement feed (BSE day files), the source the AsOfLedger
  dates them from (`lib/events._record`, date = day file). Read literally ("resolve in the index"), every 511144 link
  would fail `input_not_in_index`. Proposed acceptance wording: "resolve in the index (quarterly, annual) or the
  exchange day files (triggers)".
- Dates used: quarterly = `version_date` from `enumerate_versions(index)`; annual = index `filed_at` (AsOfLedger rule).
- A first link that is not a cold start is reported as a gap (nothing precedes it).

## Not done

- NSE-only companies: `stance_inputs_asof.inputs.read_inputs` raises "no BSE code" (backend/validation/stance_inputs_asof/inputs.py:43);
  NSE feed reading not implemented. Not needed by acceptance (511144 is BSE).
- Neither check is wired into e2e or a scheduler; out of scope.
- The live (symbols) mode of both CLIs was not run against production; only the `--case` mode was.

## Found

- The full suite writes `backend/data/dashboard/chart_profiles.duckdb` into the checkout (seen in both base and new
  worktrees, deleted after the run). Some test resolves a relative `data/` path; per CLAUDE.md that path should come from
  `backend.config.paths`. Not investigated.
- The frozen-case tests depend on `alto_testcases` beside the main checkout (resolved via git, raises if absent; helper
  `backend/validation/stance_chain/tests/frozen.py`). A shared helper in `backend/validation/cases/` would be a better home; I left
  it in my feature folder to avoid touching shared files.

## v2 blocker (acceptance v2, alto_hq aa2c7ec, sha256 571f1542... verified against approval)

Stopped without code changes, as instructed. The v2 rule says every input is resolved only through
`lib` DataAccess / the AsOfLedger and the company resolver, and `--case` mode points them at the case root
"via the same path mechanism". No such mechanism exists today:

- `backend/config/paths.py:11-17`: one data root, "Deliberately NO env-var override".
- `DataAccess.__init__` (`backend/lib/data_access.py:54`) takes no root. `get_announcement_index`
  (`:156-162`) reads the module-level `SOURCES["screener_announcements"]`.
- `AsOfLedger.announcements_between` calls `lib.events.company_announcements`. That reads the
  module globals `ANNOUNCEMENTS_DIR` / `ATTACHMENT_HASHES_DIR` (`backend/lib/events.py:31-32`) and the NSE day files
  through `backend.raw.utils.nse_company_rows`. None of these take a root.
- `CompanyResolver` reads module-level `MAPPING_PATH` (`backend/lib/company_resolver.py:12`). `load_nse_only_symbols` has the same problem.

Pointing these at a case root would need either a product change (a root parameter through DataAccess,
events and the resolver) or a workaround (monkeypatching module globals, or subclassing as the completeness
tests do). The first is a product change and the second is the workaround the coordinator ruled out.
`T-20261015-0321-checkout-data-root` (status `ready`, QA failed round 1) looks like the intended mechanism.

What the v2 redo would be once a root exists (about half a day): `stance_inputs_asof.inputs` builds a
DataAccess/AsOfLedger/CompanyResolver on the given root. Quarterly comes from `DataAccess.quarter_versions`, annual from
`list_annual_analyses` `filed_at`, triggers from `AsOfLedger.announcement_key` plus `announcements_between`,
which covers both exchanges. An AST test bans `open`/`read_text`/`json.load` and day-file/index helpers in
the package. The `bse_rows_between` commit `d79734f` gets reverted in the same commit. Until then the
branch still holds the v1 implementation, which v2 does not accept: it reads index and day files
itself, BSE only.

Owner decision needed: (a) wait for checkout-data-root, (b) approve a root parameter on DataAccess/events/
resolver as part of this task (it is a lib change and probably bigger than this task's kind), or (c) allow
test-side subclassing like `completeness/tests/fixtures.FixtureDataAccess`.
