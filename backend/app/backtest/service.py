from __future__ import annotations

import pandas as pd


def run_backtest(df: pd.DataFrame, long_threshold: float, short_threshold: float, initial_cash: float, fee_bps: float) -> dict:
    cash = initial_cash
    equity = []
    position = 0
    entry_price = 0.0
    wins = 0
    trades = 0

    for _, row in df.iterrows():
        score = row["composite_score"]
        price = row["close"]

        if position == 0 and score > long_threshold:
            position = 1
            entry_price = price
            cash -= cash * fee_bps / 10000
            trades += 1
        elif position == 1 and score < short_threshold:
            ret = (price - entry_price) / entry_price
            if ret > 0:
                wins += 1
            cash *= 1 + ret
            cash -= cash * fee_bps / 10000
            position = 0

        equity.append(cash if position == 0 else cash * (price / max(entry_price, 1e-9)))

    series = pd.Series(equity)
    rets = series.pct_change().dropna()
    max_dd = float(((series.cummax() - series) / series.cummax().replace(0, 1e-9)).max()) if not series.empty else 0.0
    sharpe = float((rets.mean() / (rets.std() + 1e-9)) * (252**0.5)) if not rets.empty else 0.0
    return {
        "win_rate": wins / max(trades, 1),
        "max_drawdown": max_dd,
        "sharpe_like": sharpe,
        "avg_return": float(rets.mean()) if not rets.empty else 0.0,
        "trade_count": trades,
        "equity_curve": equity,
    }
