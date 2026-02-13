import uuid
from sqlalchemy import Column, String, DateTime, func, Boolean
from app.db.base_class import Base

class SMSProvider(Base):
    __tablename__ = "sms_providers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, nullable=True)
    sender = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    registered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
