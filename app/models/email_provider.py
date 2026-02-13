# app/models/email_provider.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from app.db.base_class import Base


class EmailProvider(Base):
    __tablename__ = "email_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)       # مثلا "smtp", "mailgun", "ses"
    username = Column(String, nullable=False)                # برای SMTP یا API
    password = Column(String, nullable=False)                # پسورد یا API Key
    host = Column(String, nullable=True)                     # فقط برای SMTP
    port = Column(Integer, nullable=True)                    # فقط برای SMTP
    is_active = Column(Boolean, default=True)               # Provider فعال
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
