"""Database engines, one per URL."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine


@lru_cache
def get_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)
