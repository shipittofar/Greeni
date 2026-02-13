# app/api/v1/notifications.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.notification import NotificationCreate
from app.schemas.inapp_notification import InAppNotificationRead
from app.dependencies.auth import get_current_user
from app.tasks.notifications_tasks import send_notification_task
from app.crud.inapp_notification import CRUDInAppNotification

router = APIRouter()


@router.post("/")
def send_notification(payload: NotificationCreate):
    if hasattr(payload, "dict"):
        payload = payload.dict()
    send_notification_task.delay(payload)
    return {"status": "queued"}


@router.get("/recent", response_model=list[InAppNotificationRead])
def get_recent_notifications(
    db: Session = Depends(get_db), user=Depends(get_current_user)
):
    crud = CRUDInAppNotification(db)
    return crud.get_recent_notifications(user.id)


@router.get("/all", response_model=list[InAppNotificationRead])
def get_all_notifications(
    db: Session = Depends(get_db), user=Depends(get_current_user)
):
    crud = CRUDInAppNotification(db)
    return crud.get_user_notifications(user.id)
