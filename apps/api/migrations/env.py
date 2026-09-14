"""Alembic environment.

The database URL comes from `config.attributes["database_url"]` when a caller sets it
(the test fixtures do), otherwise from the application settings.
"""

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import get_settings

config = context.config
target_metadata = None


def database_url() -> str:
    return config.attributes.get("database_url") or get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=database_url(), target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
