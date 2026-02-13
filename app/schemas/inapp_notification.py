# app/schemas/inapp_notification.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime


class InAppNotificationBase(BaseModel):
    title: str
    message: str
    data: Optional[Dict] = None

class InAppNotificationCreate(InAppNotificationBase):
    user_id: int

class InAppNotificationInDB(InAppNotificationBase):
    id: str
    user_id: int
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class InAppNotificationRead(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    data: Optional[Dict] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class InAppNotificationResponse(BaseModel):
    """Schema برای پاسخ اعلان"""
    
    id: str
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    data: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InAppNotificationListResponse(BaseModel):
    """Schema برای لیست اعلان‌ها"""
    
    count: int
    skip: int
    limit: int
    results: list[InAppNotificationResponse]





class InAppNotificationCreate(BaseModel):
    """Schema for creating a new notification"""
    user_id: int
    title: str
    message: str
    type: str = "info"  # Default type is "info"
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    data: Optional[Dict] = None


class InAppNotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    title: Optional[str] = None
    message: Optional[str] = None
    type: Optional[str] = None
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    data: Optional[Dict] = None
    is_read: Optional[bool] = None


class InAppNotificationResponse(BaseModel):
    """Schema for notification response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    title: str
    message: str
    type: str
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    data: Optional[Dict] = None
    is_read: bool
    created_at: datetime
    updated_at: datetime


class InAppNotificationListResponse(BaseModel):
    """Schema for notification list response"""
    count: int
    skip: int
    limit: int
    results: List[InAppNotificationResponse]