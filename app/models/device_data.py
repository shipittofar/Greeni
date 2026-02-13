# app/models/device_data.py
from sqlalchemy import Column, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.base_class import Base

class DeviceData(Base):
    __tablename__ = "device_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.uuid"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON, nullable=False)

    device = relationship("Device", back_populates="data_points")
