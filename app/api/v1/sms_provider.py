from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.sms_provider import SMSProviderCreate, SMSProviderUpdate, SMSProviderIsActiveUpdate
from app.crud.sms_provider import CRUDSMSProvider

router = APIRouter()

@router.get("/")
def list_sms_providers(db: Session = Depends(get_db)):
    return CRUDSMSProvider.get_all(db)

@router.get("/countinfo")
def sms_providers_status(db: Session = Depends(get_db)):
    return CRUDSMSProvider.get_count_info(db)

@router.get("/active", summary="Get the currently active SMS provider")
def get_active_sms_provider(db: Session = Depends(get_db)):
    active_provider = CRUDSMSProvider.get_active(db)
    if not active_provider:
        return {"active_provider": None}
    return {
        "active_provider": active_provider.name,
        "is_active": active_provider.is_active
    }

@router.get("/{provider_name}/status")
def get_sms_provider_status(provider_name: str, db: Session = Depends(get_db)):
    provider = CRUDSMSProvider.get_by_name(db, provider_name)
    return {"provider_name": provider.name, "is_active": provider.is_active}

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_sms_provider(data: SMSProviderCreate, db: Session = Depends(get_db)):
    return CRUDSMSProvider.create(db, data)

@router.patch("/{provider_name}/set-active")
def update_sms_provider_is_active(provider_name: str, data: SMSProviderIsActiveUpdate, db: Session = Depends(get_db)):
    return CRUDSMSProvider.update_is_active(db, provider_name, data)

@router.patch("/{provider_name}")
def update_sms_provider(provider_name: str, data: SMSProviderUpdate, db: Session = Depends(get_db)):
    return CRUDSMSProvider.update(db, provider_name, data)

@router.get("/{provider_name}")
def get_sms_provider(provider_name: str, db: Session = Depends(get_db)):
    return CRUDSMSProvider.get_by_name(db, provider_name)

@router.delete("/{provider_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sms_provider(provider_name: str, db: Session = Depends(get_db)):
    return CRUDSMSProvider.delete(db, provider_name)
