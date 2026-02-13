from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional, List
from passlib.context import CryptContext
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(db: Session, user_in: UserCreate, current_user: Optional[User] = None) -> User:
    # چک ایمیل تکراری
    existing_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_email:
        raise ValueError("User with this email already exists")

    # چک شماره تلفن تکراری
    existing_phone = db.query(User).filter(User.phone_number == user_in.phone_number).first()
    if existing_phone:
        raise ValueError("User with this phone number already exists")

    role_id = user_in.role_id
    if not role_id or not db.query(Role).filter(Role.id == role_id).first():
        role_id = 2  # پیشفرض نقش 2 (مثلاً کاربر عادی)

    # اگر نقش 1 باشه، فقط سوپر یوزر اجازه ساختن داره
    is_superuser = False
    if role_id == 1:
        if not current_user or not current_user.is_superuser:
            raise PermissionError("Only superusers can create a superuser")
        is_superuser = True

    db_user = User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        phone_number=user_in.phone_number,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role_id=role_id,
        is_superuser=is_superuser,
        is_active=user_in.is_active,
        last_logins=[],
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception:
        db.rollback()
        raise
    return db_user


def get_all_users(db: Session) -> List[User]:
    return db.query(User).all()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone_number(db: Session, phone_number: str) -> Optional[User]:
    return db.query(User).filter(User.phone_number == phone_number).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, db_user: User, updates: UserUpdate, current_user: Optional[User] = None) -> User:
    update_data = updates.dict(exclude_unset=True)

    for field, value in update_data.items():
        if field == "password":
            if value:
                setattr(db_user, "hashed_password", get_password_hash(value))
        elif field == "role_id":
            role = db.query(Role).filter(Role.id == value).first()
            if not role:
                raise ValueError("Role not found")

            # اگر نقش 1 انتخاب شد → فقط سوپر یوزر اجازه داره
            if value == 1:
                if not current_user or not current_user.is_superuser:
                    raise PermissionError("Only superusers can assign superuser role")
                db_user.is_superuser = True
            else:
                # هر نقش دیگه → سوپر یوزر False
                db_user.is_superuser = False

            setattr(db_user, field, value)
        else:
            setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user



def add_login_timestamp(db: Session, db_user: User) -> User:
    logins = db_user.last_logins or []
    now = datetime.utcnow().isoformat()
    logins.append(now)
    if len(logins) > 50:
        logins = logins[-50:]
    db_user.last_logins = logins
    flag_modified(db_user, "last_logins")
    db.commit()
    db.refresh(db_user)
    return db_user


# def get_users_with_permission(db: Session, permission_name: str):
#     return (
#         db.query(User)
#         .join(User.role)
#         .join(Role.role_permissions)
#         .join(RolePermission.permission)
#         .filter(Permission.name == permission_name)
#         .all()
#     )

def get_users_with_permission(db: Session, permission_name: str):
    return (
        db.query(User)
        .join(User.role)
        .join(Role.role_permissions)
        .join(RolePermission.permission)
        .filter(Permission.name == permission_name)
        .options(
            joinedload(User.role)
            .joinedload(Role.role_permissions)
            .joinedload(RolePermission.permission)
        )
        .group_by(User.id)
        .all()
    )


def delete_user(db: Session, db_user: User, current_user: Optional[User] = None):
    """
    حذف کامل کاربر از دیتابیس
    فقط سوپر یوزرها می‌توانند سوپر یوزر دیگر را حذف کنند
    """
    if db_user.is_superuser and (not current_user or not current_user.is_superuser):
        raise PermissionError("Only superusers can delete another superuser")

    try:
        db.delete(db_user)
        db.commit()
    except Exception:
        db.rollback()
        raise
