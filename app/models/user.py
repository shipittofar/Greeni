from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.db.base_class import Base
from app.models.role import Role


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", back_populates="users")

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ذخیره آخرین ۵۰ ورود اخیر به صورت لیست از تاریخ‌ها
    last_logins = Column(JSON, default=[])

