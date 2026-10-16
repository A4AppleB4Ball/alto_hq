# Acceptance: test-data-guard (proposed, not approved)

Starts after checkout-data-root merges.

1. **Mode.** `.alto_checkout.yaml` accepts `mode: test`; `backend.config.paths` then takes every root from a per-run temp dir, removed at session end. A test in `backend/config/tests/` shows `STANCES_DIR` is under the temp root.
2. **Guard.** A root `conftest.py` sets test mode before any import of `backend.config.paths`. A test that builds a path under the live root fails with an error naming the path. Shown by a test that tries `CompanyStore(live_root/...).append_stance` and expects the error.
3. **Nothing reaches production, proven without polluting it.** No check writes to the live root. (a) With a modification marker on the live root, `python -m pytest backend/api/services/tests/test_rebalance_price_action_cooldown.py -q` at head leaves nothing under the live root newer than the marker, excluding `workspace/*/book/*` and `scheduler/*` (written by the live server). (b) A test in `backend/config/tests/` makes a test write under the live root (a direct file write and a store write) and shows the session-end assertion fails the session with `LiveRootChangedError` / `LiveRootAccessError` naming the path, run inside a temp copy so the real live root is untouched. The earlier base-half (reproducing pollution on base against production) is removed by the owner: production is never polluted on purpose.
4. **Full suite.** Run the whole backend suite at head with the same marker: no file under the live data root is created or modified by tests. Failures vs base: no new ones (`comm -23`).
5. **Repo checks.** Boundary test, entry-point imports.
