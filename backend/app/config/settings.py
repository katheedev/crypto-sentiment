from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeConfig(BaseModel):
    app: dict[str, Any] = Field(default_factory=dict)
    market: dict[str, Any] = Field(default_factory=dict)
    social: dict[str, Any] = Field(default_factory=dict)
    weights: dict[str, float] = Field(default_factory=dict)
    indicators: dict[str, Any] = Field(default_factory=dict)
    model: dict[str, Any] = Field(default_factory=dict)
    backtest: dict[str, Any] = Field(default_factory=dict)
    auth: dict[str, Any] = Field(default_factory=dict)


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SCL_", env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/sentiment_crypto_lab.db"
    redis_url: str | None = None
    jwt_secret: str = "change-me"
    master_key: str = ""
    twitter_bearer_token: str | None = None
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_user_agent: str = "sentiment-crypto-lab"
    admin_username: str = "admin"
    admin_password: str = "admin"


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_default_config(defaults_path: Path | None = None) -> RuntimeConfig:
    path = defaults_path or Path(__file__).with_name("defaults.yml")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return RuntimeConfig.model_validate(data)


def env_overrides() -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    weight_sentiment = os.getenv("SCL_WEIGHT_SENTIMENT")
    if weight_sentiment:
        overrides.setdefault("weights", {})["sentiment"] = float(weight_sentiment)
    default_interval = os.getenv("SCL_DEFAULT_INTERVAL")
    if default_interval:
        overrides.setdefault("market", {})["default_interval"] = default_interval
    return overrides
