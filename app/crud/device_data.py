# app/crud/device_data.py
import uuid as uuid_lib
from app.db.session import SessionLocal
from app.models.device_data import DeviceData
from loguru import logger


def create_device_data_in_db(device_id: str, data: dict) -> None:
    """
    Persist a device telemetry payload using a dedicated sync session.
    Must be called via asyncio.to_thread() from async contexts.

    DeviceData.device_id is a UUID FK → devices.uuid, so the string
    device_id from the MQTT topic is converted to uuid.UUID before insert.

    Expected 'data' keys:
        timestamp  (str | None)  – ISO-8601 timestamp from the device
        sensors    (dict | None) – sensor readings
    """
    try:
        device_uuid = uuid_lib.UUID(device_id)
    except (ValueError, AttributeError):
        logger.error(f"[DeviceData] Invalid device_id (not a UUID): '{device_id}'")
        return

    db = SessionLocal()
    try:
        record = DeviceData(
            device_id=device_uuid,
            timestamp=data.get("timestamp"),
            data=data.get("sensors"),
        )
        db.add(record)
        db.commit()
        logger.debug(f"[DeviceData] Persisted record for device '{device_id}'")
    except Exception as e:
        db.rollback()
        logger.exception(f"[DeviceData] Failed to persist record for device '{device_id}': {e}")
        raise
    finally:
        db.close()
