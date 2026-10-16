# Acceptance: results-calendar-to-stance (spike, approved)

Output is `findings.md` in the task folder, read-only on product data, no
product code changed on main, no LLM run.

1. **Coverage measured.** For the 484 companies with a stance: how many have
   a future results meeting on record, how many a past one for the latest
   ended quarter, how many none; split by exchange and SME.
2. **Date accuracy, market-wide** (owner decision
   D-20261016-2030-calendar-date-accuracy-market-wide). For the last ended
   quarter, the stored meeting date vs the date the results were published,
   for at least 50 companies on BSE and at least 50 on NSE, including
   BSE-only and NSE-only companies: BSE by its result filing, NSE by its
   outcome-of-board-meeting filing. The gap distribution in days per
   exchange, the pairing rule stated, and the effect of that rule on gap 0
   measured. The script and the raw inputs it read are saved in the task
   folder so QA reruns it without network. Stance companies are reported
   as a subset where they exist.
3. **The two known gaps counted**: BSE-only meetings before 2026-10-07 and
   SME generic purposes, with example companies.
4. **Where it enters the stance.** For agents A, B and D: the exact input
   each takes today and the proposed field (e.g. next result date, days
   away), with file:line of where it would be added; what each agent should
   do with it stated in one line.
5. **Proposed follow-up tasks**, in order, each with a one-line acceptance.
