import sys
import json
from pathlib import Path
from loguru import logger
import logging
import contextvars

# -------------------
# Context vars (برای اضافه کردن device_id / sensor_id / user_id / request_id)
# -------------------
request_id_var = contextvars.ContextVar("request_id", default=None)
device_id_var = contextvars.ContextVar("device_id", default=None)
sensor_id_var = contextvars.ContextVar("sensor_id", default=None)
user_id_var = contextvars.ContextVar("user_id", default=None)

# -------------------
# مسیر لاگ‌ها
# -------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# -------------------
# Serializer برای JSON structured logging
# -------------------
def serialize(record):
    extra = record["extra"].copy()
    # اضافه کردن context global
    extra["request_id"] = request_id_var.get()
    extra["device_id"] = device_id_var.get()
    extra["sensor_id"] = sensor_id_var.get()
    extra["user_id"] = user_id_var.get()

    return json.dumps({
        "timestamp": record["time"].strftime("%Y-%m-%dT%H:%M:%S"),
        "level": record["level"].name,
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        "exception": str(record["exception"]) if record["exception"] else None,
        "extra": extra
    })

# -------------------
# تنظیمات اصلی
# -------------------
def setup_logging():
    logger.remove()  # حذف هندلر پیش‌فرض

    # Console رنگی (برای dev)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level="DEBUG",
        backtrace=True,
        diagnose=True
    )

    # File JSON (structured logging)
    logger.add(
        LOG_DIR / "app.json",
        rotation="10 MB",
        retention="5 days",
        compression="zip",
        serialize=True,  # JSON
        level="INFO"
    )

    return logger

# -------------------
# Patch logging استاندارد پایتون برای هماهنگی
# -------------------
class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

def patch_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# -------------------
# Helper برای Context
# -------------------
def bind_context(request_id=None, device_id=None, sensor_id=None, user_id=None):
    if request_id:
        request_id_var.set(request_id)
    if device_id:
        device_id_var.set(device_id)
    if sensor_id:
        sensor_id_var.set(sensor_id)
    if user_id:
        user_id_var.set(user_id)
