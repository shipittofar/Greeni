# app/crud/inapp_notification.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.inapp_notification import InAppNotification
from app.schemas.inapp_notification import InAppNotificationCreate


class CRUDInAppNotification:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: InAppNotificationCreate) -> InAppNotification:
        """Create a new notification"""
        db_obj = InAppNotification(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_user_notifications(
        self,
        user_id: int,  # Changed from str to int
        skip: int = 0,
        limit: int = 100
    ) -> list:
        """Get all notifications for a user"""
        return (
            self.db.query(InAppNotification)
            .filter_by(user_id=user_id)
            .order_by(InAppNotification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_notifications_count(self, user_id: int) -> int:  # Changed from str to int
        """Get total count of user notifications"""
        return (
            self.db.query(func.count(InAppNotification.id))
            .filter_by(user_id=user_id)
            .scalar()
        )

    def get_recent_notifications(
        self,
        user_id: int,  # Changed from str to int
        limit: int = 3
    ) -> list:
        """Get recent notifications for a user"""
        return (
            self.db.query(InAppNotification)
            .filter(InAppNotification.user_id == user_id)
            .order_by(InAppNotification.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_unread_notifications_count(self, user_id: int) -> int:  # Changed from str to int
        """Get count of unread notifications for a user"""
        return (
            self.db.query(func.count(InAppNotification.id))
            .filter(
                InAppNotification.user_id == user_id,
                InAppNotification.is_read == False
            )
            .scalar()
        )

    def get_unread_count(self, user_id: int) -> int:  # Added this method (alias)
        """Get count of unread notifications for a user"""
        return self.get_unread_notifications_count(user_id)

    def mark_as_read_by_id(self, notification_id: int) -> InAppNotification:  # Changed from str to int
        """Mark a notification as read"""
        notif = (
            self.db.query(InAppNotification)
            .filter(InAppNotification.id == notification_id)
            .first()
        )
        if notif:
            notif.is_read = True
            self.db.commit()
            self.db.refresh(notif)
        return notif

    def mark_all_as_read(self, user_id: int) -> int:  # Changed from str to int
        """Mark all notifications for a user as read"""
        updated = (
            self.db.query(InAppNotification)
            .filter(
                InAppNotification.user_id == user_id,
                InAppNotification.is_read == False
            )
            .update({"is_read": True})
        )
        self.db.commit()
        return updated

    def delete_by_id(self, notification_id: int) -> bool:  # Changed from str to int
        """Delete a notification"""
        notif = (
            self.db.query(InAppNotification)
            .filter(InAppNotification.id == notification_id)
            .first()
        )
        if not notif:
            return False
        self.db.delete(notif)
        self.db.commit()
        return True

    def delete_all_by_user(self, user_id: int) -> dict:  # Changed from str to int
        """Delete all notifications for a user"""
        deleted_count = (
            self.db.query(InAppNotification)
            .filter(InAppNotification.user_id == user_id)
            .delete()
        )
        self.db.commit()
        return {"deleted": deleted_count}

    def delete_read_notifications(self, user_id: int, days: int = 30) -> dict:  # Changed from str to int
        """Delete old read notifications older than N days"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = (
            self.db.query(InAppNotification)
            .filter(
                InAppNotification.user_id == user_id,
                InAppNotification.is_read == True,
                InAppNotification.created_at < cutoff_date
            )
            .delete()
        )
        self.db.commit()
        return {"deleted": deleted_count}