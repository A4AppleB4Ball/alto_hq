# Findings: results calendar to stance (spike)

Run 2026-10-16 (today = 2026-10-16), worktree `.claude/worktrees/results-cal` at a5b5606,
read-only. The store was read directly with `store.read_meetings`, no capture, no network.
The latest ended quarter is Q2FY27 (ended 2026-09-30). The store was last captured
2026-10-16T03:42, holds 1149 meetings (BSE 644, NSE 505), first captured 2026-10-07.

"484 with a stance" = stance dirs with a non-empty `log.jsonl` (500 dirs, 16 empty/not companies).
All 484 resolve through `company_listings`. "Future" = meeting after today. "Past" = meeting
after 2026-09-30 and up to today (the `results_meeting_held` rule).

## 1. Coverage

| | companies |
|---|---|
| future meeting on record | 48 (47 future only, 1 future and past) |
| past meeting for Q2FY27 | 15 (14 past only, 1 both) |
| none | 422 (87%) |

By segment. BSE-only = no NSE listing (99). "NSE SME-like" = NSE-listed but absent from the
NSE EQ bhavcopy (68): the store has no SME flag, this is my proxy, none of the 68 appears in
the sampled 2026 EQ files.

| segment | n | none | future | past | both/other |
|---|---|---|---|---|---|
| NSE main board + BSE | 297 | 246 | 41 | 10 | 0 |
| NSE main board only | 20 | 18 | 1 | 1 | 0 |
| BSE-only | 99 | 92 | 4 | 2 | 1 (both) |
| NSE SME-like | 68 | 66 | 1 | 1 | 0 |

Reading: 87% "none" is mostly season timing, not a gap. Exchanges are told a meeting only
days ahead. Among meetings first captured after the 10-07 batch, notice before the meeting
has median 10 days, max 36, and 31 of 723 came with 0-2 days notice (captured_at is a ceiling
on the real notice date). Companies with a meeting in the next 7 / 14 / 30 days: 21 / 32 / 48.
So "next result date" exists for about 10% of stance companies today, and rises through the
Q2 season. It is never available more than about 5 weeks ahead. One company (542727) has two
meetings on record (10-15, 10-23): the store is add-only, so a moved or second meeting leaves
the old date in place and "which is the next result" is ambiguous. 6 of 93 BSE meetings dated
10-01..10-14 have no result filing (postponed or not a results meeting) and stay on record.

## 2. Date accuracy, market-wide (owner decision D-20261016-2030)

Stored meeting date vs the date the results were filed, Q2FY27, meetings dated 2026-10-01..15
(filings are on disk through 10-15). Rerun offline, no network, from the task folder:
`python -I date_accuracy/measure.py date_accuracy/inputs` (output saved in
`date_accuracy/measure_output.txt`). `date_accuracy/extract_inputs.py` is what copied the raw
inputs from the product data (read-only): the results-calendar store, the company mapping, the
stance keys, every BSE `Result` row and every NSE `Outcome of Board Meeting` row of the stored
daily announcement files 10-01..15 (BSE 119, NSE 303 rows, unmodified). No fetch was needed.

Actual date: BSE = the Result / Financial Results filing (`NEWS_DT`); NSE = the Outcome of Board
Meeting filing (`sort_date`). Sample: every stored meeting in the window, not a subsample.

| exchange | meeting codes | paired (rule A) | BSE-only / NSE-only / both / unmapped | stance subset |
|---|---|---|---|---|
| BSE | 140 | 95 | 11 / - / 56 / 28 | 4 |
| NSE | 112 | 107 | - / 6 / 80 / 21 | 7 |

Gap = filing date minus meeting date, days (rule A, headline):

| exchange | gap 0 | gap 1 | gap 5 |
|---|---|---|---|
| BSE (95) | 94 (98.9%) | 1 | 0 |
| NSE (107) | 105 (98.1%) | 1 | 1 |

By listing: BSE-only 11 of 11 at gap 0; NSE-only 5 of 6 at gap 0 (the other gap 5, BSHSL meeting
10-10, outcome 10-15); companies on both exchanges 56/56 (BSE) and 80/80 (NSE). Stance subset:
4 BSE and 7 NSE, all gap 0. "unmapped" = code absent from the company mapping CSV (28 BSE, 21 NSE
codes), so its listing class is not known; they are in the totals.

**Pairing rules and their effect on gap 0** (per exchange and code):
- A forward (headline): a meeting pairs with the first filing on or after it and before the
  code's next meeting. Gap is never negative by construction; a meeting with no such filing is
  "unfiled" (BSE 47 meetings, NSE 6: no filing on disk by 10-15, so postponed, not a results
  meeting or filed late; not diagnosed here).
- B backward (the round-1 rule): a filing pairs with the latest meeting on or before it.
- C nearest on either side: can show a filing before the stored date.

| rule | BSE paired / gap 0 | NSE paired / gap 0 |
|---|---|---|
| A | 95 / 94 (98.9%) | 107 / 105 (98.1%) |
| B | 95 / 94 (98.9%) | 110 / 105 (95.5%) |
| C | 97 / 94 (96.9%) | 116 / 105 (90.5%) |

Reading: gap 0 is robust on BSE (94 under every rule); the rule moves only the denominator.
Rules A and B cannot produce a negative gap, so they hide a filing earlier than the stored date.
Rule C shows them: BSE 530253 (stored 10-14, filed 10-01, -13), 543579 (stored 10-14, filed
10-09, -5); BSE 532378 stored 10-12, filed 10-13 (+1). On NSE the extra B/C pairs are mostly
other Outcome of Board Meeting filings by the same company (e.g. TCS 10-01 and 10-08), which
are not results outcomes: NSE's desc does not say whether an outcome is a results outcome, so
the NSE pairing needs the stored results meeting to select the right filing (rule A does this)
and any gap above 0 on NSE (BSHSL +5, UTKAL +1) is a candidate, not proven postponement. I did
not read filing text to decide (no keyword rule).

What this does not show: it measures only meetings the store holds, so a results meeting the
store missed (47 NSE-only and 78 dual-listed NSE outcome filers have no stored meeting in the
window; many are non-results outcomes, and SME generic purposes are a known gap) is not in the
gap table. Gap distribution is the date accuracy of what is stored: the stored date is the
filing day in about 98% of cases on both exchanges. The BSE-only meeting gap before 10-07 is in
the unfiled count, not the gap table. Concall documents trail the result (ARSSBL: 0 and 2
days), so the calendar date is the result date, not the concall date. Stance companies
(~484) re-measure against index documents after about 2026-11-15 (follow-up 1, decision's
condition).

## 3. The two known gaps, counted

- **BSE-only meetings before 2026-10-07.** 14 of 116 BSE result filers (10-01..15) filed
  before 10-07; 21 of 116 have no meeting on record. Stance impact today: 0 of the 4 stance
  filers lack a meeting. BSE-only stance companies are 99; 7 have a meeting on record
  (examples 513119 held 10-08, 519287, 524218). The larger effect is historical: no Q1FY27
  (Jul-Sep) meeting exists for any company, so the "next result date" cannot be rebuilt for
  any earlier stance date. It matters for backtests and rebuilds, not for the next result.
- **SME generic purposes.** Not countable from the store: it does not record the NSE index or
  the purpose, and a non-matching row is dropped at capture. Proxy: 2 of 68 SME-like stance
  companies have a meeting on record (ESCONET 10-23, SUPREMEPWR 10-16), 3% against 15-17% for
  main board. SMEs also report half-yearly, so this is not proof. An exact count needs
  one network read of NSE `index=sme` (excluded here); follow-up 2.

## 4. Where it enters the stance

Today's inputs (`backend/stance/prompts.py`, `backend/stance/worker.py`):

| agent | takes today | proposed field | add at | what it does with it |
|---|---|---|---|---|
| A fundamental, 4 prompts (`agent_a_first` :52, `_update` :92, `_annual` :150, `_event` :229) | quarterly/annual analysis, prior A notes, announcements since, bodies, macro FYI. No price. | `next_result: {date, days_away}` or an explicit reason it is unknown | block beside `<announcements_since_last_assessment>` (:119, :196, :289) and in `agent_a_first`; built in `worker.py` near :437-446, passed at the calls :481-513 | Knows when the next quarter lands; frames thesis metric and guidance as due for test, never forecasts the result |
| B market behaviour (`agent_b_prompt` :348) | P/E snapshot, price arc, prior B and A notes, A's output | same field | inside `<market_data>` (:397) next to `_fmt_pe`; built beside `pe_snapshot` at `worker.py:518`; call at :521 | Reads a pre-result run-up or drift as the market anticipating the result; this is the dated event B5 already tests ("known dated future event", `system_prompts.py:205`, :322) |
| D decision (`agent_d_prompt` :442) | A and B outputs, last 3 checkpoints. Source data excluded by design (`architecture.md` table). | none to D directly | pass it through A and B outputs only | D sees the date through B's B5 reading and A's note; keeps isolation. If the owner wants D to see it, add one line to `<fundamental_analyst>`, call at `worker.py:530` |

Point-in-time: the one chokepoint is `AsOfLedger` (`backend/lib/asof.py:51`). Add a method there
(near :192 `latest_annual_analysis`) returning the earliest meeting with `captured_at` at or
before `as_of` and date after `as_of`; the store already carries `captured_at` per meeting.
Read the store with `read_meetings` style access, not `reader.load_meetings` (it can capture
and call the network inside a stance run). For any as_of before 2026-10-07 the answer is
"calendar did not exist": return a typed result with a reason (as `PESnapshot` does for P/E),
rendered in the prompt as unknown, never an invented date and never a silent skip. This keeps
rebuilds and backtests honest.

## 5. Follow-up tasks, in order

1. Re-measure date accuracy after Q2 documents land (around 2026-11-15): same join over at
   least 50 stance companies, meeting date vs index `publish_date` of the Q2FY27 results and
   concall documents. Acceptance: gap distribution table for at least 50 companies in findings.
2. Count the SME gap: one read-only NSE `sme` pull compared with the store. Acceptance: number
   of SME stance companies whose results meeting NSE lists but the store does not, with
   examples.
3. Calendar store keeps what the stance needs: record superseded or moved meetings (a meeting
   absent from a later BSE listing and no result filed) and pick the next one deterministically.
   Acceptance: 542727 and the 6 unfiled meetings resolve to one next date or none, tested.
4. `AsOfLedger.next_results_meeting(symbol, as_of)` with the typed unknown reason, and tests
   for before-capture, future, held and moved. Acceptance: the tests pin each case and an
   as_of of 2026-10-01 returns "calendar not captured".
5. Add the field to Agent A (four prompts) and B, built in `worker.py`; D unchanged. Acceptance:
   prompt-render tests show the block for a company with a date and the reason for one without;
   a pilot of 3 stance runs on companies with a meeting within 14 days (owner approves the LLM
   run) whose A/B notes mention the date.
6. Make sure the daily capture runs before stance runs read the store. Acceptance: a stance run
   with `last_captured_at` older than 20 hours raises.

## Not done
- Date accuracy on 50 stance companies (data does not exist yet; owner decision moved it to follow-up 1).
- Exact SME-gap count (needs a network read).
- No LLM run; no product code changed; no data written.
