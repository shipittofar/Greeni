# app/models/push_provider.py
from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.db.base_class import Base

class PushProvider(Base):
    __tablename__ = "push_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    api_key = Column(String(512), nullable=False)
    config = Column(JSON, nullable=True)   # برای تنظیمات اضافه مثل project_id, server_key و ...
    is_active = Column(Boolean, default=True)
