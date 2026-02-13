# app/core/healthcheck.py
from sqlalchemy import text
from app.db.session import SessionLocal
from app.cache.redis import redis_client
from app.celery import celery_app
from app.iot.mqtt.client import mqtt_client


async def check_database():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return "ok"
    except Exception as e:
        return f"error: {str(e)}"
    finally:
        db.close()


async def check_redis():
    try:
        pong = await redis_client.ping()
        return "ok" if pong else "error"
    except Exception as e:
        return f"error: {str(e)}"


async def check_mqtt():
    try:
        if mqtt_client.is_connected:   # بدون ()
            return "ok"
        return "disconnected"
    except Exception as e:
        return f"error: {str(e)}"


async def check_celery():
    try:
        res = celery_app.control.ping(timeout=1)  # ping workers
        return "ok" if res else "no workers"
    except Exception as e:
        return f"error: {str(e)}"



async def run_health_checks():
    results = {}
    results["database"] = await check_database()
    results["redis"] = await check_redis()
    results["mqtt"] = await check_mqtt()
    results["celery"] = await check_celery()

    status = "ok" if all(v == "ok" for v in results.values()) else "degraded"
    return {"status": status, "services": results}
