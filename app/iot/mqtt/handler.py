# app/iot/mqtt/handler.py
import asyncio
from typing import Dict
from app.api.v1.ws.connections import get_connections
from loguru import logger
from app.db.session import SessionLocal
from app.crud.command import command as crud_command


async def handle_message(topic: str, data: dict):
    """Main dispatcher for all inbound MQTT messages."""
    try:
        logger.info(f"[MQTT Handler] topic='{topic}' data={data}")
    except Exception as e:
        logger.exception(f"[MQTT Handler] Error logging message: {e}")
        return

    # ------------------------------------------------------------------
    # greeni/device/{id}/media/media_list
    # ------------------------------------------------------------------
    if topic.endswith("/media/media_list"):
        await _handle_media_list(topic, data)

    # ------------------------------------------------------------------
    # greeni/device/{id}/commands/status
    # ------------------------------------------------------------------
    elif "commands" in topic and topic.endswith("/status"):
        await _handle_command_status(topic, data)

    # ------------------------------------------------------------------
    # greeni/device/{id}/data
    # ------------------------------------------------------------------
    elif topic.endswith("/data"):
        await _handle_device_data(topic, data)

    # ------------------------------------------------------------------
    # greeni/device/{id}/system/info
    # ------------------------------------------------------------------
    elif topic.endswith("/system/info"):
        await _handle_system_info(topic, data)

    else:
        logger.debug(f"[MQTT Handler] Unhandled topic: '{topic}'")


# ---------------------------------------------------------------------------
# Private handlers
# ---------------------------------------------------------------------------

async def _handle_media_list(topic: str, data: dict):
    files = data.get("files", [])
    ws_group = list(get_connections("media"))
    for ws in ws_group:
        try:
            await ws.send_json({"event": "media_list", "files": files})
        except Exception as e:
            logger.exception(f"[MQTT Handler] Failed to send media_list via WS: {e}")


async def _handle_command_status(topic: str, data: dict):
    # Persist to DB
    asyncio.create_task(_update_command_status_safe(topic, data))

    # Broadcast to all command WebSocket clients
    ws_group = list(get_connections("command"))
    for ws in ws_group:
        try:
            await ws.send_json({
                "event": "command_status",
                "topic": topic,
                "data": data,
            })
        except Exception as e:
            logger.exception(f"[MQTT Handler] Failed to send command_status via WS: {e}")


async def _handle_device_data(topic: str, data: dict):
    """Persist sensor/telemetry data sent by a device."""
    try:
        from app.iot.device_data.receiver import process_device_data
        await process_device_data(topic, data)
    except Exception as e:
        logger.exception(f"[MQTT Handler] Failed to process device data: {e}")


async def _handle_system_info(topic: str, data: dict):
    """Forward system info to any connected system WebSocket clients."""
    device_id = topic.split("/")[2] if len(topic.split("/")) > 2 else None
    ws_group = list(get_connections("system"))
    for ws in ws_group:
        try:
            await ws.send_json({
                "event": "system_info",
                "device_id": device_id,
                "data": data,
            })
        except Exception as e:
            logger.exception(f"[MQTT Handler] Failed to send system_info via WS: {e}")


async def _update_command_status_safe(topic: str, data: Dict):
    """Persist command status update from device — uses a dedicated sync session."""
    try:
        uuid = data.get("uuid")
        if not uuid:
            logger.warning(f"[Command Status] No uuid in payload: {data}")
            return

        db = SessionLocal()
        try:
            cmd_obj = crud_command.get_by_uuid(db, uuid)
            if not cmd_obj:
                logger.warning(f"[Command Status] Command not found: uuid={uuid}")
                return

            cmd_obj.status = data.get("status", cmd_obj.status)
            cmd_obj.payload = data.get("payload", cmd_obj.payload)
            db.commit()
            db.refresh(cmd_obj)
            logger.info(f"[Command Status] uuid={uuid} → status={cmd_obj.status}")
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"[Command Status] Failed to update from MQTT: {e}")
