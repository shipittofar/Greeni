# app/models/sensor.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from app.models.tag import sensor_type_tags
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid_lib


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid_lib.uuid4, unique=True, nullable=False)

    name = Column(String, nullable=False)
    sensor_type_id = Column(Integer, ForeignKey("sensor_types.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    pin_mapping = Column(JSON, nullable=True)  # مثلا {"data": 17} یا {"sda": 2, "scl": 3}
    config = Column(JSON, nullable=True)  # مثلا {"sampling_interval": 15, "unit": "°C"}

    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    device = relationship("Device", back_populates="sensors")
    sensor_type = relationship("SensorType", back_populates="sensors")
    attribute_values = relationship("SensorAttributeValue", back_populates="sensor")


class SensorType(Base):
    __tablename__ = "sensor_types"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid_lib.uuid4, unique=True, nullable=False)

    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    protocol = Column(String, nullable=True)  # مثل "GPIO", "I2C", "SPI", "UART", "PWM"
    default_pins = Column(JSON, nullable=True)  # مثلا {"data": 4} یا {"scl": 3, "sda": 2}
    config_schema = Column(JSON, nullable=True)  # اسکیمای تنظیمات پیکربندی اضافی

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    attributes = relationship("SensorAttribute", back_populates="sensor_type", cascade="all, delete-orphan")
    sensors = relationship("Sensor", back_populates="sensor_type")
    tags = relationship("Tag",secondary=sensor_type_tags,back_populates="sensor_types"
)


class SensorAttribute(Base):
    __tablename__ = "sensor_attributes"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid_lib.uuid4, unique=True, nullable=False)

    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # float, int, bool
    description = Column(Text, nullable=True)
    unit = Column(String, nullable=True)
    is_required = Column(Boolean, default=True)

    sensor_type_id = Column(Integer, ForeignKey("sensor_types.id"))
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    sensor_type = relationship("SensorType", back_populates="attributes")
    attribute_values = relationship("SensorAttributeValue", back_populates="attribute", cascade="all, delete-orphan", passive_deletes=True)


class SensorAttributeValue(Base):
    __tablename__ = "sensor_attribute_values"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid_lib.uuid4, unique=True, nullable=False)

    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    attribute_id = Column(Integer, ForeignKey("sensor_attributes.id", ondelete="CASCADE"), nullable=False)

    value = Column(String, nullable=True)
    source = Column(String, nullable=True)  # manual, device, api
    status = Column(String, default="normal")  # normal, warning, critical
    
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    sensor = relationship("Sensor", back_populates="attribute_values")
    attribute = relationship("SensorAttribute", back_populates="attribute_values", passive_deletes=True)


class SensorAttributeValueHistory(Base):
    __tablename__ = "sensor_attribute_value_history"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid_lib.uuid4, unique=True, nullable=False)

    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    attribute_id = Column(Integer, ForeignKey("sensor_attributes.id", ondelete="CASCADE"))
    value = Column(String, nullable=True)

    source = Column(String, nullable=True)
    status = Column(String, default="normal")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sensor = relationship("Sensor")
    attribute = relationship("SensorAttribute")
