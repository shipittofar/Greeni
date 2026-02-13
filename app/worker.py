from celery import Celery
import os

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")  # توجه: داخل داکر باید 'redis' باشه نه localhost
backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=backend_url
)

celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "default"},
}

# 🔹 مهم: import تمام تسک‌ها تا register بشن
import app.tasks.notifications_tasks
