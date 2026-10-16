# Acceptance: lib-regroup (approved)

No behaviour change. Run when nothing else is mid-flight (owner's call on
timing).

1. **Layout.** `backend/lib/` has `quarters/`, `filings/`, `prices/`,
   `resolvers/` (each with `__init__.py`) holding the modules named in the
   task; `data_access`, `asof`, `llm_client`, `search`, `env_file` stay.
2. **No stale import.** `grep -rn "backend.lib.<old module>"` over `backend/`,
   `scripts/`, `workspaces/`, docs and tests finds no old path for any moved
   module. No re-export shims exist.
3. **Same behaviour.** Full backend suite: no new failure against the base
   commit (`comm -23` empty); `test_boundaries.py` passes.
4. **Every entry point imports** (`intake.runner`, `stance.runner`,
   `e2e.run`, `workflow.cli`, `execution.runner`, `raw.master_pipeline`,
   `backtest.replay`, the API app).
5. **History kept.** `git log --follow` works for a moved file (renames
   detected).
6. **Docs.** `backend/lib/docs/architecture.md` and
   `backend/docs/30_quarter_identity.md` name the new paths.
7. **Worktrees.** The list of worktrees still on old paths is given to the
   owner; none is modified.
