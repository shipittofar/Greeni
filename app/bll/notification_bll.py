# app/bll/notification_bll.py

from typing import Optional, List, Dict
from app.core.config import settings
from app.api.v1.notifications import send_notification
from app.crud.sms_provider import CRUDSMSProvider
from app.crud.user import get_users_with_permission
from app.core.device_permissions import DEVICE_PENDING_NOTIFICATION
from app.core.level_permissions import FULL_PERMISSION
from app.tasks.notifications_tasks import send_notification_task
from app.api.v1.ws.notifications import send_to_user
import asyncio

def get_notify_users(db) -> List:
    """کاربران دارای پرمیشن‌های لازم را استخراج و یکتا می‌کند."""
    users_with_device_perm = get_users_with_permission(db, DEVICE_PENDING_NOTIFICATION)
    users_with_full_perm = get_users_with_permission(db, FULL_PERMISSION)
    user_map = {u.id: u for u in (users_with_device_perm + users_with_full_perm)}
    return list(user_map.values())

def get_user_channels(user) -> List[str]:
    """بر اساس مشخصات کاربر کانال‌های ارسال انتخاب می‌شوند."""
    channels = []
    if user.phone_number:
        channels.append("sms")
    if user.email:
        channels.append("email")
    channels.append("inapp")  # همیشه
    return channels

def build_payload(user, channel: str, device, active_sms_provider: Optional[str]) -> Optional[Dict]:
    """برای هر کاربر و کانال یک payload استاندارد می‌سازد."""
    recipient = (
        user.phone_number if channel == "sms" else
        user.email if channel == "email" else
        user.id
    )

    payload = {
        "recipient": recipient,
        "channel": channel,
        "data": {"DEVICE": device.name}
    }

    if channel == "sms":
        if not active_sms_provider:
            return None
        provider = active_sms_provider.lower()
        if provider == "smsir":
            payload["template"] = settings.SMS_PENDING_TEMPLATE
        # kavenegar → بدون template
    return payload

# def notify_users(db, device):
#     """کاربران دارای پرمیشن را پیدا کرده و برای هر کدام نوتیفیکیشن بفرستد."""
#     notify_users = get_notify_users(db)
#     active_provider_obj = CRUDSMSProvider.get_active(db)
#     active_sms_provider = active_provider_obj.name if active_provider_obj else None

#     for user in notify_users:
#         channels = get_user_channels(user)
#         for channel in channels:
#             payload = build_payload(user, channel, device, active_sms_provider)
#             if payload:
#                 send_notification(payload)
#                 print(f"Sending {channel} to {user.id}")

def notify_users(db, device):
    notify_users = get_notify_users(db)
    active_provider_obj = CRUDSMSProvider.get_active(db)
    active_sms_provider = active_provider_obj.name if active_provider_obj else None

    for user in notify_users:
        channels = get_user_channels(user)
        for channel in channels:
            payload = build_payload(user, channel, device, active_sms_provider)
            if payload:
                send_notification_task.delay(payload)   # Celery async
                print(f"Queued {channel} notification for {user.id}")

def notify_device_status_change(db, device, event_type: str):
    """برای تغییر وضعیت دستگاه: فقط push و inapp."""
    status_text_map = {
        "online": "Online",
        "offline": "Offline",
        "activate": "Activated",
        "deactivate": "Deactivated",
    }

    status_text = status_text_map.get(event_type, "Unknown")

    notify_users = get_notify_users(db)
    for user in notify_users:
        for channel in ["push", "inapp"]:
            recipient = user.email if channel == "push" else str(user.id)

            payload = {
                "recipient": recipient,
                "channel": channel,
                "template": "device_status_change",
                "data": {
                    "ID": device.id,
                    "DEVICE": device.name,
                    "STATUS": status_text,
                },
            }

            # 📤 ارسال به صف Celery
            send_notification_task.delay(payload)
            print(f"Queued {channel} notification for {recipient} (device {device.id})")

            # 🛰️ ارسال لحظه‌ای در صورت آنلاین بودن کاربر
            if channel == "inapp":
                try:
                    asyncio.run(send_to_user(str(user.id), {
                        "title": f"Device {status_text}",
                        "message": f"{device.name} is now {status_text}"
                    }))
                except RuntimeError:
                    loop = asyncio.get_event_loop()
                    loop.create_task(send_to_user(str(user.id), {
                        "title": f"Device {status_text}",
                        "message": f"{device.name} is now {status_text}"
                    }))