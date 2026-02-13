# app/tasks/notifications.py

from app.celery import celery_app
from app.db.session import SessionLocal

@celery_app.task(name="notifications.send")
def send_notification_task(payload: dict):
    from app.notifications.manager import NotificationManager
    db = SessionLocal()
    manager = NotificationManager(db)
    result = manager.send(payload)
    db.close()

    # فقط dict serializable برگردان
    if hasattr(result, "id"):  # اگر InAppNotification برگشت
        return {"id": result.id, "title": result.title, "message": result.message}

    return result

# from app.celery import celery_app
# from app.db.session import SessionLocal

# @celery_app.task(name="notifications.send")
# def send_notification_task(payload: dict):
#     from app.notifications.manager import NotificationManager
#     db = SessionLocal()
#     manager = NotificationManager(db)
#     return manager.send(payload)

