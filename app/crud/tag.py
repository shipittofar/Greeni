# app/crud/tag.py
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate


def create_tag(db: Session, payload: TagCreate, user_id: int | None = None) -> Tag:
    data = payload.model_dump()
    tag = Tag(**data)
    if user_id:
        tag.created_by = user_id
        tag.updated_by = user_id
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def update_tag(db: Session, tag: Tag, payload: TagUpdate, user_id: int | None = None) -> Tag:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(tag, key, value)
    tag.updated_at = datetime.utcnow()
    if user_id:
        tag.updated_by = user_id
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag: Tag):
    db.delete(tag)
    db.commit()


def get_tag_by_id(db: Session, tag_id: int) -> Tag | None:
    return db.query(Tag).filter(Tag.id == tag_id).first()


def list_tags(db: Session, skip: int = 0, limit: int = 100) -> list[Tag]:
    return db.query(Tag).offset(skip).limit(limit).all()
