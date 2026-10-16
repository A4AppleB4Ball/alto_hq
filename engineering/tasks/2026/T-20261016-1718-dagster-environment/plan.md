# Plan
Touches: new files only, backend/orchestration/dagster_env/ (definitions, workspace.yaml, dagster.yaml, two plists, install.sh, prune_runs.py, graphql_check.py) and docs. No existing file changed. Not a money path. Venv and DAGSTER_HOME in /Users/kmrh581/personal/projects/workspace/alto_dagster (outside repo and data root).
Change: heartbeat job and */5 schedule only; no product data touched.
Checks: 1 pip freeze diff; 2 plutil + docs; 3,4,5 owner steps; 6 prune_runs.py on a copy; 7 by construction (no code reads the data root) plus owner check of mtimes.
