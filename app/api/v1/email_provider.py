# app/api/v1/email_provider.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.email_provider import EmailProviderCreate, EmailProviderOut
from app.crud.email_provider import CRUDEmailProvider

router = APIRouter()



@router.post("/", response_model=EmailProviderOut, status_code=status.HTTP_201_CREATED)
def create_email_provider(data: EmailProviderCreate, db: Session = Depends(get_db)):
    crud = CRUDEmailProvider(db)

    if data.is_active:
        active_provider = crud.get_active()
        if active_provider:
            active_provider.is_active = False
            db.commit()

    return crud.create(data)


@router.get("/", response_model=list[EmailProviderOut])
def list_email_providers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    crud = CRUDEmailProvider(db)
    return crud.list(skip=skip, limit=limit)


@router.get("/active", response_model=EmailProviderOut | None)
def get_active_email_provider(db: Session = Depends(get_db)):
    crud = CRUDEmailProvider(db)
    return crud.get_active()


@router.patch("/{provider_id}/deactivate", response_model=EmailProviderOut)
def deactivate_email_provider(provider_id: int, db: Session = Depends(get_db)):
    crud = CRUDEmailProvider(db)
    provider = crud.deactivate(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider
