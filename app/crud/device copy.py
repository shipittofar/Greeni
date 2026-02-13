import uuid as uuid_lib
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.sms.manager import SMSManager
from app.models.device import Device
from app.models.user import User
from app.crud.user import get_users_with_permission
from app.core.device_permissions import DEVICE_PENDING_NOTIFICATION
from app.core.level_permissions import FULL_PERMISSION
from app.schemas.notification import NotificationCreate
from app.api.v1.notifications import send_notification
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.core.config import settings
from app.models.sms_provider import SMSProvider

def get_device_by_id(db: Session, device_id: int) -> Optional[Device]:
    return (
        db.query(Device)
        .options(joinedload(Device.sensors))
        .filter(Device.id == device_id)
        .first()
    )

def get_device_by_code(db: Session, code: str) -> Optional[Device]:
    return db.query(Device).filter(Device.unique_code == code).first()

def get_all_devices(db: Session) -> List[Device]:
    return db.query(Device).filter(Device.is_pending == False).all()

def get_device_by_uuid(db: Session, uuid: str) -> Optional[Device]:
    return db.query(Device).filter(Device.uuid == uuid).first()

def get_pending_devices(db: Session) -> List[Device]:
    return db.query(Device).filter(Device.is_pending == True).all()

# ✅ ایجاد دستگاه به صورت معمولی (مثلاً توسط ادمین)
def create_device(
    db: Session,
    device_in: DeviceCreate,
    *,
    active: bool = True,
    online: bool = False
) -> Device:
    db_device = Device(
        unique_code=device_in.unique_code,
        name=device_in.name,
        description=device_in.description,
        location=device_in.location,
        ip_address=device_in.ip_address,
        mac_address= device_in.mac_address,
        lat=device_in.lat,
        lon=device_in.lon,
        time_zone=device_in.time_zone,
        icon=device_in.icon,
        product_name=device_in.product_name,
        product_id=device_in.product_id,
        category=device_in.category,
        local_key=device_in.local_key,
        uuid=uuid_lib.uuid4(),
        is_active=active,
        is_online=online,
        is_pending=False,                # 👈 توسط ادمین ثبت شده
        is_system_registered=False       # 👈 دستی بوده نه سیستمی
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

# ✅ ثبت دستگاه توسط سیستم (مثلاً Raspberry Pi)
def register_device(
    db: Session,
    device_in: DeviceCreate,
    *,
    ip_address: Optional[str] = None
) -> Device:
    # چک کن آیا دستگاه با MAC Address قبلاً ثبت شده یا نه
    db_device = db.query(Device).filter(Device.mac_address == device_in.mac_address).first()

    if db_device:
        # اگر دستگاه قبلاً ثبت شده، اطلاعات به‌روز بشه
        db_device.ip_address = ip_address or device_in.ip_address
        db_device.is_online = True
        db.commit()
        db.refresh(db_device)
        return db_device

    # ثبت دستگاه جدید
    new_device = Device(
        unique_code=device_in.unique_code,
        name=device_in.name,
        description=device_in.description,
        location=device_in.location,
        ip_address=ip_address or device_in.ip_address,
        mac_address=device_in.mac_address,
        lat=device_in.lat,
        lon=device_in.lon,
        time_zone=device_in.time_zone,
        icon=device_in.icon,
        product_name=device_in.product_name,
        product_id=device_in.product_id,
        category=device_in.category,
        local_key=device_in.local_key,
        uuid=uuid_lib.uuid4(),
        is_active=False,             # هنوز فعال نشده
        is_online=True,              # چون الان درخواست داده
        is_pending=True,             # منتظر تایید ادمین
        is_system_registered=True
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    # پیدا کردن کاربرانی که باید نوتیفیکیشن دریافت کنند
    notify_users = set(
        get_users_with_permission(db, DEVICE_PENDING_NOTIFICATION)
        + get_users_with_permission(db, FULL_PERMISSION)
    )

    active_provider = SMSProvider.get_active(db)  # provider فعال

    for user in notify_users:
        channels = []
        if user.phone_number:
            channels.append("sms")
        if user.email:
            channels.append("email")
        if user.push_token:
            channels.append("push")
        channels.append("inapp")  # همیشه

        for channel in channels:
            payload = {
                "recipient": (
                    user.phone_number if channel == "sms" else
                    user.email if channel == "email" else
                    user.push_token if channel == "push" else
                    user.id
                ),
                "channel": channel,
                "data": {
                    "device_name": new_device.name,
                    "mac_address": new_device.mac_address,
                    "location": new_device.location
                }
            }

            if channel == "sms":
                # اگر provider فعال smsir بود، template اضافه کن
                if active_provider and active_provider.name.lower() == "smsir":
                    payload["template"] = settings.SMS_PENDING_TEMPLATE
                # اگر provider فعال kavenegar بود، بدون template
                if active_provider and active_provider.name.lower() in ["kavenegar"]:
                    pass
                if active_provider is None:
                    continue  # ارسال SMS لغو می‌شود
            send_notification(payload)

    return new_device


def confirm_device(db: Session, db_device: Device) -> Device:
    db_device.is_pending = False
    db_device.is_active = True
    db_device.is_online = True
    db.commit()
    db.refresh(db_device)
    return db_device

# def reject_device(db: Session, db_device: Device) -> Device:
#     db_device.is_pending = False
#     db_device.is_active = False
#     db_device.is_online = False
#     db.commit()
#     db.refresh(db_device)
#     return db_device


# ✅ بروزرسانی دستگاه
def update_device(db: Session, db_device: Device, updates: DeviceUpdate) -> Device:
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_device, field, value)
    db.commit()
    db.refresh(db_device)
    return db_device

def update_devicev1(db: Session, db_device: Device, updates: DeviceUpdate) -> Device:
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_device, field, value)
    db.commit()
    db.refresh(db_device)
    return db_device

# ✅ حذف دستگاه + ارسال پیامک
def delete_device(db: Session, db_device: Device, current_user: User) -> None:
    db.delete(db_device)
    db.commit()

    if current_user.is_superuser and current_user.phone_number:
        message = f"دستگاه {db_device.name}"
        print(message)

        try:
            sms_manager = SMSManager(db)
            sms_manager.send_sms(current_user.phone_number, message)
        except Exception as e:
            print(f"خطا در ارسال پیامک: {e}")
