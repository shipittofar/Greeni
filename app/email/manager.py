# app/email/manager.py
from sqlalchemy.orm import Session
from app.models.email_provider import EmailProvider
from app.email.smtp_service import SMTPEmailService

class EmailManager:
    def __init__(self, db: Session):
        self.db = db

    def get_active_provider(self) -> EmailProvider:
        provider = self.db.query(EmailProvider).filter_by(is_active=True).first()
        if not provider:
            raise Exception("No active email provider found")
        return provider

    def get_service(self):
        provider = self.get_active_provider()
        return SMTPEmailService(
            username=provider.username,
            password=provider.password,
            host=provider.host,
            port=provider.port
        )

    def send_email(self, to: str, subject: str, body: str):
        service = self.get_service()
        return service.send(to, subject, body)
