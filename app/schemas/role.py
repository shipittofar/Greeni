from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .permission import PermissionPublic


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permission_ids: Optional[List[int]] = None



class RoleNameUpdate(BaseModel):
    name: Optional[str]


class RoleInDB(RoleBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    permissions: List[PermissionPublic] = []

    model_config = {"from_attributes": True}


class RolePublic(RoleInDB):
    pass
