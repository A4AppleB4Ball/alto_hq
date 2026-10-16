---
schema: evidence/v1
task: T-20261016-1928-scenario-contract
round: 1
qa: pass
range: 79e66a7..efe5533
outputs_changed: unverified
---

## Round 1

Approval: acceptance.md sha256 689d3cff...b9d5 matches approvals. QA worktree `.claude/worktrees/T-20261016-1928-scenario-contract-qa` at efe5533; base worktree `-qabase` at 79e66a7. Raw logs: `news_server/verify_data/reports/T-20261016-1928-scenario-contract/`.

### Acceptance checks
1. Valid catalog passes: PASS. `test_valid_catalog_passes` passes. The CLI on a tmp catalog built by `fixtures.build_catalog` (4 curated + FCR, FC01-FC12, one BSE-only) prints `catalog valid: 5 scenarios` and exits 0. The CLI on a missing root raises `CatalogError: ... scenarios folder missing`.
2. Each rule fails with its reason: PASS. The 11 tests in `scenarios/tests/test_catalog.py` (one per rule, each matching its reason text) all pass. The registry is passed in, and the CLI default is `{completeness.policy.CHECK_ID}` = `company_completeness`.
3. No writes: PASS. `test_no_writes.py` (an AST scan of contract.py and catalog.py) passes. The imports are pydantic, yaml, hashlib, argparse and completeness.policy, and nothing that writes.
4. Doc: PASS. `backend/validation/docs/scenarios.md` states the contract and the coverage rules in prose. It is not a code copy.
5. Suite: PASS. `pytest backend/validation`: 43 passed. The full suite (dev skill command, committed trees) was run SERIALLY, base first, then head:
   - base 79e66a7: 66 failed, 1448 passed, 16 skipped
   - head efe5533: 66 failed, 1463 passed, 16 skipped (+15 = new tests)
   - `comm -23 head base` is empty. `test_partitioned_storage` failed in neither run, so dev's head-only failure was interference between their concurrent runs. `stores/tests/test_boundaries.py`: 2 passed.

### Findings (all ALERT; verifier confirmed all 4)
- ALERT catalog.py:66-73 / contract.py:63-66. `delay_arrival.arrival` is never checked against the window, so an arrival of 2030-01-01 is accepted. Repro: /tmp/qa_probe.py.
- ALERT contract.py:128. `ExpectedVerdict.verdict` accepts any string ("banana" is accepted). The doc calls it a verdict state, but record.py:18 also leaves `state` as a free str, so nothing exists to validate against yet.
- ALERT catalog.py:36-39. Malformed YAML raises a raw `yaml.ParserError` instead of a `CatalogError` naming the file. It still fails loudly.
- ALERT catalog.py:124-131. Duplicate scenario `id`s across folders are accepted.

### Dev's undecided choices (for the owner)
- `window.end` is pinned to 2026-10-15 (contract.py WINDOW_END). This rule is beyond acceptance, and every future release will need a code change.
- Validation is first-error-only: it raises on the first broken rule and does not list them all.
- plan.md was written alongside the code, not before it (process deviation).
- The shape of the random-live entry (`kind: random_live`, no case/window) is dev's invention; the design did not specify it.

### Dev claims not confirmed
None. The CLI run, the test counts and the boundary test all reproduced. The partitioned_storage failure did not reproduce in the serial run.

### What would catch this class automatically
The four gaps above would be caught by one property test per date-bearing edit field (every date field lies in the window) and a uniqueness rule on scenario ids.
