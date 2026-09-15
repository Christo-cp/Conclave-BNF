"""Database engines, one per URL."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


@lru_cache
def get_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True, connect_args={"connect_timeout": 5})


def get_session(database_url: str) -> sessionmaker[Session]:
    return sessionmaker(get_engine(database_url), expire_on_commit=False)
