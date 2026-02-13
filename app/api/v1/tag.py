from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.tag import TagCreate, TagUpdate, TagPublic
from app.schemas.common import BaseAPIResponse
from app.models.user import User
from app.models.tag import Tag as TagModel
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.bll import tag_service
from app.crud.tag import get_tag_by_id as crud_get_tag_by_id
from app.crud import tag as crud_tag

router = APIRouter(tags=["Tags"])


@router.get("/", response_model=BaseAPIResponse[List[TagPublic]])
async def list_tags(db: Session = Depends(get_db)):
    tags = await tag_service.list_tags(db)
    return BaseAPIResponse(result=tags)


@router.get("/{tag_id}", response_model=BaseAPIResponse[TagPublic])
async def get_tag_by_id(tag_id: int, db: Session = Depends(get_db)):
    tag = await tag_service.get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return BaseAPIResponse(result=tag)


@router.post("/", response_model=BaseAPIResponse[TagPublic])
async def create_tag(
    payload: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = await tag_service.create_tag(db, payload, current_user.id)
    return BaseAPIResponse(result=tag)


@router.patch("/{tag_id}", response_model=BaseAPIResponse[TagPublic])
async def update_tag(
    tag_id: int,
    updates: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = crud_tag.get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag = await tag_service.update_tag(db, tag, updates, current_user.id)
    return BaseAPIResponse(result=tag)


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = crud_tag.get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await tag_service.delete_tag(db, tag)
    return BaseAPIResponse(message="Tag deleted")
