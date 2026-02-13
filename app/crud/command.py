from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.command import Command
from app.schemas.command import CommandCreate, CommandUpdate


class CRUDCommand:
    def get(self, db: Session, id: int) -> Optional[Command]:
        return db.query(Command).filter(Command.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Command]:
        return db.query(Command).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CommandCreate) -> Command:
        db_obj = Command(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Command, obj_in: CommandUpdate) -> Command:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> Optional[Command]:
        obj = db.query(Command).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


command = CRUDCommand()
