# app/iot/mqtt/handler.py
import asyncio
from typing import Dict
from app.api.v1.ws.connections import get_connections
from loguru import logger
from app.db.session import SessionLocal
from app.crud.command import command as crud_command

async def handle_message(topic: str, data: dict):
    """
    Handler اصلی برای همه پیام‌های MQTT
    """
    try:
        logger.info(f"[MQTT Handler] Message received on {topic}: {data}")
    except Exception as e:
        logger.exception(f"❌ Error printing MQTT message: {e}")
        return

    # --------------------------------
    # پاسخ media_list
    # --------------------------------
    if topic.endswith("/media/media_list"):
        files = data.get("files", [])
        ws_group = list(get_connections("media"))
        for ws in ws_group:
            try:
                await ws.send_json({
                    "event": "media_list",
                    "files": files
                })
            except Exception as e:
                logger.exception(f"❌ Failed to send WS media_list message: {e}")

    # --------------------------------
    # پاسخ status فرمان
    # --------------------------------
    elif "commands" in topic and topic.endswith("/status"):
        # ✅ آپدیت وضعیت فرمان در DB
        asyncio.create_task(_update_command_status_safe(topic, data))

        # ارسال به همه WebSocket های command
        ws_group = list(get_connections("command"))
        for ws in ws_group:
            try:
                await ws.send_json({
                    "event": "command_status",
                    "topic": topic,
                    "data": data
                })
            except Exception as e:
                logger.exception(f"❌ Failed to send WS command_status message: {e}")


async def _update_command_status_safe(topic: str, data: Dict):
    """
    آپدیت وضعیت فرمان در DB به صورت async-safe
    """
    try:
        uuid = data.get("uuid")
        if not uuid:
            logger.warning(f"[Command Status] No uuid in message: {data}")
            return

        # استفاده از SessionLocal مستقل تا با کد sync موجود تداخل نکند
        db = SessionLocal()
        try:
            cmd_obj = crud_command.get_by_uuid(db, uuid)
            if not cmd_obj:
                logger.warning(f"[Command Status] Command not found in DB: {uuid}")
                return

            # آپدیت فیلدها
            cmd_obj.status = data.get("status", cmd_obj.status)
            cmd_obj.payload = data.get("payload", cmd_obj.payload)
            db.commit()
            db.refresh(cmd_obj)
            logger.info(f"[Command Status] Updated command {uuid} to {cmd_obj.status}")
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"❌ Failed to update command status from MQTT message: {e}")
