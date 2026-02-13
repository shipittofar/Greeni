from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate

class RoleCRUD:
    def list_roles(self, db: Session) -> List[Role]:
        return db.query(Role).all()

    def get_role(self, db: Session, role_id: int) -> Optional[Role]:
        return db.query(Role).get(role_id)

    def create_role(self, db: Session, payload: RoleCreate) -> Role:
        db_role = Role(name=payload.name)
        # ... تنظیم پرمیشن‌ها و بقیه فیلدها اگر هست
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role

    def update_role(self, db: Session, role: Role, payload: RoleUpdate) -> Role:
        if payload.name is not None:
            role.name = payload.name

        if payload.permission_ids is not None:
            from app.models.permission import Permission

            # گرفتن تمام پرمیشن‌هایی که باید نقش داشته باشد
            new_permissions = db.query(Permission).filter(
                Permission.id.in_(payload.permission_ids)
            ).all()

            # جایگزینی کامل پرمیشن‌ها
            role.permissions = new_permissions

        db.commit()
        db.refresh(role)
        return role

    def update_role_name(self, db: Session, role: Role, new_name: str) -> Role:
        role.name = new_name
        db.commit()
        db.refresh(role)
        return role

    def delete_role(self, db: Session, role: Role):
        db.delete(role)
        db.commit()
