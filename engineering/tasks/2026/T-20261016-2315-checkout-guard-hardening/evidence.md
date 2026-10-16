---
schema: evidence/v1
task: T-20261016-2315-checkout-guard-hardening
round: 1
qa: pass
outputs_changed: unverified
---

## Round 1

Worktree 8465080 at /Users/kmrh581/personal/projects/workspace/alto/.claude/worktrees/ckg-qa with a sandbox declaration on empty /tmp/qa_ckg roots; no production writes. Acceptance sha256 matches approval.

### Acceptance
1. Two-hop and 2. parent link: `pytest backend/config/tests -q` -> 45 passed. With `backend/config` reverted to 9013baa and only the new test file kept, test_two_hop_link..., test_link_to_parent... (and the 2 live-mode tests) FAIL; so fail on base, pass on head.
3. Seeded sandbox with 450000 files under DATA_ROOT: `time python -c "import backend.config.paths"` -> 0.233s total. Guard is `refuse_paths_into_live` over uppercase Path globals, no walk.
4. Live mode: test_live_in_clone_with_git_dir_refused and test_live_data_root_must_be_the_one_beside_main fail on base, pass on head. Real main checkout imports with mode live (unchanged). A worktree is still refused.
5. Boundary test 2 passed; imports ok for config.paths, dhan_client_cli, workflow.cli. Full suite (dev skill command, empty sandbox roots): head 108 FAILED/ERROR lines, base 108, `comm -23 new base` empty.

### Findings (ALERT, none BLOCK)
- A1 Regression vs base: a link below a PATH constant is accepted. Repro: sandbox with `data/alto_data/stances/ABC -> <live>/data/alto_data/book` imports fine on head (STANCES_DIR/ABC resolves into live); likewise `data/alto_data/stances_link -> <live>/data`, which base rejected with "contains the symlink ...". Acceptance 3 chose this design, but live writes through such a link are now undetected; `new_sandbox_worktree --seed-index` creates links/copies, so the owner should know. Candidate catch: have the seeding tool and the sandbox creation refuse links, or a startup check of one level of DATA_ROOT children. Self-reproduced on both commits (verifier not spawned; reproduction is deterministic).
- A2 Live layout: a throwaway clone at /tmp/.../alto with its own sibling news_server and mode live is accepted (own root, not production; reproduced). The server checkout must be named `alto` with `news_server` beside it, otherwise startup raises. I could not confirm the server layout; owner/ship should check before deploy.
- A3 The guard sits at the end of paths.py (line ~242); constants defined after it are not checked and `new_sandbox_worktree` calls only load_checkout. Currently no Path constants follow it except WorkspacePaths (class), checked via WORKSPACE_ROOT.

### Dev claims not confirmed
Server layout assumption (see A2); the entry-point list was only partly re-run (e2e.run not tried).
