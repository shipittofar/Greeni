from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid_lib
from app.db.base_class import Base

# جدول واسط Many-to-Many
sensor_type_tags = Table(
    "sensor_type_tags",
    Base.metadata,
    Column("sensor_type_id", Integer, ForeignKey("sensor_types.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid_lib.uuid4, unique=True, nullable=False)

    name = Column(String, unique=True, nullable=False)
    icon = Column(String, nullable=True)  # مثال: mdi-lightbulb
    description = Column(String, nullable=True)
    color = Column(String, nullable=True)  # مثل: '#4caf50' یا 'success'
    is_active = Column(Boolean, default=True)

    extra_metadata = Column(JSON, nullable=True)  # برای داده‌های اضافی سفارشی

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # ارتباط با SensorType
    sensor_types = relationship(
        "SensorType",
        secondary="sensor_type_tags",
        back_populates="tags"
    )
