# app/sms/manager.py

from sqlalchemy.orm import Session
from app.models.sms_provider import SMSProvider
from app.sms.smsir import SMSIRService
from app.sms.melipayamak import MeliPayamakService

class SMSManager:
    def __init__(self, db: Session):
        self.db = db

    def get_active_provider(self):
        provider = self.db.query(SMSProvider).filter_by(is_active=True).first()
        if not provider:
            raise Exception("No active SMS provider found")
        return provider

    def get_service(self):
        provider = self.get_active_provider()
        name = provider.name.lower()

        if name == "smsir":
            return SMSIRService(api_key=provider.api_key, sender=provider.sender)
        elif name == "melipayamak":
            return MeliPayamakService(api_key=provider.api_key, sender=provider.sender)
        else:
            raise Exception(f"Unsupported provider: {name}")

    def send_sms(self, to: str, message: str):
        service = self.get_service()
        return service.send(to, message)
