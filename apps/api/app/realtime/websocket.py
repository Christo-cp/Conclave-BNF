import asyncio
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.config import get_settings
from app.db.session import get_session
from app.realtime.auth import can_subscribe, websocket_user
from app.realtime.broker import broker

router = APIRouter(tags=["realtime"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Annotated[str | None, Query()] = None) -> None:
    settings = get_settings()
    session = get_session(settings.database_url)()
    user = websocket_user(session, settings, token)
    if user is None:
        await websocket.close(code=4401)
        session.close()
        return
    await websocket.accept()
    subscription = None
    try:
        while True:
            if subscription is None:
                message = await websocket.receive_json()
                if message.get("action") != "subscribe":
                    await websocket.send_json({"error": "Subscribe before sending commands."})
                    continue
                channels = {str(channel) for channel in message.get("channels", [])}
                if not channels:
                    await websocket.close(code=4400)
                    return
                if not all(can_subscribe(user, channel) for channel in channels):
                    await websocket.close(code=4403)
                    return
                subscription = broker.subscribe(channels)
                await websocket.send_json({"event": "connected", "channels": sorted(channels)})
                continue
            receive_task = asyncio.create_task(websocket.receive_json())
            event_task = asyncio.create_task(subscription.queue.get())
            done, pending = await asyncio.wait({receive_task, event_task}, timeout=30, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            if not done:
                await websocket.send_json({"event": "heartbeat", "timestamp": datetime.now(UTC).isoformat()})
                continue
            result = done.pop().result()
            if isinstance(result, dict):
                if result.get("action") != "subscribe":
                    await websocket.send_json({"error": "Only subscribe is supported."})
                    continue
                channels = {str(channel) for channel in result.get("channels", [])}
                if not channels or not all(can_subscribe(user, channel) for channel in channels):
                    await websocket.close(code=4403)
                    return
                broker.unsubscribe(subscription)
                subscription = broker.subscribe(channels)
                await websocket.send_json({"event": "connected", "channels": sorted(channels)})
            else:
                await websocket.send_json(result.as_dict())
    except WebSocketDisconnect:
        return
    finally:
        if subscription:
            broker.unsubscribe(subscription)
        session.close()
