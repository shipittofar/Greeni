# app/notifications/manager.py

from app.sms.manager import SMSManager
from app.email.manager import EmailManager
from app.notifications.templates import render_template
from app.notifications.push import PushService
from app.notifications.inapp import InAppService
from sqlalchemy.orm import Session

class NotificationManager:
    def __init__(self, db: Session):
        self.db = db

    def send(self, payload: dict):
        channel = payload["channel"]
        recipient = payload["recipient"]
        template = payload.get("template")
        data = payload.get("data", {})

        rendered = render_template(template, data)

        if channel == "sms":
            manager = SMSManager(self.db)
            return manager.send_sms(recipient, rendered["body"])

        elif channel == "email":
            manager = EmailManager(self.db)
            return manager.send_email(recipient, rendered.get("subject", ""), rendered.get("body", ""))

        elif channel == "push":
            manager = PushService(self.db)
            return manager.send_push(recipient, rendered.get("title", ""), rendered.get("body", ""))

        elif channel == "inapp":
            manager = InAppService(self.db)
            return manager.save_inapp(recipient, rendered.get("title", ""), rendered.get("body", ""))

        else:
            raise ValueError(f"Unsupported channel: {channel}")
