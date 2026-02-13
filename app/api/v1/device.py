from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate, DevicePublic, DeviceMultiMediaPublic
from app.crud.device import get_all_active_multimedia_device_codes

from app.schemas.common import BaseAPIResponse
from app.crud import device as crud_device
from app.schemas.device_full import DeviceFull
from app.models.sensor import Sensor
from app.models.sensor import SensorType
from app.models.sensor import SensorAttribute
from app.models.sensor import SensorAttributeValue
from app.bll.device_bll import register_device_bll,status_offline_device_bll,status_online_device_bll,status_activate_device_bll,status_deactivate_device_bll
from app.bll.notification_bll import notify_users

router = APIRouter(tags=["Devices"])

@router.get("/full", summary="Get all devices with full info", response_model=BaseAPIResponse[List[DeviceFull]])
def get_all_devices_full(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    devices = (
        db.query(Device)
        .options(
            joinedload(Device.sensors)
                .joinedload(Sensor.sensor_type)
                    .joinedload(SensorType.attributes),
            joinedload(Device.sensors)
                .joinedload(Sensor.attribute_values)
                    .joinedload(SensorAttributeValue.attribute),
        )
        # .filter(Device.is_deleted == False)
        .all()
    )
    return BaseAPIResponse(result=devices)

@router.get("/multimedia", summary="Get all active multimedia devices", response_model=BaseAPIResponse[List[DeviceMultiMediaPublic]])
def get_all_devices_multimedia(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    devices = get_all_active_multimedia_device_codes(db)
    return BaseAPIResponse(result=devices)


@router.get("/{device_id}/full", summary="Get one device with full info", response_model=BaseAPIResponse[DeviceFull])
def get_device_full_by_id(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = (
        db.query(Device)
        .options(
            joinedload(Device.sensors)
                .joinedload(Sensor.sensor_type)
                    .joinedload(SensorType.attributes),
            joinedload(Device.sensors)
                .joinedload(Sensor.attribute_values)
                    .joinedload(SensorAttributeValue.attribute),
        )
        # .filter(Device.id == device_id, Device.is_deleted == False)
        .filter(Device.id == device_id)
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return BaseAPIResponse(result=device)

@router.get("/pending", response_model=BaseAPIResponse[List[DevicePublic]])
def get_pending_devices(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can view pending devices")
    devices = crud_device.get_pending_devices(db)
    return BaseAPIResponse(result=devices)

# @router.post("/register", summary="Register a device (no authentication required)", response_model=BaseAPIResponse[DevicePublic])
# def register_device(device: DeviceCreate, db: Session = Depends(get_db)):
#     existing = crud_device.get_device_by_code(db, device.unique_code)
#     if existing:
#         raise HTTPException(status_code=409, detail="Device with this unique code already exists")
#     new_device = crud_device.register_device(db, device)
#     return BaseAPIResponse(result=new_device)

@router.post(
    "/register",
    summary="Register a device (no authentication required)",
    response_model=BaseAPIResponse[DevicePublic]
)
def register_device(device: DeviceCreate, db: Session = Depends(get_db)):
    existing = crud_device.get_device_by_code(db, device.unique_code)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Device with this unique code already exists"
        )

    new_device = register_device_bll(db, device)

    # ارسال نوتیفیکیشن بعد از ثبت موفق
    notify_users(db, new_device)

    return BaseAPIResponse(result=new_device)

@router.post("/", summary="Create a new device (admin)", response_model=BaseAPIResponse[DevicePublic])
def create_device(device: DeviceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = crud_device.get_device_by_code(db, device.unique_code)
    if existing:
        raise HTTPException(status_code=409, detail="Device with this unique code already exists")
    new_device = crud_device.create_device(db, device)
    return BaseAPIResponse(result=new_device)

@router.get("/", summary="Get all devices" , response_model=BaseAPIResponse[List[DevicePublic]])
def get_devices(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    devices = crud_device.get_all_devices(db)
    return BaseAPIResponse(result=devices)

@router.get("/half", summary="Get all devices half" , response_model=BaseAPIResponse[List[DevicePublic]])
def get_devices(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    devices = crud_device.get_all_devices(db)
    return BaseAPIResponse(result=devices)

@router.get("/by-unique-code/{code}", response_model=BaseAPIResponse[DevicePublic])
def get_device_by_unique_code(code: str, db: Session = Depends(get_db)):
    device = crud_device.get_device_by_code(db, code)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return BaseAPIResponse(result=device)

@router.get("/{unique_code}", response_model=BaseAPIResponse[DevicePublic])
def get_device_by_unique_code(unique_code: str, db: Session = Depends(get_db)):
    device = crud_device.get_device_by_code(db, unique_code)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return BaseAPIResponse(result=device)

@router.get("/{device_id}", response_model=BaseAPIResponse[DevicePublic])
def get_device_by_id(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    device = crud_device.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return BaseAPIResponse(result=device)

@router.patch("/{device_id}/confirm", response_model=BaseAPIResponse[DevicePublic])
def confirm_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can confirm devices")

    device = crud_device.get_device_by_id(db, device_id)
    if not device or not device.is_pending:
        raise HTTPException(status_code=404, detail="Pending device not found")

    confirmed_device = crud_device.confirm_device(db, device)
    return BaseAPIResponse(result=confirmed_device)


@router.delete("/{device_id}/reject", response_model=BaseAPIResponse[dict])
def reject_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can reject devices")

    device = crud_device.get_device_by_id(db, device_id)
    if not device or not device.is_pending:
        raise HTTPException(status_code=404, detail="Pending device not found")

    crud_device.delete_device(db, device, current_user)
    return BaseAPIResponse(result={"msg": "Device rejected and deleted"})


@router.patch("/{device_id}/activate", response_model=BaseAPIResponse[DevicePublic])
def activate_device(device_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can activate devices")

    device = crud_device.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    updated_device = status_activate_device_bll(db, device)
    return BaseAPIResponse(result=updated_device)

# ✅ PATCH - Deactivate Device
@router.patch("/{device_id}/deactivate", response_model=BaseAPIResponse[DevicePublic])
def deactivate_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can deactivate devices")
    
    device = crud_device.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    updated_device = status_deactivate_device_bll(db, device)
    
    return BaseAPIResponse(result=updated_device)



@router.patch("/{device_id}/on_line", response_model=BaseAPIResponse[DevicePublic])
def set_device_online(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can change device status")

    device = crud_device.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device = status_online_device_bll(db, device)
    return BaseAPIResponse(result=device)

@router.patch("/{device_id}/off_line", response_model=BaseAPIResponse[DevicePublic])
def set_device_offline(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can change device status")

    device = crud_device.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device = status_offline_device_bll(db, device)
    return BaseAPIResponse(result=device)

@router.patch("/{unique_code}/online", response_model=BaseAPIResponse[DevicePublic])
def device_set_online(unique_code: str, x_device_key: str = Header(...), db: Session = Depends(get_db)):
    device = crud_device.get_device_by_code(db, unique_code)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.local_key != x_device_key:
        raise HTTPException(status_code=403, detail="Invalid device key")
    device.is_online = True
    db.commit()
    db.refresh(device)
    return BaseAPIResponse(result=device)

@router.patch("/{unique_code}/offline", response_model=BaseAPIResponse[DevicePublic])
def device_set_offline(unique_code: str, x_device_key: str = Header(...), db: Session = Depends(get_db)):
    device = crud_device.get_device_by_code(db, unique_code)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.local_key != x_device_key:
        raise HTTPException(status_code=403, detail="Invalid device key")
    device.is_online = False
    db.commit()
    db.refresh(device)
    return BaseAPIResponse(result=device)

@router.patch("/{device_id}", response_model=BaseAPIResponse[DevicePublic])
def update_device(device_id: int, updates: DeviceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    device = crud_device.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    updated = crud_device.update_device(db, device, updates)
    return BaseAPIResponse(result=updated)

@router.put("/{device_id}", response_model=BaseAPIResponse[DevicePublic])
def update_device(device_id: int, updates: DeviceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    device = crud_device.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    updated = crud_device.update_devicev1(db, device, updates)
    return BaseAPIResponse(result=updated)

@router.delete("/{device_id}", response_model=BaseAPIResponse[dict])
def delete_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    device = crud_device.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    crud_device.delete_device(db, device, current_user)
    return BaseAPIResponse(result={"msg": "Device deleted successfully"})

@router.get("/status/{uuid}", summary="Check device approval status by UUID", response_model=BaseAPIResponse[dict])
def check_device_status(uuid: str, db: Session = Depends(get_db)):
    device = crud_device.get_device_by_uuid(db, uuid)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return BaseAPIResponse(result={
        "uuid": device.uuid,
        "is_approved": not device.is_pending
    })


@router.delete("/pending/{device_id}/reject", response_model=BaseAPIResponse[dict])
def reject_pending_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can reject devices")
    device = crud_device.get_device_by_id(db, device_id)
    if not device or device.is_active:
        raise HTTPException(status_code=404, detail="Pending device not found")
    crud_device.delete_device(db, device, current_user)
    return BaseAPIResponse(result={"msg": "Pending device rejected and deleted"})

# @router.post("/ping", summary="Device heartbeat", response_model=BaseAPIResponse[dict])
# def device_ping(unique_code: str, db: Session = Depends(get_db)):
#     device = crud_device.get_device_by_code(db, unique_code)
#     if not device:
#         raise HTTPException(status_code=404, detail="Device not found")

#     if not device.is_active or device.is_pending:
#         raise HTTPException(status_code=403, detail="Device not active or pending approval")

#     # فقط زمان آخرین پینگ رو ثبت کن، بدون تغییر وضعیت آنلاین
#     device.last_ping_at = datetime.utcnow()
#     db.commit()
#     db.refresh(device)

#     return BaseAPIResponse(result={"msg": "Ping received"})
