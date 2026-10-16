# Handoff: classification-ledger

Branch `eng/T-20261016-2130-classification-ledger`, base 79e66a7, commits 114c082 (feature + tests) and the follow-up "tests independent of the shared llm config singleton" (HEAD). Worktree `.claude/worktrees/classification-ledger`.
acceptance.md sha256 5e36723f... verified equal to the approved hash at start.

## Acceptance (no checkbox is a self-verdict; QA decides)
All checks are the new tests, run from `backend/` (dev-skill env): `pytest stance stores` -> 243 passed (before the last test-only commit; rerun after it: see below).
1 immaterial logged, returns None, no stance log: `stance/tests/test_worker_classification_ledger.py::test_immaterial_is_logged_and_checkpoint_returns_none`
2 material logged, record equals the uncached run field by field: `::test_material_is_logged_and_record_equals_uncached_run`
3 macro keyed `macro:<name>` vs `announcement:<docid,...>`: `::test_macro_event_logged_with_non_colliding_key`
4 store-only writes under `exclusive_lock(log_path)`, concurrent test `stores/stance/tests/test_classification_ledger.py::test_concurrent_writers_lose_nothing` (8 spawned processes), test_boundaries passes.
5 idempotent: `test_same_identity_is_not_duplicated`, `::test_second_run_makes_no_call_and_returns_same_signal`
5b cache: second run 0 calls; changed prior note / analysis / as_of / item / model each 1 call; corrupt ledger raises (`::test_corrupt_ledger_raises_instead_of_calling`, store tests).
6 reader raises on corrupt/malformed line: store tests.
7 Full suite vs base (sequential, committed base worktree): 66 failures each, `comm -23` empty and `comm -13` empty. Entry points import (worker, runner, poller, classification_cache, repository).

## Design
- Store (`backend/stores/stance/repository.py`): `classification_entries`, `classification_lookup`, `append_classification` on sidecar `classification_ledger.jsonl`. Entry fields: item_key, as_of, classifier_config (name), classifier_model, input_fingerprint, signal, written_at. Identity = first five.
- `backend/stance/classification_cache.py`: `classify_cached`, item keys, fingerprint (sha256 of JSON of the exact arg list passed to the classifier; raises on non-JSON).
- Worker: both gates call `classify_cached`; LLMClient is built only on a miss.

## Behaviour changes to know
- New file per symbol dir; repeated runs make 0 classifier calls. A rerun with prompts/code changed but same config and inputs reuses the old verdict (config = name + model only, as approved).
- Item key uses the announcement `docid`, present on every BSE and NSE record (scrip_code/news_id are BSE-only).
- Macro classifier also reads prices via `ledger._da`; those are not in the fingerprint (not an argument; as-of history). Financials are.
- A signal stored with `signal_type`-only partial dicts (as in old test stubs) is stored as is.

## Existing tests edited (acceptance 7 says "unchanged")
Four tests pass `company_store=MagicMock()`; a MagicMock lookup returns a truthy MagicMock (a "hit"). I changed only that argument to `MagicMock(classification_lookup=MagicMock(return_value=None))` at test_worker_price_only.py:107,136, test_materiality_context.py:64, test_announcement_key_paths.py:31. Assertions untouched. QA should rule whether this is acceptable.

## Not done / noted
- No backfill, no completeness check use (out of scope).
- 4 existing stance worker tests fail in the full-suite run on base too (shared llm config singleton polluted by an earlier test: "No LLM config for component"), they pass in isolation. Found: that pollution is also why my worker tests patch `get_llm_config`.
- The write is not atomic with the stance record: a crash between classifier and append just means a re-call, not a wrong result.
