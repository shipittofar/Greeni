from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class SensorDataBase(BaseModel):
    sensor_id: int
    attribute_id: Optional[int] = None
    value: str
    source: Optional[str] = "device"
    status: Optional[str] = "normal"


class SensorDataCreate(SensorDataBase):
    pass


class SensorDataInDBBase(SensorDataBase):
    id: int
    uuid: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SensorDataPublic(SensorDataInDBBase):
    pass
