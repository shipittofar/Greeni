# app/iot/device_data/receiver.py
import re
from loguru import logger
from app.crud.device_data import create_device_data_in_db


async def process_device_data(topic: str, data: dict):
    """
    Called by the MQTT handler when a device publishes to
    greeni/device/{device_id}/data.

    Expected payload structure:
        {
            "timestamp": "2024-01-01T00:00:00Z",   # optional
            "sensors": { ... }                       # sensor readings
        }
    """
    match = re.match(r"greeni/device/(.+)/data", topic)
    if not match:
        logger.warning(f"[Receiver] Invalid data topic format: '{topic}'")
        return

    device_id = match.group(1)
    logger.debug(f"[Receiver] Processing data for device '{device_id}'")

    try:
        await create_device_data_in_db(device_id=device_id, data=data)
        logger.info(f"[Receiver] Stored device data for device '{device_id}'")
    except Exception as e:
        logger.exception(f"[Receiver] Failed to store data for device '{device_id}': {e}")
