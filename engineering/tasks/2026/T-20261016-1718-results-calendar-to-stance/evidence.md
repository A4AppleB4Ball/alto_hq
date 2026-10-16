---
schema: evidence/v1
task: T-20261016-1718-results-calendar-to-stance
round: 1
qa: fail
outputs_changed: no
---

# Evidence, round 1 (spike, no code)

Step 0: approvals hold acceptance.md sha256 9a909012...a05b0; recomputed sha256 matches.
No code diff (spike). plan.md and handoff.md not read before the verdict.

## Acceptance checks

1. Coverage: PASS. Own script (`/tmp/qa_s/c.py`: `read_meetings`, `MeetingsByListing.company_dates`, `company_listings`; stance = dirs with non-empty log.jsonl) gives 484 companies, future 48, past (quarter end < d <= today) 15, both 1, none 422. BSE-only (no NSE listing): 99 = 92 none, 2 past, 5 future incl. 1 both (findings: 4 future, 2 past, 1 both). Next meeting within 7/14/30 days: 21/32/48. All match findings. The "NSE SME-like" 68 split depends on the author's bhavcopy proxy, which I did not recompute; the store has no SME flag and findings says so.
2. Date accuracy (>= 50 companies, last ended quarter, meeting date vs index publish date): FAIL. Findings itself says the criterion is not met. I confirmed that only 1 stance company (ARSSBL) has a real Q2FY27 document in the index (KAMDHENU matches only through `reporting_period_prior`, an inferred label). ARSSBL meeting 10-13, ppt publish 10-13 (exact_pdf), transcript 10-15 (first_observed): matches findings. The substitute (116 market-wide BSE scrips, result filings from BSE announcements) is a different population and a different "actual" document than the acceptance text asks for, so it does not meet the check. The nearest-earlier pairing caveat is disclosed and real (gap 0 is partly built in). I could not rerun the 94/1 gap table (needs BSE announcements, outside my no-network scope). The spike was honest, but the acceptance text is not met.
3. Two known gaps counted: counts and examples given; not independently re-run where they need network. BSE-only stance 99, 7 with meetings (513119 held 10-08 confirmed in the store). The SME gap is only a proxy (ESCONET 10-23 and SUPREMEPWR 10-16 confirmed on record); findings admits an exact count needs a network read.
4. Where it enters: PASS. Cited references verified at a5b5606: prompts.py :52 agent_a_first, :92 agent_a_update, :150 agent_a_annual, :229 agent_a_event, :348 agent_b_prompt, :442 agent_d_prompt, :397 `<market_data>`, :119/:196/:289 `<announcements_since_last_assessment>`; worker.py :437 announcements_between, :518 pe_snapshot, :521 prompt_b, :530 prompt_d, :481 agent_a_first; system_prompts.py :205 and :322 (B5 known future event); asof.py :51 AsOfLedger, :192 latest_annual_analysis. Each exists as described (worker.py :446 and :513 sit inside multi-line expressions, plausible).
5. Follow-ups: PASS. Six ordered tasks, each with an acceptance line.

## Data safety
mtimes of alto_data/stances and alto_data/system (515 entries) before and after: identical. No capture, no network, no `reader.load_meetings`.

## Confirmed findings
- Acceptance item 2 not met (above). Verdict rule: a check not met is a fail. The owner can accept the substitute or defer item 2 to follow-up 1 (about 2026-11-15).
- No other issues. The "87% none" reading is timing, not a defect.

## Dev claims not confirmed
- Market-wide gap table (94 at 0, 1 at 1) and the SME-like 68 split: not reproducible without network or the bhavcopy.

## Suggested catch
Spike acceptance items should state the data-availability precondition, so a sample-size target is not approved against a population that cannot exist yet.
