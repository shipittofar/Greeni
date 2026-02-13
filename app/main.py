from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from fastapi.staticfiles import StaticFiles
import os
import json
from app.core.config import settings

import asyncio
from uuid import uuid4

from app.api.v1 import api_router
from app.db.session import SessionLocal
from app.db.init_data import init_data
from app.core.healthcheck import run_health_checks
from app.api.v1.ws import system_health
from app.iot.mqtt.client import start_mqtt_loop
from app.core.logging_config import setup_logging, patch_logging, bind_context
import redis.asyncio as aioredis

logger = setup_logging()
patch_logging()

app = FastAPI(
    title="Greeni Management API",
    version="04.05.05",
    description="Backend API for Smart Greenhouse Management",
    swagger_ui_parameters={
        "docExpansion": "none",   # یا "list", یا "full"
        "defaultModelsExpandDepth": -1,  # برای بستن کامل مدل‌ها
    }
)

# Include v1 API
app.include_router(api_router, prefix="/v1/api")

# OAuth2 for Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/api/auth/token")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production باید محدودتر باشه
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True, mode=0o777)  # فولدر با دسترسی خواندن و نوشتن
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Health check router
app.include_router(system_health.router, prefix="/v1/ws", tags=["System WS"])

@app.get("/health", summary="Health Check", tags=["System"])
async def health_check():
    result = await run_health_checks()
    logger.info("Health check executed", extra={"health_status": result})
    return result

redis_task = None

async def redis_listener():
    redis_conn = await aioredis.from_url(settings.REDIS_URL)
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe("notifications")
    logger.info("📡 Redis listener for notifications started")

    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg is None:
                await asyncio.sleep(0.1)
                continue
            try:
                data = json.loads(msg["data"])
                user_id = str(data.get("user_id"))
                from app.api.v1.ws.notifications import send_to_user
                await send_to_user(user_id, data)
                logger.debug(f"📨 Delivered notification to user {user_id}")
            except Exception as e:
                logger.exception(f"❌ Error processing notification: {e}")
    except asyncio.CancelledError:
        logger.info("🛑 Redis listener cancelled")
    finally:
        try:
            await pubsub.unsubscribe("notifications")
            await pubsub.close()
        except Exception as e:
            logger.warning(f"⚠️ Error closing pubsub: {e}")
        try:
            await redis_conn.close()
        except Exception as e:
            logger.warning(f"⚠️ Error closing redis conn: {e}")
        logger.info("🔌 Redis listener closed cleanly")


# -------------------
# Middleware برای ست کردن request_id خودکار
# -------------------
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    bind_context(request_id=str(uuid4()))
    response = await call_next(request)
    return response

# -------------------
# MQTT و DB Startup/Shutdown
# -------------------
mqtt_task = None

@app.on_event("startup")
async def startup_event():
    global redis_task, mqtt_task
    logger.info("🚀 Starting application...")
    try:
        # Redis listener
        redis_task = asyncio.create_task(redis_listener())

        # MQTT loop
        mqtt_task = asyncio.create_task(start_mqtt_loop())

        # init DB data
        db = SessionLocal()
        try:
            init_data(db)
            logger.info("✅ Initial data loaded successfully")
        finally:
            db.close()
    except Exception:
        logger.exception("❌ Error during startup")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    global redis_task, mqtt_task
    logger.info("🛑 Shutting down application...")
    if redis_task:
        redis_task.cancel()
        try:
            await redis_task
        except asyncio.CancelledError:
            logger.info("Redis listener cancelled")
    if mqtt_task:
        mqtt_task.cancel()
        try:
            await mqtt_task
            logger.info("MQTT Task cancelled cleanly")
        except asyncio.CancelledError:
            logger.warning("MQTT Task cancellation interrupted")

# -------------------
# Custom OpenAPI for Swagger OAuth2
# -------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/v1/api/auth/token",
                    "scopes": {},
                }
            },
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"OAuth2": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
