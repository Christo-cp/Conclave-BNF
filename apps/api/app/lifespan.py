import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.db.session import get_session
from app.sweeper import expire_holds

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: object) -> AsyncIterator[None]:
    settings = get_settings()
    stop = asyncio.Event()

    async def sweep() -> None:
        while not stop.is_set():
            try:
                with get_session(settings.database_url)() as session:
                    expire_holds(session)
            except Exception:
                # A failed sweep must not terminate the API process, but it must
                # remain visible to operators for diagnosis.
                logger.exception("reservation hold sweep failed")
            try:
                await asyncio.wait_for(stop.wait(), timeout=settings.sweeper_interval_s)
            except TimeoutError:
                continue

    task = asyncio.create_task(sweep())
    try:
        yield
    finally:
        stop.set()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
