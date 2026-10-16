# Acceptance: docs-system-map-validation-dagster-checkout

Starts after test-data-guard and cockpit-dagster-link are merged, so the docs describe what is on main.

1. **System map.** `backend/docs/00_system_map.md` has a section on the Dagster chain (assets, the gate, the asyncio scheduler it coexists with, no cut-over yet, the query exit code as the truth, runs on the Mac not the server) and a section on validation (completeness verdicts, stage checks, cases, scenarios) linking to `backend/validation/docs/` and `backend/orchestration/docs/`.
2. **Checkout modes.** A new `backend/config/docs/checkout_modes.md` explains `.alto_checkout.yaml` (live, sandbox, test), the live-root guard and its documented gaps, how to create a sandbox (`new_sandbox_worktree`), where tests write, and the server prerequisite (a `mode: live` file in a directory named `alto` with `news_server` beside it).
3. **Prices and holidays.** The same doc or the lib docs state where the Dhan daily cache and `nse_holidays.json` live in `NSE_BSE_Data`, who writes them (the owner / price ingestion; `write_holidays` yearly), and what a non-live checkout does on a miss (`PriceCacheMissError`, `HolidayYearMissingError`, `HolidayListMissingError`).
4. **CLAUDE.md.** Its Data paths section is corrected for the checkout declaration and links to `checkout_modes.md`; its Key directories list `backend/validation/` and `backend/orchestration/`. No other section is rewritten.
5. **Docs are true.** A script run in the check lists every file path, module, command and constant the new text names and shows each exists on main (output attached). No design text duplicates code; docs state invariants.
6. **Repo checks.** Boundary test unaffected; no code files in the diff.
