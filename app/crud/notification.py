# app/crud/crud_notification.py
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

class CRUDNotification:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: NotificationCreate) -> Notification:
        db_obj = Notification(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get(self, notification_id: int) -> Notification:
        return self.db.query(Notification).filter(Notification.id == notification_id).first()

    def list(self, skip: int = 0, limit: int = 100):
        return self.db.query(Notification).offset(skip).limit(limit).all()

    def update_status(self, notification_id: int, status: str, error_message: str = None):
        notif = self.get(notification_id)
        if notif:
            notif.status = status
            notif.error_message = error_message
            self.db.commit()
            self.db.refresh(notif)
        return notif

    def delete(self, notification_id: int):
        notif = self.get(notification_id)
        if notif:
            self.db.delete(notif)
            self.db.commit()
        return notif
