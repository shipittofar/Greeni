from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# -- خلاصه Attribute داخل value
class SensorAttributeShort(BaseModel):
    id: int
    name: str
    unit: Optional[str]

    model_config = ConfigDict(from_attributes=True)

# -- مقدار به‌همراه attribute خلاصه‌شده
class SensorAttributeValueWithAttr(BaseModel):
    id: int
    sensor_id: int
    value: str
    attribute: SensorAttributeShort

    model_config = ConfigDict(from_attributes=True)

# -- نوع سنسور به‌همراه اتریبیوت‌های کامل
class SensorTypeWithAttrs(BaseModel):
    id: int
    uuid: UUID
    name: str
    attributes: List[SensorAttributeShort]

    model_config = ConfigDict(from_attributes=True)

# -- سنسور با اطلاعات کامل
class SensorFull(BaseModel):
    id: int
    uuid: UUID
    name: str
    is_active: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    sensor_type: SensorTypeWithAttrs
    attribute_values: List[SensorAttributeValueWithAttr]

    model_config = ConfigDict(from_attributes=True)

# -- دیوایس کامل
class DeviceFull(BaseModel):
    id: int
    unique_code: str
    name: Optional[str]
    is_active: bool
    is_online: bool
    is_pending: bool
    is_system_registered: bool
    registered_at: datetime
    updated_at: Optional[datetime]
    sensors: List[SensorFull]

    model_config = ConfigDict(from_attributes=True)