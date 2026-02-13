# app/api/v1/ws/notifications.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
from jose import jwt, JWTError
from app.core.config import settings
from app.models.user import User
from app.db.session import SessionLocal
import asyncio
import json
import redis.asyncio as aioredis

router = APIRouter()

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
    if user_id not in connections:
        connections[user_id] = []
    connections[user_id].append(websocket)

def remove_connection(user_id: str, websocket: WebSocket):
    if user_id in connections:
        connections[user_id].remove(websocket)
        if not connections[user_id]:
            del connections[user_id]

async def send_to_user(user_id: str, message: dict):
    """ارسال نوتیف به همه WebSocketهای کاربر"""
    if user_id in connections:
        dead = []
        for ws in connections[user_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        # حذف کانکشن‌های قطع‌شده
        for ws in dead:
            remove_connection(user_id, ws)


# ------------------ REDIS LISTENER ------------------
async def redis_listener():
    redis = await aioredis.from_url(settings.REDIS_URL)
    pubsub = redis.pubsub()
    await pubsub.subscribe("notifications")

    print("[WS] Redis listener started for in-app notifications")

    async for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"])
                user_id = str(data.get("user_id"))
                if user_id:
                    await send_to_user(user_id, data)
                    print(f"[WS] Notification sent to {user_id}")
            except Exception as e:
                print("[WS] Redis listener error:", e)


# ------------------ WEBSOCKET ROUTE ------------------
@router.websocket("/notifications")
async def notifications_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")
    print("*1*")

    if not token:
        await websocket.close(code=4001)
        print("*2*")
        return

    user = get_current_user_ws(token)
    print("*3*")
    if not user:
        print("*4*")
        await websocket.close(code=4001)
        return

    await websocket.accept()
    print(f"[WS] {user.id} connected")

    await add_connection(str(user.id), websocket)

    try:
        while True:
            await websocket.receive_text()  # فقط برای نگه داشتن اتصال
    except WebSocketDisconnect:
        print(f"[WS] {user.id} disconnected")
        remove_connection(str(user.id), websocket)
