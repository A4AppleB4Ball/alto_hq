# Handoff
Branch eng/T-20261016-2315-checkout-guard-hardening, base 9013baa, commit 8465080 (one commit, 3 items together in checkout.py/paths.py).
Worktree: /Users/kmrh581/personal/projects/workspace/alto/.claude/worktrees/T-20261016-2315-checkout-guard-hardening

## Acceptance
1,2,4: tests in backend/config/tests/test_checkout.py: two_hop_link_into_live_refused_at_import, link_to_parent_of_live_refused_at_import, live_in_clone_with_git_dir_refused, live_data_root_must_be_the_one_beside_main. On base (checkout.py/paths.py reverted) these 4 fail; after, 45 passed in backend/config/tests.
3: refuse_paths_into_live resolves every uppercase Path in paths.py; no walk. Sandbox with 450000 files: import backend.config.paths = 0.237s total wall.
5: boundary test 2 passed; entry points import clean (intake.runner, stance.runner, e2e.run, workflow.cli, execution.runner, raw.master_pipeline, backtest.replay). Full suite on empty /tmp sandbox roots: new 108 FAILED/ERROR lines, base 108, comm -23 empty.

## Behaviour changes the owner must know
- mode: live now requires checkout dir named "alto" with data_root == <parent>/news_server (current main matches). Server layout assumed the same; if the server checkout is elsewhere, startup raises. A clone named alto beside its own news_server still passes (it is its own live root).
- Guard runs at end of paths.py constants (not in load_checkout); new_sandbox_worktree still calls load_checkout only. Old walk test replaced by one-hop import test.
- Test fixtures now name main "alto" and live root "news_server".
## Not done
Only named PATH constants are resolved; links below them (e.g. a subdir of blob_storage linking into live) are not caught. Chat/dashboard cwd paths out of scope.
