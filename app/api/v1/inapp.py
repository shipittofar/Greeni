# app/api/v1/inapp.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.crud.inapp_notification import CRUDInAppNotification
from app.schemas.inapp_notification import (
    InAppNotificationCreate,
    InAppNotificationResponse,
    InAppNotificationListResponse
)

router = APIRouter(tags=["In-App Notifications"])


# 🔹 Create a new notification
@router.post("/", response_model=dict)
def create_inapp_notification(
    data: InAppNotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new in-app notification"""
    crud = CRUDInAppNotification(db)
    notif = crud.create(data)
    return {
        "message": "Notification created successfully",
        "notification": notif.to_dict()
    }


# 🔹 Get user notifications with pagination
@router.get("/{user_id}", response_model=dict)
def get_user_notifications(
    user_id: int,  # Changed from str to int
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get all notifications for a user"""
    crud = CRUDInAppNotification(db)
    notifications = crud.get_user_notifications(user_id, skip, limit)
    total_count = crud.get_user_notifications_count(user_id)
    
    return {
        "count": total_count,
        "skip": skip,
        "limit": limit,
        "results": [notif.to_dict() for notif in notifications]
    }


# 🔹 Get recent notifications
@router.get("/recent/{user_id}", response_model=dict)
def get_recent_notifications(
    user_id: int,  # Changed from str to int
    limit: int = 3,
    db: Session = Depends(get_db)
):
    """Get recent notifications for a user"""
    crud = CRUDInAppNotification(db)
    notifications = crud.get_recent_notifications(user_id, limit)
    
    return {
        "results": [notif.to_dict() for notif in notifications]
    }


# 🔹 Get unread notification count
@router.get("/unread/count/{user_id}", response_model=dict)
def get_unread_count(
    user_id: int,  # Changed from str to int
    db: Session = Depends(get_db)
):
    """Get count of unread notifications for a user"""
    crud = CRUDInAppNotification(db)
    count = crud.get_unread_notifications_count(user_id)
    
    return {
        "user_id": user_id,
        "unread_count": count
    }


# 🔹 Mark notification as read
@router.patch("/mark-read/{notification_id}", response_model=dict)
def mark_notification_as_read(
    notification_id: int,  # Changed from str to int
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    crud = CRUDInAppNotification(db)
    notif = crud.mark_as_read_by_id(notification_id)
    
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {
        "message": "Notification marked as read",
        "notification": notif.to_dict()
    }


# 🔹 Delete a specific notification
@router.delete("/{notification_id}", response_model=dict)
def delete_notification(
    notification_id: int,  # Changed from str to int
    db: Session = Depends(get_db)
):
    """Delete a specific notification"""
    crud = CRUDInAppNotification(db)
    deleted = crud.delete_by_id(notification_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {
        "message": "Notification deleted successfully",
        "deleted_id": notification_id
    }


# 🔹 Delete all notifications for a user
@router.delete("/user/{user_id}/all", response_model=dict)
def delete_all_user_notifications(
    user_id: int,  # Changed from str to int
    db: Session = Depends(get_db)
):
    """Delete all notifications for a user"""
    crud = CRUDInAppNotification(db)
    result = crud.delete_all_by_user(user_id)
    
    return {
        "message": "All user notifications deleted",
        **result
    }


# 🔹 Mark all notifications as read
@router.patch("/user/{user_id}/mark-all-read", response_model=dict)
def mark_all_notifications_as_read(
    user_id: int,  # Changed from str to int
    db: Session = Depends(get_db)
):
    """Mark all notifications for a user as read"""
    crud = CRUDInAppNotification(db)
    result = crud.mark_all_as_read(user_id)
    
    return {
        "message": "All notifications marked as read",
        "updated_count": result
    }










# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.dependencies.db import get_db
# from app.crud.inapp_notification import CRUDInAppNotification
# from app.schemas.inapp_notification import InAppNotificationCreate
# from fastapi import HTTPException



# router = APIRouter(tags=["In-App Notifications"])

# @router.post("/")
# def create_inapp_notification(data: InAppNotificationCreate, db: Session = Depends(get_db)):
#     crud = CRUDInAppNotification(db)
#     return crud.create(data)

# @router.get("/{user_id}")
# def get_user_notifications(user_id: str, db: Session = Depends(get_db)):
#     crud = CRUDInAppNotification(db)
#     return crud.get_user_notifications(user_id)

# @router.patch("/mark-read/{notification_id}")
# def mark_notification_as_read(notification_id: str, db: Session = Depends(get_db)):
#     crud = CRUDInAppNotification(db)
#     notif = crud.mark_as_read_by_id(notification_id)
#     if not notif:
#         raise HTTPException(status_code=404, detail="Notification not found")
#     return notif


# @router.delete("/user/{user_id}")
# def delete_all_user_notifications(user_id: str, db: Session = Depends(get_db)):
#     crud = CRUDInAppNotification(db)
#     result = crud.delete_all_by_user(user_id)
#     return {"message": "All user notifications deleted", **result}