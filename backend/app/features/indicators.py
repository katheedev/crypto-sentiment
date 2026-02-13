from __future__ import annotations

import pandas as pd


def compute_indicators(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    out = df.copy()
    close = out["close"]
    high = out["high"]
    low = out["low"]
    volume = out["volume"]

    rsi_period = int(params["rsi_period"])
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(rsi_period).mean()
    loss = -delta.clip(upper=0).rolling(rsi_period).mean()
    rs = gain / loss.replace(0, 1e-9)
    out["rsi"] = 100 - (100 / (1 + rs))

    ema_fast = int(params["ema_fast"])
    ema_slow = int(params["ema_slow"])
    out["ema_fast"] = close.ewm(span=ema_fast, adjust=False).mean()
    out["ema_slow"] = close.ewm(span=ema_slow, adjust=False).mean()
    out["macd"] = out["ema_fast"] - out["ema_slow"]
    out["macd_signal"] = out["macd"].ewm(span=int(params["macd_signal"]), adjust=False).mean()

    atr_period = int(params["atr_period"])
    tr = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    out["atr"] = tr.rolling(atr_period).mean()

    out["volatility"] = close.pct_change().rolling(int(params["volatility_window"])).std()
    out["volume_change"] = volume.pct_change(int(params["volume_change_window"])).fillna(0)
    out["returns"] = close.pct_change().fillna(0)
    return out.fillna(0)
