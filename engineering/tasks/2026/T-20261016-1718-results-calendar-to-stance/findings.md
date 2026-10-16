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

## 2. Date accuracy: criterion not met on stance companies

Target was at least 50 companies for the last ended quarter. It cannot be met from stored
data, and I did not loosen it:
- Stance companies with Q2FY27 documents in the index: 1 (ARSSBL: meeting 10-13, ppt
  publish_date 10-13 `exact_pdf`, transcript 10-15 `first_observed`). The index holds only
  concall ppt/transcript/annual types; results filings are not in it.
- Q1FY27 (the last quarter with documents) has no meetings on record: capture began 10-07 and
  reads NSE only from the day after quarter end.

What I measured instead, market-wide, with the result filing as the "actual publish date"
(BSE daily announcements, category Result / Financial Results, 2026-10-01..15, 116 scrips,
95 have a meeting on record): filing date minus meeting date (nearest meeting on or before
the first filing):

| gap days | 0 | 1 |
|---|---|---|
| scrips | 94 | 1 |

Stance subset: 4 BSE scrips, all gap 0. NSE "Outcome of Board Meeting" text for 7 stance
symbols (ALOKINDS, ARSSBL, CYIENTDLM, EMMVEE, KABRAEXTRU, PREMIERPOL, SBC): all gap 0.
Caveat: the pairing picks the nearest earlier meeting, so a gap of 0 is partly built in.
It shows the date is the result day, not that a postponement is caught. Concall documents
trail the result (ARSSBL: 0 and 2 days; typically days to weeks), so the calendar date is the
result date, not the concall date. Needs a re-run once Q2 documents exist (see follow-up 1).

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
- Date accuracy at 50 stance companies (data does not exist yet, see 2).
- Exact SME-gap count (needs a network read).
- No LLM run; no product code changed; no data written.
