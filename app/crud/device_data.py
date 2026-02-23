# app/crud/device_data.py
from app.db.session import SessionLocal
from app.models.device_data import DeviceData
from loguru import logger


async def create_device_data_in_db(device_id: str, data: dict) -> None:
    """
    Persist a device telemetry payload.  Uses a dedicated sync session so it
    can be called from any async MQTT handler without needing an injected db.

    Expected 'data' keys:
        timestamp  (str | None)  – ISO-8601 timestamp from the device
        sensors    (dict | None) – sensor readings
    """
    db = SessionLocal()
    try:
        record = DeviceData(
            device_id=device_id,
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
