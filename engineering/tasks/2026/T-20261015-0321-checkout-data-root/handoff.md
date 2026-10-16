# Handoff (round 2): T-20261015-0321-checkout-data-root

Branch eng/T-20261015-0321-checkout-data-root, worktree /Users/kmrh581/personal/projects/workspace/alto/.claude/worktrees/T-20261015-0321-checkout-data-root.
Rebased onto local main 9950df7 (the ledger eb1eee9 is below it). Head 20e6afe, 7 commits: `git log 9950df7..20e6afe`. New this round: fbfe4ca (bse_collector paths), 20e6afe (--seed-index).
Acceptance hash approved: 0d5e9c99... (second approval in task.md), matches the file now.

Method: the branch is unmerged, so main runs old code. All checks ran in a throwaway clone of the branch, /tmp/t0321.ZPjp/alto_live (real .git dir, live file = production root /Users/kmrh581/personal/projects/workspace/news_server). Dumps, mtime snapshots, suite lists and logs are in /tmp/t0321.ZPjp. QA should rerun the same way (or in main after merge).

## Item 1: seeding
`python -m backend.config.new_sandbox_worktree <name> --seed-index SYMBOL [--seed-index ...]` copies `{SYMBOL}_index.json` from the live root's data/1/screener_announcements into the sandbox at the same path. Live is only read. A missing index raises before the worktree is created. Test: /Users/kmrh581/personal/projects/workspace/alto/.claude/worktrees/T-20261015-0321-checkout-data-root/backend/config/tests/test_new_sandbox_worktree.py.

## Item 2: reworded check 3, run end to end (golden company 544332)
- `python -m backend.config.new_sandbox_worktree chk3 --base HEAD --seed-index 544332` (from the live clone). Sandbox root /tmp/t0321.ZPjp/alto_sandboxes/chk3/news_server.
- Dump in the sandbox (/tmp/t0321.ZPjp/sb_dump.txt): 69 lines; 55 under the sandbox root; 0 name the live root. The 14 others are not data-root paths: ALTO_ROOT-derived paths inside the sandbox worktree itself (ALTO_ROOT, ALTO_WORKSPACE_REPO_ROOT, data/custom_triggers.jsonl, data/metadata/*, data/macro_events) and external read-only NSE paths (/Users/kmrh581/NSE_BSE_Data, nse_data_root/eq/index). known_user_ids() is [].
- `python -m backend.e2e.run --symbols 544332 --steps documents --end 2026-10-15` in the sandbox: "passed all 1 steps", documents ok 1s. I did not trace file reads at the syscall level; the evidence that it read sandbox only is that the empty sandbox failed on sandbox paths before seeding and passed after.
- Real write: `CompanyStore().append_stance("544332", record)` in the sandbox (record = live latest.json read, as_of 2026-10-16). store base printed: /private/tmp/t0321.ZPjp/alto_sandboxes/chk3/news_server/data/alto_data/stances. Landed: .../stances/544332/log.jsonl (13702 bytes), latest.json, log.jsonl.lock.
- Live mtimes: full walk of /Users/kmrh581/personal/projects/workspace/news_server before and after (401878 files each): modified 1, new 0, removed 0. The one file: data/alto_data/workspace/scienceamit1/book/default/snapshots.jsonl (mtime 21:47:39), written by the running API (book snapshots). Excluded only that file. Paths containing 544332 touched in live: none.

## Item 3: rebase and checks 1-5 on the rebased head
1. Dump identical: before = old code on main (69 lines), after = live clone with the clone prefix rewritten to main's (ALTO_ROOT and ALTO_WORKSPACE_REPO_ROOT, both derived from the checkout location). `diff` : IDENTICAL.
2. Each raised CheckoutDeclarationError naming the file and problem: no file; missing field ['data_root']; unknown field ['extra']; unknown mode 'bogus'; sandbox == live root; sandbox inside live root (both run in the sandbox worktree); mode live in a worktree. Also pinned in backend/config/tests/test_checkout.py (9 pass).
3. See item 2.
4. Live: `--llm-config backend/config/llm_benchmark_deepseek.yaml` and `LLM_CONFIG_PATH=<benchmark>` (e2e.run, and stance.runner --help) raise NonProductionLLMConfigOnLiveError before any work. Sandbox: the same `--llm-config` on e2e.run (documents step) passes.
5. Full suite, sequential (new, then base; base = detached worktree at 9950df7, since removed): new 66 failed / 1556 passed, base 66 failed / 1544 passed; `comm -23 new base` empty (same 66 pre-existing failures; lists /tmp/t0321.ZPjp/new, base, outputs .full). test_boundaries not in the failures. outputs_changed: no (the only store write was in the sandbox).

## bse_collector (fbfe4ca)
/Users/kmrh581/personal/projects/workspace/alto/.claude/worktrees/T-20261015-0321-checkout-data-root/backend/raw/scrappers/bse_collector.py: the two hardcoded production paths now come from backend.config.paths (DAILY_ANNOUNCEMENTS_DIR; SHARED_DATA_ROOT/"1"/"companies_announcements", no constant exists for it). Import checked; no test (both are in `__main__`-style helper functions that call live scrapers).

## Owner must know
- Merging breaks every checkout without .alto_checkout.yaml. Main checkout's file exists (owner approved leaving it): /Users/kmrh581/personal/projects/workspace/alto/.alto_checkout.yaml. Server file is a deploy step.
- The sandbox command must run from a live main checkout; until merge that is why I used a clone.
- Also in main: the stray worktree dir creation was avoided; I did not touch the .claude/worktrees/news_server symlink (owner's call).

## Not done
- Symlink removal. Help texts naming news_server/data/alto_data (backend/stance/runner.py:12,774; backtest compare_*): text still correct.
- plan.md was written after coding in round 1.

# Round 3 (final fix round after QA round 1 FAIL)
Acceptance hash a8ad8dd8... (third approval in task.md) matches the file. Rebased: already on local main 9950df7. Head: dce991f. New commits: ffaecf3 (symlink guard), dce991f (script removed). Method as before: throwaway clone /tmp/t0321r2.3umm/alto_live (live file = production root), sandbox chk5 with --seed-index 544332.

## Findings answered
- QA finding 4 (symlink): fixed in ffaecf3. /Users/kmrh581/personal/projects/workspace/alto/.claude/worktrees/T-20261015-0321-checkout-data-root/backend/config/checkout.py walks the sandbox root and raises if any symlink resolves to the live root or inside it. Test test_sandbox_with_symlink_into_live_refused in backend/config/tests/test_checkout.py (temp dir). Also reproduced by hand: data_root /tmp/symbox containing data -> live/data raises CheckoutDeclarationError "contains the symlink ... inside the live data root".
- Script: grep for rename_gujgasltd across the checkout found no reference; git rm in dce991f.
- Findings 2, 3 (other): out of scope per owner (Dhan caches, other scripts, start/stop, cwd-relative paths). Not touched.
- Finding 1 (check 3): amended acceptance; see below.

## Checks as amended
1. Dump (69 lines) base 9950df7 (old code, with dump_paths.py copied in) vs live clone: identical after normalising the checkout prefix, ALTO_WORKSPACE_REPO_ROOT, and base's .claude/worktrees/news_server symlink (which resolves to the same news_server dir).
2. Each raises CheckoutDeclarationError naming the file: no file, missing field, unknown field, unknown mode, sandbox==live, sandbox inside live, live in worktree, plus symlink into live.
3. Sandbox chk5: dump 55 of 69 lines under sandbox root, 0 name the live root; the other 14 are the two named classes (NSE read-only root, ALTO_ROOT-derived). `python -m backend.e2e.run --symbols 544332 --steps documents --end 2026-10-16` passes in the seeded sandbox ("none: every company passed"); seeding the index alone is enough with --end set to the run date, so no extra seeding option was needed. Write: CompanyStore().append_stance("544332", record) landed under .../alto_sandboxes/chk5/news_server/data/alto_data/stances/544332/log.jsonl. Live mtime walk (401909 files) before vs after the write: 0 modified, 0 new, 0 gone.
4. Live: --llm-config benchmark and LLM_CONFIG_PATH=benchmark (e2e.run, stance.runner, workflow.cli) raise NonProductionLLMConfigOnLiveError. Sandbox: same --llm-config on e2e.run completes.
5. Suite, sequential, live root, committed trees: new 66 failed/1557 passed, base 66 failed/1544 passed; comm -23 new base empty (lists /tmp/t0321r2.3umm/new, /tmp/t0321r2.3umm/base). Targeted: backend/config/tests 40 passed.

## Honest notes
- Mishap: my first chk5 attempt failed (a local branch named eng blocked eng/chk5) and my script then ran the e2e documents command in the live clone (mode live, production root) instead of the sandbox. Afterwards a find for files in the live root newer than 5 minutes showed none, and the later full mtime walk shows no change from it; the clone's logs/e2e/progress.jsonl was the only thing touched (reverted).
- During the two suite runs the live root changed by: scienceamit1 book snapshots.jsonl and dashboard chat duckdb files (running API), and two new files data/screener_data/raw_reports/stocks/HDFCBANK/html/HDFCBANK_page_20261016_223016.html and ..._223143.html. Nothing under 544332. I could not tell whether the new HDFCBANK pages come from the suite (new or base) or the live scrapers; if from the suite it is pre-existing behaviour of an existing test, and base also ran.
- outputs_changed: no for 544332 and all golden-company stores from the change itself (no store write on live).
