# qa notes — to my future self

Read this before Step 2 and brief sub-agents with the relevant parts.
Curated: keep what keeps finding bugs, drop what never does.

## Bug classes seen in Alto (look for these first)
- Cross-user leak: a path or store keyed by symbol/stance, not by user.
- Swallowed errors: `except` that logs and continues (e.g. `record_trade`
  in manager.py, fixed 2026-10-11).
- Partial writes: two files written in sequence with no crash safety
  (revise_decision, FillLedger.sync).
- Default-user routes: API routes that act on "default" instead of the
  logged-in user.
- Order lifecycle: TWAP slices placed but not cancelled on abort; broker
  timeout treated as failure when the order may exist.

## Scenarios that paid off
- Two users, same symbol, run both pipelines, diff their workspaces.

## Checks still missing (candidates for backend/invariants/)
- (add as found)

## Added 2026-10-11 (round on 47458f2..734ac38)
- Bug class: cancel/abort that sets slice or order state without reading broker fills (fill lost, not booked).
- Bug class: an order that stays LIVE after a refused cancel keeps placing new slices.
- Bug class: a commit's own new test only checks mock.call_args (the last call) and fails.
- Scenario that paid off: fake-broker TWAP with slices in placed/partial/filled/pending, then cancel, retry exhaustion, expiry, cutoff.
- Verifier tip: brief verifiers to avoid the FAILED alert path (alerts.py urlopen); one verifier hung.

## Added 2026-10-16 (T-20261016-2146 paper broker)
- Bug class: an e2e test patches the real helpers a new broker hits (adv.previous_close builds DhanPriceStore, which raises for non-dhan; execution/market_analysis/adv.py:48). Run the real helper once for the new broker type.
- Bug class: a JSON store that saves on read paths, with no lock (executor/paper/broker.py _settled), loses updates across two processes.
