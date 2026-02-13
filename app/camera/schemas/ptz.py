from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum

# PTZ Schemas
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
