---
schema: evidence/v1
task: T-20261016-2146-paper-broker
round: 3
qa: pass
qa_by: qa@engineering
commits: 9013baa..9801fba (my tree .claude/worktrees/T-20261016-2146-qa3, mode sandbox over an empty temp root; baseline -qa3-base at 9013baa, same setup)
acceptance_sha256: f9882844a8ee21b95588a0e3ff035e36c9744d8fd3c1b80d43f23e1ae73d0138
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

## Round 2

The approval sha256 still matches acceptance.md (3b391c3c...). My tree: `.claude/worktrees/T-20261016-2146-qa2`, which is 70c1c1c merged with 20e6afe. Its `.alto_checkout.yaml` is mode sandbox over an empty temp root. The baseline tree is `-qa-mbase` (20e6afe). Logs are in `news_server/verify_data/reports/T-20261016-2146-paper-broker/r2_*.log` and my scratch tests are in `/tmp/qa2_r2/`. I placed or cancelled no orders, read no credentials and wrote no production data.

### Acceptance checks
Command (qa2): `python -m pytest -q -p no:cacheprovider backend/executor/paper backend/executor/broker_factory backend/executor/tests/test_credentials.py backend/api/routes/tests/test_broker_switch.py backend/config/tests` gave `73 passed` (r2_accept.log).
1. Interface: PASS (test unchanged).
2. Fill model: PASS. The owner accepted the fill decisions, so they are not failures.
3. Book: PASS.
4. Live refusal: PASS on the merge.
5. End to end: **FAIL.** The test passes, and the round-1 mocks are gone. It now runs the real factory and gate, real previous_close/ADV over the stored prices, and the real lot lookup from a seeded instrument-master cache. It passes only because `test_end_to_end.py:126` replaces `RebalanceService._build_planner_inputs`, which `submit_decision` calls on every approval. Check 5 says the proposal goes "through `RebalanceService.submit_decision`". The real one fails for a paper user (B2). The rule I applied is the same as for B1: the test passes only with a mock over a path a real paper user hits. Replacing `plan_orders` alone, which is a pure function of its inputs, would have been acceptable as "the proposal is given".
6. Suite: PASS (see Suite below).

### B1 and A2, re-verified
- **B1 is fixed.** `adv.py:48,81` now go through `broker_factory/prices.py:create_daily_price_store`. I tested the live path in `/tmp/qa2_r2/test_live.py`: with mode live and a dhan user, DhanPriceStore is called with exactly `("u", ["X"], [], "2024-01-01", today)`, the same call as at base. A paper user in live mode raises. The e2e test builds the broker with the real `create_broker_client`.
- **A2 is fixed.** I wrote my own cross-process test, `/tmp/qa2_r2/test_mp_race.py`: 3 forked processes place 90 orders and read holdings and funds while they do. All 90 ids are unique and stored, and `orders_issued` is 90. After that, holdings, funds, positions and order_status leave account.json byte-identical. The lock is a real flock (`stores/locking.py:22`) and the write is atomic.

### Findings (the verifier confirmed this one)
- **BLOCK B2: a paper user who holds anything cannot approve a proposal, and probably cannot build one.** Path: `backend/api/services/rebalance_service.py:937` (submit_decision calls `_build_planner_inputs` on every approval), then `:255` (`_trading_calendar(holdings)`), then `:431` (`DhanPriceStore(...)`), then `price_feed/dhan_price_store.py:~50`, which raises `RuntimeError: DhanPriceStore requires BROKER=dhan. Current: paper`. After the first paper fill, holdings are non-empty, so every later approval raises. Repro: with the e2e `_seed_sandbox`, `RebalanceService(USER)._trading_calendar({"ACME": None})` raises, and `({})` returns []. The verifier reproduced this independently. The e2e test hides it: its patched inputs have empty holdings and an empty `trading_calendar`. Dropping only that patch also fails, earlier, on `KeyError: 'stance'` from the seeded desired.json. So the real approval path for a paper user is untested beyond that point. This is the same class as B1, in RebalanceService instead of the EMS.
- **ALERT A1 (merge order)** still stands for ship. The daily price store now also imports the gate, so main alone would fail every broker build and every previous_close/ADV call.
- **ALERT:** account.json now requires `orders_issued` with no default. Round-1 sandbox accounts must be reopened. This fails closed, so it is acceptable.

### Suite
I ran the dev-skill command (PYTHONPATH=.., dummy env, from backend/) on qa2 and on qa-mbase:
- head: 83 failed, 1551 passed, 8 errors
- base: 83 failed, 1531 passed, 8 errors
- `comm -23` is empty, so there are no new failures.
- `stores/tests/test_boundaries.py`: 2 passed.

### Dev claims compared after the verdict
Dev's handoff itself says the planner mock remains and that the task is "not done" if QA reads check 5 strictly. I confirm that. Dev frames the mock as "planning is the release runner's job". But the method the test replaces is also the approval path inside submit_decision, and it raises for any paper user who holds a position. I did not re-run the entry-point imports; I relied on dev's list. The rest matches what I found.

### Automatic check that would catch this class
A test that a paper user's `RebalanceService._build_planner_inputs` runs over a seeded sandbox that holds one name. More generally: grep for `DhanPriceStore(` outside `broker_factory/` in code reachable from rebalance_service and the EMS. trading_loop_service.py:147, strategy_service.py:362 and price_chart_service.py:117 are other places a paper user would hit; I did not run them.

## Round 3

The approval sha256 (f9882844..., Amendment v2 included) matches acceptance.md. Range 9013baa..9801fba, rebased onto main, which now carries checkout-data-root, so I used no merged tree. My tree is `.claude/worktrees/T-20261016-2146-qa3` with `.alto_checkout.yaml` set to mode sandbox over an empty `/tmp/qa3root.*`. The baseline is `-qa3-base` (9013baa) over its own empty temp root. Logs are in `news_server/verify_data/reports/T-20261016-2146-paper-broker/r3_*.log` and my scratch tests are in `/tmp/qa3_r3/`. I placed or cancelled no orders, read no credentials and wrote no production data.

### Acceptance checks
Command: `pytest -q -p no:cacheprovider backend/executor/paper backend/executor/broker_factory backend/executor/tests/test_credentials.py backend/api/routes/tests/test_broker_switch.py backend/config/tests backend/api/services/tests/test_trading_loop_service.py` gave **95 passed** (r3_accept.log).
1. Interface: PASS.
2. Fill model: PASS. The owner's fill decisions are accepted, so they are not failures.
3. Book: PASS.
4. Live refusal: PASS, now on the branch itself.
5. End to end: PASS. It runs the real factory, gate, lot lookup, previous_close/ADV, EMS and reconciler, with sockets blocked.
5a. Planner inputs: PASS. `rebalance_service._trading_calendar`, `strategy_service._trading_calendar` and `trading_loop_service:147` all call `create_daily_price_store`. No `DhanPriceStore(` construction is left in those modules. My own test (`/tmp/qa3_r3/test_dhan_args.py`) shows that in a live checkout a dhan user gets exactly `DhanPriceStore("u", ["B","A"], [], start, end)`, the same as the base call shape, with symbol order kept. In live mode a paper user raises, and in a sandbox a dhan user raises.
5b. Two approvals: PASS. The test replaces only `plan_orders`, which 5b allows. The real `submit_decision` runs `_build_planner_inputs`. On the second approval the planner gets holdings `{ACME: 60}` (entry 2026-10-05) and the stored trading calendar `[10-01, 10-05, 10-07]`. That is the B2 path, and it raised in round 2. Both orders fill. The ledger, current.json and cash match the hand calculation in the test.

### Judgement on 5b's limits
- **Path-constant patches** (`STANCES_DIR`, `PRICE_WATCHLIST_PATH`, `CUSTOM_WATCHLIST_PATH`, `MAPPING_PATH`, `LEGACY_CHAIN_STARTS_PATH`, `read_calendar.__defaults__`): I count these as seeding stores, not hiding a path. Every one of them is derived from `backend.config.paths` (repository.py:22, union/store.py:11, custom_picks.py:12, company_resolver.py:9-12 via METADATA_ROOT, chain_start/store.py:12, calendar_source.py:10,30). In a real sandbox they resolve from the checkout's data_root. The test only re-binds what was bound at import, before it could set the checkout. No code under test is replaced.
- **Completeness gate over Not-initiated companies:** this is a real limit, but acceptable. The gate code runs for real; only its "initiated" branch is not exercised for paper users. That branch reads no prices and has no broker dependency, so this is not the B1/B2 class. ALERT, for a later release-runner fixture: seed one stance log and index so the gate takes its full path.

### Findings
No BLOCK or ALERT findings on the diff. With none to disprove, I did not run a verifier.

### Observations (not failures)
- `backend/api/services/price_chart_service.py:117` builds `DhanPriceStore("default", ...)` directly. A chart route for a paper sandbox would raise. It is not on the approval path.
- `backend/trading/scripts/rebuild_price_refs.py:39` (handoff says :22) is a maintenance script on DhanPriceStore.
- `backend/trading/harness.py:237`: `_resolve_price` builds DhanPriceStore when no `price_store` is passed. All three callers (harness.py:211,270,434) pass one through. This is a latent paper-user trap if a caller ever omits it.

### Suite
Dev-skill command from backend/, each tree over its own temp root:
- head: 100 failed / 1580 passed / 8 errors
- base: 100 failed / 1553 passed / 8 errors
- `comm -23` is empty (108 lines each), so there are no new failures.
- `stores/tests/test_boundaries.py`: 2 passed.
- No attribution lines and no relative imports in the commits.

### Dev claims compared after the verdict
The handoff matches what I found: the call sites, the 5b patches, the suite counts and the observations. I did not re-run dev's fail-before revert or the entry-point import list. The handoff gives rebuild_price_refs at :22; the construction is at :39.

### Automatic check for this class
A test that fails on any `DhanPriceStore(` construction outside `broker_factory/` in modules reachable from rebalance_service, trading_loop_service, strategy_service and the EMS.
