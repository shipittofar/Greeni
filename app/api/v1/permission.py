from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models.user import User
from app.schemas.permission import PermissionCreate, PermissionPublic, PermissionUpdate
from app.schemas.common import BaseAPIResponse
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.crud import permission as crud_permission

router = APIRouter(tags=["Permissions"])


@router.post("/", response_model=BaseAPIResponse[PermissionPublic], summary="Create a new permission")
def create_permission(
    permission: PermissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    perm = crud_permission.create_permission(db, permission)
    return BaseAPIResponse(result=perm)


@router.get("/", response_model=BaseAPIResponse[List[PermissionPublic]], summary="Get all permissions")
def list_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    perms = crud_permission.list_permissions(db)
    return BaseAPIResponse(result=perms)


@router.put("/{permission_id}", response_model=BaseAPIResponse[PermissionPublic], summary="Update a permission")
def update_permission(
    permission_id: int,
    update: PermissionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    perm = crud_permission.update_permission(db, permission_id, update)
    return BaseAPIResponse(result=perm)


@router.delete("/{permission_id}", response_model=BaseAPIResponse[None], summary="Delete a permission")
def delete_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    crud_permission.delete_permission(db, permission_id, current_user.is_superuser)
    return BaseAPIResponse(result=None)
