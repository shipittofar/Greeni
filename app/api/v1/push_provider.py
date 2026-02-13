# app/api/v1/push_provider.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.push_provider import PushProviderCreate, PushProviderOut, PushProviderUpdate
from app.models.push_provider import PushProvider
from app.dependencies.db import get_db
from app.crud.push_provider import CRUDPushProvider

router = APIRouter()

@router.post("/", response_model=PushProviderOut)
def create_push_provider(payload: PushProviderCreate, db: Session = Depends(get_db)):
    crud = CRUDPushProvider(db)
    return crud.create(payload)

@router.get("/", response_model=List[PushProviderOut])
def list_push_providers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    crud = CRUDPushProvider(db)
    return crud.list(skip=skip, limit=limit)

@router.get("/active", response_model=PushProviderOut)
def get_active_push_provider(db: Session = Depends(get_db)):
    crud = CRUDPushProvider(db)
    provider = crud.get_active()
    if not provider:
        raise HTTPException(status_code=404, detail="No active push provider found")
    return provider

@router.put("/{provider_id}", response_model=PushProviderOut)
def update_push_provider(provider_id: int, payload: PushProviderUpdate, db: Session = Depends(get_db)):
    crud = CRUDPushProvider(db)
    provider = crud.update(provider_id, payload)
    if not provider:
        raise HTTPException(status_code=404, detail="Push provider not found")
    return provider

@router.post("/{provider_id}/deactivate", response_model=PushProviderOut)
def deactivate_push_provider(provider_id: int, db: Session = Depends(get_db)):
    crud = CRUDPushProvider(db)
    provider = crud.deactivate(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Push provider not found")
    return provider
