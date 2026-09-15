"""Reset and seed the isolated simulated database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))

from app.core.config import get_settings
from app.db.session import get_session
from app.simulation.seed import migrate, reset_and_seed


def main() -> None:
    settings = get_settings()
    migrate(settings.database_url)
    with get_session(settings.database_url)() as session:
        reset_and_seed(session, settings)
    print("demo database reset and seeded")


if __name__ == "__main__":
    main()
