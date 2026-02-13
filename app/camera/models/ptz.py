from sqlalchemy import Column, String, Integer, Boolean, Float, Enum as SQLEnum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base_class import Base

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