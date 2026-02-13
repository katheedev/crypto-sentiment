from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ConfigOverride(Base):
    __tablename__ = "config_overrides"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class ProviderKey(Base):
    __tablename__ = "provider_keys"

    provider_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    encrypted_key_value: Mapped[str] = mapped_column(Text, nullable=False)


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(30), index=True)
    interval: Mapped[str] = mapped_column(String(10), index=True)
    summary_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class BacktestRecord(Base):
    __tablename__ = "backtests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    params_json: Mapped[str] = mapped_column(Text, nullable=False)
    metrics_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
