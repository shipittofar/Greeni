# app/schemas/sensor.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.tag import Tag, TagPublic
from uuid import UUID

# ---------- SensorAttribute ----------
class SensorAttributeBase(BaseModel):
    name: str
    type: str
    unit: Optional[str] = None
    sensor_type_id: int
    description: Optional[str] = None
    is_required: bool = True

class SensorAttributeCreate(SensorAttributeBase):
    # uuid: Optional[UUID] = None  # اختیاری: در صورت تولید سمت کلاینت

    model_config = ConfigDict(extra="forbid")

class SensorAttributeUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    unit: Optional[str] = None
    sensor_type_id: Optional[int] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")

class SensorAttribute(SensorAttributeBase):
    id: int
    uuid: UUID
    is_deleted: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class SensorAttributePublic(BaseModel):
    id: int
    uuid: UUID
    name: str
    type: str
    unit: Optional[str]
    sensor_type_id: int
    description: Optional[str]
    is_required: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

# ---------- SensorType ----------
class SensorTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

    protocol: Optional[str] = None
    default_pins: Optional[dict] = None
    config_schema: Optional[dict] = None 

class SensorTypeCreate(SensorTypeBase):
    tag_ids: Optional[List[int]] = []

    model_config = ConfigDict(extra="forbid")

class SensorTypeUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_active: Optional[bool]
    protocol: Optional[str]
    default_pins: Optional[dict]
    config_schema: Optional[dict]
    tag_ids: Optional[List[int]] = None

    model_config = ConfigDict(extra="forbid")
class SensorType(SensorTypeBase):
    id: int
    uuid: UUID
    attributes: List[SensorAttribute] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool = False

    created_by: Optional[int] = None  # ✅ اضافه شود
    updated_by: Optional[int] = None  # ✅ اضافه شود

    tags: List[TagPublic] = []

    model_config = ConfigDict(from_attributes=True)

class SensorTypePublic(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: Optional[str]
    is_active: Optional[bool]
    protocol: Optional[str]
    default_pins: Optional[dict]
    config_schema: Optional[dict]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    tags: Optional[List[TagPublic]] = []

    model_config = ConfigDict(from_attributes=True)

class SensorTypeTagsPublic(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: Optional[str]
    is_active: Optional[bool]
    protocol: Optional[str]
    
    tags: Optional[List[TagPublic]] = []

    model_config = ConfigDict(from_attributes=True)

class SensorTypeTagAssignmentRequest(BaseModel):
    sensor_type_id: int
    tag_ids: List[int]
    
# ---------- SensorAttributeValue ----------
class SensorAttributeValueBase(BaseModel):
    sensor_id: int
    attribute_id: int
    value: str
    source: Optional[str] = "device"
    status: Optional[str] = "normal"

class SensorAttributeValueCreate(SensorAttributeValueBase):
    # uuid: Optional[UUID] = None

    model_config = ConfigDict(extra="forbid")

class SensorAttributeValueUpdate(BaseModel):
    value: Optional[str] = None
    sensor_id: Optional[int] = None
    attribute_id: Optional[int] = None
    source: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

class SensorAttributeValue(SensorAttributeValueBase):
    id: int
    uuid: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class SensorAttributeValuePublic(BaseModel):
    id: int
    uuid: UUID
    sensor_id: int
    attribute_id: int
    value: str
    source: Optional[str]
    status: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
# ---------- Sensor ----------
class SensorBase(BaseModel):
    name: str
    device_id: Optional[int] = None
    sensor_type_id: int
    is_active: Optional[bool] = True
    is_online: Optional[bool] = True

class SensorCreate(SensorBase):
    # uuid: Optional[UUID] = None

    model_config = ConfigDict(extra="forbid")

class SensorUpdate(BaseModel):
    name: Optional[str] = None
    device_id: Optional[int] = None
    sensor_type_id: Optional[int] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")

class Sensor(SensorBase):
    id: int
    uuid: UUID
    is_deleted: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    attribute_values: List[SensorAttributeValue] = []
    sensor_type: SensorType

    model_config = ConfigDict(from_attributes=True)

class SensorPublic(BaseModel):
    id: int
    uuid: UUID
    name: str
    is_active: Optional[bool]
    is_online: Optional[bool]
    is_deleted: Optional[bool]
    sensor_type_id: int
    device_id: Optional[int] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

# ---------- View Helpers ----------
class SensorAttributeShort(BaseModel):
    id: int
    name: str
    unit: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SensorAttributeValueWithAttr(BaseModel):
    id: int
    sensor_id: int
    value: str
    attribute: SensorAttributeShort
    sensor: Optional[dict]  # شامل نام سنسور

    model_config = ConfigDict(from_attributes=True)

