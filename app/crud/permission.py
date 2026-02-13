from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    db_perm = Permission(
        title=permission.title,
        name=permission.name,
        description=permission.description,
        is_active=permission.is_active
    )
    try:
        db.add(db_perm)
        db.commit()
        db.refresh(db_perm)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission with this name already exists"
        )
    return db_perm


def list_permissions(db: Session) -> list[Permission]:
    return db.query(Permission).all()


def update_permission(db: Session, permission_id: int, update: PermissionUpdate) -> Permission:
    db_perm = db.query(Permission).get(permission_id)
    if not db_perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    for field, value in update.dict(exclude_unset=True).items():
        setattr(db_perm, field, value)

    try:
        db.commit()
        db.refresh(db_perm)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission with this name already exists"
        )
    return db_perm


def delete_permission(db: Session, permission_id: int, is_superuser: bool) -> None:
    if not is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can delete permissions")

    db_perm = db.query(Permission).get(permission_id)
    if not db_perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    db.delete(db_perm)
    db.commit()
