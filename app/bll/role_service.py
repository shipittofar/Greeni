# app/bll/role_service.py
from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

from app.crud.role import RoleCRUD
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from app.cache.base_cache import BaseCache
from datetime import datetime, date
from app.models.role_permission import RolePermission
from app.schemas.role import RolePublic
from fastapi.encoders import jsonable_encoder

role_crud = RoleCRUD()
role_cache = BaseCache(namespace="roles", expire_seconds=36000)


def sqlalchemy_to_dict(obj):
    result = {}
    for c in obj.__mapper__.column_attrs:
        value = getattr(obj, c.key)
        if isinstance(value, (datetime, date)):
            value = value.isoformat()
        result[c.key] = value

    # handle permissions if role
    if hasattr(obj, "permissions"):
        result["permissions"] = [
            {
                "id": p.id,
                "name": p.name,
                "title": getattr(p, "title", None),
                "description": getattr(p, "description", None),
                "is_active": getattr(p, "is_active", None),
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in obj.permissions
        ]
    return result



async def list_roles(db: Session) -> List[RolePublic]:
    cache_key = "list:All"
    cached = await role_cache.get(cache_key)
    if cached:
        print("[Cache] list_roles: fetched roles list from cache")
        return [RolePublic(**item) for item in cached]   # ✅

    print("[DB] list_roles: fetching roles list from database")
    roles = db.query(Role).options(selectinload(Role.permissions)).all()

    # serialize با Pydantic
    serialized = [jsonable_encoder(RolePublic.from_orm(r)) for r in roles]
    await role_cache.set(cache_key, serialized)
    print("[Cache] list_roles: cached roles list")

    return [RolePublic.from_orm(r) for r in roles]   # ✅


async def get_role(db: Session, role_id: int) -> Optional[RolePublic]:
    cache_key = f"id:{role_id}"
    cached = await role_cache.get(cache_key)
    if cached:
        print(f"[Cache] get_role: fetched role id={role_id} from cache")
        return RolePublic(**cached)   # ✅

    print(f"[DB] get_role: fetching role id={role_id} from database")
    role = role_crud.get_role(db, role_id)
    if role:
        serialized = jsonable_encoder(RolePublic.from_orm(role))
        await role_cache.set(cache_key, serialized)
        print(f"[Cache] get_role: cached role id={role_id}")
        return RolePublic.from_orm(role)
    return None


async def create_role(db: Session, payload: RoleCreate) -> Role:
    print("[DB] create_role: creating a new role")
    try:
        # ساخت رول اصلی
        role = role_crud.create_role(db, payload)

        # ساخت RolePermission برای هر permission_id
        for pid in payload.permission_ids:
            rp = RolePermission(role_id=role.id, permission_id=pid)
            db.add(rp)
        db.commit()
        db.refresh(role)

    except IntegrityError:
        print("[Error] create_role: IntegrityError, role name might exist")
        raise

    await role_cache.invalidate_all()
    print("[Cache] create_role: invalidated all role caches")
    return role


async def update_role(db: Session, role_id: int, payload: RoleUpdate) -> Optional[Role]:
    print(f"[DB] update_role: updating role id={role_id}")
    role = role_crud.get_role(db, role_id)
    if not role:
        print(f"[DB] update_role: role id={role_id} not found")
        return None
    try:
        updated_role = role_crud.update_role(db, role, payload)
    except IntegrityError:
        print(f"[Error] update_role: IntegrityError updating role id={role_id}")
        raise
    await role_cache.invalidate(f"id:{role_id}")
    await role_cache.invalidate_all()
    print(f"[Cache] update_role: invalidated cache for role id={role_id} and all lists")
    return updated_role


async def update_role_name(db: Session, role_id: int, new_name: str) -> Optional[Role]:
    print(f"[DB] update_role_name: updating name of role id={role_id}")
    role = role_crud.get_role(db, role_id)
    if not role:
        print(f"[DB] update_role_name: role id={role_id} not found")
        return None
    try:
        updated_role = role_crud.update_role_name(db, role, new_name)
    except IntegrityError:
        print(f"[Error] update_role_name: IntegrityError updating name for role id={role_id}")
        raise
    await role_cache.invalidate(f"id:{role_id}")
    await role_cache.invalidate_all()
    print(f"[Cache] update_role_name: invalidated cache for role id={role_id} and all lists")
    return updated_role


async def delete_role(db: Session, role_id: int) -> bool:
    print(f"[DB] delete_role: deleting role id={role_id}")
    role = role_crud.get_role(db, role_id)
    if not role:
        print(f"[DB] delete_role: role id={role_id} not found")
        return False
    role_crud.delete_role(db, role)
    await role_cache.invalidate(f"id:{role_id}")
    await role_cache.invalidate_all()
    print(f"[Cache] delete_role: invalidated cache for role id={role_id} and all lists")
    return True
