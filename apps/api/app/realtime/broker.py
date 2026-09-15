from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlalchemy.orm import Session


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event_id: str
    event: str
    entity_id: str
    entity_version: int
    timestamp: str
    mode: str
    payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class EventSubscription:
    def __init__(self, channels: set[str]) -> None:
        self.channels = channels
        self.queue: asyncio.Queue[EventEnvelope] = asyncio.Queue()
        self._event_ids: set[str] = set()
        self._versions: dict[str, int] = {}

    def accepts(self, envelope: EventEnvelope) -> bool:
        if envelope.event_id in self._event_ids:
            return False
        if envelope.entity_version < self._versions.get(envelope.entity_id, -1):
            return False
        related = {
            envelope.entity_id,
            envelope.payload.get("mission_id"),
            envelope.payload.get("incident_id"),
            envelope.payload.get("hospital_id"),
            envelope.payload.get("ambulance_id"),
        }
        return not self.channels or bool(self.channels.intersection(related))

    async def put(self, envelope: EventEnvelope) -> None:
        if self.accepts(envelope):
            self._event_ids.add(envelope.event_id)
            self._versions[envelope.entity_id] = envelope.entity_version
            await self.queue.put(envelope)


class EventBroker:
    def __init__(self) -> None:
        self._subscriptions: set[EventSubscription] = set()
        self.published: list[EventEnvelope] = []
        self._loops: set[asyncio.AbstractEventLoop] = set()

    def subscribe(self, channels: set[str]) -> EventSubscription:
        subscription = EventSubscription(channels)
        self._subscriptions.add(subscription)
        try:
            self._loops.add(asyncio.get_running_loop())
        except RuntimeError:
            pass
        return subscription

    def unsubscribe(self, subscription: EventSubscription) -> None:
        self._subscriptions.discard(subscription)

    def publish_after_commit(self, envelope: EventEnvelope) -> None:
        for loop in tuple(self._loops):
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(self.publish(envelope), loop)
                return
        self.published.append(envelope)

    async def publish(self, envelope: EventEnvelope) -> None:
        self.published.append(envelope)
        await asyncio.gather(*(subscription.put(envelope) for subscription in tuple(self._subscriptions)))

    def clear(self) -> None:
        self.published.clear()


broker = EventBroker()
_LISTENERS_INSTALLED = False


def install_session_listeners() -> None:
    global _LISTENERS_INSTALLED
    if _LISTENERS_INSTALLED:
        return

    @event.listens_for(Session, "after_commit")
    def publish_after_commit(session: Session) -> None:
        pending = session.info.pop("realtime_events", [])
        if not pending:
            return
        for envelope in pending:
            broker.publish_after_commit(envelope)

    @event.listens_for(Session, "after_rollback")
    def discard_after_rollback(session: Session) -> None:
        session.info.pop("realtime_events", None)

    _LISTENERS_INSTALLED = True


def queue_event(
    session: Session,
    event_name: str,
    entity_id: UUID | str,
    entity_version: int = 1,
    payload: dict[str, Any] | None = None,
    mode: str = "SIMULATED",
) -> EventEnvelope:
    install_session_listeners()
    envelope = EventEnvelope(
        event_id=str(uuid4()),
        event=event_name,
        entity_id=str(entity_id),
        entity_version=entity_version,
        timestamp=datetime.now(UTC).isoformat(),
        mode=mode,
        payload=payload or {},
    )
    session.info.setdefault("realtime_events", []).append(envelope)
    return envelope
