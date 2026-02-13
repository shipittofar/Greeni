from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class CommandBase(BaseModel):
    device_id: int
    command: str
    payload: Optional[str] = None


class CommandCreate(CommandBase):
    pass


class CommandUpdate(BaseModel):
    status: Optional[str] = None
    executed_at: Optional[datetime] = None


class CommandInDBBase(CommandBase):
    id: int
    uuid: UUID
    status: str
    executed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommandPublic(CommandInDBBase):
    pass
