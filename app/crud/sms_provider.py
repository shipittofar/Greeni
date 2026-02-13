from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.sms_provider import SMSProvider
from app.schemas.sms_provider import SMSProviderCreate, SMSProviderUpdate, SMSProviderIsActiveUpdate

class CRUDSMSProvider:

    @staticmethod
    def get_all(db: Session):
        return db.query(SMSProvider).all()

    @staticmethod
    def get_count_info(db: Session):
        total = db.query(SMSProvider).count()
        active = db.query(SMSProvider).filter_by(is_active=True).count()
        inactive = total - active
        return {
            "total_providers": total,
            "active_providers": active,
            "inactive_providers": inactive
        }

    @staticmethod
    def get_by_name(db: Session, provider_name: str):
        provider = db.query(SMSProvider).filter_by(name=provider_name).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        return provider

    @staticmethod
    def get_active(db: Session):
        provider = db.query(SMSProvider).filter_by(is_active=True).first()
        if not provider:
            return None
        return provider

    @staticmethod
    def create(db: Session, data: SMSProviderCreate):
        existing = db.query(SMSProvider).filter_by(name=data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Provider with this name already exists")

        if data.is_active:
            db.query(SMSProvider).update({SMSProvider.is_active: False})

        provider = SMSProvider(
            name=data.name,
            api_key=data.api_key,
            sender=data.sender,
            is_active=data.is_active,
        )
        db.add(provider)
        db.commit()
        db.refresh(provider)
        return provider

    @staticmethod
    def update_is_active(db: Session, provider_name: str, data: SMSProviderIsActiveUpdate):
        provider = CRUDSMSProvider.get_by_name(db, provider_name)

        if data.is_active is True:
            db.query(SMSProvider).update({SMSProvider.is_active: False})

        for key, value in data.dict(exclude_unset=True).items():
            setattr(provider, key, value)

        db.commit()
        db.refresh(provider)
        return provider

    @staticmethod
    def update(db: Session, provider_name: str, data: SMSProviderUpdate):
        provider = CRUDSMSProvider.get_by_name(db, provider_name)

        if data.is_active is True:
            db.query(SMSProvider).update({SMSProvider.is_active: False})

        for key, value in data.dict(exclude_unset=True).items():
            setattr(provider, key, value)

        db.commit()
        db.refresh(provider)
        return provider

    @staticmethod
    def delete(db: Session, provider_name: str):
        provider = CRUDSMSProvider.get_by_name(db, provider_name)
        db.delete(provider)
        db.commit()
        return
