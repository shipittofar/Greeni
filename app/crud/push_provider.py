# app/crud/push_provider.py
from sqlalchemy.orm import Session
from app.models.push_provider import PushProvider
from app.schemas.push_provider import PushProviderCreate, PushProviderUpdate

class CRUDPushProvider:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: PushProviderCreate) -> PushProvider:
        db_obj = PushProvider(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_active(self) -> PushProvider:
        return self.db.query(PushProvider).filter_by(is_active=True).first()

    def list(self, skip: int = 0, limit: int = 100):
        return self.db.query(PushProvider).offset(skip).limit(limit).all()

    def deactivate(self, provider_id: int):
        provider = self.db.query(PushProvider).filter(PushProvider.id == provider_id).first()
        if provider:
            provider.is_active = False
            self.db.commit()
            self.db.refresh(provider)
        return provider

    def update(self, provider_id: int, obj_in: PushProviderUpdate):
        provider = self.db.query(PushProvider).filter(PushProvider.id == provider_id).first()
        if not provider:
            return None
        update_data = obj_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(provider, key, value)
        self.db.commit()
        self.db.refresh(provider)
        return provider
