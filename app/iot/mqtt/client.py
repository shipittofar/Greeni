import sys
import json
import asyncio
import os
from dotenv import load_dotenv
from gmqtt import Client as MQTTClient
from loguru import logger

load_dotenv()

BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "greeni-device-client")
USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")
USE_TLS = os.getenv("MQTT_USE_TLS", "false").lower() == "true"

ssl_context = None
if USE_TLS:
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

# Logger setup
logger.remove()
logger.add(
    sink=sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}"
)
logger.add(
    sink="mqtt_logs.json",
    serialize=True,
    level="INFO"
)

mqtt_client = MQTTClient(CLIENT_ID)
_mqtt_connected_event = asyncio.Event()
_mqtt_task = None


async def on_connect(client, flags, rc, properties):
    logger.info("[MQTT] Connected")
    _mqtt_connected_event.set()
    client.subscribe("greeni/device/+/media/media_list", qos=0)


async def on_message(client, topic, payload, qos, properties):
    try:
        # decode فقط همینجا
        if isinstance(payload, bytes):
            payload = payload.decode()

        if isinstance(payload, str):
            data = json.loads(payload)
        elif isinstance(payload, dict):
            data = payload
        else:
            raise TypeError(f"Unexpected payload type: {type(payload)}")

        device_id = topic.split("/")[2] if len(topic.split("/")) > 2 else None
        logger.bind(device_id=device_id).info(f"Received message: {data}")

        from app.iot.mqtt.handler import handle_message
        # ⚠️ توجه: اینجا دیگه نیازی نیست دوباره json.loads توی handle_message بزنی
        asyncio.create_task(handle_message(topic, data))

    except Exception as e:
        logger.exception(f"Failed to handle message from topic {topic}: {e}")


# async def start_mqtt_loop():
#     global _mqtt_task

#     mqtt_client.on_connect = lambda c, f, r, p: asyncio.create_task(on_connect(c, f, r, p))
#     mqtt_client.on_message = lambda c, t, p, q, pr: asyncio.create_task(on_message(c, t, p, q, pr))

#     mqtt_client.set_auth_credentials(USERNAME, PASSWORD)

#     await mqtt_client.connect(BROKER_HOST, BROKER_PORT, ssl=ssl_context)
#     await _mqtt_connected_event.wait()
#     logger.info("[MQTT] Ready")

#     _mqtt_task = asyncio.create_task(mqtt_client.listen())
#     logger.info("[MQTT] Listen task started")
#     await _mqtt_task

async def start_mqtt_loop():
    global _mqtt_task

    mqtt_client.on_connect = lambda c, f, r, p: asyncio.create_task(on_connect(c, f, r, p))
    mqtt_client.on_message = lambda c, t, p, q, pr: asyncio.create_task(on_message(c, t, p, q, pr))

    mqtt_client.set_auth_credentials(USERNAME, PASSWORD)

    # اتصال به بروکر
    await mqtt_client.connect(BROKER_HOST, BROKER_PORT, ssl=ssl_context)

    # صبر کن تا connected event فعال بشه
    await _mqtt_connected_event.wait()
    logger.info("[MQTT] Ready")


def mqtt_publish(topic: str, payload: dict, device_id: str = None):
    if not _mqtt_connected_event.is_set():
        logger.warning("⚠ MQTT not connected yet")
        return
    mqtt_client.publish(topic, json.dumps(payload))
    logger.bind(device_id=device_id).info(f"[MQTT] Published to {topic}: {payload}")


# async def shutdown_mqtt():
#     if _mqtt_task:
#         _mqtt_task.cancel()
#         try:
#             await _mqtt_task
#         except asyncio.CancelledError:
#             pass
#     await mqtt_client.disconnect()
#     logger.info("[MQTT] Disconnected cleanly")

async def shutdown_mqtt():
    await mqtt_client.disconnect()
    logger.info("[MQTT] Disconnected cleanly")
