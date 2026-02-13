# /app/api/v1/command.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List

from app.crud import command as crud_command
from app.schemas.command import CommandPublic, CommandCreate
from app.schemas.common import BaseAPIResponse
from app.db.session import get_db
from app.iot.mqtt.publisher import publish_command


router = APIRouter()


@router.post("/", response_model=BaseAPIResponse[CommandPublic])
async def create_command(
    command_in: CommandCreate,
    db: Session = Depends(get_db)
):
    command = crud_command.command.create(db=db, obj_in=command_in)

    # ⚡ ارسال به MQTT بلافاصله بعد از ذخیره
    publish_command(command)

    return BaseAPIResponse(result=command)

@router.get("/{command_id}", response_model=BaseAPIResponse[CommandPublic])
async def read_command(
    command_id: int = Path(..., description="ID of the command to retrieve"),
    db: Session = Depends(get_db)
):
    command = crud_command.command.get(db=db, id=command_id)
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    return BaseAPIResponse(result=command)


@router.get("/", response_model=BaseAPIResponse[List[CommandPublic]])
async def read_commands(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    commands = crud_command.command.get_multi(db=db, skip=skip, limit=limit)
    return BaseAPIResponse(result=commands)
