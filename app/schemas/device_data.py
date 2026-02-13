# app/schemas/device_data.py
from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from pydantic import BaseModel

class DeviceDataCreate(BaseModel):
    device_id: UUID
    timestamp: datetime
    data: Dict[str, Any]

class DeviceDataPublic(BaseModel):
    id: UUID
    device_id: UUID
    timestamp: datetime
    data: Dict[str, Any]

    class Config:
        from_attributes = True
