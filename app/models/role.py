from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.role_permission import RolePermission
# from sqlalchemy.sql import func

# class Role(Base):
#     __tablename__ = "roles"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True, nullable=False)
#     users = relationship("User", back_populates="role")

#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

#     role_permissions = relationship(
#         "RolePermission",
#         back_populates="role",
#         cascade="all, delete-orphan",
#         lazy="joined"
#     )
#     permissions = relationship(
#         "Permission",
#         secondary="role_permissions",
#         back_populates="roles",
#         lazy="selectin"
#     )

#     # @property
#     # def permissions(self):
#     #     return [rp.permission for rp in self.role_permissions]

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="role")

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
        overlaps="role_permissions,permission,role"
    )