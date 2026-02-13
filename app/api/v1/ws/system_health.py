from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from app.core.healthcheck import run_health_checks
import logging

router = APIRouter()
logger = logging.getLogger("app.health")

@router.websocket("/health")
async def websocket_health(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                health_data = await run_health_checks()
                await websocket.send_json(health_data)
            except WebSocketDisconnect:
                # client disconnected
                break
            except Exception as e:
                # فقط وقتی هنوز بازه ارسال کن
                if websocket.application_state == "connected":
                    await websocket.send_json({"status": "error", "message": str(e)})
            await asyncio.sleep(10)
    finally:
        logger.info("Health WS: client disconnected or loop exited")
