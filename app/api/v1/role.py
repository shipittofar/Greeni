from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.schemas.role import RoleCreate, RoleUpdate, RolePublic, RoleNameUpdate
from app.models.user import User
from app.models.role import Role
from app.schemas.common import BaseAPIResponse

from app.bll import role_service

router = APIRouter(tags=["Roles"])


@router.post(
    "/",
    response_model=BaseAPIResponse[RolePublic],
    summary="Create a new role",
    responses={
        400: {"description": "Bad Request – Invalid input"},
        409: {"description": "Conflict – Role name already exists"},
        500: {"description": "Internal Server Error"},
    },
)
async def create_role(
    role: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        db_role = await role_service.create_role(db, role)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role with this name already exists",
        )
    return BaseAPIResponse(result=db_role)


@router.get(
    "/",
    response_model=BaseAPIResponse[List[RolePublic]],
    summary="Get all roles",
    responses={500: {"description": "Internal Server Error"}},
)
async def list_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roles = await role_service.list_roles(db)
    return BaseAPIResponse(result=roles)


@router.put(
    "/{role_id}",
    response_model=BaseAPIResponse[RolePublic],
    summary="Update a role",
    responses={
        404: {"description": "Role not found"},
        400: {"description": "Bad Request"},
        409: {"description": "Conflict – Role name already exists"},
        500: {"description": "Internal Server Error"},
    },
)
async def update_role(
    role_id: int,
    update: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_role = await role_service.update_role(db, role_id, update)
    if not updated_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return BaseAPIResponse(result=updated_role)


@router.patch(
    "/{role_id}/name",
    response_model=BaseAPIResponse[RolePublic],
    summary="Update role name only",
    responses={
        404: {"description": "Role not found"},
        409: {"description": "Role name already exists"},
        500: {"description": "Internal Server Error"},
    },
)
async def update_role_name(
    role_id: int,
    update: RoleNameUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_role = await role_service.update_role_name(db, role_id, update.name)
    if not updated_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return BaseAPIResponse(result=updated_role)


@router.delete(
    "/{role_id}",
    response_model=BaseAPIResponse[None],
    summary="Delete a role",
    responses={
        404: {"description": "Role not found"},
        403: {"description": "Not authorized"},
        500: {"description": "Internal Server Error"},
    },
)
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can delete roles")

    deleted = await role_service.delete_role(db, role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")

    return BaseAPIResponse(result=None)
