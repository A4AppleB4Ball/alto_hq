---
schema: evidence/v1
task: T-20261016-2200-completeness-awaiting-state
round: 1
qa: pass
qa_by: qa@claude
commits: 79e66a7..4544f94
acceptance_sha256: 891784628abcc1d4c874db17848220c890d1d56fb386b4808066075ca74e7e88
outputs_changed: unverified
---

## Round 1

Acceptance hash matched the approval. Worktrees: `.claude/worktrees/T-20261016-2200-qa` (head), `...-qa-base` (base).

### Acceptance check results
1. Fleet (own loop `/tmp/qa2200/fleet.py`, fixed now=2026-10-16 12:00 IST, `CompanyStore.symbols_with_stances()`, 485 companies, read-only).
   - Base: 224 complete / 261 incomplete (matches the task's before). Quarter states: unknown 423, final 276, open 259, due_nothing_in 259, expected 47, missing 11.
   - Head: 475 complete / 10 incomplete. Quarter states identical except due_nothing_in 259 -> awaiting 259.
   - Missing set identical base vs head: ABDL Q1, ARSSBL Q1+Q2, CHANDAN Q1, EMUDHRA Q1, FAIRCHEMOR Q1, KRISHNADEF Q1, PNGSREVA Q1, RAYMOND Q1, SMCGLOBAL Q1, TAC Q1 FY27 (11 quarters, 10 companies). CLI on ARSSBL/CHANDAN confirms.
   - Incomplete only because of a due quarter, head: 0 (base: 251; 259 companies had a due quarter, 8 of them also Missing). Every non-due quarter state is unchanged; stance-without-chain-start violations 0 in both, identical.
   - Note: dev's 474/10 and 484 companies differ from my 475/10 and 485 (fleet moved by one); no consequence.
2. Awaiting, 3. Closes, 4. unchanged states, 5. version: tests `test_due_with_nothing_in_is_awaiting_and_does_not_block`, `test_older_and_newer_undocumented_due_quarters_are_all_awaiting`, `test_awaiting_closes_to_not_released_when_a_later_quarter_holds_a_document`, `test_a_verdict_recorded_under_version_1_reads_stale` pass; `pytest backend/validation` 31 passed. Diff changes only the Due-nothing-in line of existing tests; Missing/Stale/violation tests untouched.
6. Docs: `backend/validation/docs/completeness_design.md` amended note names D-20261016-2200-due-nothing-in-awaiting and table row Awaiting.
7. Repo checks: no relative imports or shims in diff; tests in `completeness/tests/`.

### Findings
None.

### Suite (backend, dev-skill command, base vs head)
Base 66 failures; head 67. `comm -23` showed one: `api/services/tests/test_partitioned_storage.py::test_partitioned_storage`. It passes alone at head and base (run concurrently the two suites share the production data root), so it is a flake from my parallel run, not a regression. Boundary test is in the suite and not among the failures. No verifier batch needed (no findings).

### Dev claims not confirmed
handoff counts (484 companies, 474/10, 258 awaiting) are off by one from the fleet as it is now; explained by fleet movement.

### Risks
A company whose due quarter never gets documents stays complete indefinitely; this is the owner's decision (D-20261016-2200), and the reason text states it. outputs_changed left unverified (no stored outputs compared).
