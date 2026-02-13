from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from app.schemas.sensor import SensorPublic
from datetime import datetime
from uuid import UUID

class DeviceBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    lat: Optional[str] = None
    lon: Optional[str] = None
    time_zone: Optional[str] = None
    icon: Optional[str] = None
    product_name: Optional[str] = None
    product_id: Optional[str] = None
    category: Optional[str] = None
    local_key: Optional[str] = None

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class DeviceCreate(DeviceBase):
    unique_code: str = Field(..., description="Unique code to identify the device")
    # اختیاری: اگر نخواهی کاربر اینها رو بده، نذار اینجا
    # is_pending: Optional[bool] = None
    # is_system_registered: Optional[bool] = None


class DeviceUpdate(DeviceBase):
    is_active: Optional[bool] = None
    is_online: Optional[bool] = None
    is_pending: Optional[bool] = None
    is_system_registered: Optional[bool] = None


class DeviceInDB(DeviceBase):
    id: int
    uuid: UUID
    unique_code: str
    is_active: bool
    is_online: bool
    is_pending: bool
    is_system_registered: bool
    registered_at: datetime
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }


class DevicePublic(DeviceBase):
    id: int
    uuid: UUID
    unique_code: str
    is_active: bool
    is_online: bool
    is_pending: bool
    is_system_registered: bool
    registered_at: datetime
    updated_at: Optional[datetime]
    
    sensors: List[SensorPublic] = []

    model_config = {
        "from_attributes": True
    }


class DeviceMultiMediaPublic(BaseModel):
    id: int
    uuid: UUID
    unique_code: str
    is_active: bool
    is_online: bool
    is_pending: bool
    is_system_registered: bool
    is_multimedia: bool
    registered_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {
        "from_attributes": True
    }
