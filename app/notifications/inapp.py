# app/notifications/inapp.py
from app.crud.inapp_notification import CRUDInAppNotification
from app.schemas.inapp_notification import InAppNotificationCreate, InAppNotificationRead
from sqlalchemy.orm import Session
from app.api.v1.ws.notifications import send_to_user
import asyncio
import redis
import json
from app.core.config import settings


class InAppService:
    def __init__(self, db: Session):
        self.db = db
        self.redis = redis.Redis.from_url(settings.REDIS_URL)

    def save_inapp(self, user_id, title, message, data=None):
        notif_dict = {
            "user_id": str(user_id),
            "title": title,
            "message": message,
            "data": data,
        }
        created = CRUDInAppNotification(self.db).create(InAppNotificationCreate(**notif_dict))
        notif_schema = InAppNotificationRead.from_orm(created)

        # 📨 Publish to Redis instead of direct WS send
        self.redis.publish("notifications", json.dumps(notif_schema.model_dump()))

        return created
