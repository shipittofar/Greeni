# app/models/notification.py
from sqlalchemy import Column, Integer, String, JSON, Enum, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class ChannelEnum(str, enum.Enum):
    sms = "sms"
    email = "email"
    push = "push"
    inapp = "inapp"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient = Column(String, nullable=False)      # ایمیل، شماره موبایل یا user_id / device token
    channel = Column(Enum(ChannelEnum), nullable=False)
    template = Column(String, nullable=False)
    data = Column(JSON, nullable=True)              # محتوای داینامیک
    status = Column(String, default="queued")      # queued / sent / failed
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
