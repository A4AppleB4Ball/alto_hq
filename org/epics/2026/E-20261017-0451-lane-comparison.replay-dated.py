"""Live replay engine — replays the trading system one trading day at a time.

This is the backtest loop that uses:
- Real stance history (from CompanyStore via signal_loader)
- Real daily prices from Dhan (via DhanDailyPriceStore)
- Same decision core as live (compute_target_weights, plan_orders, run_step)

Every trade is a T-close decision: the whole book is derived at T's close from
information public by then, and filled at T+1's open. There are no intraday
price-action trades: they were sized at T's close but filled at an earlier
intraday candle, which is look-ahead. The dip/jump overlay inside
compute_target_weights still applies, as part of the T-close book.

DhanDailyPriceStore is daily-only (no 15-min candles): every signal order
fills at the next trading day's open, no intraday gap handling. The day's
real high/low still back peak/trough tracking. A slippage model applies to
every fill.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
from scipy.optimize import brentq

from backend.backtest.universe import PublishedUniverse
from backend.price_feed.dhan_daily_store import DhanDailyPriceStore
from backend.trading.config import StrategyConfig
from backend.trading.core import compute_target_weights, signal_strength
from backend.trading.lots import load_lot_sizes
from backend.trading.models import SignalState, PositionView, TargetWeightResult, PlannedOrder
from backend.trading.pipeline import run_step
from backend.trading.review import AutoReviewer

logger = logging.getLogger("backtest.replay")

_AUTO_REVIEWER = AutoReviewer()
DATED_FLOWS: dict = {}
TARGET_LOG: dict = {}
SIGNAL_LOG: dict = {}


@dataclass
class Position:
    symbol: str
    shares: float
    avg_cost: float
    entry_date: str
    peak_since_last_buy: float
    trough_since_last_sell: float


@dataclass
class Trade:
    date: str
    timestamp: str
    symbol: str
    action: str
    shares: float
    price: float
    fill_price: float
    notional: float
    cost: float
    slippage: float
    reason: str
    target_weight: float
    fill_source: str


@dataclass
class DailySnapshot:
    date: str
    portfolio_value: float
    cash: float
    num_positions: int
    contribution: float


@dataclass
class ReplayConfig:
    """Configuration for the replay engine on top of StrategyConfig."""
    slippage_bps: float = 5.0
    list_all_trades: bool = False


def _close_as_of(store: DhanDailyPriceStore, symbol: str, as_of: pd.Timestamp,
                 fallback: float) -> float:
    """Last daily close at or before `as_of`.

    `fallback` (the position's average cost) is used only when the symbol has no
    daily series at all, matching the pre-existing behaviour for an unpriceable
    holding. A symbol WITH a series but no bar inside the window is a real data
    gap, so it raises rather than silently marking the position at cost.
    """
    daily = store.series(symbol)
    if daily is None or daily.empty:
        return fallback
    window = daily[daily.index <= as_of]
    if window.empty:
        raise ValueError(
            f"{symbol} has daily prices but none at or before {as_of.date()} — "
            f"cannot value the position as of the window end."
        )
    return float(window["close"].iloc[-1])


def _portfolio_value(positions: dict[str, Position], cash: float, prices: dict[str, float]) -> float:
    equity = sum(
        pos.shares * prices.get(pos.symbol, pos.avg_cost)
        for pos in positions.values()
    )
    return cash + equity


def _build_position_view(pos: Position, price: float, total_value: float) -> PositionView:
    market_value = pos.shares * price
    current_w = market_value / total_value if total_value > 0 else 0.0
    return PositionView(
        symbol=pos.symbol,
        shares=pos.shares,
        avg_cost=pos.avg_cost,
        current_price=price,
        current_weight=current_w,
        peak_since_last_buy=pos.peak_since_last_buy,
        trough_since_last_sell=pos.trough_since_last_sell,
        entry_date=pos.entry_date,
    )


def _apply_fill(
    order: PlannedOrder,
    fill_price: float,
    date: str,
    timestamp: str,
    positions: dict[str, Position],
    cash: float,
    trades: list[Trade],
    slippage_bps: float,
    fill_source: str,
) -> float:
    """Apply a fill at the resolved price with slippage. Returns updated cash."""
    sym = order.symbol

    if order.action == "BUY":
        slipped_price = fill_price * (1 + slippage_bps / 10_000)
    else:
        slipped_price = fill_price * (1 - slippage_bps / 10_000)

    shares = order.shares
    notional = shares * slipped_price
    cost = notional * (order.cost / order.notional) if order.notional > 0 else 0.0
    slippage_cost = abs(slipped_price - fill_price) * shares

    if order.action == "BUY":
        cash -= (notional + cost)
        pos = positions.get(sym)
        if pos is not None:
            total_cost_basis = pos.shares * pos.avg_cost + notional
            pos.shares += shares
            pos.avg_cost = total_cost_basis / pos.shares
            pos.peak_since_last_buy = slipped_price
        else:
            positions[sym] = Position(
                symbol=sym, shares=shares, avg_cost=slipped_price,
                entry_date=date, peak_since_last_buy=slipped_price,
                trough_since_last_sell=slipped_price,
            )
    else:
        cash += (notional - cost)
        pos = positions.get(sym)
        if pos is not None:
            pos.shares -= shares
            pos.trough_since_last_sell = slipped_price
            if pos.shares <= 1e-6 or order.is_full_exit:
                del positions[sym]

    trades.append(Trade(
        date=date,
        timestamp=timestamp,
        symbol=sym,
        action=order.action,
        shares=shares,
        price=order.price,
        fill_price=slipped_price,
        notional=notional,
        cost=cost,
        slippage=slippage_cost,
        reason=order.reason,
        target_weight=order.target_weight,
        fill_source=fill_source,
    ))
    return cash


def _signal_state_from_row(sig_row: pd.Series, signal_date: str) -> Optional[SignalState]:
    """Build a SignalState from one signals-df row, or None if stance is unset."""
    stance = sig_row["d_stance"]
    if stance is None or (isinstance(stance, float) and math.isnan(stance)):
        return None
    prev_stance = sig_row.get("prev_stance")
    if prev_stance is not None and (isinstance(prev_stance, float) and math.isnan(prev_stance)):
        prev_stance = None
    return SignalState(
        stance=str(stance),
        conviction=str(sig_row.get("d_conviction", "MEDIUM")),
        thesis_direction=str(sig_row.get("a_thesis_direction", "FLAT")),
        credibility=str(sig_row.get("a_credibility", "INTACT")),
        discount_to_median=(
            None if pd.isna(sig_row.get("b_discount_to_median_pct"))
            else float(sig_row["b_discount_to_median_pct"])
        ),
        tier=int(sig_row["tier"]),
        signal_date=signal_date,
        prev_stance=str(prev_stance) if prev_stance is not None else None,
        expected_return=(
            None if pd.isna(sig_row.get("d_expected_return_pct"))
            else float(sig_row["d_expected_return_pct"])
        ),
        arm1=(
            None if pd.isna(sig_row.get("d_arm1_pct"))
            else float(sig_row["d_arm1_pct"])
        ),
        arm2=(
            None if pd.isna(sig_row.get("d_arm2_pct"))
            else float(sig_row["d_arm2_pct"])
        ),
    )


def _close_prices(store: DhanDailyPriceStore, symbols, date: str) -> dict[str, float]:
    """Each symbol's close on `date` (symbols with no candles that day are absent)."""
    prices = {}
    for sym in symbols:
        close = store.close_price(sym, date)
        if close is not None:
            prices[sym] = close
    return prices


def _book_targets(
    signal_states: dict[str, SignalState],
    positions: dict[str, Position],
    cash: float,
    prices: dict[str, float],
    today: str,
    cfg: StrategyConfig,
    trading_dates: list[str],
    preference_ranks,
    decided_signal_dates: dict[str, str],
) -> list[TargetWeightResult]:
    """The whole-book target weights at `prices` (via the same function the
    live path calls, harness.py). compute_target_weights iterates
    signals | positions, so every held and every signalled name is visible."""
    total_value = _portfolio_value(positions, cash, prices)
    position_views = {
        sym: _build_position_view(pos, prices[sym], total_value)
        for sym, pos in positions.items()
        if sym in prices
    }
    return compute_target_weights(
        signal_states, position_views, prices, total_value,
        today, cfg, trading_dates, preference_ranks,
        decided_signal_dates=decided_signal_dates,
    )


def _signal_dates(signal_states: dict[str, SignalState]) -> dict[str, str]:
    """Each name's signal_date at a decision, kept with the queued fills so the
    own-change guard compares the next decision with the last one acted on."""
    return {sym: sig.signal_date for sym, sig in signal_states.items()}


def _rankable(
    signal_states: dict[str, SignalState],
    positions: dict[str, Position],
    universe: Optional[PublishedUniverse],
    date: str,
) -> dict[str, SignalState]:
    """Signals the book may rank on `date`: all of them, or the published list's (live ranks list ∪ held)."""
    if universe is None:
        return signal_states
    members = universe.members(date, set(positions))
    return {sym: sig for sym, sig in signal_states.items() if sym in members}


def _overnight_signals(signals: pd.DataFrame, prev_trading_date: str, date: str) -> pd.DataFrame:
    """Signals dated strictly between two consecutive trading days (weekends,
    holidays). Their checkpoint saw data up to its own date, and the next
    chance to act is `date`'s open."""
    as_of = signals["as_of"]
    return signals[(as_of > pd.Timestamp(prev_trading_date)) & (as_of < pd.Timestamp(date))]


def _signal_fill_price(store: DhanDailyPriceStore, order: PlannedOrder, date: str) -> tuple[float, str]:
    """Signal order fill on `date` (the trading day after the decision): the
    day's open. No intraday candles here (DhanDailyPriceStore is daily-only),
    so there is no 9:15/9:30 gap distinction to make — every fill is at the
    day's open. Raises if `date` has no open."""
    open_px = store.open_price(order.symbol, date)
    if open_px is None:
        raise ValueError(f"{order.symbol} {order.action} on {date}: no open price to fill a signal order")
    return open_px, f"{date} open"


def run_replay(
    cfg: StrategyConfig,
    signals: pd.DataFrame,
    store: DhanDailyPriceStore,
    replay_cfg: ReplayConfig = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    verbose: bool = True,
    return_detail: bool = False,
    universe: Optional[PublishedUniverse] = None,
    lot_sizes: Optional[dict[str, int]] = None,
) -> dict:
    """Run a full replay backtest, one trading day at a time.

    For each trading day T:
    1. Fill the book decided at the previous close at T's open (9:30, or 9:15 on a favourable 5% gap)
    2. Ingest T's stance signals and re-derive the whole book at T's close → queue for T+1's open
    3. Update peaks/troughs from T's high/low (after the book, so it sees only data through T-1)
    4. Monthly contribution at month-end

    Returns summary dict with metrics, unless `return_detail=True` — then
    returns `(result, trades, snapshots)` instead, for callers that need the
    trade-by-trade / day-by-day detail (e.g. comparing two arms' trade books
    symbol-by-symbol) rather than just the aggregate metrics. Off by default
    so every existing caller's return type is unchanged.

    `universe` rebuilds the published watchlist per day (backtest/universe.py);
    None ranks every signalled name.

    `lot_sizes` defaults to the real Dhan instrument master (via the
    "backtest" user) for every symbol in `signals` — never 1 across the
    board, since that would hide an SME-board name's real minimum tradeable
    quantity from the replay.
    """
    if replay_cfg is None:
        replay_cfg = ReplayConfig()
    if lot_sizes is None:
        lot_sizes = load_lot_sizes(sorted(signals["symbol"].unique().tolist()), user_id="backtest")

    trading_dates_raw = [d.strftime("%Y-%m-%d") for d in store.trading_days]
    if start is not None and end is not None and start > end:
        raise ValueError(f"--end ({end}) is before --start ({start})")

    trading_dates = [
        d for d in trading_dates_raw
        if (start is None or d >= start) and (end is None or d <= end)
    ]
    if not trading_dates:
        raise ValueError(f"No trading days in [{start or 'first'}, {end or 'today'}]")

    month_ends = _month_end_dates(trading_dates)

    # Preference ranks are set on today's custom picks, which have no history
    # inside the window (backtest/universe.py), so the replay ties break with none.
    preference_ranks: dict[str, int] = {}

    cash = cfg.initial_capital
    positions: dict[str, Position] = {}
    signal_states: dict[str, SignalState] = {}
    decided_signal_dates: dict[str, str] = {}
    trades: list[Trade] = []
    snapshots: list[DailySnapshot] = []

    signals_by_date = signals.groupby(signals["as_of"].dt.strftime("%Y-%m-%d"))

    # (decision date, targets, decision prices): a book decided at a close,
    # filled at the next trading day's open, sized at the decision close.
    pending_signal_fills: list[tuple[str, list[TargetWeightResult], dict[str, float]]] = []

    # Seed signal_states with each symbol's latest signal strictly before the
    # window, keeping its true as_of date so max_signal_age_days staleness
    # checks still see how old it really is. Without this, a symbol whose most
    # recent stance predates `start` has NO SignalState on day one — it can't
    # be sized or bought until some unrelated new signal happens to arrive —
    # even though live would have known about it all along (previous_stance
    # always reads full CompanyStore history, not just what's inside the
    # window; see signal_loader.py's module docstring).
    first_date = trading_dates[0]
    prior = signals[signals["as_of"] < pd.Timestamp(first_date)]
    if not prior.empty:
        latest_prior = prior.sort_values("as_of").groupby("symbol").tail(1)
        for _, sig_row in latest_prior.iterrows():
            signal_date = sig_row["as_of"].strftime("%Y-%m-%d")
            state = _signal_state_from_row(sig_row, signal_date)
            if state is not None:
                signal_states[sig_row["symbol"]] = state

    t_replay_start = time.time()
    logger.info(
        "Replaying %d trading days (%s to %s), %d signals, capital=%s",
        len(trading_dates), trading_dates[0], trading_dates[-1],
        len(signals), f"{cfg.initial_capital:,.0f}",
    )

    for day_index, date in enumerate(trading_dates):
        day_prices = _close_prices(store, set(positions) | set(signal_states), date)
        cash += DATED_FLOWS.get(date, 0.0)

        if (day_index + 1) % 50 == 0:
            elapsed = time.time() - t_replay_start
            pv = _portfolio_value(positions, cash, day_prices)
            logger.info(
                "Day %d/%d (%s) — positions=%d, value=%s, trades=%d — %.1fs elapsed",
                day_index + 1, len(trading_dates), date,
                len(positions), f"{pv:,.0f}", len(trades), elapsed,
            )

        # --- (0) Weekend/holiday checkpoints: decided on their own date from
        # data up to the previous trading close, so the book is re-derived at
        # that close (replacing the one queued there) and filled at today's open.
        if day_index > 0:
            prev_date = trading_dates[day_index - 1]
            overnight = _overnight_signals(signals, prev_date, date)
            if not overnight.empty:
                for _, sig_row in overnight.sort_values("as_of").iterrows():
                    state = _signal_state_from_row(sig_row, sig_row["as_of"].strftime("%Y-%m-%d"))
                    if state is not None:
                        signal_states[sig_row["symbol"]] = state
                prev_prices = _close_prices(store, set(positions) | set(signal_states), prev_date)
                if universe is not None:
                    universe.update_kept(signal_states, prev_prices, date, cfg, preference_ranks)
                overnight_targets = _book_targets(
                    _rankable(signal_states, positions, universe, date), positions, cash, prev_prices, date, cfg,
                    trading_dates, preference_ranks, decided_signal_dates,
                )
                pending_signal_fills = (
                    [(prev_date, overnight_targets, prev_prices, _signal_dates(signal_states))]
                    if overnight_targets else []
                )

        # --- (1) Execute pending signal fills (9:15 if favorable gap, else 9:30) ---
        # Sized and approved at the decision close's prices; today's close is
        # not known at today's open.
        if pending_signal_fills:
            for decision_date, fill_targets, decision_prices, decision_signal_dates in pending_signal_fills:
                total_value = _portfolio_value(positions, cash, decision_prices)
                holdings = {}
                for sym, pos in positions.items():
                    price = decision_prices.get(sym, pos.avg_cost)
                    holdings[sym] = _build_position_view(pos, price, total_value)

                _, decision = run_step(
                    targets=fill_targets, holdings=holdings, signals=signal_states,
                    prices=decision_prices, cash=cash, total_value=total_value, cfg=cfg,
                    reviewer=_AUTO_REVIEWER, today=date,
                    trading_calendar=trading_dates, lot_sizes=lot_sizes,
                    allow_rotation=True,
                )

                for order in decision.approved:
                    fill_px, fill_ts = _signal_fill_price(store, order, date)

                    cash = _apply_fill(
                        order, fill_px, date, fill_ts,
                        positions, cash, trades,
                        replay_cfg.slippage_bps, "next_day_open",
                    )

                decided_signal_dates = decision_signal_dates

            pending_signal_fills = []

        # --- (2) Ingest new signals for today → queue for next-day fill ---
        if date in signals_by_date.groups:
            for _, sig_row in signals_by_date.get_group(date).iterrows():
                state = _signal_state_from_row(sig_row, date)
                if state is not None:
                    signal_states[sig_row["symbol"]] = state

        # --- (2b) Re-derive the whole book, every trading day ---
        # Deliberately OUTSIDE the "did a signal arrive today" guard above. The
        # ranked book is a relative comparison, so it changes when any name's
        # standing changes — including when a signal merely ages past
        # max_signal_age_days and leaves the ranking. Gating this on today's
        # signal arrivals would mean a holding could only be evicted, and a
        # top-ranked name only bought, on days some unrelated company published.
        if signal_states:
            # Whole-book pass (_book_targets). Previously this loop built
            # targets ONLY for symbols whose signal was dated today — roughly 3
            # of a ~75-name investable universe — so the backtest could neither
            # buy a top-ranked name it did not already hold nor re-evaluate a
            # holding whose signal had not just been restamped.
            signal_targets = _book_targets(
                _rankable(signal_states, positions, universe, date), positions, cash, day_prices, date, cfg,
                trading_dates, preference_ranks, decided_signal_dates,
            )
            TARGET_LOG[date] = {t.symbol: {"w": t.target_weight, "base": t.base_weight, "rank": t.rank, "reason": t.reason} for t in signal_targets}
            SIGNAL_LOG[date] = {sym: {"stance": st.stance, "conviction": st.conviction, "dir": st.thesis_direction, "signal_date": sd} for sym, st in signal_states.items() for sd in [decided_signal_dates.get(sym)]}
            if universe is not None:
                universe.update_kept(signal_states, day_prices, date, cfg, preference_ranks)

            if signal_targets:
                pending_signal_fills.append(
                    (date, signal_targets, dict(day_prices), _signal_dates(signal_states))
                )
                logger.debug(
                    "%s: queued %d signal targets for next-day fill",
                    date, len(signal_targets),
                )

        # --- (3) Update peaks/troughs from today's high/low ---
        for sym, pos in positions.items():
            candles = store.candles_for_day(sym, date)
            if not candles.empty:
                pos.peak_since_last_buy = max(pos.peak_since_last_buy, float(candles["high"].max()))
                pos.trough_since_last_sell = min(pos.trough_since_last_sell, float(candles["low"].min()))

        # --- (4) Monthly contribution ---
        contribution = DATED_FLOWS.get(date, 0.0)

        # --- (5) EOD snapshot ---
        eod_prices = {}
        for sym in positions:
            close = store.close_price(sym, date)
            if close is not None:
                eod_prices[sym] = close
            elif sym in day_prices:
                eod_prices[sym] = day_prices[sym]
            else:
                eod_prices[sym] = positions[sym].avg_cost

        snapshots.append(DailySnapshot(
            date=date,
            portfolio_value=_portfolio_value(positions, cash, eod_prices),
            cash=cash,
            num_positions=len(positions),
            contribution=contribution,
        ))

    total_replay_time = time.time() - t_replay_start
    logger.info(
        "Replay loop done: %d days in %.1fs (%.1f days/sec), %d trades",
        len(trading_dates), total_replay_time,
        len(trading_dates) / total_replay_time if total_replay_time > 0 else 0,
        len(trades),
    )

    result = _summarize(cfg, replay_cfg, positions, cash, trades, snapshots, store,
                        verbose, as_of=trading_dates[-1])
    if return_detail:
        return result, trades, snapshots
    return result


def _idle_cash_pct(s: DailySnapshot) -> float:
    """Cash the book left uninvested, as % of the book, before the day's contribution.

    A contribution lands after that day's orders are queued, so the raw EOD
    cash on a contribution day counts money that has had no chance to be spent.
    """
    invested_base = s.portfolio_value - s.contribution
    if invested_base <= 0:
        raise ValueError(f"{s.date}: non-positive portfolio value {invested_base}")
    return (s.cash - s.contribution) / invested_base * 100.0


def _month_end_dates(trading_dates: list[str]) -> set:
    ends = set()
    for i, d in enumerate(trading_dates):
        is_last = (i == len(trading_dates) - 1) or (trading_dates[i + 1][:7] != d[:7])
        if is_last:
            ends.add(d)
    return ends


def _xirr(cash_flows: list[tuple[pd.Timestamp, float]]) -> Optional[float]:
    """Annualized money-weighted return (IRR) given dated cash flows.

    Solves for `r` such that sum(cf / (1+r)^(days/365)) == 0. Unlike TWR/CAGR,
    each flow is weighted by both its size and how long it sat in the
    portfolio — this is the metric that answers "what return did my actual
    money earn," as opposed to TWR's "what return would a lump sum have
    earned regardless of contribution timing."
    """
    if len(cash_flows) < 2:
        return None
    t0 = cash_flows[0][0]
    years = [(t - t0).days / 365.0 for t, _ in cash_flows]
    amounts = [amt for _, amt in cash_flows]

    def npv(rate: float) -> float:
        return sum(amt / (1.0 + rate) ** yr for amt, yr in zip(amounts, years))

    try:
        return brentq(npv, -0.9999, 100.0) * 100.0
    except ValueError:
        return None


def _summarize(
    cfg: StrategyConfig,
    replay_cfg: ReplayConfig,
    positions: dict[str, Position],
    cash: float,
    trades: list[Trade],
    snapshots: list[DailySnapshot],
    store: DhanDailyPriceStore,
    verbose: bool,
    as_of: str,
) -> dict:
    """Compute metrics. `as_of` is the LAST DAY OF THE REPLAY WINDOW.

    Required, not optional: the price store's calendar covers everything it
    loaded, which extends past `--end` (299 days loaded for a 234-day window in
    the 2025-07-01..2026-06-11 case). Marking final positions at the store's
    last close therefore valued them months past the window — liquidation came
    out ABOVE the final snapshot it derives from, and the reported CAGR was
    annualising a return the portfolio never earned in that window.
    """
    if not snapshots:
        return {"config": cfg.name, "final_value": cfg.initial_capital}

    values = [s.portfolio_value for s in snapshots]
    contribs = [s.contribution for s in snapshots]
    final_value = values[-1]

    total_contributed = cfg.initial_capital + sum(contribs)
    net_gain = final_value - total_contributed

    daily_rets: list[float] = []
    for i in range(1, len(values)):
        prev = values[i - 1]
        if prev <= 0:
            daily_rets.append(0.0)
            continue
        daily_rets.append((values[i] - contribs[i]) / prev - 1.0)

    rets = pd.Series(daily_rets)
    twr_growth = float((1.0 + rets).prod()) if len(rets) else 1.0
    twr_total = (twr_growth - 1.0) * 100.0

    n_days = len(values)
    cagr = (twr_growth ** (252.0 / n_days) - 1.0) * 100.0 if n_days > 0 else 0.0
    ann_vol = rets.std() * (252 ** 0.5) * 100 if len(rets) > 1 else 0.0
    sharpe = (rets.mean() / rets.std() * (252 ** 0.5)) if len(rets) > 1 and rets.std() > 0 else 0.0

    growth_curve = [1.0] + (1.0 + rets).cumprod().tolist()
    peak, max_dd = growth_curve[0], 0.0
    for g in growth_curve:
        peak = max(peak, g)
        max_dd = min(max_dd, (g - peak) / peak)
    max_dd *= 100.0

    total_cost = sum(t.cost for t in trades)
    total_slippage = sum(t.slippage for t in trades)
    buys = sum(1 for t in trades if t.action == "BUY")
    sells = sum(1 for t in trades if t.action == "SELL")

    signal_trades = [t for t in trades if t.fill_source == "next_day_open"]
    rotation_trades = [t for t in trades if t.reason.startswith("ROTATE->")]

    signal_cost = sum(t.cost for t in signal_trades)
    rotation_cost = sum(t.cost for t in rotation_trades)

    bps = cfg.cost_bps / 10_000.0
    as_of_ts = pd.Timestamp(as_of)
    equity_at_last = 0.0
    position_values: dict[str, float] = {}
    for sym, pos in positions.items():
        val = pos.shares * _close_as_of(store, sym, as_of_ts, pos.avg_cost)
        position_values[sym] = val
        equity_at_last += val
    exit_cost = equity_at_last * bps
    liquidation_value = cash + equity_at_last - exit_cost

    cash_flows = [(pd.Timestamp(snapshots[0].date), -cfg.initial_capital)]
    for s in snapshots:
        if s.contribution != 0:
            cash_flows.append((pd.Timestamp(s.date), -s.contribution))
    cash_flows.append((as_of_ts, liquidation_value))
    mwr_xirr = _xirr(cash_flows)

    bench_return = None
    bidx = store.series(cfg.benchmark_index, is_index=True)
    if bidx is not None and not bidx.empty:
        # Clipped at BOTH ends: the store's window is wider than the replay's, so
        # an unclipped first/last close measured a different period than the
        # strategy return it is printed next to.
        bwin = bidx[bidx.index <= as_of_ts]
        if not bwin.empty:
            bench_return = ((bwin["close"].iloc[-1] - bwin["close"].iloc[0])
                            / bwin["close"].iloc[0] * 100)

    idle_pcts = [_idle_cash_pct(s) for s in snapshots]

    result = {
        "config": cfg.name,
        "final_value": final_value,
        "total_contributed": total_contributed,
        "net_gain": net_gain,
        "twr_pct": twr_total,
        "liquidation_value": liquidation_value,
        "exit_cost": exit_cost,
        "cash": cash,
        "idle_cash": snapshots[-1].cash - snapshots[-1].contribution,
        "idle_cash_pct": idle_pcts[-1],
        "avg_idle_cash_pct": sum(idle_pcts) / len(idle_pcts),
        "cagr_pct": cagr,
        "mwr_xirr_pct": mwr_xirr,
        "max_drawdown_pct": max_dd,
        "ann_vol_pct": ann_vol,
        "sharpe": sharpe,
        "num_trades": len(trades),
        "buys": buys,
        "sells": sells,
        "signal_trades": len(signal_trades),
        "rotation_trades": len(rotation_trades),
        "total_cost": total_cost,
        "signal_cost": signal_cost,
        "rotation_cost": rotation_cost,
        "total_slippage": total_slippage,
        "final_positions": len(positions),
        # The names, not just the count. Composition of the closing book (how much
        # of it is DETERIORATING, REDUCE, etc.) is the question the ranked book
        # exists to answer, and a count cannot answer it. Callers previously had
        # to monkeypatch run_step and read a snapshot one step stale.
        "final_symbols": sorted(positions),
        # Weight, not just membership: whether the book actually spreads across
        # max_positions slots or clusters most of the book into a handful of
        # names sitting at max_weight is exactly what a saturating multiplier
        # (e.g. stance_change_mult) would distort, and final_symbols alone
        # cannot show that.
        "final_weights": {
            sym: (val / final_value * 100.0 if final_value > 0 else 0.0)
            for sym, val in sorted(position_values.items(), key=lambda kv: -kv[1])
        },
        "benchmark_return_pct": bench_return,
        "slippage_bps": replay_cfg.slippage_bps,
    }

    if verbose:
        _print_report(cfg, replay_cfg, positions, cash, trades, snapshots, store, result)

    return result


def _print_report(
    cfg: StrategyConfig,
    replay_cfg: ReplayConfig,
    positions: dict[str, Position],
    cash: float,
    trades: list[Trade],
    snapshots: list[DailySnapshot],
    store: DhanDailyPriceStore,
    r: dict,
):
    print("\n" + "=" * 90)
    print(f"LIVE REPLAY RESULTS — preset '{cfg.name}' (slippage {replay_cfg.slippage_bps} bps)")
    print("=" * 90)

    print("\nMONEY VIEW")
    print(f"  Total Contributed     : {r['total_contributed']:>14,.0f}")
    print(f"  Final Portfolio Value : {r['final_value']:>14,.0f}")
    print(f"  Cash on Hand          : {r['cash']:>14,.0f}")
    print(f"  Idle Cash (ex contrib): {r['idle_cash']:>14,.0f}  ({r['idle_cash_pct']:.2f}% of book)")
    print(f"  Avg Idle Cash         : {r['avg_idle_cash_pct']:>13.2f}%  (reserve {cfg.cash_reserve_pct * 100:.2f}%)")
    print(f"  LIQUIDATION VALUE     : {r['liquidation_value']:>14,.0f}")
    print(f"  Net Gain (vs contrib) : {r['net_gain']:>+14,.0f}")
    xirr_str = f"{r['mwr_xirr_pct']:>12.2f}%" if r["mwr_xirr_pct"] is not None else "         n/a"
    print(f"  MWR (XIRR, annualized): {xirr_str}")

    if r["mwr_xirr_pct"] is not None:
        base = r["liquidation_value"]
        annual_rate = r["mwr_xirr_pct"] / 100
        monthly_rate = (1 + annual_rate) ** (1 / 12) - 1
        contribution = cfg.monthly_contribution
        print(f"\nFORWARD PROJECTION (if XIRR holds, contributing {contribution:,.0f}/month)")
        print(f"  Today's Value         : {base:>14,.0f}")
        for months in (6, 12, 18, 24, 36, 48):
            grown_base = base * (1 + monthly_rate) ** months
            if monthly_rate != 0:
                grown_contrib = contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
            else:
                grown_contrib = contribution * months
            projected = grown_base + grown_contrib
            total_contrib = contribution * months
            print(f"  +{months:>2} months            : {projected:>14,.0f}  ({projected - base - total_contrib:>+14,.0f} gain, "
                  f"{total_contrib:>+13,.0f} contributed)")

    print("\nPERFORMANCE (time-weighted)")
    bench_str = (f"  (benchmark {cfg.benchmark_index}: {r['benchmark_return_pct']:+.2f}%)"
                 if r["benchmark_return_pct"] is not None else "  (benchmark unavailable)")
    print(f"  TWR                   : {r['twr_pct']:>13.2f}%{bench_str}")
    print(f"  CAGR                  : {r['cagr_pct']:>13.2f}%")
    print(f"  Max Drawdown          : {r['max_drawdown_pct']:>13.2f}%")
    print(f"  Annualized Vol        : {r['ann_vol_pct']:>13.2f}%")
    print(f"  Sharpe (rf=0)         : {r['sharpe']:>13.2f}")

    print("\nTRADING ACTIVITY")
    print(f"  Total Trades          : {r['num_trades']:>13}")
    print(f"    Signal fills (open) : {r['signal_trades']:>13}")
    print(f"    of which rotation   : {r['rotation_trades']:>13}")
    print(f"  Buys / Sells          : {r['buys']:>6} / {r['sells']}")
    print(f"  Transaction Costs     : {r['total_cost']:>14,.0f}")
    print(f"    Signal fills        : {r['signal_cost']:>14,.0f}")
    print(f"    of which rotation   : {r['rotation_cost']:>14,.0f}")
    print(f"  Slippage Cost         : {r['total_slippage']:>14,.0f}")
    print(f"  Positions (end)       : {r['final_positions']:>13}")

    print("\n--- Final Weight Distribution ---")
    for sym, wt in r["final_weights"].items():
        print(f"  {sym:<14}{wt:>7.2f}%")

    print("\n--- Monthly Portfolio Value ---")
    monthly: dict[str, DailySnapshot] = {}
    for s in snapshots:
        monthly[s.date[:7]] = s
    prev = cfg.initial_capital
    for month, s in monthly.items():
        gain = (s.portfolio_value - s.contribution) - prev
        mret = gain / prev * 100 if prev > 0 else 0.0
        print(f"  {month}: {s.portfolio_value:>14,.0f} | {mret:>+7.2f}% | pos {s.num_positions:>2} "
              f"| cash {s.cash:>12,.0f} | idle {s.cash - s.contribution:>11,.0f} "
              f"({_idle_cash_pct(s):>5.2f}%) | +{s.contribution:>9,.0f}")
        prev = s.portfolio_value

    print("\n--- Final Positions ---")
    if positions:
        rows = []
        for sym, pos in positions.items():
            daily = store.series(sym)
            if daily is not None and not daily.empty:
                px = float(daily["close"].iloc[-1])
            else:
                px = pos.avg_cost
            rows.append((sym, pos.shares * px, (px - pos.avg_cost) / pos.avg_cost * 100, pos.entry_date))
        rows.sort(key=lambda x: x[1], reverse=True)
        print(f"  {'Symbol':<12}{'Value':>13}{'P&L%':>9}  {'Entry'}")
        for sym, val, pnl, entry in rows:
            print(f"  {sym:<12}{val:>13,.0f}{pnl:>+8.1f}%  {entry}")
    else:
        print("  (none)")

    print("\n--- All Trades ---")
    if not replay_cfg.list_all_trades:
        print(f"  ({len(trades)} trades — pass --list-all-trades to list them)")
    elif trades:
        print(f"  {'Date':<12}{'Time':<20}{'Symbol':<12}{'Action':<6}{'Shares':>8}{'Fill':>10}{'Notional':>12}{'P&L':>10}{'Source':<20}{'Reason'}")
        avg_costs: dict[str, float] = {}
        holdings_qty: dict[str, float] = {}
        for t in trades:
            pnl_str = ""
            if t.action == "BUY":
                prev_qty = holdings_qty.get(t.symbol, 0.0)
                prev_cost = avg_costs.get(t.symbol, 0.0)
                new_qty = prev_qty + t.shares
                if new_qty > 0:
                    avg_costs[t.symbol] = (prev_cost * prev_qty + t.fill_price * t.shares) / new_qty
                holdings_qty[t.symbol] = new_qty
            else:
                avg = avg_costs.get(t.symbol, t.fill_price)
                pnl = (t.fill_price - avg) * t.shares
                pnl_str = f"{pnl:>+10,.0f}"
                prev_qty = holdings_qty.get(t.symbol, 0.0)
                holdings_qty[t.symbol] = max(0.0, prev_qty - t.shares)
                if holdings_qty[t.symbol] <= 1e-6:
                    holdings_qty.pop(t.symbol, None)
                    avg_costs.pop(t.symbol, None)

            print(f"  {t.date:<12}{t.timestamp:<20}{t.symbol:<12}{t.action:<6}"
                  f"{t.shares:>8.0f}{t.fill_price:>10,.2f}{t.notional:>12,.0f}"
                  f"{pnl_str:>10}  {t.fill_source:<20}{t.reason}")
    else:
        print("  (none)")
