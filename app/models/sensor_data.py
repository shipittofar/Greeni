from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
import uuid as uuid_lib


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid_lib.uuid4, unique=True, nullable=False)

    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    attribute_id = Column(Integer, ForeignKey("sensor_attributes.id"), nullable=True)

    value = Column(String, nullable=False)     # مقدار سنسور
    source = Column(String, default="device")  # منبع داده (device, api, manual)
    status = Column(String, default="normal")  # normal, warning, error

    created_at = Column(DateTime(timezone=True), server_default=func.now())
