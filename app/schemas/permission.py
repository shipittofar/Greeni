# app/schemas/permission.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PermissionBase(BaseModel):
    title: str
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    title: Optional[str]
    name: Optional[str]
    description: Optional[str]
    is_active: Optional[bool]

class PermissionInDB(PermissionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

class PermissionPublic(PermissionInDB):
    pass
