# app/api/v1/ws/notifications_ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
from jose import jwt, JWTError
from app.core.config import settings
from app.models.user import User
from app.db.session import SessionLocal
import json
import redis.asyncio as aioredis
import asyncio

router = APIRouter(tags=["WebSocket - Notifications"])

# ------------------ AUTH ------------------
def get_current_user_ws(token: str) -> User | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None

    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    return user

# ------------------ CONNECTIONS ------------------
connections: Dict[str, List[WebSocket]] = {}

async def add_connection(user_id: str, websocket: WebSocket):
    connections.setdefault(user_id, []).append(websocket)

def remove_connection(user_id: str, websocket: WebSocket):
    if user_id in connections and websocket in connections[user_id]:
        connections[user_id].remove(websocket)
        if not connections[user_id]:
            del connections[user_id]

async def send_to_user(user_id: str, message: dict):
    """ارسال پیام به همه WebSocketهای کاربر"""
    if user_id in connections:
        dead_sockets = []
        for ws in connections[user_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead_sockets.append(ws)
        for ws in dead_sockets:
            remove_connection(user_id, ws)

# ------------------ REDIS LISTENER ------------------
stop_event = asyncio.Event()

async def redis_listener():
    redis = await aioredis.from_url(settings.REDIS_URL)
    pubsub = redis.pubsub()
    await pubsub.subscribe("notifications")
    print("[WS] Redis listener started for in-app notifications")

    try:
        while not stop_event.is_set():
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg is None:
                await asyncio.sleep(0.1)
                continue

            try:
                data = json.loads(msg["data"])
                user_id = str(data.get("user_id"))
                if user_id:
                    await send_to_user(user_id, data)
                    print(f"[WS] Notification sent to {user_id}")
            except Exception as e:
                print("[WS] Redis listener error:", e)
    except asyncio.CancelledError:
        print("[WS] Redis listener cancelled")
    finally:
        await pubsub.unsubscribe("notifications")
        await pubsub.close()
        await redis.close()
        print("[WS] Redis listener closed cleanly")

# اجرای listener در پس‌زمینه به صورت امن
redis_task = asyncio.create_task(redis_listener())

# ------------------ WEBSOCKET ROUTE ------------------
@router.websocket("/database-notifications")
async def notifications_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    user = get_current_user_ws(token)
    if not user:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    await add_connection(str(user.id), websocket)
    print(f"[WS] {user.id} connected")

    try:
        while True:
            await websocket.receive_text()  # فقط برای نگه داشتن اتصال
    except WebSocketDisconnect:
        print(f"[WS] {user.id} disconnected")
        remove_connection(str(user.id), websocket)

# ------------------ CLEANUP ON SHUTDOWN ------------------
import atexit

def cleanup_redis_listener():
    if not redis_task.done():
        stop_event.set()
        redis_task.cancel()

atexit.register(cleanup_redis_listener)
