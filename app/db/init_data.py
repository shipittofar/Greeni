from sqlalchemy.orm import Session
from sqlalchemy.sql import text  # ⬅️ فراموش نکن ایمپورتش کنی!
from app.models.user import User
from app.models.role import Role
from app.models.device import Device
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.core.security import get_password_hash
from datetime import datetime

def init_data(db: Session):
    # چک کن Permission با id=1 هست یا نه
    permission = db.query(Permission).filter_by(id=1).first()
    if not permission:
        permission = Permission(id=1, name="تمام دسترسی‌ها", title="full_access", description="دسترسی کامل به همه بخش‌ها", is_active=True)
        db.add(permission)
        db.flush()

    # چک کن role_superuser هست یا نه
    role_superuser = db.query(Role).filter_by(id=1).first()
    if not role_superuser:
        role_superuser = Role(id=1, name="superuser")
        db.add(role_superuser)

    role_user = db.query(Role).filter_by(id=2).first()
    if not role_user:
        role_user = Role(id=2, name="user")
        db.add(role_user)

    db.flush()

    # چک کن رابطه role_permission هست یا نه
    role_permission = db.query(RolePermission).filter_by(role_id=role_superuser.id, permission_id=permission.id).first()
    if not role_permission:
        role_permission = RolePermission(role_id=role_superuser.id, permission_id=permission.id)
        db.add(role_permission)

    # چک کن کاربر پیش‌فرض هست یا نه
    user = db.query(User).filter_by(email="mojtaba.ts1970@gmail.com").first()
    if not user:
        hashed_password = get_password_hash("1234")
        user = User(
            first_name="مجتبی",
            last_name="خسروشاهی",
            phone_number="09011754128",
            email="mojtaba.ts1970@gmail.com",
            hashed_password=hashed_password,
            role_id=role_superuser.id,
            is_active=True,
            is_superuser=True
        )
        db.add(user)

    db.commit()
