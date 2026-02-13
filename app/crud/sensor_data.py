from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.sensor_data import SensorData
from app.schemas.sensor_data import SensorDataCreate


class CRUDSensorData:
    def get(self, db: Session, id: int) -> Optional[SensorData]:
        return db.query(SensorData).filter(SensorData.id == id).first()

    def get_latest_by_sensor(self, db: Session, sensor_id: int) -> Optional[SensorData]:
        return (
            db.query(SensorData)
            .filter(SensorData.sensor_id == sensor_id)
            .order_by(SensorData.created_at.desc())
            .first()
        )

    def get_history(self, db: Session, sensor_id: int, skip: int = 0, limit: int = 100) -> List[SensorData]:
        return (
            db.query(SensorData)
            .filter(SensorData.sensor_id == sensor_id)
            .order_by(SensorData.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, obj_in: SensorDataCreate) -> SensorData:
        db_obj = SensorData(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


sensor_data = CRUDSensorData()
