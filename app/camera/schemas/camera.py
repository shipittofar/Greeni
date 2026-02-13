from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CameraType(str, Enum):
    IP = "ip"
    USB = "usb"
    RTSP = "rtsp"

class CameraStatus(str, Enum):
    ONLINE = "onLine"
    OFFLINE = "offLine"
    DISCONNECTED = "disconnected"
    ERROR = "error"

class CameraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: CameraType
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    port: Optional[int] = 554
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    fps: Optional[int] = 30
    has_ptz: bool = False
    ptz_type: Optional[str] = None  # "onvif", "pelco", "generic"
    streaming_enabled: bool = True
    streaming_bitrate: int = 2500
    streaming_quality: str = "medium"
    recording_enabled: bool = False
    retention_days: int = 7
    location: Optional[str] = None

class CameraCreate(CameraBase):
    device_id: int

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    port: Optional[int] = None
    fps: Optional[int] = None
    has_ptz: Optional[bool] = None
    ptz_type: Optional[str] = None
    streaming_enabled: Optional[bool] = None
    streaming_bitrate: Optional[int] = None
    streaming_quality: Optional[str] = None
    recording_enabled: Optional[bool] = None
    retention_days: Optional[int] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[CameraStatus] = None

class CameraResponse(CameraBase):
    id: int
    device_id: int
    status: CameraStatus
    is_active: bool
    is_pending: bool
    created_at: datetime
    updated_at: datetime
    last_heartbeat: Optional[datetime]

    class Config:
        from_attributes = True

class CameraListResponse(BaseModel):
    total: int
    cameras: List[CameraResponse]

# ============= PENDING CAMERA SCHEMAS =============

class CameraApprovePending(BaseModel):
    """Schema for approving or rejecting a pending camera"""
    approved: bool = Field(..., description="Whether to approve (True) or reject (False) the camera")
    notes: Optional[str] = Field(None, max_length=500, description="Admin notes on the approval/rejection")

class CameraPendingResponse(BaseModel):
    """Schema for pending camera response"""
    id: int
    device_id: int
    name: str
    type: CameraType
    url: str
    is_pending: bool
    status: CameraStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class CameraPendingListResponse(BaseModel):
    """List response for pending cameras"""
    total: int
    pending_cameras: List[CameraPendingResponse]

class CameraPendingCountResponse(BaseModel):
    """Response for pending camera count"""
    pending_count: int

# ============= PTZ SCHEMAS =============

class PTZControlBase(BaseModel):
    pan_position: float = Field(0.5, ge=0, le=1)
    tilt_position: float = Field(0.5, ge=0, le=1)
    zoom_position: float = Field(0.0, ge=0, le=1)
    pan_speed: float = Field(0.5, ge=0, le=1)
    tilt_speed: float = Field(0.5, ge=0, le=1)
    zoom_speed: float = Field(0.5, ge=0, le=1)

class PTZMove(BaseModel):
    direction: str = Field(..., pattern="^(up|down|left|right|home|zoom_in|zoom_out)$")
    duration: Optional[float] = 0.5  # seconds
    speed: float = Field(0.5, ge=0, le=1)

class PTZPreset(BaseModel):
    preset_name: str
    action: str = Field(..., pattern="^(save|load|delete)$")

class PTZControlResponse(PTZControlBase):
    id: int
    camera_id: int
    preset_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True