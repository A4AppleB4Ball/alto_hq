# Plan: completeness Awaiting state

**Touches:** backend/validation/completeness/{policy,quarters,check}.py, tests/test_quarter_states.py,
docs/completeness_design.md. Callers of DUE_NOTHING_IN: only the package itself and its test (grep of
backend: no other importer of validation.completeness yet). Not a money path (no weights/orders); the
proposal gate is a later task.

**Change:** rename state DUE_NOTHING_IN -> AWAITING ("awaiting"), removed from BLOCKING; reason
"due per the results calendar; no document in; closes when a later quarter holds documents".
Condition unchanged (due, no docs, no later quarter with docs); the rule already applies per quarter so
older and newer such quarters are all Awaiting. CHECK_VERSION "1" -> "2". Closing already yields Not released.
Unchanged: Missing, Stale, stance-without-chain-start, Expected/Unknown/Calendar_stale.
Owner-visible: ~259 companies flip incomplete -> complete; the "complete" reason text still reads
"every quarter analysed or not yet releasable".

**Acceptance runs:** (1) $TMPDIR/fleet.py loops all_latest_stances companies with check_company, read-only,
run on base (before) and branch (after) tree; table of states + Missing list. (2,3,4,5) pytest in
validation/completeness/tests (new tests for awaiting, closes, version-2 stale). (6) design doc grep.
(7) full suite vs base worktree comm -23, boundary test, imports.
