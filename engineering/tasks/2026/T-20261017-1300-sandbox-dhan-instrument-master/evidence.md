---
schema: evidence/v1
task: T-20261017-1300-sandbox-dhan-instrument-master
round: 1
range: 909272f..4ad96b4
acceptance_sha256: a38f8586911b941e325cfcd6d50216773d3d1b478f657ca5b8d36592c186138f
qa: fail
outputs_changed: unverified
---

## Round 1

The acceptance sha matches the approval. All runs used HTTP(S)_PROXY=http://127.0.0.1:9. QA ran them in sandbox worktrees made by the main checkout's `new_sandbox_worktree`: T1300-qahead (4ad96b4) and T1300-qabase (909272f). Raw logs are in `news_server/verify_data/reports/T-20261017-1300-sandbox-dhan-instrument-master/`.

**Verdict: FAIL, on procedure only.** Check 7 cannot run as written before merge. Every other check passed, and the code has no BLOCK. Dev has nothing to fix. The owner decides between two options: (a) amend check 7 to the `create()` form, or (b) accept QA's create() run now and require the exact CLI run after merge as a release-checklist item. QA recommends (b).

### Checks
1. Pass. `pytest backend/config/tests/test_new_sandbox_worktree.py` covers byte-identical copy, unchanged live bytes and mtime, and requests.get and _fetch_and_cache patched to raise.
2. Pass. The same file covers: no live file gives FileNotFoundError naming the path, with no worktree and no sandbox root created; a master missing `date` or any one of the 6 keys gives ValueError naming the path and the key. Parametrized, 7 cases.
3. Pass. `--help` lists `--seed-instrument-master USER_ID`. `test_cli_seeds_the_master` drives `main()` (main_checkout_root monkeypatched to a temp live checkout).
4. Pass. `backend/executor/tests/test_dhan_instruments_load_stored.py`: 10-16 and 10-01 load; 10-17 raises with the path and both dates; an undated master raises; calling without as_of is a TypeError.
5. Pass. `broker_factory/tests/test_sandbox_instrument_master.py` passes. `git grep -n "load_stored()" -- backend/executor` is empty (rc 1).
6. Pass. Those tests patch socket.socket.connect to raise. Targeted run: 62 passed.
7. **Not run as written.** The CLI takes its main root from its own file and refuses anything but the live main, and main lacks this code. QA ran the same path the CLI calls, from the head worktree: `create(Path(main), 'T1300-qa', '4ad96b4', 'qa/T1300-qa', ('SHILPAMED',), ('scienceamit1',))`. It succeeded. The sandbox master was byte-identical to live (cmp). The live master is dated **2026-10-17**, sha1 af04e370…, and its mtime was unchanged before and after.
   - In T1300-qa, `create_symbol_daily_series('scienceamit1','SHILPAMED','2026-01-01','2026-10-13').exchange_of()` returned NSE_EQ. The SHILPAMED cache ends 2026-10-13.
   - `_stored_exchange_of('scienceamit1','2026-10-17')` returned NSE_EQ.
   - The 2026-10-18 read raised `ValueError ... dated 2026-10-17, older than the read's date 2026-10-18`.
   - Ends 10-16 and 10-17 on the series itself hit the NSE holiday fetch (require_current, cache older than end; blocked by the proxy). That is T-1200's scope, not this change.
   - The worktree, branch qa/T1300-qa and sandbox root were removed.
   - **Judgment:** this proves the intent. main() only parses argv and calls the same create(), and check 3 covers that. **The exact CLI run must still be repeated after merge**, since that is the only proof the merged main wires the flag.
8. Pass. Suite head 98 failed/8 errors/1717 passed; base 98/8/1698. `comm -23 head base` is empty (107 lines each, identical). test_boundaries and test_new_sandbox_worktree pass. These import cleanly: backend.api.main_cockpit, backend.api.app_factory, backend.e2e.lanes, backend.trading.harness, backend.config.new_sandbox_worktree.
9. Held. Dead proxy throughout. No Dhan, LLM or credentials. On live, QA only read the scienceamit1 master and the SHILPAMED index.

### Review
- **A1 fix (aa285b1).** The closure keeps its own `loaded` flag instead of reading `mapper._loaded`. A raise does not set the flag, so a later call retries and raises again. Correct.
- **Fixture re-date** (test_sandbox_shared_cache.py:140, 2026-01-01 -> 2026-10-16). Justified: the fixture's reads end on or before 2026-10-16 (lines 68-114), and the old date passed only because any date was accepted. The value is fixed, not today-relative, so it does not rot.

### Confirmed findings (a verifier failed to disprove both)
- **ALERT F1.** `backend/config/new_sandbox_worktree.py:48-56` with `instrument_master/contract.py:20`: the seeder checks that `date` is present, not that it is valid. A master with date "garbage", null or "2026-10-16T09:00" seeds OK. `load_stored` (`dhan_instruments.py`, `date.fromisoformat`) then raises ValueError or TypeError without naming the path. Reproduced in a temp dir. Only a hand-edit or corruption causes it, since the writer always writes `str(date.today())`. It is loud, never silent.
- **ALERT F2.** `backend/executor/instrument_master/contract.py:9` hard-codes `data/alto_data/workspace`, duplicating `paths.py:245` WORKSPACE_ROOT outside `backend.config.paths`. On a live non-local machine WORKSPACE_ROOT is `ALTO_WORKSPACE_REPO_ROOT/workspace`, so a seed there reads a path `load()` never writes. Usually that gives FileNotFoundError. A stale leftover file there would be copied, but the freshness check still raises for later reads. It agrees on the local Mac.

### Dev claims not confirmed
None. Handoff and plan match what QA observed. Dev's sandbox root `alto_sandboxes/T1300-dev` remains, and dev says to remove it with the dev worktree.

### Check that would catch this class
A release-checklist step that runs every acceptance CLI from main after merge, for any task whose CLI is gated on the live main. Proposed for the qa/ship skills: let acceptance name a pre-merge equivalent for main-gated CLIs.
