from __future__ import annotations

import json
from typing import Any

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.deps import require_admin
from app.auth.jwt import create_access_token
from app.backtest.service import run_backtest
from app.cache.store import cache
from app.config.settings import EnvSettings, deep_merge, env_overrides, load_default_config
from app.db.models import BacktestRecord, ConfigOverride, Run
from app.db.session import get_db, init_db
from app.features.indicators import compute_indicators
from app.models.service import predict, train_model
from app.providers.market.binance import BinanceMarketDataProvider
from app.providers.social.reddit import RedditProvider
from app.providers.social.twitter import TwitterProvider
from app.sentiment.service import aggregate_sentiment, generate_keywords, score_posts

settings = EnvSettings()
default_cfg = load_default_config().model_dump()

app = FastAPI(title="sentiment-crypto-lab")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup() -> None:
    init_db()


def load_runtime_config(db: Session) -> dict[str, Any]:
    cfg = deep_merge(default_cfg, env_overrides())
    rows = db.query(ConfigOverride).all()
    db_overrides: dict[str, Any] = {}
    for row in rows:
        db_overrides[row.key] = json.loads(row.value)
    return deep_merge(cfg, db_overrides)


def interval_to_minutes(interval: str) -> int:
    mapping = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
    if interval not in mapping:
        raise HTTPException(400, "Unsupported interval")
    return mapping[interval]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/token")
async def login(form_data: dict[str, str]) -> dict[str, str]:
    if form_data.get("username") == settings.admin_username and form_data.get("password") == settings.admin_password:
        return {"access_token": create_access_token(settings.admin_username), "token_type": "bearer"}
    raise HTTPException(401, "Bad credentials")


@app.get("/symbols")
async def symbols(query: str = "", db: Session = Depends(get_db)) -> list[str]:
    cfg = load_runtime_config(db)
    provider = BinanceMarketDataProvider(cfg["market"]["base_url"], cfg["market"]["request_timeout_seconds"])
    cache_key = f"symbols:{query}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    found = await provider.search_symbols(query)
    cache.set(cache_key, found, cfg["app"]["cache_ttl_seconds"])
    return found


def compose_analysis(symbol: str, interval: str, limit: int, cfg: dict[str, Any]):
    provider = BinanceMarketDataProvider(cfg["market"]["base_url"], cfg["market"]["request_timeout_seconds"])
    return provider


@app.get("/analyze")
async def analyze(symbol: str, interval: str, limit: int = Query(default=200, le=1000), db: Session = Depends(get_db)) -> dict[str, Any]:
    cfg = load_runtime_config(db)
    provider = BinanceMarketDataProvider(cfg["market"]["base_url"], cfg["market"]["request_timeout_seconds"])
    candles = await provider.get_ohlcv(symbol, interval, min(limit, cfg["app"]["max_candle_limit"]))
    df = compute_indicators(pd.DataFrame(candles), cfg["indicators"])

    keywords = generate_keywords(symbol, cfg["social"]["keyword_rules"])
    tw = TwitterProvider(settings.twitter_bearer_token)
    rd = RedditProvider(settings.reddit_client_id, settings.reddit_client_secret, settings.reddit_user_agent)
    posts = await tw.fetch_posts(keywords, cfg["social"]["lookback_posts"])
    posts += await rd.fetch_posts(keywords, cfg["social"]["lookback_posts"])
    scored = score_posts(posts)
    sentiment_buckets = aggregate_sentiment(scored, interval_to_minutes(interval)) if scored else []
    sentiment_signal = sum(x["sentiment"] for x in sentiment_buckets) / max(len(sentiment_buckets), 1)

    price_signal = float(df["returns"].tail(5).mean())
    tech_signal = float((df["macd"].iloc[-1] - df["macd_signal"].iloc[-1]) / max(abs(df["close"].iloc[-1]), 1e-9))
    composite = (
        cfg["weights"]["price"] * price_signal
        + cfg["weights"]["technical"] * tech_signal
        + cfg["weights"]["sentiment"] * sentiment_signal
    )
    df["sentiment_signal"] = sentiment_signal
    df["composite_score"] = composite

    run = Run(symbol=symbol, interval=interval, summary_json=json.dumps({"composite": composite, "sentiment_posts": len(posts)}))
    db.add(run)
    db.commit()

    return {
        "symbol": symbol,
        "interval": interval,
        "candles": candles,
        "indicators": df.tail(200).to_dict(orient="records"),
        "sentiment_timeline": sentiment_buckets,
        "signals": {
            "price": price_signal,
            "technical": tech_signal,
            "sentiment": sentiment_signal,
            "composite": composite,
        },
    }


@app.get("/predict")
async def prediction(symbol: str, interval: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    analysis = await analyze(symbol=symbol, interval=interval, db=db)
    df = pd.DataFrame(analysis["indicators"])
    result = predict(df, symbol, interval)
    return {"symbol": symbol, "interval": interval, **result}


class TrainRequest(BaseModel):
    symbol: str
    interval: str
    limit: int = 500


@app.post("/train")
async def train(req: TrainRequest, _: str = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    analysis = await analyze(symbol=req.symbol, interval=req.interval, limit=req.limit, db=db)
    df = pd.DataFrame(analysis["indicators"])
    cfg = load_runtime_config(db)
    trained = train_model(df, req.symbol, req.interval, horizon=cfg["model"]["target_horizon"])
    return {"status": "trained", **trained}


class BacktestRequest(BaseModel):
    symbol: str
    interval: str
    limit: int = 300


@app.post("/backtest")
async def backtest(req: BacktestRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    analysis = await analyze(symbol=req.symbol, interval=req.interval, limit=req.limit, db=db)
    cfg = load_runtime_config(db)
    df = pd.DataFrame(analysis["indicators"])
    metrics = run_backtest(
        df,
        cfg["backtest"]["long_threshold"],
        cfg["backtest"]["short_threshold"],
        cfg["backtest"]["initial_cash"],
        cfg["backtest"]["fee_bps"],
    )
    record = BacktestRecord(params_json=req.model_dump_json(), metrics_json=json.dumps(metrics))
    db.add(record)
    db.commit()
    return metrics


@app.get("/config")
async def get_config(_: str = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, Any]:
    return load_runtime_config(db)


@app.put("/config")
async def put_config(payload: dict[str, Any], _: str = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, str]:
    for key, value in payload.items():
        row = db.get(ConfigOverride, key)
        if row:
            row.value = json.dumps(value)
        else:
            db.add(ConfigOverride(key=key, value=json.dumps(value)))
    db.commit()
    return {"status": "updated"}


@app.post("/config/reset")
async def reset_config(_: str = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, str]:
    db.query(ConfigOverride).delete()
    db.commit()
    return {"status": "reset"}
