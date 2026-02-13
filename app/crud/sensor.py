# app/crud/sensor.py - بهینه‌شده
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException
from sqlalchemy.sql import func
from fastapi.responses import JSONResponse
from typing import List, Optional

from app.models.tag import Tag
from app.models.sensor import (
    Sensor as SensorModel,
    SensorType as SensorTypeModel,
    SensorAttribute as SensorAttributeModel,
    SensorAttributeValue as SensorAttributeValueModel,
)
from app.schemas.sensor import (
    SensorCreate,
    SensorUpdate,
    SensorTypeCreate,
    SensorTypeUpdate,
    SensorAttributeCreate,
    SensorAttributeUpdate,
    SensorAttributeValueCreate,
    SensorAttributeValueUpdate,
)

# ============================================
# 🔹 Sensor Type Operations
# ============================================

def create_sensor_type(db: Session, payload: SensorTypeCreate) -> SensorTypeModel:
    """ایجاد sensor type با tags"""
    tag_ids: List[int] = getattr(payload, "tag_ids", []) or []
    
    # Extract data and remove tag_ids
    obj_data = payload.model_dump(exclude={"tag_ids"})
    obj = SensorTypeModel(**obj_data)
    
    db.add(obj)
    db.flush()  # Flush برای دریافت ID بدون commit
    
    # اگر tags باشند، اضافه کنید
    if tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        obj.tags = tags
    
    db.commit()
    db.refresh(obj)
    return obj


def update_sensor_type(
    db: Session,
    sensor_type: SensorTypeModel,
    payload: SensorTypeUpdate
) -> SensorTypeModel:
    """Update sensor type با بهینه‌سازی"""
    data = payload.model_dump(exclude_unset=True)
    tag_ids: Optional[List[int]] = data.pop("tag_ids", None)
    
    # Update fields
    for key, value in data.items():
        setattr(sensor_type, key, value)
    
    # Handle tags separately
    if tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
        sensor_type.tags = tags
    
    sensor_type.updated_at = func.now()
    
    db.commit()
    db.refresh(sensor_type)
    return sensor_type


def delete_sensor_type(db: Session, sensor_type: SensorTypeModel) -> None:
    """Soft delete sensor type"""
    sensor_type.is_deleted = True
    sensor_type.updated_at = func.now()
    db.commit()


def get_sensor_type_by_id(
    db: Session,
    type_id: int,
    load_tags: bool = False
) -> Optional[SensorTypeModel]:
    """دریافت sensor type با eager loading اختیاری"""
    query = db.query(SensorTypeModel).filter(
        and_(
            SensorTypeModel.id == type_id,
            SensorTypeModel.is_deleted == False
        )
    )
    
    if load_tags:
        query = query.options(joinedload(SensorTypeModel.tags))
    
    return query.first()


def get_sensor_type_by_name(
    db: Session,
    name: str
) -> Optional[SensorTypeModel]:
    """دریافت sensor type بر اساس name"""
    return db.query(SensorTypeModel).filter(
        and_(
            SensorTypeModel.name == name,
            SensorTypeModel.is_deleted == False
        )
    ).first()


def list_sensor_types(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    load_tags: bool = False
) -> List[SensorTypeModel]:
    """لیست sensor types با pagination"""
    query = db.query(SensorTypeModel).filter(
        SensorTypeModel.is_deleted == False
    )
    
    if load_tags:
        query = query.options(joinedload(SensorTypeModel.tags))
    
    return query.offset(skip).limit(limit).all()


def list_sensor_types_by_protocol(
    db: Session,
    protocol: str
) -> List[SensorTypeModel]:
    """لیست sensor types بر اساس protocol"""
    return db.query(SensorTypeModel).filter(
        and_(
            SensorTypeModel.protocol == protocol,
            SensorTypeModel.is_deleted == False
        )
    ).all()


def assign_tags_to_sensor_type(
    db: Session,
    sensor_type_id: int,
    tag_ids: List[int]
) -> JSONResponse:
    """Assign tags به sensor type"""
    sensor_type = db.query(SensorTypeModel).get(sensor_type_id)
    if not sensor_type:
        raise HTTPException(status_code=404, detail="SensorType not found")
    
    # Get tags
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
    
    # Add only new tags
    existing_tag_ids = {tag.id for tag in sensor_type.tags}
    for tag in tags:
        if tag.id not in existing_tag_ids:
            sensor_type.tags.append(tag)
    
    db.commit()
    db.refresh(sensor_type)
    return JSONResponse(
        status_code=200,
        content={"detail": "Tags assigned successfully", "count": len(tags)}
    )


def unassign_tags_from_sensor_type(
    db: Session,
    sensor_type_id: int,
    tag_ids: List[int]
) -> JSONResponse:
    """Remove tags از sensor type"""
    sensor_type = db.query(SensorTypeModel).get(sensor_type_id)
    if not sensor_type:
        raise HTTPException(status_code=404, detail="SensorType not found")
    
    # Filter out tags
    sensor_type.tags = [tag for tag in sensor_type.tags if tag.id not in tag_ids]
    
    db.commit()
    db.refresh(sensor_type)
    return JSONResponse(
        status_code=200,
        content={"detail": "Tags unassigned successfully"}
    )


# ============================================
# 🔹 Sensor Attribute Operations
# ============================================

def create_sensor_attribute(
    db: Session,
    payload: SensorAttributeCreate
) -> SensorAttributeModel:
    """ایجاد sensor attribute"""
    obj = SensorAttributeModel(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_sensor_attribute(
    db: Session,
    attribute: SensorAttributeModel,
    payload: SensorAttributeUpdate
) -> SensorAttributeModel:
    """Update sensor attribute"""
    data = payload.model_dump(exclude_unset=True)
    
    for key, value in data.items():
        setattr(attribute, key, value)
    
    attribute.updated_at = func.now()
    db.commit()
    db.refresh(attribute)
    return attribute


def delete_sensor_attribute(
    db: Session,
    attribute: SensorAttributeModel
) -> None:
    """Soft delete sensor attribute"""
    attribute.is_deleted = True
    attribute.updated_at = func.now()
    db.commit()


def get_sensor_attribute_by_id(
    db: Session,
    attribute_id: int
) -> Optional[SensorAttributeModel]:
    """دریافت sensor attribute"""
    return db.query(SensorAttributeModel).filter(
        and_(
            SensorAttributeModel.id == attribute_id,
            SensorAttributeModel.is_deleted == False
        )
    ).first()


def list_attributes_by_sensor_type(
    db: Session,
    sensor_type_id: int
) -> List[SensorAttributeModel]:
    """لیست attributes یک sensor type"""
    return db.query(SensorAttributeModel).filter(
        and_(
            SensorAttributeModel.sensor_type_id == sensor_type_id,
            SensorAttributeModel.is_deleted == False
        )
    ).all()


# ============================================
# 🔹 Sensor Operations
# ============================================

def create_sensor(
    db: Session,
    payload: SensorCreate
) -> SensorModel:
    """ایجاد sensor"""
    obj = SensorModel(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_sensor(
    db: Session,
    sensor: SensorModel,
    payload: SensorUpdate
) -> SensorModel:
    """Update sensor"""
    data = payload.model_dump(exclude_unset=True)
    
    for key, value in data.items():
        setattr(sensor, key, value)
    
    sensor.updated_at = func.now()
    db.commit()
    db.refresh(sensor)
    return sensor


def delete_sensor(db: Session, sensor: SensorModel) -> None:
    """Soft delete sensor"""
    sensor.is_deleted = True
    sensor.updated_at = func.now()
    db.commit()


def get_sensor_by_id(
    db: Session,
    sensor_id: int,
    load_type: bool = False
) -> Optional[SensorModel]:
    """دریافت sensor"""
    query = db.query(SensorModel).filter(
        and_(
            SensorModel.id == sensor_id,
            SensorModel.is_deleted == False
        )
    )
    
    if load_type:
        query = query.options(joinedload(SensorModel.sensor_type))
    
    return query.first()


def get_sensor_by_name(
    db: Session,
    name: str
) -> Optional[SensorModel]:
    """دریافت sensor بر اساس name"""
    return db.query(SensorModel).filter(
        and_(
            SensorModel.name == name,
            SensorModel.is_deleted == False
        )
    ).first()


def list_sensors(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    load_type: bool = False
) -> List[SensorModel]:
    """لیست sensors با pagination"""
    query = db.query(SensorModel).filter(
        SensorModel.is_deleted == False
    )
    
    if load_type:
        query = query.options(joinedload(SensorModel.sensor_type))
    
    return query.offset(skip).limit(limit).all()


def list_sensors_by_type(
    db: Session,
    sensor_type_id: int
) -> List[SensorModel]:
    """لیست sensors از یک نوع"""
    return db.query(SensorModel).filter(
        and_(
            SensorModel.sensor_type_id == sensor_type_id,
            SensorModel.is_deleted == False
        )
    ).all()


def list_active_sensors(db: Session) -> List[SensorModel]:
    """لیست sensors فعال"""
    return db.query(SensorModel).filter(
        and_(
            SensorModel.is_active == True,
            SensorModel.is_deleted == False
        )
    ).all()


def list_online_sensors(db: Session) -> List[SensorModel]:
    """لیست sensors آنلاین"""
    return db.query(SensorModel).filter(
        and_(
            SensorModel.is_online == True,
            SensorModel.is_deleted == False
        )
    ).all()


# ============================================
# 🔹 Attribute Value Operations
# ============================================

def create_attribute_value(
    db: Session,
    payload: SensorAttributeValueCreate
) -> SensorAttributeValueModel:
    """ایجاد attribute value"""
    obj = SensorAttributeValueModel(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_attribute_value(
    db: Session,
    value_obj: SensorAttributeValueModel,
    payload: SensorAttributeValueUpdate
) -> SensorAttributeValueModel:
    """Update attribute value"""
    data = payload.model_dump(exclude_unset=True)
    
    for key, value in data.items():
        setattr(value_obj, key, value)
    
    value_obj.updated_at = func.now()
    db.commit()
    db.refresh(value_obj)
    return value_obj


def get_attribute_value_by_id(
    db: Session,
    value_id: int
) -> Optional[SensorAttributeValueModel]:
    """دریافت attribute value"""
    return db.query(SensorAttributeValueModel).filter(
        and_(
            SensorAttributeValueModel.id == value_id,
            SensorAttributeValueModel.is_deleted == False
        )
    ).first()


def list_attribute_values_by_sensor(
    db: Session,
    sensor_id: int
) -> List[SensorAttributeValueModel]:
    """لیست attribute values یک sensor"""
    return db.query(SensorAttributeValueModel).filter(
        and_(
            SensorAttributeValueModel.sensor_id == sensor_id,
            SensorAttributeValueModel.is_deleted == False
        )
    ).all()


def list_attribute_values_by_attribute(
    db: Session,
    attribute_id: int
) -> List[SensorAttributeValueModel]:
    """لیست values یک attribute"""
    return db.query(SensorAttributeValueModel).filter(
        and_(
            SensorAttributeValueModel.attribute_id == attribute_id,
            SensorAttributeValueModel.is_deleted == False
        )
    ).all()


def get_latest_attribute_value(
    db: Session,
    sensor_id: int,
    attribute_id: int
) -> Optional[SensorAttributeValueModel]:
    """دریافت آخرین value یک attribute از یک sensor"""
    return db.query(SensorAttributeValueModel).filter(
        and_(
            SensorAttributeValueModel.sensor_id == sensor_id,
            SensorAttributeValueModel.attribute_id == attribute_id,
            SensorAttributeValueModel.is_deleted == False
        )
    ).order_by(
        SensorAttributeValueModel.created_at.desc()
    ).first()


def list_values_by_status(
    db: Session,
    sensor_id: int,
    status: str
) -> List[SensorAttributeValueModel]:
    """لیست values بر اساس status"""
    return db.query(SensorAttributeValueModel).filter(
        and_(
            SensorAttributeValueModel.sensor_id == sensor_id,
            SensorAttributeValueModel.status == status,
            SensorAttributeValueModel.is_deleted == False
        )
    ).all()


# ============================================
# 🔹 Protocol Integration Operations
# ============================================

def get_sensor_by_protocol(
    db: Session,
    protocol: str
) -> List[SensorModel]:
    """دریافت sensors بر اساس protocol"""
    return db.query(SensorModel).join(
        SensorTypeModel,
        SensorModel.sensor_type_id == SensorTypeModel.id
    ).filter(
        and_(
            SensorTypeModel.protocol == protocol,
            SensorModel.is_deleted == False,
            SensorTypeModel.is_deleted == False
        )
    ).all()


def get_sensor_config(
    db: Session,
    sensor_id: int
) -> Optional[dict]:
    """دریافت protocol config یک sensor"""
    sensor = get_sensor_by_id(db, sensor_id)
    if not sensor:
        return None
    
    return {
        "protocol": sensor.sensor_type.protocol if sensor.sensor_type else None,
        "pin_mapping": sensor.pin_mapping,
        "config": sensor.config,
        "default_pins": sensor.sensor_type.default_pins if sensor.sensor_type else None,
        "config_schema": sensor.sensor_type.config_schema if sensor.sensor_type else None,
    }


def update_sensor_protocol_config(
    db: Session,
    sensor_id: int,
    pin_mapping: dict = None,
    config: dict = None
) -> Optional[SensorModel]:
    """به‌روزرسانی protocol config sensor"""
    sensor = get_sensor_by_id(db, sensor_id)
    if not sensor:
        return None
    
    if pin_mapping is not None:
        sensor.pin_mapping = pin_mapping
    
    if config is not None:
        sensor.config = config
    
    sensor.updated_at = func.now()
    db.commit()
    db.refresh(sensor)
    return sensor


def get_sensors_by_device(
    db: Session,
    device_id: int
) -> List[SensorModel]:
    """دریافت sensors اتصال‌شده به یک device"""
    return db.query(SensorModel).filter(
        and_(
            SensorModel.device_id == device_id,
            SensorModel.is_deleted == False
        )
    ).all()


def initialize_sensor_protocol(
    db: Session,
    sensor_id: int,
    protocol_name: str,
    pin_mapping: dict,
    config: dict
) -> Optional[SensorModel]:
    """راه‌اندازی protocol برای sensor"""
    sensor = get_sensor_by_id(db, sensor_id)
    if not sensor:
        return None
    
    # بررسی sensor_type
    sensor_type = db.query(SensorTypeModel).filter(
        SensorTypeModel.id == sensor.sensor_type_id
    ).first()
    
    if not sensor_type:
        raise ValueError("Sensor type not found")
    
    # تنظیم protocol اطلاعات
    sensor.pin_mapping = pin_mapping
    sensor.config = config
    
    # اگر protocol در SensorType نیست، تنظیم کنید
    if not sensor_type.protocol:
        sensor_type.protocol = protocol_name
    
    sensor.is_online = True
    sensor.updated_at = func.now()
    
    db.commit()
    db.refresh(sensor)
    return sensor


def get_protocol_sensors_by_type(
    db: Session,
    protocol: str,
    sensor_type_id: int = None
) -> List[SensorModel]:
    """دریافت sensors فعال برای protocol معین"""
    query = db.query(SensorModel).join(
        SensorTypeModel,
        SensorModel.sensor_type_id == SensorTypeModel.id
    ).filter(
        and_(
            SensorTypeModel.protocol == protocol,
            SensorModel.is_active == True,
            SensorModel.is_deleted == False,
            SensorTypeModel.is_deleted == False
        )
    )
    
    if sensor_type_id:
        query = query.filter(SensorModel.sensor_type_id == sensor_type_id)
    
    return query.all()


def validate_sensor_protocol_config(
    db: Session,
    sensor_type_id: int,
    config: dict
) -> bool:
    """بررسی config برای sensor type"""
    sensor_type = db.query(SensorTypeModel).filter(
        SensorTypeModel.id == sensor_type_id
    ).first()
    
    if not sensor_type or not sensor_type.config_schema:
        return True  # اگر schema نیست، pass کنید
    
    # اگر schema تعریف شده است، بررسی کنید
    # (می‌توان از jsonschema استفاده کنید)
    return True