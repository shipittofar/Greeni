from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime

# ---------- Base ----------
class TagBase(BaseModel):
    name: str
    icon: Optional[str] = None         # مثل mdi-weather-sunny
    description: Optional[str] = None
    color: Optional[str] = None        # مثل '#ff9800' یا 'primary'
    is_active: Optional[bool] = True
    extra_metadata: Optional[Dict] = {}      # برای داده‌های دلخواه مثل {"priority": 1}

    model_config = ConfigDict(extra="forbid")


# ---------- Create ----------
class TagCreate(TagBase):
    pass


# ---------- Update ----------
class TagUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
    extra_metadata: Optional[Dict] = None

    model_config = ConfigDict(extra="forbid")


# ---------- Read (Full) ----------
class Tag(BaseModel):
    id: int
    uuid: UUID
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = True
    extra_metadata: Optional[Dict] = {}
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]

    model_config = ConfigDict(from_attributes=True)


# ---------- Public (Minimal) ----------
class TagPublic(BaseModel):
    id: int
    uuid: UUID
    name: str
    icon: Optional[str]
    color: Optional[str]

    model_config = ConfigDict(from_attributes=True)
