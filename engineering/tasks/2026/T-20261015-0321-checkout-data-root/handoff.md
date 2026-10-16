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
