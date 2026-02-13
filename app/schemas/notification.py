# app/schemas/notification.py
from pydantic import BaseModel
from typing import Optional, Dict
from app.models.notification import ChannelEnum

class NotificationCreate(BaseModel):
    recipient: str
    channel: ChannelEnum
    template: str
    data: Optional[Dict] = {}

class NotificationRead(BaseModel):
    id: int
    recipient: str
    channel: ChannelEnum
    template: str
    data: Optional[Dict] = {}
    status: str
    error_message: Optional[str]

    class Config:
        from_attributes = True

