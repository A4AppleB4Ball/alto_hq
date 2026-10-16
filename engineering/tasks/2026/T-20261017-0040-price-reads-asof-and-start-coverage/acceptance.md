# Acceptance: price-reads-asof-and-start-coverage (approved)

1. **Non-trading as_of.** A test: cache ends on a Friday; a non-live read with a Saturday or holiday `end` returns the series through Friday, the last trading day by the market-day module (`backend/lib/prices`), not a hand-made weekday rule. A date after the last trading day the cache could know raises `PriceCacheMissError`. Fails on base, passes after.
2. **Start coverage.** A test: cache starts 2026-01-01, read with `start=2024-01-01` raises `PriceCacheMissError` naming the first cached date, unless the symbol's listing date is after `start` as recorded by an existing store (state which). Fails on base, passes after.
3. **Live unchanged.** Existing live-path tests pass unedited.
4. **Pilot read.** A 20MICRONS read in a credential-less sandbox for a Saturday as_of after 2026-10-13 behaves per check 1.
5. **Repo checks.** Boundary test, entry-point imports, full suite vs base with `comm -23`.
