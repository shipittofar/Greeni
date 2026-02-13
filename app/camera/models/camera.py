from sqlalchemy import Column, String, Integer, Boolean, Float, Enum as SQLEnum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base_class import Base

class CameraType(str, enum.Enum):
    IP = "ip"
    USB = "usb"
    RTSP = "rtsp"

class CameraStatus(str, enum.Enum):
    ONLINE = "onLine"
    OFFLINE = "offLine"
    DISCONNECTED = "disconnected"
    ERROR = "error"

class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(CameraType), default=CameraType.IP, nullable=False)
    status = Column(SQLEnum(CameraStatus), default=CameraStatus.OFFLINE, nullable=False)
    is_pending = Column(Boolean, default=True)

    # Connection details
    url = Column(String, nullable=False)  # RTSP URL, IP address, or USB device path
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    port = Column(Integer, default=554, nullable=True)  # RTSP default port
    is_active = Column(Boolean, default=True)
    
    # Camera capabilities
    resolution_width = Column(Integer, nullable=True)
    resolution_height = Column(Integer, nullable=True)
    fps = Column(Integer, default=30, nullable=True)
    
    # PTZ support
    has_ptz = Column(Boolean, default=False, nullable=False)
    ptz_type = Column(String, nullable=True)  # "onvif", "pelco", "generic"
    
    # Streaming
    streaming_enabled = Column(Boolean, default=True, nullable=False)
    streaming_bitrate = Column(Integer, default=2500, nullable=False)  # kbps
    streaming_quality = Column(String, default="medium", nullable=False)  # low, medium, high
    
    # Storage
    recording_enabled = Column(Boolean, default=False, nullable=False)
    retention_days = Column(Integer, default=7, nullable=False)
    
    # Metadata
    location = Column(String, nullable=True)
    # is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_heartbeat = Column(DateTime, nullable=True)
    
    # Relationships
    device = relationship("Device", back_populates="cameras")
    ptz_controls = relationship("PTZControl", back_populates="camera", cascade="all, delete-orphan")

class PTZControl(Base):
    __tablename__ = "ptz_controls"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    
    # Pan, Tilt, Zoom positions (normalized 0-1)
    pan_position = Column(Float, default=0.5, nullable=False)
    tilt_position = Column(Float, default=0.5, nullable=False)
    zoom_position = Column(Float, default=0.0, nullable=False)
    
    # Speed settings (0-1)
    pan_speed = Column(Float, default=0.5, nullable=False)
    tilt_speed = Column(Float, default=0.5, nullable=False)
    zoom_speed = Column(Float, default=0.5, nullable=False)
    
    # Presets
    preset_name = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    camera = relationship("Camera", back_populates="ptz_controls")