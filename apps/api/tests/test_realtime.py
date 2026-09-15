import asyncio
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Role, User
from app.realtime.auth import can_subscribe
from app.realtime.broker import EventEnvelope, broker, queue_event


def test_rolled_back_write_publishes_nothing():
    broker.clear()
    session = Session(create_engine("sqlite://"))
    queue_event(session, "resource.reserved", uuid4(), 1, {"incident_id": "INC-000001"})
    session.rollback()
    assert broker.published == []
    session.close()


def test_event_envelope_contains_dedupe_fields_and_drops_old_versions():
    broker.clear()
    entity_id = uuid4()
    session = Session(create_engine("sqlite://"))
    envelope = queue_event(session, "mission.state.changed", entity_id, 3, {"mission_id": str(entity_id)})
    session.commit()
    assert {"event_id", "event", "entity_id", "entity_version", "timestamp", "mode", "payload"} <= envelope.as_dict().keys()
    subscription = broker.subscribe({str(entity_id)})
    asyncio.run(subscription.put(envelope))
    asyncio.run(subscription.put(envelope))
    older = EventEnvelope("old", envelope.event, str(entity_id), 2, envelope.timestamp, envelope.mode, envelope.payload)
    asyncio.run(subscription.put(older))
    assert subscription.queue.qsize() == 1
    broker.unsubscribe(subscription)
    session.close()


def test_hospital_subscription_is_scoped_to_own_hospital():
    hospital_id = uuid4()
    role = Role(code="HOSPITAL_STAFF", name="Hospital Staff")
    user = User(hospital_id=hospital_id, status="ACTIVE", roles=[role])
    assert can_subscribe(user, f"hospital:{hospital_id}")
    assert not can_subscribe(user, f"hospital:{uuid4()}")


def test_backend_event_payload_is_metadata_and_consumers_resync_by_entity_id():
    session = Session(create_engine("sqlite://"))
    envelope = queue_event(session, "mission.state.changed", "mission-1", 2, {"mission_id": "mission-1", "status": "ARRIVED"})
    assert envelope.entity_id == "mission-1"
    assert envelope.payload["status"] == "ARRIVED"
    assert "mission" not in envelope.payload
    session.close()
