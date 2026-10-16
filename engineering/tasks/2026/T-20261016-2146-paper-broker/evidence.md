---
schema: evidence/v1
task: T-20261016-2146-paper-broker
round: 1
qa: fail
qa_by: qa@engineering
commits: 9950df7..f706d57 (checks 4-6 on a merge with 20e6afe, tree 032c7b08, identical to dev's check-4 tree)
acceptance_sha256: 3b391c3c9004c78c0de337009837d167bd4dcc348042619406e48baec59650ef
outputs_changed: unverified
---

## Round 1

Approval sha256 matches acceptance.md. My trees: `.claude/worktrees/T-20261016-2146-qa` (f706d57),
`-qa-merge` (f706d57 + 20e6afe merge, `.alto_checkout.yaml` mode sandbox with an empty temp data root),
`-qa-mbase` (20e6afe, same yaml). Logs: `news_server/verify_data/reports/T-20261016-2146-paper-broker/`.
No order placed or cancelled, no credentials read, no production data written.

### Acceptance check results
Command (qa-merge): `python -m pytest -q -p no:cacheprovider backend/executor/paper backend/executor/broker_factory backend/executor/tests/test_credentials.py backend/api/routes/tests/test_broker_switch.py backend/config/tests` -> `69 passed` (qa_accept_merge.log).
1. Interface: test_interface.py passes; AST scan covers manager, reconcile, ledger_sync and the modules they hand the client to. PASS.
2. Fill model: 6 tests pass (yesterday/today data, sell, off-lot refused, FC11 rejection, look-ahead). PASS (off-lot refused vs rounded is an open owner decision).
3. Book: 2 tests pass, hand-calculated. PASS.
4. Live refusal: 4 gate tests pass on the merged tree. On the branch alone the test cannot be collected (no backend.config.checkout). PASS on the merge, as the check allows.
5. End to end: the test passes, but only because it patches the real paths a paper user hits (finding B1). **FAIL.**
6. Suite: see Suite. PASS.

### Findings (all confirmed by the verifier; scripts in reports/.../verifier/)
- **BLOCK B1: check 5 passes only with mocks that hide a real-path failure.** `backend/executor/paper/tests/test_end_to_end.py:44-45` patches `manager.previous_close` and `manager.average_daily_volume`. In the real code, `backend/execution/market_analysis/adv.py:48/81` builds `DhanPriceStore`, which raises `RuntimeError DhanPriceStore requires BROKER=dhan. Current: paper` (`backend/price_feed/dhan_price_store.py:50-51`). `manager.py:479` calls previous_close for every signal order before it is placed, so a real paper user's EMS tick raises and nothing fills. The task's goal is to run the EMS end to end without Dhan, and that does not hold. Reproduced in `f3_real_prevclose.py`. Dev's handoff says this path "would make Dhan calls". It does not: it raises. The test also patches `service.create_broker_client` (line 96), so the factory and gate are never on the e2e path, and it patches the real `load_lot_sizes`/`_lot_sizes_for`, which are untested for paper.
- **ALERT A1: merge order.** `backend/executor/broker_factory/gate.py:20` imports `CHECKOUT` from `backend.config.paths`. On main plus this branch alone, `create_broker_client` raises ImportError for a dhan user before credentials are read, so live ExecutionService and RebalanceService cannot build Dhan. This fails closed and is the stated dependency, but ship must land 20e6afe first. Nothing else on main breaks live Dhan construction.
- **ALERT A2: lost update in the paper account.** `backend/executor/paper/state.py:72-90` does load/save with no lock, and `PaperBroker._settled` (`broker.py:268-279`) saves on the read paths (holdings, funds, order_status). With two brokers on one user (API refresh plus EMS tick), an order B placed is overwritten by A's stale settle. Repro `test_f2_race.py`: on-disk ids `['PAPER-1']`, then `KeyError 'No paper order PAPER-2'`. Order ids `PAPER-{len+1}` (`broker.py:134`) are then reused.

### Observations (outside the task, as asked)
- In a sandbox, DhanClient is built outside the factory with no checkout gate: `price_feed/feed.py:43` (reads Dhan credentials regardless of the active broker), `executor/dhan_client_cli.py:23`, and `api/routes/dhan_auth.py:259`. All are read-only; none places orders. `price_feed/prices.py` (~365) and `dhan_price_store.py:48` refuse non-dhan users. refresh_price_cache found no loop over all users, so it does not pick paper users. Order placement exists only in the EMS (`manager.py:619,803`) on the gated broker.
- `broker_factory/build.py` `_paper_broker` calls `DhanInstrumentMapper.lot_map()/tick_map()`. Without today's cache this downloads the public instrument master (`dhan_instruments.py:164,246,318`), which is a network call in a sandbox.
- The fill model fills an order placed at 11:00 at the same day's 09:15 open. This is the owner's model, so I note it and do not count it as a failure.

### Suite
Full suite from backend/ on qa-merge vs qa-mbase (both against the temp sandbox root). New failures: only `api/services/tests/test_partitioned_storage.py`. It passes alone on both trees; the failure comes from both suites sharing one sqlite temp root in my parallel run. So: no new failures. `stores/tests/test_boundaries.py` passes on both. Commits carry no attribution lines and no relative imports.

### Dev claims not confirmed
- The handoff says adv.py "would make Dhan calls". In fact it raises for paper users (B1).
- I did not re-run the entry-point imports or the branch-alone vs main suite comparison; main-alone collection fails as stated.

### Risks / automatic check
An invariant test that runs the e2e with only the clock patched (real adv, lot lookup and factory over a seeded sandbox) would catch B1. A concurrency test on PaperAccountStore would catch A2.
