---
schema: evidence/v1
task: T-20261016-2130-classification-ledger
round: 1
qa: fail
qa_by: qa@claude-sonnet-5.5
commits: 79e66a7..02564f9
acceptance_sha256: 5e36723fc4d56bb48cb59842ee920577296cca97cb593309ef595d19d7370238
outputs_changed: unverified
---

## Round 1

Verdict is FAIL on the literal text of check 7 and one stray committed binary. Both are small. If the owner rules the four test edits acceptable, only the binary remains.

### Acceptance check results
Worktrees: head `.claude/worktrees/classledger-qa`, base `.claude/worktrees/classledger-base`, rebase scratch `.claude/worktrees/classledger-rebase` (all under /Users/kmrh581/personal/projects/workspace/alto). Hash of acceptance.md matches the approval.

- 1-3 immaterial, material and macro logged: `pytest backend/stance backend/stores/stance` at head, 144 passed (includes `test_worker_classification_ledger.py` immaterial/material/macro tests; macro key `macro:<name>` vs `announcement:<docids>`). PASS.
- 2 field-by-field vs old code: the dev test compares to the same new code with a lookup-None store, not to base. I compared directly: same stub material fixture run in base and head worktrees (/tmp/clqa/rec.py), record JSON minus written_at diff: IDENTICAL (1376 bytes each). PASS.
- 4 store only, lock, boundaries: `pytest backend/stores/tests/test_boundaries.py` 2 passed. Append goes through `CompanyStore.append_classification` under `exclusive_lock(log_path)`. My own 6-process test (/tmp/clqa/conc.py, overlapping and duplicate keys, 120 appends): 63 lines, 63 distinct keys (expected 63 distinct). No loss, no dup. PASS.
- 5 idempotent: `test_same_identity_is_not_duplicated` and second-run test pass. PASS.
- 5b cache: tests show second run 0 calls with the same signal, and prior note / annual / as_of / item docid / model change each make 1 call; macro second run 0 calls. PASS (judgement 2 below).
- 6 reader raises on corrupt line and wrong fields: store tests pass. PASS.
- 7 existing stance tests unchanged: NOT as written. Four existing tests were edited (see judgement 1). Suite vs base: no new failure. Entry points import (worker, runner, poller, classification_cache, repository). Check not met literally.

### Judgements the owner asked for
1. Check 7 "pass unchanged". Edits confirmed: `/Users/kmrh581/personal/projects/workspace/alto/backend/stance/tests/test_worker_price_only.py` lines 107 and 136, `.../test_materiality_context.py:64`, `.../test_announcement_key_paths.py:31`. Each changes only `company_store=MagicMock()` to `MagicMock(classification_lookup=MagicMock(return_value=None))`; assertions untouched (diff checked). The edit is needed: a bare MagicMock's `classification_lookup` returns a truthy MagicMock, so the worker would treat it as a cache hit and skip the classifier. So the literal check fails, but the change only supplies a store that behaves as an empty ledger, which is what the old tests assumed. QA does not pass or fail this silently: OWNER RULING NEEDED. QA view: acceptable in substance, a literal failure of the text.
2. 5b: confirmed by the tests and by reading `classify_cached`: identity = item_key, as_of, config name, model (`get_llm_config(...).model`), sha256 of canonical JSON of the exact classifier args; lookup before `classify()`. No call on hit, one call on any one-field change.
3. Macro fingerprint and `ledger._da`: `classify_macro_event` only uses `da` in `_extract_key_financials` via `FinancialsView.as_of(da, ...)`; it reads no prices. The financials dict from `da.get_financials` is itself in the hashed args (worker.py:393, macro_args), so a restated or newly published period changes the fingerprint and misses. No stale verdict from that. Dev's handoff statement about prices is therefore inaccurate, harmless. Side effect: the fingerprint changes whenever any later period is added to the financials file, so macro hits are lost on rerun after new results. A cache miss, not a stale hit. Residual: the cache key excludes prompt text and code (config = name and model only, as approved); a prompt edit still serves old verdicts. Known and approved.
4. Corrupt ledger: raises ValueError with path:line on read, lookup and append (test and my read). A torn last line from a crash also raises forever for that symbol until repaired; that is the spec, but note the ops consequence.
5. Material-path record vs base: done above, identical.

### Findings
- ALERT (fix before merge) `/Users/kmrh581/personal/projects/workspace/alto/backend/data/dashboard/chart_profiles.duckdb`: 274 KB generated binary added by commit 02564f9 (`git diff --stat 79e66a7 02564f9`). It is also untracked in main's status, so it is test or runtime output swept up by `git add`. Unrelated to the task; would put a DuckDB file into main.
- ALERT `backend/stance/worker.py` (classify_cached call sites): lookup is outside the lock, so two concurrent runs on one item can both call the LLM; append keeps the first entry, but the second caller returns its own differing signal while the ledger holds the first. Benign for temperature-0 identical verdicts; not reproduced as a divergence. Not run through the verifier (no subagent used; stated here as unconfirmed).
- No BLOCK found.

### Suite
Sequential, committed trees, dev-skill command from `backend/`: head 66 failed 1468 passed; base 66 failed 1448 passed; `comm -23 new base` empty (same 66 failures, +20 new passing tests). Rebase: the two commits cherry-pick cleanly on 66871a6 (note the cherry-pick carries the duckdb file); `pytest backend/stance backend/stores` there 243 passed; worker, runner, classification_cache, repository import fine.

### Dev claims not confirmed
- "Macro classifier also reads prices via ledger._da": not true, it reads financials only (harmless).
- The 4 base-failing stance tests from config singleton pollution: not separately checked; they are within the 66 equal failures.

### Risks and a check that would catch this class
- Stray generated files in commits: a boundary or pre-commit check that fails on new binaries under `backend/data/`.
- Per-symbol corrupt ledger blocks that symbol's checkpoint (intended); consider an alert path when the follow-up completeness check lands.
