"""Create smart_ambulance_{dev,test,demo} with postgis and pgcrypto.

Plan S0; db:4142-4150, db:5415-5427. Connects with DATABASE_URL's credentials to the
server's `postgres` maintenance database and skips anything that already exists.
Prints database names only, never connection details.
"""

import psycopg
from app.core.config import get_settings
from psycopg import sql
from sqlalchemy.engine import make_url

DATABASES = ("smart_ambulance_dev", "smart_ambulance_test", "smart_ambulance_demo")
EXTENSIONS = ("postgis", "pgcrypto")
MAINTENANCE_DATABASE = "postgres"


def connect(database: str) -> psycopg.Connection:
    url = make_url(get_settings().database_url)
    return psycopg.connect(
        host=url.host,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname=database,
        autocommit=True,
    )


def main() -> None:
    with connect(MAINTENANCE_DATABASE) as conn:
        for name in DATABASES:
            row = conn.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (name,)
            ).fetchone()
            if row:
                print(f"{name}: exists")
            else:
                conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
                print(f"{name}: created")

    for name in DATABASES:
        with connect(name) as conn:
            for extension in EXTENSIONS:
                conn.execute(
                    sql.SQL("CREATE EXTENSION IF NOT EXISTS {}").format(
                        sql.Identifier(extension)
                    )
                )
        print(f"{name}: extensions {', '.join(EXTENSIONS)} present")


if __name__ == "__main__":
    main()
