# Acceptance: exchange-quarterly-parse (draft)

Spike acceptance only. Parser tasks follow from its findings, not from this
file. Read-only; downloads go to a temp dir, via Python (no curl), and the
owner approves the network reads. Scope: 20 companies (10 BSE-only, 10 on
both) that filed Q2FY27 results on or before 2026-10-15.

1. **What exists.** For the 20, the filing types the exchanges publish for
   the results (names, formats, sizes) are listed, with the URL and filing
   date. The count of the 20 with a machine-readable file (XBRL or equivalent)
   against PDF only is printed.
2. **Field parity.** For the 20, the parsed revenue, profit and EPS of the
   quarter are compared with `backend/lib/financials` values (Screener) for
   the same period: agree / differ per field, differences listed with both
   values. No tolerance rule hides a difference.
3. **Timing.** For each, exchange filing time against the date Screener's
   period appears in `screener_financials` (first observed), in days.
4. **Coverage estimate.** From the stored daily announcement files
   (`1/daily_announcements`), the share of Result filings 2026-10-01..15 on
   BSE (119 rows) and NSE (303 outcome rows) that have a parseable file,
   measured, not extrapolated from the 20.
5. **Findings file** states the recommended next tasks (parser, backfill,
   Screener cutover) with the numbers above; no product code changed
   (`git -C <alto> status` clean).
