# app/bll/tag_service.py
from sqlalchemy.orm import Session
from app.cache.base_cache import BaseCache
from app.crud import tag as crud_tag
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate
from app.utils.sqlalchemy_to_dict import sqlalchemy_to_dict as stc

tag_cache = BaseCache(namespace="tags", expire_seconds=36000)


async def list_tags(db: Session, skip: int = 0, limit: int = 300) -> list[Tag]:
    cache_key = f"list:{skip}:{limit}"
    cached = await tag_cache.get(cache_key)
    if cached:
        print("[Cache] list_tags: fetched from Redis cache")
        return [Tag(**item) for item in cached]

    print("[DB] list_tags: fetching from database")
    tags = crud_tag.list_tags(db, skip=skip, limit=limit)
    await tag_cache.set(cache_key, [stc(t) for t in tags])
    print("[Cache] list_tags: cached result set")
    return tags


async def get_tag_by_id(db: Session, tag_id: int) -> Tag | None:
    cache_key = f"id:{tag_id}"
    cached = await tag_cache.get(cache_key)
    if cached:
        print(f"[Cache] get_tag_by_id: fetched tag {tag_id} from Redis cache")
        return Tag(**cached)

    print(f"[DB] get_tag_by_id: fetching tag {tag_id} from database")
    tag = crud_tag.get_tag_by_id(db, tag_id)
    if tag:
        await tag_cache.set(cache_key, stc(tag))
        print(f"[Cache] get_tag_by_id: cached tag {tag_id}")
    return tag


async def create_tag(db: Session, payload: TagCreate, user_id: int) -> Tag:
    print("[DB] create_tag: creating new tag")
    tag = crud_tag.create_tag(db, payload, user_id)
    await tag_cache.invalidate_all()
    print("[Cache] create_tag: invalidated all cache")
    return tag


async def update_tag(db: Session, tag: Tag, payload: TagUpdate, user_id: int) -> Tag:
    print(f"[DB] update_tag: updating tag {tag.id}")
    tag = crud_tag.update_tag(db, tag, payload, user_id)
    await tag_cache.invalidate(f"id:{tag.id}")
    await tag_cache.invalidate_all()
    print(f"[Cache] update_tag: invalidated cache for tag {tag.id} and all lists")
    return tag


async def delete_tag(db: Session, tag: Tag):
    print(f"[DB] delete_tag: deleting tag {tag.id}")
    await tag_cache.invalidate(f"id:{tag.id}")
    await tag_cache.invalidate_all()
    crud_tag.delete_tag(db, tag)
    print(f"[Cache] delete_tag: invalidated cache for tag {tag.id} and all lists")
