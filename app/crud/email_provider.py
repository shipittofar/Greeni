# app/crud/email_provider.py
from sqlalchemy.orm import Session
from app.models.email_provider import EmailProvider
from app.schemas.email_provider import EmailProviderCreate

class CRUDEmailProvider:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: EmailProviderCreate) -> EmailProvider:
        db_obj = EmailProvider(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_active(self) -> EmailProvider:
        return self.db.query(EmailProvider).filter_by(is_active=True).first()

    def list(self, skip: int = 0, limit: int = 100):
        return self.db.query(EmailProvider).offset(skip).limit(limit).all()

    def deactivate(self, provider_id: int):
        provider = self.db.query(EmailProvider).filter(EmailProvider.id == provider_id).first()
        if provider:
            provider.is_active = False
            self.db.commit()
            self.db.refresh(provider)
        return provider
