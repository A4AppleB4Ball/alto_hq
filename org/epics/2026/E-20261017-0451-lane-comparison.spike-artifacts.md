# Spike artifacts (throwaway, 2026-10-17)

Not product code. Written to learn what data exists; paths are hardcoded to /tmp/spike and the user scienceamit1. Read them for the method; rewrite, do not import.

| File | What it shows |
|---|---|
| `E-20261017-0451-lane-comparison.replay-dated.diff.md` | The whole change to `backend/backtest/replay.py` for dated deposits (story 1), plus per-day target and signal logs |
| `E-20261017-0451-lane-comparison.replay-dated.py` | The patched copy of replay.py that produced the numbers |
| `E-20261017-0451-lane-comparison.run-dated.py` | Runs it: preset v2, start cash 193,994, deposits 21 Sep 499,632 / 25 Sep 150,000 / 8 Oct 30,000 / 12 Oct 150,000, 10 bps |
| `E-20261017-0451-lane-comparison.real-daily.py` | Builds the real daily series from the Dhan ledger and fills (story 2); ledger rows needed: Money added/transferred, Trades, Charges |
| `E-20261017-0451-lane-comparison.build-data.py` | Metrics, XIRR, Sharpe ± se, exact rupee gap split, overlap, per-name contribution, execution vs open, decision trace (stories 4, 5) |
| `E-20261017-0451-lane-comparison.mockup-v8.html` | Layout mockup with four lanes; shadows are copies of production. Needs a data JSON injected at `/*DATA*/null` |

Run order: real-daily, run-dated, build-data. Not kept: the Dhan ledger and the output JSON (account data; rebuild from the ledger CLI `python -m backend.executor.dhan_client_cli ledger --from D --to D`).

Gotchas found: flows posted on non-trading days must roll to the next trading day (else TWR explodes); the Dhan price store refetches stale series and needs a valid token; the price store's last bar set the window end (2026-10-15).
