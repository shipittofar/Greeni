from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List

from app.crud import sensor_data as crud_sensor_data
from app.schemas.sensor_data import SensorDataPublic, SensorDataCreate
from app.schemas.common import BaseAPIResponse
from app.db.session import get_db

router = APIRouter()


@router.post("/", response_model=BaseAPIResponse[SensorDataPublic])
async def create_sensor_data(
    sensor_data_in: SensorDataCreate,
    db: Session = Depends(get_db)
):
    data = crud_sensor_data.sensor_data.create(db=db, obj_in=sensor_data_in)
    return BaseAPIResponse(result=data)


@router.get("/{sensor_id}/latest", response_model=BaseAPIResponse[SensorDataPublic])
async def read_latest_sensor_data(
    sensor_id: int = Path(..., description="ID of the sensor"),
    db: Session = Depends(get_db)
):
    data = crud_sensor_data.sensor_data.get_latest_by_sensor(db=db, sensor_id=sensor_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this sensor")
    return BaseAPIResponse(result=data)


@router.get("/{sensor_id}/history", response_model=BaseAPIResponse[List[SensorDataPublic]])
async def read_sensor_data_history(
    sensor_id: int = Path(..., description="ID of the sensor"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    data_history = crud_sensor_data.sensor_data.get_history(db=db, sensor_id=sensor_id, skip=skip, limit=limit)
    return BaseAPIResponse(result=data_history)
