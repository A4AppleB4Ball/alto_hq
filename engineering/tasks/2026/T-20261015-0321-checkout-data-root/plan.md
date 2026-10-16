# Plan (written late: after the first implementation pass, before QA)

Touches: backend/config/{checkout,paths,llm_settings,dump_paths,new_sandbox_worktree}.py, .gitignore, tests in backend/config/tests and e2e/tests/test_llm_config_cli.py.
Money path: no. Not touched: backend/stance/worker.py, backend/stores/stance/repository.py.
Change: paths.py reads .alto_checkout.yaml (mode, data_root); raises on missing/unknown/bad fields, sandbox at/inside the live root (live root = main checkout's own file), live in a worktree. Live resolves as today. Sandbox WORKSPACE_ROOT is always under its DATA_ROOT. llm_settings refuses a non-production config on live (--llm-config, and LLM_CONFIG_PATH at import and use).
Not done: symlink removal, server live file, help texts (owner's calls / no behaviour).
Checks: dump_paths before (main, old code) vs after (live checkout of the branch); import failures per case; sandbox worktree e2e step + mtime compare; --llm-config / env on live and sandbox; suite base vs new.
