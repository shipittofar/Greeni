# app/api/v1/sensor.py - بهینه‌شده

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from sqlalchemy import and_
from typing import List, Optional

from app.schemas.sensor import (
    SensorCreate,
    Sensor,
    SensorTypeCreate,
    SensorType,
    SensorAttributeCreate,
    SensorAttribute,
    SensorAttributeValueCreate,
    SensorAttributeValue,
    SensorAttributeValueWithAttr,
    SensorPublic,
    SensorUpdate,
    SensorTypePublic,
    SensorTypeUpdate,
    SensorAttributeUpdate,
    SensorAttributePublic,
    SensorAttributeValuePublic,
    SensorAttributeValueUpdate,
    SensorTypeTagsPublic,
    SensorTypeTagAssignmentRequest
)
from app.models.sensor import Sensor as SensorModel
from app.models.sensor import SensorType as SensorTypeModel
from app.models.sensor import SensorAttribute as SensorAttributeModel
from app.models.sensor import SensorAttributeValue as SensorAttributeValueModel
from app.models.user import User
from app.models.tag import Tag
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.schemas.common import BaseAPIResponse
from app.crud.sensor import (
    # Sensor Type
    create_sensor_type,
    update_sensor_type,
    delete_sensor_type,
    get_sensor_type_by_id,
    get_sensor_type_by_name,
    list_sensor_types,
    list_sensor_types_by_protocol,
    assign_tags_to_sensor_type,
    unassign_tags_from_sensor_type,
    # Sensor Attribute
    create_sensor_attribute,
    update_sensor_attribute,
    delete_sensor_attribute,
    get_sensor_attribute_by_id,
    list_attributes_by_sensor_type,
    # Sensor
    create_sensor,
    update_sensor,
    delete_sensor,
    get_sensor_by_id,
    get_sensor_by_name,
    list_sensors,
    list_sensors_by_type,
    list_active_sensors,
    list_online_sensors,
    # Attribute Value
    create_attribute_value,
    update_attribute_value,
    get_attribute_value_by_id,
    list_attribute_values_by_sensor,
    list_attribute_values_by_attribute,
    get_latest_attribute_value,
    list_values_by_status,
)

router = APIRouter(tags=["Sensors"])


# ============================================
# 🔹 Sensor Attributes - نقاط پایانی
# ============================================

@router.get("/attributes", response_model=BaseAPIResponse[List[SensorAttribute]], summary="لیست تمام attributes")
def list_sensor_attributes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """لیست تمام sensor attributes با pagination"""
    attributes = db.query(SensorAttributeModel).filter(
        SensorAttributeModel.is_deleted == False
    ).offset(skip).limit(limit).all()
    
    return BaseAPIResponse(result=attributes)


@router.get("/attributes/{attribute_id}", response_model=BaseAPIResponse[SensorAttribute], summary="دریافت attribute")
def get_sensor_attribute_by_id_endpoint(
    attribute_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """دریافت sensor attribute توسط ID"""
    attribute = get_sensor_attribute_by_id(db, attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Sensor attribute not found")
    return BaseAPIResponse(result=attribute)


@router.post("/attributes", response_model=BaseAPIResponse[SensorAttribute], summary="ایجاد attribute")
def create_sensor_attribute_endpoint(
    payload: SensorAttributeCreate,
    db: Session = Depends(get_db)
):
    """ایجاد sensor attribute جدید"""
    attribute = create_sensor_attribute(db, payload)
    return BaseAPIResponse(result=attribute)


@router.put("/attributes/{attribute_id}", response_model=BaseAPIResponse[SensorAttribute], summary="بروزرسانی attribute")
def update_sensor_attribute_endpoint(
    attribute_id: int = Path(..., gt=0),
    payload: SensorAttributeCreate = None,
    db: Session = Depends(get_db)
):
    """بروزرسانی کامل sensor attribute"""
    attribute = get_sensor_attribute_by_id(db, attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Sensor attribute not found")
    
    updated = update_sensor_attribute(db, attribute, payload)
    return BaseAPIResponse(result=updated)


@router.patch("/attributes/{attribute_id}", response_model=BaseAPIResponse[SensorAttributePublic], summary="بروزرسانی جزئی attribute")
def patch_sensor_attribute(
    attribute_id: int = Path(..., gt=0),
    updates: SensorAttributeUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """بروزرسانی جزئی sensor attribute"""
    attribute = get_sensor_attribute_by_id(db, attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Sensor attribute not found")
    
    updated = update_sensor_attribute(db, attribute, updates)
    updated.updated_by = current_user.id
    db.commit()
    
    return BaseAPIResponse(result=updated)


@router.delete("/attributes/{attribute_id}", summary="حذف attribute")
def delete_sensor_attribute_endpoint(
    attribute_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """حذف (نرم) sensor attribute"""
    attribute = get_sensor_attribute_by_id(db, attribute_id)
    if not attribute:
        raise HTTPException(status_code=404, detail="Sensor attribute not found")
    
    delete_sensor_attribute(db, attribute)
    return BaseAPIResponse(message="Sensor attribute soft-deleted")


# ============================================
# 🔹 Sensor Types - نقاط پایانی
# ============================================

@router.get("/types", response_model=BaseAPIResponse[List[SensorType]], summary="لیست sensor types")
def list_sensor_types_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    protocol: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """لیست sensor types با فیلتر اختیاری"""
    if protocol:
        types = list_sensor_types_by_protocol(db, protocol)
    else:
        types = list_sensor_types(db, skip, limit)
    
    return BaseAPIResponse(result=types)


@router.get("/types/tags", response_model=BaseAPIResponse[List[SensorTypeTagsPublic]], summary="لیست types با tags")
def list_sensor_types_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """لیست sensor types با tags نگاه‌شده"""
    sensor_types = list_sensor_types(db, skip, limit, load_tags=True)
    return BaseAPIResponse(result=sensor_types)


@router.post("/types", response_model=BaseAPIResponse[SensorType], summary="ایجاد sensor type")
def create_sensor_type_endpoint(
    payload: SensorTypeCreate,
    db: Session = Depends(get_db)
):
    """ایجاد sensor type جدید"""
    # بررسی تکراری نبودن نام
    existing = get_sensor_type_by_name(db, payload.name)
    if existing:
        raise HTTPException(status_code=400, detail="Sensor type name already exists")
    
    sensor_type = create_sensor_type(db, payload)
    return BaseAPIResponse(result=sensor_type)


@router.get("/types/{type_id}", response_model=BaseAPIResponse[SensorType], summary="دریافت sensor type")
def get_sensor_type_endpoint(
    type_id: int = Path(..., gt=0),
    load_tags: bool = Query(False),
    db: Session = Depends(get_db)
):
    """دریافت sensor type توسط ID"""
    sensor_type = get_sensor_type_by_id(db, type_id, load_tags=load_tags)
    if not sensor_type:
        raise HTTPException(status_code=404, detail="Sensor type not found")
    return BaseAPIResponse(result=sensor_type)


@router.get("/types/{type_id}/tags", response_model=BaseAPIResponse[SensorTypePublic], summary="دریافت type با tags")
def get_sensor_type_with_tags(
    type_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """دریافت sensor type با tags نگاه‌شده"""
    sensor_type = get_sensor_type_by_id(db, type_id, load_tags=True)
    if not sensor_type:
        raise HTTPException(status_code=404, detail="Sensor type not found")
    return BaseAPIResponse(result=sensor_type)


@router.put("/types/{type_id}", response_model=BaseAPIResponse[SensorType], summary="بروزرسانی کامل type")
def update_sensor_type_endpoint(
    type_id: int = Path(..., gt=0),
    payload: SensorTypeCreate = None,
    db: Session = Depends(get_db)
):
    """بروزرسانی کامل sensor type"""
    sensor_type = get_sensor_type_by_id(db, type_id)
    if not sensor_type:
        raise HTTPException(status_code=404, detail="Sensor type not found")
    
    updated = update_sensor_type(db, sensor_type, payload)
    return BaseAPIResponse(result=updated)


@router.patch("/types/{type_id}", response_model=BaseAPIResponse[SensorTypePublic], summary="بروزرسانی جزئی type")
def patch_sensor_type(
    type_id: int = Path(..., gt=0),
    updates: SensorTypeUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """بروزرسانی جزئی sensor type"""
    sensor_type = get_sensor_type_by_id(db, type_id)
    if not sensor_type:
        raise HTTPException(status_code=404, detail="Sensor type not found")
    
    updated = update_sensor_type(db, sensor_type, updates)
    updated.updated_by = current_user.id
    db.commit()
    
    return BaseAPIResponse(result=updated)


@router.delete("/types/{type_id}", summary="حذف sensor type")
def delete_sensor_type_endpoint(
    type_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """حذف (نرم) sensor type"""
    sensor_type = get_sensor_type_by_id(db, type_id)
    if not sensor_type:
        raise HTTPException(status_code=404, detail="Sensor type not found")
    
    delete_sensor_type(db, sensor_type)
    return BaseAPIResponse(message="Sensor type soft-deleted")


# @router.post("/types/{type_id}/assign-tags")
@router.post("/types/assign-tags")
def assign_tags_endpoint(
    # type_id: int = Path(..., gt=0),
    data: SensorTypeTagAssignmentRequest = None,
    db: Session = Depends(get_db)
):
    """اختصاص tags به sensor type"""
    # return assign_tags_to_sensor_type(db, type_id, data.tag_ids)
    return assign_tags_to_sensor_type(db, data)


# @router.post("/types/{type_id}/unassign-tags")
@router.post("/types/unassign-tags")
def unassign_tags_endpoint(
    # type_id: int = Path(..., gt=0),
    data: SensorTypeTagAssignmentRequest = None,
    db: Session = Depends(get_db)
):
    """حذف اختصاص tags از sensor type"""
    # return unassign_tags_from_sensor_type(db, type_id, data.tag_ids)
    return unassign_tags_from_sensor_type(db, data)


# ============================================
# 🔹 Sensors - نقاط پایانی
# ============================================

@router.get("/", response_model=BaseAPIResponse[List[Sensor]], summary="لیست سنسورها")
def list_sensors_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sensor_type_id: Optional[int] = Query(None, gt=0),
    is_active: Optional[bool] = Query(None),
    is_online: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """لیست sensors با فیلتر اختیاری"""
    query = db.query(SensorModel).filter(
        SensorModel.is_deleted == False
    ).options(joinedload(SensorModel.sensor_type))
    
    if sensor_type_id:
        query = query.filter(SensorModel.sensor_type_id == sensor_type_id)
    if is_active is not None:
        query = query.filter(SensorModel.is_active == is_active)
    if is_online is not None:
        query = query.filter(SensorModel.is_online == is_online)
    
    sensors = query.offset(skip).limit(limit).all()
    return BaseAPIResponse(result=sensors)


@router.post("/", response_model=BaseAPIResponse[Sensor], summary="ایجاد سنسور")
def create_sensor_endpoint(
    payload: SensorCreate,
    db: Session = Depends(get_db)
):
    """ایجاد سنسور جدید"""
    sensor = create_sensor(db, payload)
    db.refresh(sensor, ["sensor_type"])
    return BaseAPIResponse(result=sensor)


@router.get("/{sensor_id}", response_model=BaseAPIResponse[Sensor], summary="دریافت سنسور")
def get_sensor_endpoint(
    sensor_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """دریافت سنسور توسط ID"""
    sensor = get_sensor_by_id(db, sensor_id, load_type=True)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return BaseAPIResponse(result=sensor)


@router.put("/{sensor_id}", response_model=BaseAPIResponse[Sensor], summary="بروزرسانی کامل سنسور")
def update_sensor_endpoint(
    sensor_id: int = Path(..., gt=0),
    payload: SensorCreate = None,
    db: Session = Depends(get_db)
):
    """بروزرسانی کامل سنسور"""
    sensor = get_sensor_by_id(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    updated = update_sensor(db, sensor, payload)
    db.refresh(updated, ["sensor_type"])
    return BaseAPIResponse(result=updated)


@router.patch("/{sensor_id}", response_model=BaseAPIResponse[SensorPublic], summary="بروزرسانی جزئی سنسور")
def patch_sensor(
    sensor_id: int = Path(..., gt=0),
    updates: SensorUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """بروزرسانی جزئی سنسور"""
    sensor = get_sensor_by_id(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    updated = update_sensor(db, sensor, updates)
    
    return BaseAPIResponse(result=updated)


@router.delete("/{sensor_id}", summary="حذف سنسور")
def delete_sensor_endpoint(
    sensor_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """حذف (نرم) سنسور"""
    sensor = get_sensor_by_id(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    delete_sensor(db, sensor)
    return BaseAPIResponse(message="Sensor soft-deleted")


# ============================================
# 🔹 Attribute Values - نقاط پایانی
# ============================================

@router.get("/values", response_model=BaseAPIResponse[List[SensorAttributeValue]], summary="لیست تمام values")
def list_all_attribute_values(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """لیست تمام attribute values"""
    values = db.query(SensorAttributeValueModel).filter(
        SensorAttributeValueModel.is_deleted == False
    ).offset(skip).limit(limit).all()
    
    return BaseAPIResponse(result=values)


@router.get("/attribute-values/full", response_model=BaseAPIResponse[List[SensorAttributeValueWithAttr]], summary="تمام values با جزئیات")
def get_all_attribute_values_with_attributes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """دریافت تمام attribute values با جزئیات"""
    results = (
        db.query(SensorAttributeValueModel)
        .filter(SensorAttributeValueModel.is_deleted == False)
        .join(SensorAttributeModel, SensorAttributeModel.id == SensorAttributeValueModel.attribute_id)
        .join(SensorModel, SensorModel.id == SensorAttributeValueModel.sensor_id)
        .filter(and_(
            SensorAttributeModel.is_deleted == False,
            SensorModel.is_deleted == False
        ))
        .with_entities(
            SensorAttributeValueModel.id,
            SensorAttributeValueModel.sensor_id,
            SensorAttributeValueModel.value,
            SensorAttributeModel.id.label("attribute_id"),
            SensorAttributeModel.name.label("attribute_name"),
            SensorAttributeModel.unit.label("attribute_unit"),
            SensorModel.name.label("sensor_name")
        )
        .offset(skip).limit(limit)
        .all()
    )

    formatted = [
        SensorAttributeValueWithAttr(
            id=row.id,
            sensor_id=row.sensor_id,
            value=row.value,
            attribute={
                "id": row.attribute_id,
                "name": row.attribute_name,
                "unit": row.attribute_unit
            },
            sensor={"id": row.sensor_id, "name": row.sensor_name}
        )
        for row in results
    ]
    return BaseAPIResponse(result=formatted)


@router.get("/{sensor_id}/attribute-values/full", response_model=BaseAPIResponse[List[SensorAttributeValueWithAttr]], summary="values سنسور با جزئیات")
def get_attribute_values_with_attributes(
    sensor_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """دریافت attribute values سنسور با جزئیات"""
    # اول sensor رو بگیریم
    sensor = get_sensor_by_id(db, sensor_id, load_type=True)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    results = (
        db.query(SensorAttributeValueModel)
        .filter(and_(
            SensorAttributeValueModel.sensor_id == sensor_id,
            SensorAttributeValueModel.is_deleted == False
        ))
        .join(SensorAttributeModel, SensorAttributeModel.id == SensorAttributeValueModel.attribute_id)
        .filter(SensorAttributeModel.is_deleted == False)
        .with_entities(
            SensorAttributeValueModel.id,
            SensorAttributeValueModel.sensor_id,
            SensorAttributeValueModel.value,
            SensorAttributeModel.id.label("attribute_id"),
            SensorAttributeModel.name.label("attribute_name"),
            SensorAttributeModel.unit.label("attribute_unit")
        )
        .all()
    )

    formatted = [
        SensorAttributeValueWithAttr(
            id=row.id,
            sensor_id=row.sensor_id,
            value=row.value,
            attribute={
                "id": row.attribute_id,
                "name": row.attribute_name,
                "unit": row.attribute_unit
            },
            sensor={"id": sensor.id, "name": sensor.name}
        )
        for row in results
    ]
    return BaseAPIResponse(result=formatted)


@router.get("/{sensor_id}/attribute-values", response_model=BaseAPIResponse[List[SensorAttributeValue]], summary="values سنسور")
def list_attribute_values_for_sensor(
    sensor_id: int = Path(..., gt=0),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """لیست attribute values سنسور"""
    if status:
        values = list_values_by_status(db, sensor_id, status)
    else:
        values = list_attribute_values_by_sensor(db, sensor_id)
    
    return BaseAPIResponse(result=values)


@router.post("/attribute-values", response_model=BaseAPIResponse[SensorAttributeValue], summary="ایجاد attribute value")
def create_attribute_value_endpoint(
    payload: SensorAttributeValueCreate,
    db: Session = Depends(get_db)
):
    """ایجاد attribute value جدید"""
    value = create_attribute_value(db, payload)
    return BaseAPIResponse(result=value)


@router.get("/attribute-values/{value_id}", response_model=BaseAPIResponse[SensorAttributeValue], summary="دریافت value")
def get_attribute_value_endpoint(
    value_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """دریافت attribute value"""
    value = get_attribute_value_by_id(db, value_id)
    if not value:
        raise HTTPException(status_code=404, detail="Attribute value not found")
    return BaseAPIResponse(result=value)


@router.patch("/attribute-values/{value_id}", response_model=BaseAPIResponse[SensorAttributeValuePublic], summary="بروزرسانی value")
def patch_attribute_value(
    value_id: int = Path(..., gt=0),
    updates: SensorAttributeValueUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """بروزرسانی attribute value"""
    attribute_value = get_attribute_value_by_id(db, value_id)
    if not attribute_value:
        raise HTTPException(status_code=404, detail="Attribute value not found")
    
    updated = update_attribute_value(db, attribute_value, updates)
    updated.updated_by = current_user.id
    db.commit()
    
    return BaseAPIResponse(result=updated)


# ============================================
# 🔹 Protocol Integration Routes
# ============================================

@router.get("/protocols/available", response_model=BaseAPIResponse[List[str]], summary="پروتکل‌های موجود")
def get_available_protocols(db: Session = Depends(get_db)):
    """دریافت لیست پروتکل‌های موجود"""
    protocols = db.query(SensorTypeModel.protocol).distinct().filter(
        and_(
            SensorTypeModel.protocol.isnot(None),
            SensorTypeModel.is_deleted == False
        )
    ).all()
    
    protocol_list = [p[0] for p in protocols]
    return BaseAPIResponse(result=protocol_list)


@router.get("/by-protocol/{protocol}", response_model=BaseAPIResponse[List[Sensor]], summary="sensors بر اساس protocol")
def get_sensors_by_protocol(
    protocol: str = Path(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """دریافت sensors بر اساس protocol"""
    from app.crud.sensor import get_sensor_by_protocol
    
    sensors = get_sensor_by_protocol(db, protocol)
    return BaseAPIResponse(result=sensors[skip:skip+limit])


@router.get("/{sensor_id}/protocol-config", response_model=BaseAPIResponse[dict], summary="protocol config سنسور")
def get_sensor_protocol_config(
    sensor_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """دریافت protocol config یک sensor"""
    from app.crud.sensor import get_sensor_config
    
    config = get_sensor_config(db, sensor_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    return BaseAPIResponse(result=config)


@router.post("/{sensor_id}/initialize-protocol", response_model=BaseAPIResponse[SensorPublic], summary="راه‌اندازی protocol")
def initialize_protocol(
    sensor_id: int = Path(..., gt=0),
    protocol_name: str = Query(...),
    pin_mapping: dict = None,
    config: dict = None,
    db: Session = Depends(get_db)
):
    """راه‌اندازی protocol برای sensor"""
    from app.crud.sensor import initialize_sensor_protocol
    
    if pin_mapping is None:
        pin_mapping = {}
    if config is None:
        config = {}
    
    try:
        sensor = initialize_sensor_protocol(
            db, sensor_id, protocol_name, pin_mapping, config
        )
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        return BaseAPIResponse(result=sensor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{sensor_id}/protocol-config", response_model=BaseAPIResponse[SensorPublic], summary="به‌روزرسانی protocol config")
def update_protocol_config(
    sensor_id: int = Path(..., gt=0),
    pin_mapping: dict = None,
    config: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """به‌روزرسانی protocol config سنسور"""
    from app.crud.sensor import update_sensor_protocol_config
    
    sensor = update_sensor_protocol_config(db, sensor_id, pin_mapping, config)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    return BaseAPIResponse(result=sensor)


@router.get("/device/{device_id}/sensors", response_model=BaseAPIResponse[List[Sensor]], summary="sensors device")
def get_device_sensors(
    device_id: int = Path(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """دریافت sensors اتصال‌شده به device"""
    from app.crud.sensor import get_sensors_by_device
    
    sensors = get_sensors_by_device(db, device_id)
    return BaseAPIResponse(result=sensors[skip:skip+limit])


@router.get("/protocol/{protocol}/active", response_model=BaseAPIResponse[List[Sensor]], summary="active sensors برای protocol")
def get_active_protocol_sensors(
    protocol: str = Path(...),
    sensor_type_id: int = Query(None, gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """دریافت sensors فعال برای protocol"""
    from app.crud.sensor import get_protocol_sensors_by_type
    
    sensors = get_protocol_sensors_by_type(db, protocol, sensor_type_id)
    return BaseAPIResponse(result=sensors[skip:skip+limit])


@router.post("/{sensor_id}/validate-protocol-config", response_model=BaseAPIResponse[dict], summary="تأیید protocol config")
def validate_protocol_config(
    sensor_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """تأیید protocol config سنسور"""
    from app.crud.sensor import validate_sensor_protocol_config
    
    sensor = get_sensor_by_id(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    is_valid = validate_sensor_protocol_config(
        db, sensor.sensor_type_id, sensor.config or {}
    )
    
    return BaseAPIResponse(result={
        "sensor_id": sensor_id,
        "protocol": sensor.sensor_type.protocol if sensor.sensor_type else None,
        "is_valid": is_valid,
        "pin_mapping": sensor.pin_mapping,
        "config": sensor.config
    })


@router.get("/protocol-types/{protocol}", response_model=BaseAPIResponse[List[SensorType]], summary="sensor types برای protocol")
def get_protocol_sensor_types(
    protocol: str = Path(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """دریافت sensor types برای protocol معین"""
    types = db.query(SensorTypeModel).filter(
        and_(
            SensorTypeModel.protocol == protocol,
            SensorTypeModel.is_deleted == False
        )
    ).offset(skip).limit(limit).all()
    
    return BaseAPIResponse(result=types)