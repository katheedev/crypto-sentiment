from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

MODEL_DIR = Path("data/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COLUMNS = [
    "returns",
    "rsi",
    "macd",
    "macd_signal",
    "atr",
    "volatility",
    "volume_change",
    "sentiment_signal",
    "composite_score",
]


def model_path(symbol: str, interval: str) -> Path:
    return MODEL_DIR / f"{symbol}_{interval}.joblib"


def train_model(df: pd.DataFrame, symbol: str, interval: str, horizon: int = 1) -> dict:
    data = df.copy()
    data["target"] = (data["close"].shift(-horizon) > data["close"]).astype(int)
    data = data.dropna()
    X = data[FEATURE_COLUMNS]
    y = data["target"]
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X, y)
    joblib.dump(model, model_path(symbol, interval))
    return {"rows": len(data), "features": FEATURE_COLUMNS}


def predict(df: pd.DataFrame, symbol: str, interval: str) -> dict:
    path = model_path(symbol, interval)
    if not path.exists():
        train_model(df, symbol, interval)
    model = joblib.load(path)
    latest = df.iloc[-1:][FEATURE_COLUMNS]
    prob_up = float(model.predict_proba(latest)[0][1])
    direction = "up" if prob_up >= 0.5 else "down"
    importances = {f: float(v) for f, v in zip(FEATURE_COLUMNS, model.feature_importances_)}
    top = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5]
    return {"direction": direction, "confidence": prob_up if direction == "up" else 1 - prob_up, "top_features": top}
