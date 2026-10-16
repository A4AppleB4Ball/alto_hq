# Handoff: T-20261016-1928-scenario-contract

- Branch `eng/T-20261016-1928-scenario-contract`, worktree
  `alto/.claude/worktrees/T-20261016-1928-scenario-contract`.
- Base `79e66a7`; commit `efe5533` (Validation: scenario/v1 contract,
  catalog validator and scenarios doc). Not pushed.

## Acceptance

1. Valid catalog passes: `test_catalog.py::test_valid_catalog_passes`
   (4 curated covering FC01-FC12 + FCR entry, one BSE-only). Also via CLI:
   `python -m backend.validation.scenarios.catalog --root <tmp>` printed
   `catalog valid: 5 scenarios`, exit 0; with the FCR entry removed it raised
   `CatalogError: release set needs exactly one random-live entry, found 0`.
2. One test each, asserting the reason text, in
   `backend/validation/scenarios/tests/test_catalog.py`: unknown op, target
   absent from manifest, case missing, case failing hash, checkpoint outside
   window, expected file missing, unknown check id (registry is passed in;
   CLI default = `{company_completeness}`), class uncovered, >5 curated, no
   BSE-only, window.start vs manifest.
3. `tests/test_no_writes.py`: AST scan of contract.py and catalog.py for
   write/dump/mkdir/unlink/rename/open/... calls; none. (The validator reads
   files with `read_text`/`read_bytes` only.)
4. `backend/validation/docs/scenarios.md`: contract and coverage rules.
5. `pytest backend/validation`: 43 passed. Full suite: new 67 failed, 1462 passed
   (base 66 failed, 1448 passed). `comm -23 new base` showed one line,
   `api/services/tests/test_partitioned_storage.py::test_partitioned_storage`;
   it passes alone in both trees (I ran both suites concurrently, so I
   read it as interference between the two runs, not a regression; QA
   should confirm with a serial run). `stores/tests/test_boundaries.py` passes.

## Contract decisions the owner/QA should know

- Case manifest fields this contract needs (for the cases/ agent):
  `symbol`, `nse_symbol` (null = BSE-only), `window_start` (date),
  `files: {path relative to case root: sha256}`. Extra fields allowed.
  Edit `target.doc` is matched against `files` keys exactly (e.g.
  `sources/bse/...pdf`). If the freezer picks other names, `CaseManifest`
  in `contract.py` must follow.
- Scenarios have `kind: curated | random_live`. The random-live entry is a
  `scenario.yaml` with `classes: [FCR]` and no case/window/edits. The design
  did not specify how it is represented.
- Edit shape: every op has `target` (`{doc}` or, for drop_price_day,
  `{date}`); `duplicate_from_source` adds `as: {source, publish_date}`,
  `corrupt_file` `mode`, `delay_arrival` `arrival`.
- `window.end` must be 2026-10-15. This is an extra rule beyond acceptance.
- Validation stops at the first broken rule (raise) rather than listing them all.
- Expected `verdict` values are not checked against each check's states;
  only check ids are checked against the registry.
- The FC10 exception to window start (2026-07-01) belongs to the case freezer;
  this validator only compares against the manifest.

## Not done

- No FC12 edit op (design: after investigation).
- plan.md was written alongside the code, not before it.

## QA round 1 alerts (evidence.md)

Fixed in commit `9f274dd`, one test each in `scenarios/tests/test_catalog.py`:
- Alert 1: `delay_arrival.arrival` outside the window now raises CatalogError
  (`test_delay_arrival_outside_window`).
- Alert 3: malformed YAML now raises CatalogError naming the file
  (`test_malformed_yaml_names_file`).
- Alert 4: duplicate scenario ids now raise CatalogError naming both folders
  (`test_duplicate_scenario_id`).
- Alert 2 (expected `verdict` is free text): left as is, per the coordinator.
  It waits on the verdict contract defining its set of states.

`pytest backend/validation`: 46 passed.
