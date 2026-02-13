from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
import uuid as uuid_lib


class Command(Base):
    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid_lib.uuid4, unique=True, nullable=False)

    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)

    command = Column(String, nullable=False)   # مثل: "turn_on_pump"
    payload = Column(Text, nullable=True)      # JSON string (مثلا {"speed": 5})

    status = Column(String, default="pending")  # pending, sent, executed, failed
    executed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
