# /app/api/v1/ws/command_ws.py

from fastapi import APIRouter, WebSocket
from app.api.v1.ws.connections import add_connection, remove_connection

router = APIRouter()

@router.websocket("/commands")
async def command_ws(websocket: WebSocket):
    await websocket.accept()
    add_connection("command", websocket)
    print("[WS] Command WebSocket connected")

    try:
        while True:
            msg_text = await websocket.receive_text()
            # اختیاری: پردازش پیام‌های کلاینت
    except Exception as e:
        print(f"❌ WS error: {e}")
    finally:
        remove_connection("command", websocket)
        print("[WS] Command WebSocket closed")
