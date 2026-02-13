import pandas as pd

from app.features.indicators import compute_indicators


def test_compute_indicators_has_columns():
    df = pd.DataFrame(
        {
            "open": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "high": [2] * 15,
            "low": [1] * 15,
            "close": [1, 2, 3, 2, 4, 5, 5, 6, 7, 8, 9, 8, 9, 10, 11],
            "volume": [100] * 15,
        }
    )
    params = {
        "rsi_period": 14,
        "ema_fast": 12,
        "ema_slow": 26,
        "macd_signal": 9,
        "atr_period": 14,
        "volatility_window": 5,
        "volume_change_window": 2,
    }
    out = compute_indicators(df, params)
    assert "rsi" in out.columns
    assert "macd" in out.columns
