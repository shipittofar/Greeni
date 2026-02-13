# app/iot/device_data/receiver.py
import re
from app.crud.device_data import create_device_data_in_db

async def process_device_data(topic: str, data: dict):
    match = re.match(r'greeni/device/(.+)/data', topic)
    if not match:
        print("[Receiver] Invalid topic format")
        return

    device_id = match.group(1)
    await create_device_data_in_db(device_id=device_id, data=data)
