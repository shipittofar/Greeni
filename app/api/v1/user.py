import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserPublic, UserUpdate, UserBasicUpdate
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.crud import user as crud_user
from app.schemas.common import BaseAPIResponse

router = APIRouter(tags=["Users"])

logger = logging.getLogger("app.users")

@router.post(
    "/",
    response_model=BaseAPIResponse[UserPublic],
    summary="Create a new user",
    responses={
        400: {"description": "Bad Request – Invalid input"},
        409: {"description": "Conflict – Email or phone number already exists"},
        500: {"description": "Internal Server Error"},
    }
)
def create_user(user_in: UserCreate,current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Attempting to create user with email={user_in.email}, phone={user_in.phone_number}")
    
    existing_email = crud_user.get_user_by_email(db, user_in.email)
    existing_phone_number = crud_user.get_user_by_phone_number(db, user_in.phone_number)
    
    if existing_email:
        logger.warning(f"Conflict: Email already exists: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    if existing_phone_number:
        logger.warning(f"Conflict: Phone number already exists: {user_in.phone_number}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this phone number already exists"
        )

    new_user = crud_user.create_user(db, user_in, current_user=current_user)

    logger.info(f"User created successfully: id={new_user.id}")
    return BaseAPIResponse(result=new_user)


@router.get(
    "/{user_id}",
    response_model=BaseAPIResponse[UserPublic],
    summary="Get user by ID",
    responses={
        404: {"description": "User not found"},
        500: {"description": "Internal Server Error"},
    }
)
def get_user(user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Fetching user by id={user_id}")
    user_obj = crud_user.get_user_by_id(db, user_id)
    if not user_obj:
        logger.warning(f"User not found: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User retrieved: id={user_obj.id}")
    return BaseAPIResponse(result=user_obj)


@router.put(
    "/{user_id}",
    response_model=BaseAPIResponse[UserPublic],
    summary="Update user info",
    responses={
        404: {"description": "User not found"},
        400: {"description": "Bad Request"},
        500: {"description": "Internal Server Error"},
    }
)
def update_user(user_id: int, updates: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Updating user id={user_id} with data={updates.dict()}")
    db_user = crud_user.get_user_by_id(db, user_id)
    if not db_user:
        logger.warning(f"User not found for update: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    updated = crud_user.update_user(db, db_user, updates, current_user=current_user)

    logger.info(f"User updated successfully: id={updated.id}")
    return BaseAPIResponse(result=updated)


@router.patch(
    "/{user_id}/basic",
    response_model=BaseAPIResponse[UserPublic],
    summary="Update basic user info (first name, last name, email, phone)",
    responses={
        404: {"description": "User not found"},
        400: {"description": "Bad Request"},
        500: {"description": "Internal Server Error"},
    }
)
def update_basic_user(user_id: int, updates: UserBasicUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Updating basic info for user id={user_id} with data={updates.dict()}")
    db_user = crud_user.get_user_by_id(db, user_id)
    if not db_user:
        logger.warning(f"User not found for basic update: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    updated = crud_user.update_user(db, db_user, updates, current_user=current_user)

    logger.info(f"Basic info updated successfully for user id={updated.id}")
    return BaseAPIResponse(result=updated)


@router.post(
    "/{user_id}/login",
    response_model=BaseAPIResponse[dict],
    summary="Record a login timestamp for user",
    responses={
        404: {"description": "User not found"},
        500: {"description": "Internal Server Error"},
    }
)
def register_login(user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Recording login for user id={user_id}")
    user_obj = crud_user.get_user_by_id(db, user_id)
    if not user_obj:
        logger.warning(f"User not found for login recording: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = crud_user.add_login_timestamp(db, user_obj)
    logger.info(f"Login recorded for user id={updated_user.id}")
    return BaseAPIResponse(result={
        "msg": "Login recorded",
        "last_logins": updated_user.last_logins
    })


@router.get(
    "/by-permission/{permission_name}",
    response_model=BaseAPIResponse[List[UserPublic]],
    summary="Get users with a specific permission",
    responses={
        404: {"description": "No users found with this permission"},
        500: {"description": "Internal Server Error"},
    }
)
def get_users_by_permission(
    permission_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Fetching users with permission='{permission_name}'")
    from app.crud.user import get_users_with_permission
    users = get_users_with_permission(db, permission_name)
    if not users:
        logger.warning(f"No users found with permission: {permission_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No users found with permission '{permission_name}'"
        )
    logger.info(f"Found {len(users)} users with permission '{permission_name}'")
    return BaseAPIResponse(result=users)


@router.get(
    "/",
    response_model=BaseAPIResponse[List[UserPublic]],
    summary="Get all users",
    responses={
        500: {"description": "Internal Server Error"},
    }
)
def get_all_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info("Fetching all users")
    users = crud_user.get_all_users(db)
    logger.info(f"Total users retrieved: {len(users)}")
    return BaseAPIResponse(result=users)

@router.delete(
    "/{user_id}",
    response_model=BaseAPIResponse[dict],
    summary="Delete user permanently",
    responses={
        404: {"description": "User not found"},
        500: {"description": "Internal Server Error"},
    }
)
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Attempting to delete user {user_id}")
    
    db_user = crud_user.get_user_by_id(db, user_id)
    if not db_user:
        logger.warning(f"User {user_id} not found for deletion")
        raise HTTPException(status_code=404, detail="User not found")
    
    crud_user.delete_user(db, db_user, current_user=current_user)

    logger.info(f"User {user_id} deleted permanently")
    
    return BaseAPIResponse(result={"msg": f"User {user_id} deleted permanently"})
