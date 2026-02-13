from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

# class Permission(Base):
#     __tablename__ = "permissions"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, nullable=False)
#     name = Column(String, unique=True, nullable=False)
#     description = Column(String)

#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     role_permissions = relationship(
#         "RolePermission",
#         back_populates="permission",
#         cascade="all, delete-orphan"
#     )
#     roles = relationship(
#         "Role",
#         secondary="role_permissions",
#         back_populates="permissions",
#         lazy="selectin"
#     )

#     # @property
#     # def roles(self):
#     #     return [rp.role for rp in self.role_permissions]

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        overlaps="roles,permissions,role" 
    )

    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
        overlaps="role_permissions,permission,permissions,role"
    )

