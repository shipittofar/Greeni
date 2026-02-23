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
CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "greeni-server")
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
_mqtt_listen_task = None  # tracks the inner listen coroutine


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

async def on_connect(client, flags, rc, properties):
    logger.info("[MQTT] Connected to broker")
    _mqtt_connected_event.set()

    # Subscribe to all uplink topics
    client.subscribe("greeni/device/+/media/media_list", qos=1)
    client.subscribe("greeni/device/+/commands/status", qos=1)
    client.subscribe("greeni/device/+/data", qos=1)
    client.subscribe("greeni/device/+/system/info", qos=0)
    logger.info("[MQTT] Subscribed to all device topics")


async def on_disconnect(client, packet, exc=None):
    _mqtt_connected_event.clear()
    logger.warning("[MQTT] Disconnected from broker")


async def on_message(client, topic: str, payload, qos, properties):
    try:
        if isinstance(payload, bytes):
            payload = payload.decode()

        if isinstance(payload, str):
            data = json.loads(payload)
        elif isinstance(payload, dict):
            data = payload
        else:
            raise TypeError(f"Unexpected payload type: {type(payload)}")

        device_id = topic.split("/")[2] if len(topic.split("/")) > 2 else None
        logger.bind(device_id=device_id).info(f"[MQTT] Message on '{topic}': {data}")

        from app.iot.mqtt.handler import handle_message
        asyncio.create_task(handle_message(topic, data))

    except json.JSONDecodeError as e:
        logger.error(f"[MQTT] Invalid JSON on topic '{topic}': {e}")
    except Exception as e:
        logger.exception(f"[MQTT] Failed to handle message from topic '{topic}': {e}")


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

async def start_mqtt_loop():
    """
    Connect to the MQTT broker, subscribe to all topics, then run the
    blocking listen loop.  This coroutine only returns when the listen
    task is cancelled (e.g. on application shutdown).
    """
    global _mqtt_listen_task

    mqtt_client.on_connect = lambda c, f, r, p: asyncio.create_task(on_connect(c, f, r, p))
    mqtt_client.on_disconnect = lambda c, pkt, exc=None: asyncio.create_task(on_disconnect(c, pkt, exc))
    mqtt_client.on_message = lambda c, t, p, q, pr: asyncio.create_task(on_message(c, t, p, q, pr))

    if USERNAME:
        mqtt_client.set_auth_credentials(USERNAME, PASSWORD)

    await mqtt_client.connect(BROKER_HOST, BROKER_PORT, ssl=ssl_context)

    # Wait until the on_connect callback fires
    await _mqtt_connected_event.wait()
    logger.info("[MQTT] Ready — starting listen loop")

    # gmqtt's listen() is a blocking coroutine that drives the I/O loop.
    # Wrap it in a task so shutdown_mqtt() can cancel it independently.
    _mqtt_listen_task = asyncio.create_task(mqtt_client.listen())
    try:
        await _mqtt_listen_task
    except asyncio.CancelledError:
        logger.info("[MQTT] Listen task cancelled")
        raise  # propagate so main.py can await the outer task cleanly


async def shutdown_mqtt():
    """Cancel the listen task and disconnect cleanly."""
    global _mqtt_listen_task

    if _mqtt_listen_task and not _mqtt_listen_task.done():
        _mqtt_listen_task.cancel()
        try:
            await _mqtt_listen_task
        except asyncio.CancelledError:
            pass

    try:
        await mqtt_client.disconnect()
        logger.info("[MQTT] Disconnected cleanly")
    except Exception as e:
        logger.warning(f"[MQTT] Error during disconnect: {e}")


# ---------------------------------------------------------------------------
# Publish helper
# ---------------------------------------------------------------------------

def mqtt_publish(topic: str, payload: dict, device_id: str = None, qos: int = 1):
    """
    Synchronous publish helper — safe to call from sync or async context.
    gmqtt.publish() is non-blocking internally (it queues the message).
    """
    if not _mqtt_connected_event.is_set():
        logger.warning(f"[MQTT] Cannot publish — not connected (topic={topic})")
        return False

    try:
        mqtt_client.publish(topic, json.dumps(payload), qos=qos)
        logger.bind(device_id=device_id).info(f"[MQTT] Published to '{topic}': {payload}")
        return True
    except Exception as e:
        logger.error(f"[MQTT] Publish failed (topic={topic}): {e}")
        return False
