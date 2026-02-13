# app/bll/device_bll.py
from typing import Optional
from sqlalchemy.orm import Session
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.crud.device import register_device, set_online, set_offline, set_active, set_deactive
from app.bll.notification_bll import notify_users, notify_device_status_change

def register_device_bll(db: Session, device_in: DeviceCreate):
    """ثبت دستگاه جدید یا آپدیت دستگاه موجود + اطلاع‌رسانی به کاربران دارای پرمیشن."""
    device = register_device(db, device_in)
    print("start notify users")
    notify_users(db, device)
    print("done notify users")
    return device

# def status_online_device_bll(db: Session, device: Device) -> Device:
#     """آنلاین کردن دستگاه و ارسال نوتیفیکیشن وضعیت."""
#     device = set_online(db, device)
#     print("start notify users (online)")
#     notify_device_status_change(db, device, True)
#     print("done notify users (online)")
#     return device

# def status_offline_device_bll(db: Session, device: Device) -> Device:
#     """آفلاین کردن دستگاه و ارسال نوتیفیکیشن وضعیت."""
#     device = set_offline(db, device)
#     print("start notify users (offline)")
#     notify_device_status_change(db, device, False)
#     print("done notify users (offline)")
#     return device

# def status_activate_device_bll(db: Session, device: Device) -> Device:
#     """فعال کردن دستگاه و ارسال نوتیفیکیشن وضعیت."""
#     device = set_active(db, device)
#     print("start notify users (online)")
#     notify_device_status_change(db, device, True)
#     print("done notify users (online)")
#     return device

# def status_deactivate_device_bll(db: Session, device: Device) -> Device:
#     """غیرفعال کردن دستگاه و ارسال نوتیفیکیشن وضعیت."""
#     device = set_deactive(db, device)
#     print("start notify users (offline)")
#     notify_device_status_change(db, device, False)
#     print("done notify users (offline)")
#     return device

def status_online_device_bll(db: Session, device: Device) -> Device:
    device = set_online(db, device)
    print("start notify users (online)")
    notify_device_status_change(db, device, "online")
    print("done notify users (online)")
    return device

def status_offline_device_bll(db: Session, device: Device) -> Device:
    device = set_offline(db, device)
    print("start notify users (offline)")
    notify_device_status_change(db, device, "offline")
    print("done notify users (offline)")
    return device

def status_activate_device_bll(db: Session, device: Device) -> Device:
    device = set_active(db, device)
    print("start notify users (activate)")
    notify_device_status_change(db, device, "activate")
    print("done notify users (activate)")
    return device

def status_deactivate_device_bll(db: Session, device: Device) -> Device:
    device = set_deactive(db, device)
    print("start notify users (deactivate)")
    notify_device_status_change(db, device, "deactivate")
    print("done notify users (deactivate)")
    return device
