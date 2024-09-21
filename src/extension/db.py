from __future__ import annotations

from sqlalchemy import QueuePool
from sqlmodel import create_engine

from src.setting import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_size=100,
    max_overflow=100,
    pool_recycle=3600,
    pool_reset_on_return="rollback",
    pool_timeout=30,
)
