---
schema: evidence/v1
task: T-20261017-1300-sandbox-dhan-instrument-master
round: 2
range: 8cf276e..060f850
acceptance_sha256: a38f8586911b941e325cfcd6d50216773d3d1b478f657ca5b8d36592c186138f
qa: pass
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

## Round 2

The acceptance sha a38f8586... still matches the approval. Range 8cf276e..060f850. Sandboxes T1300-qa2head (060f850) and T1300-qa2base (8cf276e) were made by main's new_sandbox_worktree. HTTP(S)_PROXY was the dead 127.0.0.1:9 throughout. Logs are in `news_server/verify_data/reports/T-20261017-1300-sandbox-dhan-instrument-master/r2/`.

**Verdict: PASS.** The owner accepts check 7 in create() form, and the exact CLI run is a post-merge release-checklist item. There is one ALERT (A3) and no BLOCK.

### Checks
1-6. Pass. Ran in the head sandbox: `pytest -q backend/config/tests/test_new_sandbox_worktree.py backend/executor/tests/test_dhan_instruments_load_stored.py backend/executor/broker_factory/tests/ backend/stores/tests/test_boundaries.py`, 72 passed. `--help` lists `--seed-instrument-master USER_ID`. `git grep -n "load_stored()" -- backend/executor` returned rc=1 (empty).
7. Pass, in create() form per the owner. Ran from the head sandbox: `create(Path(main),'T1300-qa','060f850','qa/T1300-qa',('SHILPAMED',),('scienceamit1',))` succeeded.
   - The sandbox master `cmp`s identical to live. Live is dated 2026-10-17, sha1 af04e370..., and its mtime 1792187663 and size are unchanged before and after.
   - `create_symbol_daily_series(...,'2026-10-13').exchange_of()` returned NSE_EQ.
   - `_stored_exchange_of('scienceamit1','2026-10-17')` returned NSE_EQ. The 2026-10-18 read raised the check-4 message with the path and both dates.
   - A series ending 2026-10-18 first hits the NSE holiday fetch, which the proxy blocked. This is T-1200's scope, as in round 1.
   - The worktree, branch and sandbox were removed. **Release checklist:** run the exact CLI from main after merge.
8. Pass. Suite head: 99 failed/8 errors/1760 passed. Base: 99/8/1711. Both have 108 FAILED/ERROR lines, and `comm -23 head base` is empty.
   - Boundaries and the new_sandbox_worktree tests pass.
   - Imports: main_cockpit, app_factory, e2e.lanes, harness and new_sandbox_worktree have rc 0 on both head and base. The API modules need the dummy env vars from the dev skill, because worktrees have no .env. Base behaves the same way.
9. Held. No Dhan, LLM or credentials. On live, QA read only the scienceamit1 master and the SHILPAMED index.

### 060f850 production-path review
- **WORKSPACE_ROOT is identical.**
  - Local live checkout: main `paths.WORKSPACE_ROOT` and head `workspace_root_for(load_checkout(main), is_local_machine_at(main))` (True) both give `.../news_server/data/alto_data/workspace`.
  - Temp live checkouts built by `git archive` of each commit, importing `backend.config.paths`:

    | .env | base | head |
    |---|---|---|
    | absent | `<T>/news_server/data/alto_data/workspace` | same |
    | `LOCAL_EXECUTION=1` | `<T>/news_server/data/alto_data/workspace` | same |
    | server-style (`OTHER=1`) | `<T>/alto_workspace/workspace` | same |
    | `LOCAL_EXECUTION=yes` | RuntimeError | RuntimeError |

    Log: `r2/workspace_root_equiv.txt`.
  - By construction too: `checkout.data_root/"data"/"alto_data"` equals DATA_ROOT, and `checkout.alto_root` equals ALTO_ROOT.
- **Seeder arguments.**
  - `seed_instrument_master(main_root, worktree)` resolves each side from that checkout's own file and `.env`. Its only caller is `create`.
  - The pre-check runs before `git worktree add`, the same order as before.
  - The server live master resolves to alto_workspace (dev test, and QA's table above).
- **F1/F2 tests fail before the fix.** QA restored the 4e92ebf sources and kept the 060f850 tests: 11 failed and 17 passed (`r2/f1f2_prefix.txt`). They pass at head.

### Confirmed finding (the verifier reproduced it)
- **ALERT A3. Import-time strictness changed in sandboxes.** `backend/config/paths.py:265` (`WORKSPACE_ROOT = workspace_root_for(CHECKOUT, is_local_machine())`) now always calls `is_local_machine()`. Base short-circuited on `CHECKOUT.mode == "sandbox"`.
  - Scenario: a sandbox worktree whose root .env has `LOCAL_EXECUTION=yes`. `import backend.config.paths` raises RuntimeError at head, where base imported OK.
  - The same eager call happens in `new_sandbox_worktree.instrument_master_path` for the sandbox target. QA read this in the code; the verifier did not run it.
  - It is loud, never silent, and does not change any resolved path for live or server checkouts. No base module calls `is_local_machine` at import (verifier's git grep).
  - Low risk, but it is an unannounced import-time change in a production module. Dev could pass the call only when it is needed, or the owner can accept it as stricter.

### Dev claims not confirmed
None materially. Dev reports 98 failed per side and QA saw 99 per side. The diff is empty either way, so this is machine or time variance.

### Check that would catch this class
A paths test that imports `backend.config.paths` under a matrix of (mode x .env state) at base and head and diffs every exported path and every raise. That is the table above, automated.
